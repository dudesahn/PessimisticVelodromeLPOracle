// SPDX-License-Identifier: AGLP-3.0
pragma solidity ^0.8.19;

import {IERC4626} from "@openzeppelin/contracts@4.9.3/interfaces/IERC4626.sol";
import {IYearnVaultV2} from "./interfaces/IYearnVaultV2.sol";
import {IVeloPool} from "./interfaces/IVeloPool.sol";
import {IChainLinkOracle} from "./interfaces/IChainLinkOracle.sol";
import {ShareValueHelper} from "./ShareValueHelper.sol";
import {FixedPointMathLib} from "./FixedPointMathLib.sol";

/**
 * @title Velodrome LP Pessimistic Oracle
 * @author Yearn Finance
 * @notice This oracle may be used to price Velodrome-style LP pools (both vAMM and sAMM) in a manipulation-resistant
 *  manner. A pool must contain at least one asset with a Chainlink feed to be valid. If only one asset has a Chainlink
 *  feed, an internal TWAP may be used to price the other asset , with a default 2 hour window. Version 2.0.0 added
 *  view functions for pricing V2 and V3 Yearn vault tokens built on top of Velodrome LPs.
 *
 *  The pessimistic oracle stores daily lows, and prices are checked over the past two (or three) days of stored data
 *  when calculating an LP's value. A manual price cap (upper and lower bounds) may be enabled to further limit the
 *  impact of manipulations in a given direction. Note that manual price caps (just as the ability to set price feeds)
 *  are the main centralization risk of an oracle such as this, and if used, should be treated with great consideration.
 *
 *  With this oracle, price manipulation attacks are substantially more difficult, as an attacker needs to log
 *  artificially high lows but still come in under any price cap (if set). Additionally, if three-day lows are used, the
 *  oracle becomes more robust for public price updates, as the minimum time covered by all observations jumps from two
 *  seconds (two-day window) to 24 hours (three-day window). However, using the pessimistic oracle does have the
 *  disadvantage of reducing borrow power of borrowers to a multi-day minimum value of their collateral, where the price
 *  also must have been seen by the oracle.
 *
 *  This work builds on that of Inverse Finance (pessimistic pricing oracle), Alpha Homora (x*y=k fair reserves) and
 *  VMEX (xy^3+yx^3=k fair reserves derivation).
 */

contract PessimisticVelodromeLPOracle {
    struct FeedInfo {
        address feedAddress;
        uint96 heartbeat;
    }

    /* ========== STATE VARIABLES ========== */

    /// @notice Daily low price stored per token.
    mapping(address => mapping(uint256 => uint256)) public dailyLows; // token => day => price

    /// @notice Number of times a token's price was checked on a given day.
    mapping(address => mapping(uint256 => uint256)) public dailyUpdates; // token => day => number of updates

    /// @notice A hard upper bound on our LP token price. This puts a cap on bad debt from oracle errors in a market.
    /// @dev May only be updated by operator.
    mapping(address => uint256) public upperPriceBound;

    /// @notice A hard lower bound on our LP token price. This helps prevent liquidations from artificially low prices.
    /// @dev May only be updated by operator.
    mapping(address => uint256) public lowerPriceBound;

    /// @notice Whether we use our pessimistic pricing or not, along with our upper and lower price bounds.
    /// @dev May only be updated by operator.
    bool public useAdjustedPricing = true;

    /// @notice Whether we use a three-day low instead of a two-day low.
    /// @dev May only be updated by operator. Realistically most useful when price updating is public, as this
    ///  guarantees any price observations used must be at least 24 hours apart.
    bool public useThreeDayLow = false;

    /// @notice Whether we only use Chainlink feeds or allow TWAP for one of the two assets.
    /// @dev May only be updated by operator.
    bool public useChainlinkOnly = false;

    /// @notice Address of the Chainlink price feed for a given underlying token.
    /// @dev May only be updated by operator.
    mapping(address => FeedInfo) public feeds;

    /// @notice Custom number of periods our TWAP price should cover.
    /// @dev May only be updated by operator, default is 4 (2 hours).
    mapping(address => uint256) public pointsOverride;

    /// @notice Chainlink feed to check that Optimism's sequencer is online.
    /// @dev This prevents transactions sent while the sequencer is down from being executed when it comes back online.
    IChainLinkOracle public constant sequencerUptimeFeed =
        IChainLinkOracle(0x371EAD81c9102C9BF4874A9075FFFf170F2Ee389);

    /// @notice Check if an address can update our LP pricing.
    /// @dev May only be updated by operator.
    mapping(address => bool) public priceUpdatooors;

    /// @notice Role that controls permissioned functions and setters.
    address public operator;

    /// @notice Pending operator must accept the role before it can be transferred.
    /// @dev This can help prevent setting to incorrect addresses.
    address public pendingOperator;

    /// @notice The default number of periods (points) we look back in time for TWAP pricing.
    /// @dev Each period is 30 mins, so default is 2 hours. Override via pointsOverride if needed.
    uint256 public constant DEFAULT_POINTS = 4;

    /// @notice Used to track the deployed version of this contract.
    string public constant apiVersion = "2.0.0";

    // our pool/LP token decimals, just in case velodrome has weird pools in the future with different decimals
    uint256 internal constant DECIMALS = 10 ** 18;

    /* ========== CONSTRUCTOR ========== */

    constructor(address _operator) {
        operator = _operator;
        priceUpdatooors[_operator] = true;
    }

    /* ========== EVENTS/MODIFIERS ========== */

    event RecordDailyLow(address indexed token, uint256 price);
    event ManualPriceCapsUpdated(
        address indexed token,
        uint256 upperPriceCap,
        uint256 lowerPriceCap
    );
    event UpdatedPointsOverride(address pool, uint256 points);
    event ChangeOperator(address indexed newOperator);
    event SetTokenFeed(
        address indexed token,
        address indexed feed,
        uint96 heartbeat
    );
    event SetUseAdjustedPricing(bool useAdjusted, bool useThreeDayWindow);
    event SetUseChainlinkOnly(bool onlyChainlink);
    event ApprovedPriceUpdatooor(address account, bool canEndorse);

    modifier onlyOperator() {
        require(msg.sender == operator, "ONLY OPERATOR");
        _;
    }

    /* ========== VIEW FUNCTIONS ========== */

    /**
     * @notice Check the last time a token's Chainlink price was updated.
     * @dev Useful for external checks if a price is stale.
     * @param _token The address of the token to get the price of.
     * @return updatedAt The timestamp of our last price update.
     */
    function chainlinkPriceLastUpdated(
        address _token
    ) external view returns (uint256 updatedAt) {
        (, , , updatedAt, ) = IChainLinkOracle(feeds[_token].feedAddress)
            .latestRoundData();
    }

    /// @notice Current day used for storing daily lows.
    /// @dev Note that this is in unix time.
    function currentDay() public view returns (uint256) {
        return block.timestamp / 1 days;
    }

    /*
     * @notice Gets the current price of Yearn V3 Velodrome vault token.
     * @dev Will use fair reserves and pessimistic pricing if enabled, and account for vault profits.
     * @param _pool LP token whose price we want to check.
     * @return The current price of one LP token.
     */
    function getCurrentVaultPriceV3(
        address _vault
    ) external view returns (uint256) {
        IERC4626 vault = IERC4626(_vault);
        address _pool = vault.asset();

        if (useAdjustedPricing) {
            return
                (_getAdjustedPrice(_pool) * vault.convertToAssets(DECIMALS)) /
                DECIMALS;
        } else {
            return
                (_getFairReservesPricing(_pool) *
                    vault.convertToAssets(DECIMALS)) / DECIMALS;
        }
    }

    /*
     * @notice Gets the current price of Yearn V2 Velodrome vault token.
     * @dev Will use fair reserves and pessimistic pricing if enabled, and account for vault profits.
     * @param _pool LP token whose price we want to check.
     * @return The current price of one LP token.
     */
    function getCurrentVaultPriceV2(
        address _vault
    ) external view returns (uint256) {
        IYearnVaultV2 vault = IYearnVaultV2(_vault);
        address _pool = vault.token();

        if (useAdjustedPricing) {
            return
                (_getAdjustedPrice(_pool) *
                    ShareValueHelper.sharesToAmount(_vault, DECIMALS)) /
                DECIMALS;
        } else {
            return
                (_getFairReservesPricing(_pool) *
                    ShareValueHelper.sharesToAmount(_vault, DECIMALS)) /
                DECIMALS;
        }
    }

    /*
     * @notice Gets the current price of a given Velodrome LP token.
     * @dev Will use fair reserves and pessimistic pricing if enabled.
     * @param _pool LP token whose price we want to check.
     * @return The current price of one LP token.
     */
    function getCurrentPoolPrice(
        address _pool
    ) external view returns (uint256) {
        if (useAdjustedPricing) {
            return _getAdjustedPrice(_pool);
        } else {
            return _getFairReservesPricing(_pool);
        }
    }

    /**
     * @notice Returns the Chainlink feed price of the given token address.
     * @dev Will revert if price is negative or feed is not added.
     * @param _token The address of the token to get the price of.
     * @return currentPrice The current price of the underlying token.
     */
    function getChainlinkPrice(
        address _token
    ) public view returns (uint256 currentPrice) {
        (, int256 price, , uint256 updatedAt, ) = IChainLinkOracle(
            feeds[_token].feedAddress
        ).latestRoundData();

        // we always expect 8 decimals for USD pricing
        if (IChainLinkOracle(feeds[_token].feedAddress).decimals() != 8) {
            revert("Must be 8 decimals");
        }

        // you mean we can't have negative prices?
        if (price <= 0) {
            revert("Invalid feed price");
        }

        // if a price is older than our preset heartbeat, we're in trouble
        if (block.timestamp - updatedAt > feeds[_token].heartbeat) {
            revert("Price is stale");
        }

        // make sure the sequencer is up
        // uint80 roundID int256 sequencerAnswer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound
        (, int256 sequencerAnswer, , , ) = sequencerUptimeFeed
            .latestRoundData();

        // Answer == 0: Sequencer is up
        // Answer == 1: Sequencer is down
        if (sequencerAnswer == 1) {
            revert("L2 sequencer down");
        }
        currentPrice = uint256(price);
    }

    /**
     * @notice Returns the TWAP price for a token relative to the other token in its pool.
     * @dev Note that we can customize the length of points but we default to 4 points (2 hours).
     * @param _pool The address of the LP (pool) token we are using to price our assets with.
     * @param _token The address of the token to get the price of, and that we are swapping in.
     * @param _oneToken One of the token we are swapping in.
     * @return twapPrice Amount of the other token we get when swapping in _oneToken looking back over our TWAP period.
     */
    function getTwapPrice(
        address _pool,
        address _token,
        uint256 _oneToken
    ) public view returns (uint256 twapPrice) {
        IVeloPool pool = IVeloPool(_pool);

        // how far back in time should we look?
        uint256 points = pointsOverride[_pool];
        if (points == 0) {
            points = DEFAULT_POINTS;
        }

        // swapping one of our token gets us this many otherToken, returned in decimals of the other token
        twapPrice = pool.quote(_token, _oneToken, points);
    }

    function getTokenPrices(
        address _pool
    ) public view returns (uint256 price0, uint256 price1) {
        IVeloPool pool = IVeloPool(_pool);
        (
            uint256 decimals0, // note that this will be "1e18"", not "18"
            uint256 decimals1,
            ,
            ,
            ,
            address token0,
            address token1
        ) = pool.metadata();

        // check if we have chainlink feeds or TWAP for each token
        if (feeds[token0].feedAddress != address(0)) {
            price0 = getChainlinkPrice(token0); // returned with 8 decimals
            if (feeds[token1].feedAddress != address(0)) {
                price1 = getChainlinkPrice(token1); // returned with 8 decimals
            } else {
                // revert if we are supposed to only use chainlink
                if (useChainlinkOnly) {
                    revert("Only Chainlink feeds supported");
                }

                // get twap price for token1. this is the amount of token1 we would get from 1 token0
                price1 =
                    (decimals1 * decimals1) /
                    getTwapPrice(_pool, token0, decimals0); // returned in decimals1
                price1 = (price0 * price1) / (decimals1);
            }
        } else if (feeds[token1].feedAddress != address(0)) {
            price1 = getChainlinkPrice(token1); // returned with 8 decimals
            // get twap price for token0
            price0 =
                (decimals0 * decimals0) /
                getTwapPrice(_pool, token1, decimals1); // returned in decimals0
            price0 = (price0 * price1) / (decimals0);
        } else {
            revert("At least one token must have CL oracle");
        }
    }

    /* ========== MUTATIVE FUNCTIONS ========== */

    /// @notice Checks current token price and saves the price if it is the day's lowest.
    /// @dev This may only be called by approved addresses; the more frequently it is called the better.
    // @param _pool LP token to update pricing for.
    function updatePrice(address _pool) external {
        // don't let just anyone update deez prices
        require(priceUpdatooors[msg.sender], "unauthorized");

        _updatePrice(_pool);
    }

    /// @notice Checks current LP token prices and saves the price if it is the day's lowest.
    /// @dev This may only be called by approved addresses; the more frequently it is called the better.
    // @param _pools Array of LP token to update pricing for.
    function updateManyPrices(address[] memory _pools) external {
        // don't let just anyone update deez prices
        require(priceUpdatooors[msg.sender], "unauthorized");

        for (uint256 i; i < _pools.length; ++i) {
            address _pool = _pools[i];
            _updatePrice(_pool);
        }
    }

    // internal logic to update our stored daily low pool prices
    function _updatePrice(address _pool) internal {
        // get current fair reserves pricing
        uint256 currentPrice = _getFairReservesPricing(_pool);

        // increment our counter whether we store the price or not
        uint256 day = currentDay();
        dailyUpdates[_pool][day] += 1;

        // store price if it's today's low
        uint256 todaysLow = dailyLows[_pool][day];
        if (todaysLow == 0 || currentPrice < todaysLow) {
            dailyLows[_pool][day] = currentPrice;
            emit RecordDailyLow(_pool, currentPrice);
        }
    }

    /* ========== HELPER VIEW FUNCTIONS ========== */

    // adjust our reported pool price as needed for 48-hour lows and hard upper/lower limits
    function _getAdjustedPrice(
        address _pool
    ) internal view returns (uint256 adjustedPrice) {
        // start off with our standard price
        uint256 currentPrice = _getFairReservesPricing(_pool);
        uint256 day = currentDay();

        // get today's low
        uint256 todaysLow = dailyLows[_pool][day];
        if (todaysLow == 0 || currentPrice < todaysLow) {
            todaysLow = currentPrice;
        }

        // get yesterday's low
        uint256 yesterdaysLow = dailyLows[_pool][day - 1];

        // calculate price based on two-day low
        adjustedPrice = todaysLow > yesterdaysLow && yesterdaysLow > 0
            ? yesterdaysLow
            : todaysLow;

        // if using three-day low, compare again
        if (useThreeDayLow) {
            uint256 dayBeforeYesterdaysLow = dailyLows[_pool][day - 2];
            adjustedPrice = adjustedPrice > dayBeforeYesterdaysLow &&
                dayBeforeYesterdaysLow > 0
                ? dayBeforeYesterdaysLow
                : adjustedPrice;
        }

        // use a hard cap to protect against oracle pricing errors
        uint256 upperBound = upperPriceBound[_pool];
        uint256 lowerBound = lowerPriceBound[_pool];

        if (upperBound > 0 && adjustedPrice > upperBound) {
            revert("Price above upper bound");
        } else if (adjustedPrice < lowerBound) {
            revert("Price below lower bound");
        }
    }

    // calculate price based on fair reserves, not spot reserves
    function _getFairReservesPricing(
        address _pool
    ) internal view returns (uint256 fairReservesPricing) {
        // get what we need to calculate our reserves and pricing
        IVeloPool pool = IVeloPool(_pool);
        if (pool.decimals() != 18) {
            revert("Lp token must have 18 decimals");
        }
        (
            uint256 decimals0, // note that this will be "1e18"", not "18"
            uint256 decimals1,
            uint256 reserve0,
            uint256 reserve1,
            ,
            ,

        ) = pool.metadata();

        // make sure our reserves are normalized to 18 decimals (looking at you, USDC)
        reserve0 = (reserve0 * DECIMALS) / decimals0;
        reserve1 = (reserve1 * DECIMALS) / decimals1;

        // pull our prices
        (uint256 price0, uint256 price1) = getTokenPrices(_pool);

        if (pool.stable()) {
            fairReservesPricing = _calculate_stable_lp_token_price(
                pool.totalSupply(),
                price0,
                price1,
                reserve0,
                reserve1,
                8
            );
        } else {
            uint256 k = FixedPointMathLib.sqrt(reserve0 * reserve1); // xy = k, p0r0' = p1r1', this is in 1e18
            uint256 p = FixedPointMathLib.sqrt(price0 * 1e16 * price1); // boost this to 1e16 to give us more precision

            // we want k and total supply to have same number of decimals so price has decimals of chainlink oracle
            fairReservesPricing = (2 * p * k) / (1e8 * pool.totalSupply());
        }
    }

    //solves for cases where curve is x^3 * y + y^3 * x = k
    //fair reserves math formula author: @ksyao2002
    function _calculate_stable_lp_token_price(
        uint256 total_supply,
        uint256 price0,
        uint256 price1,
        uint256 reserve0,
        uint256 reserve1,
        uint256 priceDecimals
    ) internal pure returns (uint256) {
        uint256 k = _getK(reserve0, reserve1);
        //fair_reserves = ( (k * (price0 ** 3) * (price1 ** 3)) )^(1/4) / ((price0 ** 2) + (price1 ** 2));
        price0 *= 1e18 / (10 ** priceDecimals); //convert to 18 dec
        price1 *= 1e18 / (10 ** priceDecimals);
        uint256 a = FixedPointMathLib.rpow(price0, 3, 1e18); //keep same decimals as chainlink
        uint256 b = FixedPointMathLib.rpow(price1, 3, 1e18);
        uint256 c = FixedPointMathLib.rpow(price0, 2, 1e18);
        uint256 d = FixedPointMathLib.rpow(price1, 2, 1e18);

        uint256 p0 = k * FixedPointMathLib.mulWadDown(a, b); //2*18 decimals

        uint256 fair = p0 / (c + d); // number of decimals is 18

        // each sqrt divides the num decimals by 2. So need to replenish the decimals midway through with another 1e18
        uint256 frth_fair = FixedPointMathLib.sqrt(
            FixedPointMathLib.sqrt(fair * 1e18) * 1e18
        ); // number of decimals is 18

        return 2 * ((frth_fair * (10 ** priceDecimals)) / total_supply); // converts to chainlink decimals
    }

    function _getK(uint256 x, uint256 y) internal pure returns (uint256) {
        //x, n, scalar
        uint256 x_cubed = FixedPointMathLib.rpow(x, 3, 1e18);
        uint256 newX = FixedPointMathLib.mulWadDown(x_cubed, y);
        uint256 y_cubed = FixedPointMathLib.rpow(y, 3, 1e18);
        uint256 newY = FixedPointMathLib.mulWadDown(y_cubed, x);

        return newX + newY; //18 decimals
    }

    /* ========== SETTERS ========== */

    /*
     * @notice Set whether we use pessimistic pricing, and if so, whether we look back two or three days.
     * @dev This may only be called by operator. Note that if useAdjusted is false, it doesn't really matter whether
     *  useThreeDayLow is true or not, but we add the revert statement to ensure that adjusted pricing isn't
     *  accidentally turned off when switching to use a three day low.
     * @param _useAdjusted Use adjusted pricing, yes or no?
     * @param _useThreeDayLow True for three day window, false for two day window.
     */
    function setUseAdjustedPrice(
        bool _useAdjusted,
        bool _useThreeDayLow
    ) external onlyOperator {
        if ((_useThreeDayLow == true) && (_useAdjusted == false)) {
            revert("Need to use adjusted pricing with 3 day low");
        }

        useAdjustedPricing = _useAdjusted;
        useThreeDayLow = _useThreeDayLow;
        emit SetUseAdjustedPricing(_useAdjusted, _useThreeDayLow);
    }

    /*
     * @notice Set whether we use only Chainlink for price feeds.
     * @dev This may only be called by operator. Defaults to true.
     * @param _useChainlinkOnly Use Chainlink only, yes or no?
     */
    function setUseChainlinkOnly(bool _useChainlinkOnly) external onlyOperator {
        useChainlinkOnly = _useChainlinkOnly;
        emit SetUseChainlinkOnly(_useChainlinkOnly);
    }

    /*
     * @notice Set a hard price caps for a given Velodrome LP.
     * @dev This may only be called by operator.
     * @param _pool LP token whose price caps we want to set.
     * @param _upperBound Upper price bound in USD, 8 decimals.
     * @param _lowerBound Lower price bound in USD, 8 decimals.
     */
    function setManualPriceCaps(
        address _pool,
        uint256 _upperBound,
        uint256 _lowerBound
    ) external onlyOperator {
        if (_lowerBound > _upperBound) {
            revert("Lower bound cannot be higher than upper");
        }
        upperPriceBound[_pool] = _upperBound;
        lowerPriceBound[_pool] = _lowerBound;
        emit ManualPriceCapsUpdated(_pool, _upperBound, _lowerBound);
    }

    /*
     * @notice Set the number of readings we look in the past for TWAP data.
     * @dev This may only be called by operator. One point = 30 minutes. Default is 2 hours.
     * @param _pool LP token to set a custom points length for.
     * @param _points Number of points to use.
     */
    function setPointsOverride(
        address _pool,
        uint256 _points
    ) external onlyOperator {
        pointsOverride[_pool] = _points;
        emit UpdatedPointsOverride(_pool, _points);
    }

    /**
     * @notice Sets the price feed of a specific token address.
     * @dev Even though the price feeds implement Chainlink's interface, it's possible to create custom feeds.
     * @param _token Address of the ERC20 token to set a feed for
     * @param _feed The Chainlink feed of the ERC20 token.
     * @param _heartbeat The heartbeat for our feed (maximum time allowed before refresh).
     */
    function setFeed(
        address _token,
        address _feed,
        uint96 _heartbeat
    ) public onlyOperator {
        feeds[_token].feedAddress = _feed;
        feeds[_token].heartbeat = _heartbeat;
        emit SetTokenFeed(_token, _feed, _heartbeat);
    }

    /**
     * @notice Set the ability of an address to update LP pricing.
     * @dev Throws if caller is not operator.
     * @param _addr The address to approve or deny access.
     * @param _approved Allowed to update prices
     */
    function setPriceUpdatooors(
        address _addr,
        bool _approved
    ) external onlyOperator {
        priceUpdatooors[_addr] = _approved;
        emit ApprovedPriceUpdatooor(_addr, _approved);
    }

    /**
     * @notice Sets the pending operator of the oracle. Only callable by operator.
     * @param _newOperator The address of the pending operator.
     */
    function setPendingOperator(address _newOperator) public onlyOperator {
        pendingOperator = _newOperator;
    }

    /**
     * @notice Claims the operator role. Only successfully callable by the pending operator.
     */
    function claimOperator() public {
        require(msg.sender == pendingOperator, "ONLY PENDING OPERATOR");
        operator = pendingOperator;
        pendingOperator = address(0);
        emit ChangeOperator(operator);
    }
}

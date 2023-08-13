// SPDX-License-Identifier: AGLP-3.0
pragma solidity 0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

interface IVeloPool is IERC20 {
    function quote(
        address tokenIn,
        uint256 amountIn,
        uint256 granularity
    ) external view returns (uint256);

    function metadata()
        external
        view
        returns (
            uint256 dec0,
            uint256 dec1,
            uint256 r0,
            uint256 r1,
            bool st,
            address t0,
            address t1
        );

    function decimals() external view returns (uint8);

    function stable() external view returns (bool);
}

interface IChainLinkOracle {
    function latestRoundData()
        external
        view
        returns (uint80, int256, uint256, uint256, uint80);
}

/**
@title Velodrome LP Pessimistic Oracle
@notice Oracle used to price Velodrome LP tokens. A pool must contain at least one asset with a Chainlink feed to be valid.
If only one asset has a Chainlink feed, an internal TWAP may be used to price the other, with a default 2 hour window.
The pessimistic oracle stores daily lows, and prices are checked over the past 48 hours when calculating an LP's value.
A manual price cap (upper bound) can be enabled to further prevent manipulations in the upward direction.
With this oracle, price manipulation attacks are substantially more difficult, as an attacker needs to log artificially high lows but still come in under any price cap.
It has the disadvantage of reducing borrow power of borrowers to a 2-day minimum value of their collateral, where the value must have been seen by the oracle.
This work builds on that of Inverse Finance (pessimistic oracle), Alpha Homora (fair reserves) and VMEX (xy^3+yx^3=k fair reserves derivation).
*/

contract PessimisticVelodromeLPOracle {
    /* ========== STATE VARIABLES ========== */

    /// @notice Daily low price stored per token.
    mapping(address => mapping(uint => uint)) public dailyLows; // token => day => price

    /// @notice Set a hard cap on our LP token price. This puts a cap on bad debt from oracle errors in a given market.
    /// @dev This may be adjusted by operator.
    mapping(address => uint256) public manualPriceCap;

    /// @notice Whether we use our 48-hour low (pessimistic) pricing or not.
    /// @dev May only be updated by operator. Defaults to true.
    bool public usePessimistic = true;

    /// @notice Whether we only use Chainlink feeds or allow TWAP for one of the two assets.
    /// @dev May only be updated by operator. Defaults to false.
    bool public useChainlinkOnly = false;

    /// @notice Address of the Chainlink price feed for a given underlying token.
    /// @dev May only be updated by operator.
    mapping(address => address) public feeds;

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

    // our pool/LP token decimals, just in case velodrome has weird pools in the future with different decimals
    uint256 internal constant DECIMALS = 10 ** 18;

    /* ========== CONSTRUCTOR ========== */

    constructor(address _operator) {
        operator = _operator;
        priceUpdatooors[_operator] = true;
    }

    /* ========== EVENTS/MODIFIERS ========== */

    event RecordDailyLow(address indexed token, uint256 price);
    event ManualPriceCapUpdated(address indexed token, uint256 manualPriceCap);
    event UpdatedPointsOverride(address pool, uint256 points);
    event ChangeOperator(address indexed newOperator);
    event SetTokenFeed(address indexed token, address indexed feed);
    event SetUsePessimisticPricing(bool usePessimistic);
    event SetUseChainlinkOnly(bool onlyChainlink);
    event ApprovedPriceUpdatooor(address account, bool canEndorse);

    modifier onlyOperator() {
        require(msg.sender == operator, "ONLY OPERATOR");
        _;
    }

    /* ========== VIEW FUNCTIONS ========== */

    /* 
    @notice Gets the current price of a given Velodrome LP token.
    @dev Will use fair reserves and pessimistic pricing if enabled.
    @param _pool LP token whose price we want to check.
    @return The current price of one LP token.
    */
    function getCurrentPrice(address _pool) public view returns (uint256) {
        if (usePessimistic) {
            return _getAdjustedPrice(_pool);
        } else {
            return _getFairReservesPricing(_pool);
        }
    }

    /**
    @notice Returns the Chainlink feed price of the given token address.
    @dev Will revert if price is negative or feed is not added.
    @param _token The address of the token to get the price of.
    @return The current price of the underlying token.
    */
    function getChainlinkPrice(address _token) public view returns (uint) {
        (, int256 price, , , ) = IChainLinkOracle(feeds[_token])
            .latestRoundData();
        if (price <= 0) {
            revert("Invalid feed price");
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
        return uint(price);
    }

    /**
    @notice Check the last time a token's Chainlink price was updated.
    @dev Useful to check if a price is stale.
    @param _token The address of the token to get the price of
    @return The timestamp of our last price update.
    */
    function chainlinkPriceLastUpdated(
        address _token
    ) external view returns (uint) {
        (, , , uint256 updatedAt, ) = IChainLinkOracle(feeds[_token])
            .latestRoundData();
        return updatedAt;
    }

    /**
    @notice Returns the TWAP price for a token relative to the other token in its pool.
    @dev Note that we can customize the length of points but we default to 4 points (2 hours).
    @param _pool The address of the LP (pool) token we are using to price our assets with.
    @param _token The address of the token to get the price of, and that we are swapping in.
    @param _oneToken One of the token we are swapping in.
    @return Amount of the other token we get when swapping in _oneToken looking back over our TWAP period.
    */
    function getTwapPrice(
        address _pool,
        address _token,
        uint256 _oneToken
    ) public view returns (uint) {
        IVeloPool pool = IVeloPool(_pool);

        // how far back in time should we look?
        uint256 points = pointsOverride[_pool];
        if (points == 0) {
            points = DEFAULT_POINTS;
        }

        // swapping one of our token gets us this many otherToken, returned in decimals of the other token
        return pool.quote(_token, _oneToken, points);
    }

    /// @notice Current day used for storing daily lows
    /// @dev Note that this is in unix time
    function currentDay() public view returns (uint256) {
        return block.timestamp / 1 days;
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
        // get fair reserves pricing, then later decide
        uint256 currentPrice = _getFairReservesPricing(_pool);

        // store price if it's today's low
        uint256 day = currentDay();
        uint256 todaysLow = dailyLows[_pool][day];
        if (todaysLow == 0 || currentPrice < todaysLow) {
            dailyLows[_pool][day] = currentPrice;
            emit RecordDailyLow(_pool, currentPrice);
        }
    }

    // adjust our reported pool price as needed for 48-hour lows and hard upper limit
    function _getAdjustedPrice(address _pool) internal view returns (uint256) {
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
        uint256 twoDayLow = todaysLow > yesterdaysLow && yesterdaysLow > 0
            ? yesterdaysLow
            : todaysLow;
        if (twoDayLow > 0 && currentPrice > twoDayLow) {
            return twoDayLow;
        }

        // use a hard cap to protect against oracle pricing errors upwards
        uint256 manualCap = manualPriceCap[_pool];

        // if we don't have a cap set then don't worry about it
        if (manualCap > 0 && currentPrice > manualCap) {
            currentPrice = manualCap;
        }

        return currentPrice;
    }

    // calculate price based on fair reserves, not spot reserves
    function _getFairReservesPricing(
        address _pool
    ) internal view returns (uint256 fairReservesPricing) {
        // get what we need to calculate our reserves and pricing
        IVeloPool pool = IVeloPool(_pool);
        uint256 lpDecimals = pool.decimals();
        if (lpDecimals != 18) {
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

        uint256 k;
        uint256 p;

        // pull our prices to calculate k and p
        (uint256 price0, uint256 price1) = getTokenPrices(_pool);

        if (pool.stable()) {
            k = Math.sqrt(
                1e18 *
                    Math.sqrt(
                        (((((reserve0 * reserve1) / 1e18) * reserve1) / 1e18) *
                            reserve1) +
                            (((((reserve1 * reserve0) / 1e18) * reserve0) /
                                1e18) * reserve0)
                    )
            ); // xy^3 + yx^3 = k, p0r0' = p1r1', this is in 1e18
            p = Math.sqrt(
                1e16 *
                    Math.sqrt(
                        1e16 *
                            ((((price0 * price0 * price0 * price1) / 1e16) *
                                price1 *
                                price1) / (price0 * price0 + price0 * price0))
                    )
            ); // boost this to 1e16 to give us more precision
        } else {
            k = Math.sqrt(reserve0 * reserve1); // xy = k, p0r0' = p1r1', this is in 1e18
            p = Math.sqrt(price0 * 1e16 * price1); // boost this to 1e16 to give us more precision
        }

        // we want k and total supply to have same number of decimals so price has decimals of chainlink oracle
        fairReservesPricing = (2 * p * k) / (1e8 * pool.totalSupply());
    }

    function getTokenPrices(
        address _pool
    ) public view returns (uint256 price0, uint256 price1) {
        IVeloPool pool = IVeloPool(_pool);
        // check if we have chainlink oracle
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
        if (feeds[token0] != address(0)) {
            price0 = getChainlinkPrice(token0); // returned with 8 decimals
            if (feeds[token1] != address(0)) {
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
        } else if (feeds[token1] != address(0)) {
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

    /* ========== SETTERS ========== */

    /*
    @notice Set whether we use pessimistic pricing (48-hour low).
    @dev This may only be called by operator. Defaults to true.
    @param _usePessimistic Use pessimistic pricing, yes or no?
    */
    function setUsePessimistic(bool _usePessimistic) external onlyOperator {
        usePessimistic = _usePessimistic;
        emit SetUsePessimisticPricing(_usePessimistic);
    }

    /*
    @notice Set whether we use only Chainlink for price feeds.
    @dev This may only be called by operator. Defaults to true.
    @param _useChainlinkOnly Use Chainlink only, yes or no?
    */
    function setUseChainlinkOnly(bool _useChainlinkOnly) external onlyOperator {
        useChainlinkOnly = _useChainlinkOnly;
        emit SetUseChainlinkOnly(_useChainlinkOnly);
    }

    /*
    @notice Set a hard price cap for a given Velodrome LP.
    @dev This may only be called by operator.
    @param _pool LP token whose price cap we want to set.
    @param _manualPriceCap Upper price bound in USD, 8 decimals.
    */
    function setManualPriceCap(
        address _pool,
        uint256 _manualPriceCap
    ) external onlyOperator {
        manualPriceCap[_pool] = _manualPriceCap;
        emit ManualPriceCapUpdated(_pool, _manualPriceCap);
    }

    /*
    @notice Set the number of readings we look in the past for TWAP data.
    @dev This may only be called by operator. One point = 30 minutes. Default is 2 hours.
    @param _pool LP token to set a custom points length for.
    @param _points Number of points to use.
    */
    function setPointsOverride(
        address _pool,
        uint256 _points
    ) external onlyOperator {
        pointsOverride[_pool] = _points;
        emit UpdatedPointsOverride(_pool, _points);
    }

    /**
    @notice Sets the price feed of a specific token address.
    @dev Even though the price feeds implement Chainlink's interface, it's possible to create custom feeds.
    @param token Address of the ERC20 token to set a feed for
    @param feed The Chainlink feed of the ERC20 token.
    */
    function setFeed(address token, address feed) public onlyOperator {
        feeds[token] = feed;
        emit SetTokenFeed(token, feed);
    }

    /**
    @notice Set the ability of an address to update LP pricing.
    @dev Throws if caller is not operator.
    @param _addr The address to approve or deny access.
    @param _approved Allowed to update prices
     */
    function setPriceUpdatooors(
        address _addr,
        bool _approved
    ) external onlyOperator {
        priceUpdatooors[_addr] = _approved;
        emit ApprovedPriceUpdatooor(_addr, _approved);
    }

    /**
    @notice Sets the pending operator of the oracle. Only callable by operator.
    @param _newOperator The address of the pending operator.
    */
    function setPendingOperator(address _newOperator) public onlyOperator {
        pendingOperator = _newOperator;
    }

    /**
    @notice Claims the operator role. Only successfully callable by the pending operator.
    */
    function claimOperator() public {
        require(msg.sender == pendingOperator, "ONLY PENDING OPERATOR");
        operator = pendingOperator;
        pendingOperator = address(0);
        emit ChangeOperator(operator);
    }
}

// SPDX-License-Identifier: AGLP-3.0
pragma solidity 0.8.17;

//import '../utils/HomoraMath.sol'; // should I just import OZ math instead? probably maybe, worth testing them against each other******
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
    function latestAnswer() external view returns (uint256 answer); // should be checking if sequencer is up and also for staleness of prices *******

    function decimals() external view returns (uint8);

    function latestRoundData()
        external
        view
        returns (uint80, int256, uint256, uint256, uint80);
}

/**
@title Velodrome LP Pessimistic Oracle
@notice Oracle used by markets. Uses Chainlink-style feeds for prices.
The Pessimistic Oracle introduces collateral factor into the pricing formula. It ensures that any given oracle price is dampened to prevent borrowers from borrowing more than the lowest recorded value of their collateral over the past 2 days.
This has the advantage of making price manipulation attacks more difficult, as an attacker needs to log artificially high lows.
It has the disadvantage of reducing borrow power of borrowers to a 2-day minimum value of their collateral, where the value must have been seen by the oracle.
*/

contract PessimisticVelodromeLPOracle {
    /* ========== STATE VARIABLES ========== */

    IChainLinkOracle constant sequencerUptimeFeed =
        IChainLinkOracle(0x371EAD81c9102C9BF4874A9075FFFf170F2Ee389);

    address public operator;
    address public pendingOperator;

    /// @notice Set a hard cap on our LP token price. This puts a cap on bad debt from oracle errors in a given market.
    /// @dev This may be adjusted by operator.
    mapping(address => uint256) public manualPriceCap;

    mapping(address => bool) public hasChainlinkOracle;
    mapping(address => address) public feeds;

    mapping(address => mapping(uint => uint)) public dailyLows; // token => day => price

    /// @notice The number of periods we look back in time for TWAP pricing.
    /// @dev Each period is 30 mins. Operator can adjust this length as needed.
    uint256 public points = 4;

    uint256 internal constant DECIMALS = 10 ** 18;

    // should add setter to adjust length of pessimistic look-back
    // make the points a mapping, so different pairs can have different length (for instance, stable pairs can have significantly longer look-backs)

    /* ========== CONSTRUCTOR ========== */

    constructor(address _operator) {
        operator = _operator;
    }

    /* ========== EVENTS/MODIFIERS ========== */

    event RecordDailyLow(address indexed token, uint256 price);
    event ManualPriceCapUpdated(address indexed token, uint256 manualPriceCap);
    event UpdatedPoints(uint256 points);
    event ChangeOperator(address indexed newOperator);
    event SetTokenFeed(address indexed token, address indexed feed);

    modifier onlyOperator() {
        require(msg.sender == operator, "ONLY OPERATOR");
        _;
    }

    /* ========== VIEW FUNCTIONS ========== */

    /// @notice Gets the current price of the LP token.
    /// @dev Return our price using a standard Chainlink aggregator interface.
    /// @return The 48-hour low price of our LP token.
    function latestRoundData(
        address _token
    ) public view returns (uint80, int256, uint256, uint256, uint80) {
        return (
            uint80(0),
            int256(_getPessimisticPrice(_token)),
            uint256(0),
            uint256(0),
            uint80(0)
        );
    }

    /// @notice Gets the current price of wMLP colateral without any corrections
    function getCurrentPrice(address _token) public view returns (uint256) {
        return _getFairReservesPricing(_token);
    }

    /**
    @notice returns the underlying feed price of the given token address
    @dev Will revert if price is negative or token is not in the oracle
    @param token The address of the token to get the price of
    @return Return the unaltered price of the underlying token
    */
    function getChainlinkPrice(address token) public view returns (uint) {
        (, int256 price, , , ) = IChainLinkOracle(feeds[token])
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
    @dev Useful to check for price staleness.
    @param token The address of the token to get the price of
    @return The timestamp of our last price update.
    */
    function chainlinkPriceLastUpdated(
        address token
    ) external view returns (uint) {
        (, , , uint256 updatedAt, ) = IChainLinkOracle(feeds[token])
            .latestRoundData();
        return updatedAt;
    }

    /**
    @notice returns the underlying feed price of the given token address
    @dev Will revert if price is negative or token is not in the oracle
    @param _pool The address of the LP (pool) token we are using to price our assets with.
    @param _token The address of the token to get the price of, and that we are swapping in.
    @param _oneToken One of the token we are swapping in.
    @return Amount of the other token we get when swapping in _oneToken over our TWAP period.
    */
    function getTwapPrice(
        address _pool,
        address _token,
        uint256 _oneToken
    ) public view returns (uint) {
        IVeloPool pool = IVeloPool(_pool);

        // swapping one of our token gets us this many otherToken, returned in decimals of the other token
        return pool.quote(_token, _oneToken, points);
    }

    /// @notice Current day used for storing daily lows
    /// @dev Note that this is in unix time
    function currentDay() public view returns (uint256) {
        return block.timestamp / 1 days;
    }

    /* ========== MUTATIVE FUNCTIONS ========== */

    /// @notice Checks current token price and saves the price if it is the day's lowest
    /// @dev This may be called by anyone. Will revert if price drops >25% from previous low.
    function updatePrice(address _token) external {
        _updatePrice(_token, false);
    }

    /// @notice Checks current token price and saves the price if it is the day's lowest
    /// @dev This may only be called by operator.
    function updatePriceOperator(address _token) external onlyOperator {
        _updatePrice(_token, true);
    }

    /// @notice Checks current LP token prices and saves the price if it is the day's lowest.
    /// @dev This may be called by anyone; the more times it is called the better
    function updateAllPrices(address[] memory _allTokens) external {
        for (uint256 i; i < _allTokens.length; ++i) {
            address _token = _allTokens[i];
            _updatePrice(_token, false);
        }
    }

    function _updatePrice(address _token, bool _operatorOverride) internal {
        // get normalized price (pessimistic)
        uint256 normalizedPrice = _getPessimisticPrice(_token);

        // store price if it's today's low
        uint256 day = currentDay();
        uint256 todaysLow = dailyLows[_token][day];
        if (todaysLow == 0 || normalizedPrice < todaysLow) {
            // make sure normalizedPrice isn't too low (<25% drop between oracle updates is not expected)
            if (
                (todaysLow * 75) / 100 > normalizedPrice && !_operatorOverride
            ) {
                revert("Price drop more than 25%");
            }

            dailyLows[_token][day] = normalizedPrice;
            emit RecordDailyLow(_token, normalizedPrice);
        }
    }

    function _getPessimisticPrice(
        address _token
    ) internal view returns (uint256) {
        // start off with our standard price
        uint256 normalizedPrice = _getFairReservesPricing(_token);
        uint256 day = currentDay();

        // get today's low
        uint256 todaysLow = dailyLows[_token][day];
        if (todaysLow == 0 || normalizedPrice < todaysLow) {
            todaysLow = normalizedPrice;
        }

        // get yesterday's low
        uint256 yesterdaysLow = dailyLows[_token][day - 1];

        // calculate price based on two-day low
        uint256 twoDayLow = todaysLow > yesterdaysLow && yesterdaysLow > 0
            ? yesterdaysLow
            : todaysLow;
        if (twoDayLow > 0 && normalizedPrice > twoDayLow) {
            return twoDayLow;
        }

        // use a hard cap to protect against oracle pricing errors
        uint256 manualCap = manualPriceCap[_token];
        if (manualCap > 0 && normalizedPrice > manualCap) {
            normalizedPrice = manualCap;
        }

        // if the current price is our lowest, use it
        return normalizedPrice;
    }

    // rename these functions so they make more sense
    function _getFairReservesPricing(
        address _lpToken
    ) internal view returns (uint256 fairReservesPricing) {
        // get what we need to calculate our reserves and pricing
        IVeloPool pool = IVeloPool(_lpToken);
        uint256 lpDecimals = pool.decimals();
        if (lpDecimals != 18) {
            revert("Lp token must have 18 decimals");
        }
        (
            uint256 decimals0,
            uint256 decimals1,
            uint256 reserve0,
            uint256 reserve1,
            ,
            ,

        ) = pool.metadata();

        //converts to number of decimals that lp token has, regardless of original number of decimals that it has
        //this is independent of chainlink oracle denomination in USD or ETH
        reserve0 = (reserve0 * DECIMALS) / decimals0;
        reserve1 = (reserve1 * DECIMALS) / decimals1;

        uint256 k;
        uint256 p;
        (uint256 price0, uint256 price1) = getTokenPrices(_lpToken);

        if (pool.stable()) {
            k = Math.sqrt(
                1e18 *
                    Math.sqrt(
                        (((((reserve0 * reserve1) / 1e18) * reserve1) / 1e18) *
                            reserve1) +
                            (((((reserve1 * reserve0) / 1e18) * reserve0) /
                                1e18) * reserve0)
                    )
            ); // xy^3 + yx^3 = k, this is in 1e18
            p = Math.sqrt(
                Math.sqrt(
                    (price0 * price0 * price0 * price1 * price1 * price1) /
                        (price0 * price0 + price0 * price0)
                )
            ); //this is in decimals of chainlink oracle, 1e8
        } else {
            k = Math.sqrt(reserve0 * reserve1); // xy = k, this is in 1e18
            p = Math.sqrt(price0 * price1); //this is in decimals of chainlink oracle, 1e8
        }

        // we want k and total supply to have same number of decimals so price has decimals of chainlink oracle
        fairReservesPricing = (2 * p * k) / pool.totalSupply();
    }

    function getTokenPrices(
        address _veloPool
    ) public view returns (uint256 price0, uint256 price1) {
        IVeloPool pool = IVeloPool(_veloPool);
        // check if we have chainlink oracle
        (
            uint256 decimals0,
            uint256 decimals1,
            ,
            ,
            ,
            address token0,
            address token1
        ) = pool.metadata();

        if (hasChainlinkOracle[token0]) {
            price0 = getChainlinkPrice(token0); // returned with 8 decimals
            if (hasChainlinkOracle[token1]) {
                price1 = getChainlinkPrice(token1); // returned with 8 decimals
            } else {
                // get twap price for token1. this is the amount of token1 we would get from 1 token0
                price1 =
                    (decimals1 * decimals1) /
                    getTwapPrice(_veloPool, token0, decimals0); // returned in decimals1
                price1 = (price0 * price1) / (decimals1);
            }
        } else if (hasChainlinkOracle[token1]) {
            price1 = getChainlinkPrice(token1); // returned with 8 decimals
            // get twap price for token0
            price0 =
                (decimals0 * decimals0) /
                getTwapPrice(_veloPool, token1, decimals1); // returned in decimals0
            price0 = (price0 * price1) / (decimals0);
        } else {
            revert("At least one token must have CL oracle");
        }
    }

    /* ========== SETTERS ========== */

    /// @notice Set the hard price cap a given LP token asset.
    /// @dev This may only be called by operator.
    function setManualPriceCap(
        address _lpToken,
        uint256 _manualPriceCap
    ) external onlyOperator {
        manualPriceCap[_lpToken] = _manualPriceCap;
        emit ManualPriceCapUpdated(_lpToken, _manualPriceCap);
    }

    /// @notice Set the number of readings we look in the past for TWAP data.
    /// @dev This may only be called by operator. One point = 30 minutes.
    function setPoints(uint256 _points) external onlyOperator {
        points = _points;
        emit UpdatedPoints(_points);
    }

    /**
    @notice Sets the price feed of a specific token address.
    @dev Even though the price feeds implement the chainlink interface, it's possible to use other price oracle.
    @param token Address of the ERC20 token to set a feed for
    @param feed The chainlink feed of the ERC20 token.
    */
    function setFeed(address token, address feed) public onlyOperator {
        if (feed == address(0)) {
            hasChainlinkOracle[token] = false;
        } else {
            hasChainlinkOracle[token] = true;
        }
        feeds[token] = feed;
        emit SetTokenFeed(token, feed);
    }

    /**
    @notice Sets the pending operator of the oracle. Only callable by operator.
    @param newOperator_ The address of the pending operator.
    */
    function setPendingOperator(address newOperator_) public onlyOperator {
        pendingOperator = newOperator_;
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

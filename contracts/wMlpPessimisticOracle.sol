// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.15;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IVault is IERC20 {
    // returns value of one wMLP in MLP tokens
    function pricePerShare() external view returns (uint256);
}

interface IMlpManager {
    // Returns AUM of MLP for calculating price.
    function getAum(bool maximise) external view returns (uint256);
}

contract wMlpPessimisticOracle is Ownable {
    /* ========== STATE VARIABLES ========== */

    /// @notice Morphex's MLP Manager, use this to pull our total AUM in MLP.
    IMlpManager public immutable mlpManager;

    /// @notice Address for MLP, Morphex's LP token and the want token for our wMLP vault.
    IERC20 public immutable mlp;

    /// @notice Address of our wMLP, a Yearn vault token.
    IVault public immutable wMlp;

    /// @notice Set a hard cap on our wMLP price that we know it is unlikely to go above any time soon.
    /// @dev This may be adjusted by owner.
    uint256 public manualPriceCap;

    /// @notice Mapping of the low price for a given day.
    mapping(uint256 => uint256) public dailyLows;

    /* ========== CONSTRUCTOR ========== */

    constructor(IMlpManager _mlpManager, IERC20 _mlp, IVault _wMlp) {
        mlpManager = _mlpManager;
        mlp = _mlp;
        wMlp = _wMlp;
        manualPriceCap = 1.5e18;
    }

    /* ========== EVENTS ========== */

    event RecordDailyLow(uint256 price);
    event ManualPriceCapUpdated(uint256 manualWmlpPriceCap);

    /* ========== VIEWS ========== */

    /// @notice Decimals of our price, used by Scream's main oracle
    function decimals() external pure returns (uint8) {
        return 18;
    }

    /// @notice Current day used for storing daily lows
    /// @dev Note that this is in unix time
    function currentDay() public view returns (uint256) {
        return block.timestamp / 1 days;
    }

    /// @notice Gets the current price of wMLP colateral
    /// @dev Return our price using a standard Chainlink aggregator interface
    /// @return The 48-hour low price of wMLP
    function latestRoundData()
        public
        view
        returns (uint80, int256, uint256, uint256, uint80)
    {
        return (
            uint80(0),
            int256(_getPrice()),
            uint256(0),
            uint256(0),
            uint80(0)
        );
    }

    /// @notice Gets the current price of wMLP colateral without any corrections
    function getLivePrice() public view returns (uint256) {
        // aum reported in USD with 30 decimals
        uint256 mlpPrice = (mlpManager.getAum(false) * 1e6) / mlp.totalSupply();

        // add in vault gains
        uint256 sharePrice = wMlp.pricePerShare();

        return (mlpPrice * sharePrice) / 1e18;
    }

    function _getPrice() internal view returns (uint256) {
        uint256 normalizedPrice = _getNormalizedPrice();
        uint256 day = currentDay();

        // get today's low
        uint256 todaysLow = dailyLows[day];
        if (todaysLow == 0 || normalizedPrice < todaysLow) {
            todaysLow = normalizedPrice;
        }

        // get yesterday's low
        uint256 yesterdaysLow = dailyLows[day - 1];

        // calculate price based on two-day low
        uint256 twoDayLow = todaysLow > yesterdaysLow && yesterdaysLow > 0
            ? yesterdaysLow
            : todaysLow;
        if (twoDayLow > 0 && normalizedPrice > twoDayLow) {
            return twoDayLow;
        }

        // if the current price is our lowest, use it
        return normalizedPrice;
    }

    // pull the total AUM in Morphex's MLP, and multiply by our vault token's share price
    function _getNormalizedPrice()
        internal
        view
        returns (uint256 normalizedPrice)
    {
        // aum reported in USD with 30 decimals
        uint256 mlpPrice = (mlpManager.getAum(false) * 1e6) / mlp.totalSupply();

        // add in vault gains
        uint256 sharePrice = wMlp.pricePerShare();

        normalizedPrice = (mlpPrice * sharePrice) / 1e18;

        // use a hard cap to protect against oracle pricing errors
        if (normalizedPrice > manualPriceCap) {
            normalizedPrice = manualPriceCap;
        }
    }

    /* ========== CORE FUNCTIONS ========== */

    /// @notice Checks current wMLP price and saves the price if it is the day's lowest
    /// @dev This may be called by anyone; the more times it is called the better
    function updatePrice() external {
        // get normalized price
        uint256 normalizedPrice = _getNormalizedPrice();

        // potentially store price as today's low
        uint256 day = currentDay();
        uint256 todaysLow = dailyLows[day];
        if (todaysLow == 0 || normalizedPrice < todaysLow) {
            dailyLows[day] = normalizedPrice;
            todaysLow = normalizedPrice;
            emit RecordDailyLow(normalizedPrice);
        }
    }

    /* ========== SETTERS ========== */

    /// @notice Set the hard price cap for our wMLP, which has 18 decimals
    /// @dev This may only be called by owner
    function setManualWmlpPriceCap(
        uint256 _manualWmlpPriceCap
    ) external onlyOwner {
        manualPriceCap = _manualWmlpPriceCap;
        emit ManualPriceCapUpdated(_manualWmlpPriceCap);
    }
}

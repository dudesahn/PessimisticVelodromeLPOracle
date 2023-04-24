// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.15;

// These are the core Yearn libraries
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@yearnvaults/contracts/BaseStrategy.sol";

interface IOracle {
    // pull our asset price, in usdc, via yearn's oracle
    function getPriceUsdcRecommended(
        address tokenAddress
    ) external view returns (uint256);
}

interface IMorphex is IERC20 {
    function getVestedAmount(address) external view returns (uint256);

    function claimable(address) external view returns (uint256);

    function getMaxVestableAmount(address) external view returns (uint256);

    function pairAmounts(address) external view returns (uint256);

    function depositBalances(address, address) external view returns (uint256);

    function handleRewards(bool, bool, bool, bool, bool, bool, bool) external;

    function withdraw() external;

    function deposit(uint256) external;

    function unstakeEsGmx(uint256) external;

    function stakeEsGmx(uint256) external;

    function unstakeGmx(uint256) external;

    function signalTransfer(address) external;

    function acceptTransfer(address) external;

    function getPairAmount(address, uint256) external view returns (uint256);

    function mintAndStakeGlp(
        address,
        uint256,
        uint256,
        uint256
    ) external returns (uint256);
}

contract StrategyMLPStaker is BaseStrategy {
    using SafeERC20 for IERC20;
    /* ========== STATE VARIABLES ========== */

    /// @notice Morphex's reward router.
    /// @dev Used for staking/unstaking assets and claiming rewards.
    IMorphex public constant rewardRouter =
        IMorphex(0x20De7f8283D377fA84575A26c9D484Ee40f55877);

    /// @notice This contract manages esMPX vesting with MLP as collateral.
    /// @dev We also read vesting data from here.
    IMorphex public constant vestedMlp =
        IMorphex(0xdBa3A9993833595eAbd2cDE1c235904ad0fD0b86);

    /// @notice Address of Morphex's vanilla token.
    /// @dev We should only recieve this from vesting esMPX.
    IMorphex public constant mpx =
        IMorphex(0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb);

    /// @notice Address of escrowed MPX.
    /// @dev Must be vested over 1 year to convert to MPX.
    IMorphex public constant esMpx =
        IMorphex(0xe0f606e6730bE531EeAf42348dE43C2feeD43505);

    /// @notice Address for staked MPX.
    /// @dev Receipt token for staking esMPX or MPX.
    IMorphex public constant sMpx =
        IMorphex(0xa4157E273D88ff16B3d8Df68894e1fd809DbC007);

    /// @notice MLP, the LP token for the basket of collateral assets on Morphex.
    /// @dev This is staked for our want token.
    IMorphex public constant mlp =
        IMorphex(0xd5c313DE2d33bf36014e6c659F13acE112B80a8E);

    /// @notice fsMLP, the representation of our staked MLP that the strategy holds.
    /// @dev When reserved for vesting, this is burned for vMlp.
    IMorphex public constant fsMlp =
        IMorphex(0x49A97680938B4F1f73816d1B70C3Ab801FAd124B);

    /// @notice vMLP, tokenized reserved MLP for vesting esMPX to MPX.
    IMorphex public constant vMlp =
        IMorphex(0xdBa3A9993833595eAbd2cDE1c235904ad0fD0b86);

    /// @notice Address for WFTM, our fee token.
    IERC20 public constant wftm =
        IERC20(0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83);

    /// @notice Minimum profit size in USDC that we want to harvest.
    /// @dev Only used in harvestTrigger.
    uint256 public harvestProfitMinInUsdc;

    /// @notice Maximum profit size in USDC that we want to harvest (ignore gas price once we get here).
    /// @dev Only used in harvestTrigger.
    uint256 public harvestProfitMaxInUsdc;

    /// @notice The percent of our esMPX we would like to vest; the remainder will be staked.
    /// @dev Max 10,000 = 100%. Defaults to zero.
    uint256 public percentToVest;

    // we use this to be able to adjust our strategy's name
    string internal stratName;

    // this means all of our fee values are in basis points
    uint256 internal constant FEE_DENOMINATOR = 10_000;

    /* ========== CONSTRUCTOR ========== */

    constructor(address _vault) BaseStrategy(_vault) {
        // want = sMLP
        address mlpManager = 0xA3Ea99f8aE06bA0d9A6Cf7618d06AEa4564340E9;
        wftm.approve(address(mlpManager), type(uint256).max);
        mpx.approve(address(sMpx), type(uint256).max);

        // set up our max delay
        maxReportDelay = 7 days;

        // set our min and max profit
        harvestProfitMinInUsdc = 1_000e6;
        harvestProfitMaxInUsdc = 10_000e6;

        // set our strategy's name
        stratName = "StrategyMLPStaker";
    }

    /* ========== VIEWS ========== */

    /// @notice Strategy name.
    function name() external view override returns (string memory) {
        return stratName;
    }

    /// @notice Balance of want sitting in our strategy as fsMLP.
    function balanceOfWant() public view returns (uint256) {
        return fsMlp.balanceOf(address(this));
    }

    /// @notice Balance of want (sMLP) reserved for vesting.
    function stakedBalance() public view returns (uint256) {
        return vMlp.pairAmounts(address(this));
    }

    /// @notice Total assets the strategy holds, sum of staked and reserved MLP.
    function estimatedTotalAssets() public view override returns (uint256) {
        return stakedBalance() + balanceOfWant();
    }

    /// @notice Balance of unstaked, non-vesting esMPX sitting in our strategy.
    function balanceOfEsMpx() public view returns (uint256) {
        return esMpx.balanceOf(address(this));
    }

    /// @notice Balance of staked esMPX owned by our strategy.
    function stakedEsMpx() public view returns (uint256) {
        return sMpx.depositBalances(address(this), address(esMpx));
    }

    /// @notice Balance of currently vesting esMPX owned by this strategy.
    function vestingEsMpx() public view returns (uint256) {
        return vestedMlp.balanceOf(address(this));
    }

    /// @notice Balance of unstaked MPX sitting in our strategy.
    function balanceOfMpx() public view returns (uint256) {
        return mpx.balanceOf(address(this));
    }

    /// @notice Balance of staked MPX owned by our strategy.
    function stakedMpx() public view returns (uint256) {
        return sMpx.depositBalances(address(this), address(mpx));
    }

    /// @notice Balance of WFTM claimable from staked esMPX/MPX and MLP fees.
    function claimableWftm() public view returns (uint256) {
        return
            IMorphex(0x2D5875ab0eFB999c1f49C798acb9eFbd1cfBF63c).claimable(
                address(this)
            ) +
            IMorphex(0xd3C5dEd5F1207c80473D39230E5b0eD11B39F905).claimable(
                address(this)
            );
    }

    /* ========== CORE STRATEGY FUNCTIONS ========== */

    function prepareReturn(
        uint256 _debtOutstanding
    )
        internal
        override
        returns (uint256 _profit, uint256 _loss, uint256 _debtPayment)
    {
        // re-stake everything except for esMPX and don't convert to FTM, leave as WFTM
        _handleRewards();

        // vest some esMPX and reserve MLP based on our percentToVest
        if (percentToVest > 0) {
            _vest();
        }

        // stake whatever we have left
        uint256 _freeEsMpx = balanceOfEsMpx();
        if (_freeEsMpx > 0) {
            rewardRouter.stakeEsGmx(_freeEsMpx);
        }

        // serious loss should never happen, but if it does, let's record it accurately
        uint256 assets = estimatedTotalAssets();
        uint256 debt = vault.strategies(address(this)).totalDebt;

        // if assets are greater than debt, things are working great!
        if (assets >= debt) {
            unchecked {
                _profit = assets - debt;
            }
            _debtPayment = _debtOutstanding;

            uint256 toFree = _profit + _debtPayment;

            // freed is math.min(wantBalance, toFree)
            (uint256 freed, ) = liquidatePosition(toFree);

            if (toFree > freed) {
                if (_debtPayment > freed) {
                    _debtPayment = freed;
                    _profit = 0;
                } else {
                    unchecked {
                        _profit = freed - _debtPayment;
                    }
                }
            }
        }
        // if assets are less than debt, we are in trouble. don't worry about withdrawing here, just report losses
        else {
            unchecked {
                _loss = debt - assets;
            }
        }
    }

    /// @notice Provide any loose WFTM to MLP and stake it.
    /// @dev May only be called by vault managers.
    /// @return Amount of MLP staked from profits.
    function mintAndStake() external onlyVaultManagers returns (uint256) {
        uint256 wftmBalance = wftm.balanceOf(address(this));
        uint256 newMlp;

        // deposit our WFTM to MLP
        if (wftmBalance > 0) {
            newMlp = rewardRouter.mintAndStakeGlp(
                address(wftm),
                wftmBalance,
                0,
                0
            );
        }
        return newMlp;
    }

    function adjustPosition(uint256 _debtOutstanding) internal override {
        // if in emergency exit, we don't want to deploy any more funds
        if (emergencyExit) {
            return;
        }
    }

    function liquidatePosition(
        uint256 _amountNeeded
    ) internal override returns (uint256 _liquidatedAmount, uint256 _loss) {
        // check our "loose" want
        uint256 _wantBal = balanceOfWant();
        if (_amountNeeded > _wantBal) {
            uint256 _stakedBal = stakedBalance();
            if (_stakedBal > 0) {
                // when withdrawing from vesting, we have to withdraw it all
                vestedMlp.withdraw();
                // we can't re-vest any yet, need to manually do it later
            }
            uint256 _withdrawnBal = balanceOfWant();
            _liquidatedAmount = Math.min(_amountNeeded, _withdrawnBal);
            unchecked {
                _loss = _amountNeeded - _liquidatedAmount;
            }
        } else {
            // we have enough balance to cover the liquidation available
            return (_amountNeeded, 0);
        }
    }

    // fire sale, get rid of it all!
    function liquidateAllPositions() internal override returns (uint256) {
        uint256 _stakedBal = stakedBalance();
        if (_stakedBal > 0) {
            vestedMlp.withdraw();
        }
        return balanceOfWant();
    }

    // want is blocked by default, add any other tokens to protect from gov here.
    function protectedTokens()
        internal
        view
        override
        returns (address[] memory)
    {}

    // migrate our want token to a new strategy if needed
    function prepareMigration(address _newStrategy) internal override {
        uint256 _stakedBal = stakedBalance();
        if (_stakedBal > 0) {
            vestedMlp.withdraw();
        }

        // signal that we would like to migrate our position
        // we will also need to accept the transfer on our new strategy ***
        rewardRouter.signalTransfer(_newStrategy);

        uint256 wftmBalance = wftm.balanceOf(address(this));
        if (wftmBalance > 0) {
            wftm.safeTransfer(_newStrategy, wftmBalance);
        }
    }

    /// @notice Part 2 of our strategy migration. Must do before harvesting the new strategy.
    /// @dev May only be called by governance.
    /// @param _oldStrategy Address of the old strategy we are migrating from.
    function acceptTransfer(address _oldStrategy) external onlyGovernance {
        rewardRouter.acceptTransfer(_oldStrategy);
    }

    /// @notice Sweep out some of our fully vested MPX to gov.
    /// @dev May only be called by governance.
    /// @param amount Amount of MPX to unstake and sweep out.
    function unstakeAndSweepVestedMpx(uint256 amount) external onlyGovernance {
        // withdraw our staked MPX
        uint256 _stakedMpx = stakedMpx();
        if (_stakedMpx >= amount) {
            rewardRouter.unstakeGmx(amount);
        }

        uint256 _balanceOfMpx = balanceOfMpx();
        if (_balanceOfMpx >= amount) {
            mpx.transfer(vault.governance(), amount);
        }
    }

    /// @notice Manually claim our rewards.
    /// @dev May only be called by vault managers.
    function handleRewards() external onlyVaultManagers {
        _handleRewards();
    }

    function _handleRewards() internal onlyVaultManagers {
        // claim vested MPX, stake MPX, claim esMPX, stake esMPX, stake MPs, claim WFTM, convert WFTM to FTM
        rewardRouter.handleRewards(true, true, true, false, true, true, false);
    }

    /// @notice Manually rebalance the amount of esMPX we are vesting based on our percentToVest.
    /// @dev May only be called by vault managers.
    function rebalanceVesting() external onlyVaultManagers {
        _rebalanceVesting();
    }

    function _rebalanceVesting() internal {
        // withdraw our MLPs from vesting if we have any there
        if (stakedBalance() > 0) {
            vestedMlp.withdraw();
        }

        // withdraw our staked esMPX
        uint256 _stakedEsMpx = stakedEsMpx();
        if (_stakedEsMpx > 0) {
            rewardRouter.unstakeEsGmx(_stakedEsMpx);
        }

        // vest and stake our esMPX according to our percentToVest
        if (percentToVest > 0) {
            _vest();
        }

        // stake whatever we have left
        uint256 _freeEsMpx = balanceOfEsMpx();
        if (_freeEsMpx > 0) {
            rewardRouter.stakeEsGmx(_freeEsMpx);
        }
    }

    function _vest() internal {
        // determine how much MLP we need to be able to vest a given amount of esMPX
        uint256 totalToVest = (vMlp.getMaxVestableAmount(address(this)) *
            percentToVest) / FEE_DENOMINATOR;

        // this is how much esMPX we are already vesting
        uint256 alreadyVesting = vMlp.balanceOf(address(this));

        // only add more if we are under our limit
        if (totalToVest > alreadyVesting) {
            uint256 toVest = totalToVest - alreadyVesting;

            // determine how much MLP we need to vest the extra esMPX
            uint256 mlpNeeded = vMlp.getPairAmount(address(this), toVest);
            if (balanceOfWant() >= mlpNeeded) {
                vestedMlp.deposit(toVest);
            }
        }
    }

    /* ========== KEEP3RS ========== */

    /**
     * @notice
     *  Provide a signal to the keeper that harvest() should be called.
     *
     *  Don't harvest if a strategy is inactive.
     *  If our profit exceeds our upper limit, then harvest no matter what. For
     *  our lower profit limit, credit threshold, max delay, and manual force trigger,
     *  only harvest if our gas price is acceptable.
     *
     * @param callCostinEth The keeper's estimated gas cost to call harvest() (in wei).
     * @return True if harvest() should be called, false otherwise.
     */
    function harvestTrigger(
        uint256 callCostinEth
    ) public view override returns (bool) {
        // Should not trigger if strategy is not active (no assets and no debtRatio). This means we don't need to adjust keeper job.
        if (!isActive()) {
            return false;
        }

        // harvest if we have a profit to claim at our upper limit without considering gas price
        uint256 claimableProfit = claimableProfitInUsdc();
        if (claimableProfit > harvestProfitMaxInUsdc) {
            return true;
        }

        // check if the base fee gas price is higher than we allow. if it is, block harvests.
        if (!isBaseFeeAcceptable()) {
            return false;
        }

        // trigger if we want to manually harvest, but only if our gas price is acceptable
        if (forceHarvestTriggerOnce) {
            return true;
        }

        // harvest if we have a sufficient profit to claim, but only if our gas price is acceptable
        if (claimableProfit > harvestProfitMinInUsdc) {
            return true;
        }

        StrategyParams memory params = vault.strategies(address(this));
        // harvest regardless of profit once we reach our maxDelay
        if (block.timestamp - params.lastReport > maxReportDelay) {
            return true;
        }

        // harvest our credit if it's above our threshold
        if (vault.creditAvailable() > creditThreshold) {
            return true;
        }

        // otherwise, we don't harvest
        return false;
    }

    /// @notice Calculates the profit if all claimable assets were sold for USDC (6 decimals).
    /// @dev Uses yearn's lens oracle, if returned values are strange then troubleshoot there.
    /// @return Total return in USDC from selling claimable WFTM.
    function claimableProfitInUsdc() public view returns (uint256) {
        IOracle yearnOracle = IOracle(
            0x57AA88A0810dfe3f9b71a9b179Dd8bF5F956C46A
        ); // yearn lens oracle
        uint256 wftmPrice = yearnOracle.getPriceUsdcRecommended(address(wftm));

        // Oracle returns prices as 6 decimals, so multiply by claimable amount and divide by token decimals (1e18)
        return (wftmPrice * claimableWftm()) / 1e18;
    }

    /// @notice Convert our keeper's eth cost into want
    /// @dev We don't use this since we don't factor call cost into our harvestTrigger.
    /// @param _ethAmount Amount of ether spent.
    /// @return Value of ether in want.
    function ethToWant(
        uint256 _ethAmount
    ) public view override returns (uint256) {}

    // include so our contract plays nicely with ftm
    receive() external payable {}

    /* ========== SETTERS ========== */
    // These functions are useful for setting parameters of the strategy that may need to be adjusted.

    /// @notice Use this to set the percentage of esMPX we vest for MPX.
    /// @dev Only governance can set this.
    /// @param _percent Percent of our esMPX to vest, in basis points.
    function setPercentToVest(uint256 _percent) external onlyGovernance {
        require(_percent < 10_000, "must be less than 10,000");
        percentToVest = _percent;
    }

    /**
     * @notice
     *  Here we set various parameters to optimize our harvestTrigger.
     * @param _harvestProfitMinInUsdc The amount of profit (in USDC, 6 decimals)
     *  that will trigger a harvest if gas price is acceptable.
     * @param _harvestProfitMaxInUsdc The amount of profit in USDC that
     *  will trigger a harvest regardless of gas price.
     */
    function setHarvestTriggerParams(
        uint256 _harvestProfitMinInUsdc,
        uint256 _harvestProfitMaxInUsdc
    ) external onlyVaultManagers {
        harvestProfitMinInUsdc = _harvestProfitMinInUsdc;
        harvestProfitMaxInUsdc = _harvestProfitMaxInUsdc;
    }
}

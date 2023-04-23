// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.15;

// These are the core Yearn libraries
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@yearnvaults/contracts/BaseStrategy.sol";

interface IOracle {
    function getPriceUsdcRecommended(
        address tokenAddress
    ) external view returns (uint256);
}

interface IMorphex is IERC20 {
    function stake(uint _LQTYamount) external;

    function unstake(uint _LQTYamount) external;

    function getPendingETHGain(address _user) external view returns (uint);

    function getPendingLUSDGain(address _user) external view returns (uint);

    function stakes(address _user) external view returns (uint);
}

contract StrategyLQTYStaker is BaseStrategy {
    using SafeERC20 for IERC20;
    /* ========== STATE VARIABLES ========== */

    /// @notice LQTY staking contract
    IMorphex public constant rewardRouter =
        IMorphex(0x20De7f8283D377fA84575A26c9D484Ee40f55877);

    /// @notice Approve this for our deposits
    IMorphex public constant mlpManager =
        IMorphex(0xA3Ea99f8aE06bA0d9A6Cf7618d06AEa4564340E9);

    /// @notice This contract manages esMPX vesting with MLP as collateral.
    IMorphex public constant vestedMlp =
        IMorphex(0xdBa3A9993833595eAbd2cDE1c235904ad0fD0b86);

    /// @notice Address of Morphex's vanilla token.
    IMorphex public constant mpx =
        IMorphex(0x66eEd5FF1701E6ed8470DC391F05e27B1d0657eb);

    /// @notice Address of escrowed MPX. Must be vested over 1 year to convert to MPX.
    IMorphex public constant esMpx =
        IMorphex(0xe0f606e6730bE531EeAf42348dE43C2feeD43505);

    /// @notice Staked MPX. Receipt token for staking esMPX or MPX.
    IMorphex public constant sMpx =
        IMorphex(0xa4157E273D88ff16B3d8Df68894e1fd809DbC007);

    /// @notice MLP, the LP token for the basket of collateral assets on Morphex.
    IMorphex public constant mlp =
        IMorphex(0xd5c313DE2d33bf36014e6c659F13acE112B80a8E);

    /// @notice fsMLP, the representation of our staked MLP that the strategy holds.
    IMorphex public constant fsMlp =
        IMorphex(0x49A97680938B4F1f73816d1B70C3Ab801FAd124B);

    /// @notice The percent of our esMPX we would like to vest; the remainder will be staked.
    /// @dev Base 10,000
    uint256 public percentToVest;

    // we use this to be able to adjust our strategy's name
    string internal stratName;

    // this means all of our fee values are in basis points
    uint256 internal constant FEE_DENOMINATOR = 10000;

    /* ========== CONSTRUCTOR ========== */

    constructor(
        address _vault,
        uint256 _harvestProfitMinInUsdc,
        uint256 _harvestProfitMaxInUsdc
    ) BaseStrategy(_vault) {
        // 1:1 assignments
        harvestProfitMinInUsdc = _harvestProfitMinInUsdc;
        harvestProfitMaxInUsdc = _harvestProfitMaxInUsdc;

        // want = sMLP
        wftm.approve(address(mlpManager), type(uint256).max);
        mpx.approve(address(sMpx), type(uint256).max);

        // set up our max delay
        maxReportDelay = 365 days;

        // set our strategy's name
        stratName = "StrategyMLPStaker";
    }

    /* ========== VIEWS ========== */

    /// @notice Strategy name.
    function name() external view override returns (string memory) {
        return stratName;
    }

    /// @notice Balance of want (sMLP) locked for vesting.
    function stakedBalance() public view returns (uint256) {
        return estimatedTotalAssets() - balanceOfWant();
    }

    /// @notice Balance of want sitting in our strategy as fsMLP.
    function balanceOfWant() public view returns (uint256) {
        return fsMlp.balanceOf(address(this));
    }

    /// @notice Total assets the strategy holds, sum of staked and vesting MLP.
    function estimatedTotalAssets() public view override returns (uint256) {
        return vestedMlp.getCombinedAverageStakedAmount();
    }

    /// @notice Balance of unstaked, non-vesting esMPX sitting in our strategy.
    function balanceOfEsMpx() public view returns (uint256) {
        return esMpx.balanceOf(address(this));
    }

    /// @notice Balance of vesting esMPX owned by this strategy.
    function vestingEsMpx() public view returns (uint256) {
        return vestedMlp.getVestedAmount(address(this));
    }

    /// @notice Balance of staked esMPX owned by our strategy.
    function stakedEsMpx() public view returns (uint256) {
        return sMpx.depositBalances(address(this), address(esMpx));
    }

    /// @notice Balance of unstaked MPX sitting in our strategy.
    function balanceOfMpx() public view returns (uint256) {
        return mpx.balanceOf(address(this));
    }

    /// @notice Balance of staked MPX owned by our strategy.
    function stakedMpx() public view returns (uint256) {
        return sMpx.depositBalances(address(this), address(mpx));
    }

    /* ========== CORE STRATEGY FUNCTIONS ========== */

    function prepareReturn(
        uint256 _debtOutstanding
    )
        internal
        override
        returns (uint256 _profit, uint256 _loss, uint256 _debtPayment)
    {
        // check if this reverts with an empty strategy
        // re-stake everything except for esMPX and don't convert to FTM, leave as WFTM
        // claim MPX, stake MPX, claim esMPX, stake esMPX, stake MPs, claim WFTM, convert WFTM to FTM
        rewardRouter.handleRewards(true, true, true, false, true, true, false);
        uint256 wftmBalance = wftm.balanceOf(address(this));
        
        // deposit our WFTM to MLP
        if (wftmBalance > 0) {
            rewardRouter.mintAndStakeGlp(wftm, wftmBalance, 0, 0)
        }
        
        // rebalance our vesting esMPX and reserved MLP based on our percentToVest
        _rebalanceVesting();

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
            }
            uint256 _withdrawnBal = balanceOfWant();
            _liquidatedAmount = Math.min(_amountNeeded, _withdrawnBal);
            unchecked {
                _loss = _amountNeeded - _liquidatedAmount;
            }
            
            // re-vest our assets based on our new amount
            if _loss == 0 {
                
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
        rewardRouter.signalTransfer(_newStrategy);
        
        uint256 wftmBalance = wftm.balanceOf(address(this));
        if (wftmBalance > 0) {
            wftm.safeTransfer(_newStrategy, wftmBalance);
        }
    }

    // part 2 of our strategy migration
    function acceptTransfer(address _oldStrategy) external onlyGovernance {
        // signal that we would like to migrate our position
        rewardRouter.acceptTransfer(_oldStrategy);
    }
    
    function rebalanceVesting() external onlyVaultManagers {
        _rebalanceVesting();
    
    }
    
    function unstakeAndSweepMpx(uint256 amount) external onlyGovernance {
        // withdraw our staked MPX
        uint256 _stakedMpx = stakedMpx();
        if (_stakedMpx >= amount) {
            rewardRouter.unstakeGmx(amount);
        }
        
        uint256 _balanceOfMpx = balanceOfMpx();
        if (_balanceOfMpx >= amount) {
            mpx.transfer(screamGov, amount);
        }
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
        uint256 _toVest = balanceOfEsMpx() * percentToVest / FEE_DENOMINATOR;
        if (_toVest > 0) {
            vestedMlp.deposit(_toVest);
        }
        
        // stake whatever we have left
        rewardRouter.stakeEsGmx(balanceOfEsMpx());
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

        // check if the base fee gas price is higher than we allow. if it is, block harvests.
        if (!isBaseFeeAcceptable()) {
            return false;
        }

        // trigger if we want to manually harvest, but only if our gas price is acceptable
        if (forceHarvestTriggerOnce) {
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
        require(_percent < 10_000; "must be less than 10,000");
        percentToVest = _percent;
    }
}

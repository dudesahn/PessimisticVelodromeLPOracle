import pytest
from utils import harvest_strategy, check_status
from brownie import accounts, interface, chain
import brownie

# test migrating a strategy
def test_migration(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    sleep_time,
    contract_name,
    profit_whale,
    profit_amount,
    target,
    trade_factory,
    use_yswaps,
    is_slippery,
    no_profit,
    is_gmx,
):

    ## deposit to the vault after approving
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss, extra) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        target,
    )

    # record our current strategy's assets
    total_old = strategy.estimatedTotalAssets()

    # sleep to collect earnings
    chain.sleep(sleep_time)

    ######### THIS WILL NEED TO BE UPDATED BASED ON STRATEGY CONSTRUCTOR #########
    new_strategy = gov.deploy(contract_name, vault)

    # can we harvest an unactivated strategy? should be no
    tx = new_strategy.harvestTrigger(0, {"from": gov})
    print("\nShould we harvest? Should be False.", tx)
    assert tx == False

    # if gmx, want to harvest again so we can get some funds in vesting
    if is_gmx:
        (profit, loss, extra) = harvest_strategy(
            is_gmx,
            strategy,
            token,
            gov,
            profit_whale,
            profit_amount,
            target,
        )

    ######### ADD LOGIC TO TEST CLAIMING OF ASSETS FOR TRANSFER TO NEW STRATEGY AS NEEDED #########
    # since migrating doesn't enter prepareReturn, we may have to manually claim rewards
    strategy.handleRewards({"from": gov})
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    # gmx has a two-step migration, have to accept it on the new strategy too
    if is_gmx:
        new_strategy.acceptTransfer(strategy, {"from": gov})

    ####### ADD LOGIC TO MAKE SURE ASSET TRANSFER WENT AS EXPECTED #######
    wftm = interface.IERC20(strategy.wftm())
    assert wftm.balanceOf(strategy) == 0
    assert wftm.balanceOf(new_strategy) > 0

    # assert that our old strategy is empty
    updated_total_old = strategy.estimatedTotalAssets()
    assert updated_total_old == 0

    # harvest to get funds back in new strategy
    (profit, loss, extra) = harvest_strategy(
        is_gmx,
        new_strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        target,
    )
    new_strat_balance = new_strategy.estimatedTotalAssets()
    assert new_strat_balance > 0

    # harvest again to take our profit if needed
    if use_yswaps or is_gmx:
        strategy_params = check_status(new_strategy, vault)
        old_gain = strategy_params["totalGain"]
        (profit, loss, extra) = harvest_strategy(
            is_gmx,
            new_strategy,
            token,
            gov,
            profit_whale,
            profit_amount,
            target,
        )

        # check our current status
        print("\nAfter yswaps extra harvest")
        strategy_params = check_status(new_strategy, vault)

        # make sure we recorded our gain properly
        if not no_profit:
            assert strategy_params["totalGain"] > old_gain

    # confirm that we have the same amount of assets in our new strategy as old or have profited
    if no_profit:
        assert pytest.approx(new_strat_balance, rel=RELATIVE_APPROX) == total_old
    else:
        assert new_strat_balance > total_old

    # record our new assets
    vault_new_assets = vault.totalAssets()

    # simulate earnings
    chain.sleep(sleep_time)

    # Test out our migrated strategy, confirm we're making a profit
    (profit, loss, extra) = harvest_strategy(
        is_gmx,
        new_strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        target,
    )

    vault_newer_assets = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    if no_profit:
        assert (
            pytest.approx(vault_newer_assets, rel=RELATIVE_APPROX) == vault_new_assets
        )
    else:
        assert vault_newer_assets > vault_new_assets


# make sure we can still migrate when we don't have funds
def test_empty_migration(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    sleep_time,
    contract_name,
    profit_whale,
    profit_amount,
    target,
    trade_factory,
    use_yswaps,
    is_slippery,
    RELATIVE_APPROX,
    is_gmx,
):

    ## deposit to the vault after approving
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss, extra) = harvest_strategy(
        is_gmx,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        target,
    )

    # record our current strategy's assets
    total_old = strategy.estimatedTotalAssets()

    # sleep to collect earnings
    chain.sleep(sleep_time)

    ######### THIS WILL NEED TO BE UPDATED BASED ON STRATEGY CONSTRUCTOR #########
    new_strategy = gov.deploy(contract_name, vault)

    # set our debtRatio to zero so our harvest sends all funds back to vault
    vault.updateStrategyDebtRatio(strategy, 0, {"from": gov})
    (profit, loss, extra) = harvest_strategy(
        is_gmx,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        target,
    )

    # yswaps needs another harvest to get the final bit of profit to the vault
    if use_yswaps or is_gmx:
        (profit, loss, extra) = harvest_strategy(
            is_gmx,
            strategy,
            token,
            gov,
            profit_whale,
            profit_amount,
            target,
        )

    # shouldn't have any assets, unless we have slippage, then this might leave dust
    # for complete emptying in this situtation, use emergencyExit
    if is_slippery:
        assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == 0
        strategy.setEmergencyExit({"from": gov})

        # turn off health check since taking profit on no debt
        strategy.setDoHealthCheck(False, {"from": gov})
        (profit, loss, extra) = harvest_strategy(
            is_gmx,
            strategy,
            token,
            gov,
            profit_whale,
            profit_amount,
            target,
        )

    if is_gmx:
        # normally we would send this away, but sMLP doesn't let us transfer zero
        assert strategy.estimatedTotalAssets() == extra
    else:
        assert strategy.estimatedTotalAssets() == 0

    # make sure we transferred strat params over
    total_debt = vault.strategies(strategy)["totalDebt"]
    debt_ratio = vault.strategies(strategy)["debtRatio"]

    # migrate our old strategy
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    # gmx has a two-step migration, have to accept it on the new strategy too
    if is_gmx:
        new_strategy.acceptTransfer(strategy, {"from": gov})

    # new strategy should also be empty
    if is_gmx:
        assert new_strategy.estimatedTotalAssets() == extra
    else:
        assert new_strategy.estimatedTotalAssets() == 0

    # make sure we took our gains and losses with us
    assert total_debt == vault.strategies(new_strategy)["totalDebt"]
    assert debt_ratio == vault.strategies(new_strategy)["debtRatio"] == 0

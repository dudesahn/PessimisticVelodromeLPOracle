import pytest
from utils import harvest_strategy
from brownie import accounts, interface, chain

# perhaps make this the new base for brownie strategy mix

# last thing to do now is make sure all of my comments make sense and the calls within the tests do as well

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
    destination_strategy,
    trade_factory,
    use_yswaps,
    lusd_whale,
    is_slippery,
    no_profit,
):

    ## deposit to the vault after approving
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # record our current strategy's assets
    total_old = strategy.estimatedTotalAssets()

    # sleep to collect earnings
    chain.sleep(sleep_time)

    # will need to update this based on the strategy's constructor ******
    new_strategy = gov.deploy(contract_name, vault, trade_factory, 10_000e6, 50_000e6)

    # can we harvest an unactivated strategy? should be no
    tx = new_strategy.harvestTrigger(0, {"from": gov})
    print("\nShould we harvest? Should be False.", tx)
    assert tx == False

    ####### add logic here if we need to test claiming of assets for transferring to the new strategy #######
    lusd = interface.IERC20(strategy.lusd())
    weth = interface.IERC20(strategy.weth())
    lusd.transfer(strategy, 100e18, {"from": lusd_whale})
    lusd_whale.transfer(strategy, 2e18)

    # migrate our old strategy
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    ####### add logic here to check if the transfer of assets went as expected #######
    assert weth.balanceOf(strategy) == 0
    assert lusd.balanceOf(strategy) == 0
    assert strategy.balance() == 0
    assert weth.balanceOf(new_strategy) > 0
    assert lusd.balanceOf(new_strategy) > 0

    # assert that our old strategy is empty
    updated_total_old = strategy.estimatedTotalAssets()
    assert updated_total_old == 0

    # harvest to get funds back in new strategy
    (profit, loss) = harvest_strategy(
        use_yswaps,
        new_strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )
    new_strat_balance = new_strategy.estimatedTotalAssets()

    # confirm that we have the same amount of assets in our new strategy as old
    if no_profit and is_slippery:
        assert pytest.approx(new_strat_balance, rel=RELATIVE_APPROX) == total_old
    else:
        assert new_strat_balance >= total_old

    # record our new assets
    vault_new_assets = vault.totalAssets()

    # simulate earnings
    chain.sleep(sleep_time)
    chain.mine(1)

    # Test out our migrated strategy, confirm we're making a profit
    (profit, loss) = harvest_strategy(
        True,
        new_strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    vault_newer_assets = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    if is_slippery and no_profit:
        assert (
            pytest.approx(vault_newer_assets, rel=RELATIVE_APPROX) == vault_new_assets
        )
    else:
        assert vault_newer_assets >= vault_new_assets


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
    destination_strategy,
    trade_factory,
    use_yswaps,
):

    ## deposit to the vault after approving
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # record our current strategy's assets
    total_old = strategy.estimatedTotalAssets()

    # sleep to collect earnings
    chain.sleep(sleep_time)

    ######### THIS WILL NEED TO BE UPDATED BASED ON STRATEGY CONSTRUCTOR #########
    new_strategy = gov.deploy(contract_name, vault, trade_factory, 10_000e6, 50_000e6)

    # set our debtRatio to zero so our harvest sends all funds back to vault
    vault.updateStrategyDebtRatio(strategy, 0, {"from": gov})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # yswaps needs another harvest to get the final bit of profit to the vault
    if use_yswaps:
        (profit, loss) = harvest_strategy(
            use_yswaps,
            strategy,
            token,
            gov,
            profit_whale,
            profit_amount,
            destination_strategy,
        )

    # confirm we emptied the strategy
    assert strategy.estimatedTotalAssets() == 0

    # make sure we transferred strat params over
    total_debt = vault.strategies(strategy)["totalDebt"]
    debt_ratio = vault.strategies(strategy)["debtRatio"]

    # migrate our old strategy
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    # new strategy should also be empty
    assert new_strategy.estimatedTotalAssets() == 0

    # make sure we took our gains and losses with us
    assert total_debt == vault.strategies(new_strategy)["totalDebt"]
    assert debt_ratio == vault.strategies(new_strategy)["debtRatio"] == 0

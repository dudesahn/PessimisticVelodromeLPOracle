import math
from utils import harvest_strategy
from brownie import accounts, interface

# go back and check the intent for all previous tests, make sure those are still covered
# make sure all steps still make sense, or if we can replace it with something better (like whether we want to know for sure we made money in a step or not), potentially
# depending on other fixtures and whether they are true or false
# add tests for liquity voter as well
# odds and ends test on desktop, also check curve and convex one too
# make sure to check default brownie mix tests too, then perhaps make this the new base for brownie strategy mix

# test migrating a strategy
def test_migration(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    sleep_time,
    contract_name,
    profit_whale,
    profit_amount,
    destination_strategy,
    trade_factory,
    use_yswaps,
    lusd_whale,
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

    # confirm we made money, or at least that we have about the same
    assert new_strat_balance >= total_old or math.isclose(
        new_strat_balance, total_old, abs_tol=5
    )

    startingVault = vault.totalAssets()
    print("\nVault starting assets with new strategy: ", startingVault)

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
    vaultAssets_2 = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    assert vaultAssets_2 >= startingVault or math.isclose(
        vaultAssets_2, startingVault, abs_tol=5
    )
    print("\nAssets after 1 day harvest: ", vaultAssets_2)


# make sure we can still migrate when we don't have funds
def test_empty_migration(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
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

    assert strategy.estimatedTotalAssets() == 0

    # make sure we transferred strat params over
    total_debt = vault.strategies(strategy)["totalDebt"]
    debt_ratio = vault.strategies(strategy)["debtRatio"]

    # migrate our old strategy
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    # make sure we took our gains and losses with us
    assert total_debt == vault.strategies(new_strategy)["totalDebt"]
    assert debt_ratio == vault.strategies(new_strategy)["debtRatio"] == 0

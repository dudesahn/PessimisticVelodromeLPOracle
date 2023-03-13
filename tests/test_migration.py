import math
from utils import harvest_strategy

# go back and check the intent for all previous tests, make sure those are still covered
# make sure all steps still make sense, or if we can replace it with something better (like whether we want to know for sure we made money in a step or not), potentially 
# depending on other fixtures and whether they are true or false

# test migrating a strategy
def test_migration(
    gov,
    token,
    vault,
    strategist,
    whale,
    strategy,
    chain,
    amount,
    sleep_time,
    is_slippery,
    no_profit,
    contract_name,
    profit_whale,
    profit_amount,
    destination_strategy,
    trade_factory,
):

    ## deposit to the vault after approving
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
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

    # migrate our old strategy
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    # assert that our old strategy is empty
    updated_total_old = strategy.estimatedTotalAssets()
    assert updated_total_old == 0

    # harvest to get funds back in new strategy
    (profit, loss) = harvest_strategy(
        True, new_strategy, token, gov, profit_whale, profit_amount, destination_strategy
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
        True, new_strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )
    vaultAssets_2 = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    assert vaultAssets_2 >= startingVault or math.isclose(
        vaultAssets_2, startingVault, abs_tol=5
    )
    print("\nAssets after 1 day harvest: ", vaultAssets_2)

import brownie
from brownie import Contract, config, interface
import math
from utils import harvest_strategy

# do any extra testing here to hit all parts of liquidatePosition
# generally this involves sending away all assets and then withdrawing before another harvest
def test_odds_and_ends_liquidatePosition(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
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

    # send all funds away, need to update this based on strategy
    staking = Contract(strategy.lqtyStaking())
    staking.unstake(staking.stakes(strategy), {"from": strategy})
    token.transfer(gov, token.balanceOf(strategy), {"from": strategy})
    assert strategy.estimatedTotalAssets() == 0

    # withdraw and see how down bad we are, confirm we can withdraw from an empty vault
    # it's important to do this before harvesting, also allow max loss
    vault.withdraw(vault.balanceOf(whale), whale, 10_000, {"from": whale})


# there also may be situations where the destination protocol is exploited or funds are locked but you still hold the same number of wrapper tokens
# though liquity doesn't have this as an option, it's important to test if it is to make sure debt is maintained properly in the case future assets free up
def test_odds_and_ends_locked_funds(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
):
    print("No way to test this for current strategy")


# here we take a loss intentionally without entering emergencyExit
def test_odds_and_ends_rekt(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
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

    # send all funds away, need to update this based on strategy
    staking = Contract(strategy.lqtyStaking())
    staking.unstake(staking.stakes(strategy), {"from": strategy})
    token.transfer(gov, token.balanceOf(strategy), {"from": strategy})
    assert strategy.estimatedTotalAssets() == 0

    # our whale donates 1 wei to the vault so we don't divide by zero (needed for older vaults)
    if old_vault:
        token.transfer(strategy, 1, {"from": whale})

    # set debtRatio to zero so we try and pull everything that we can out. turn off health check because of massive losses
    vault.updateStrategyDebtRatio(strategy, 0, {"from": gov})
    strategy.setDoHealthCheck(False, {"from": gov})
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

    if old_vault:
        assert vault.totalAssets() == 1
    else:
        assert vault.totalAssets() == 0

    # simulate 5 days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and see how down bad we are, confirm we can withdraw from an empty vault
    vault.withdraw({"from": whale})

    print(
        "Raw loss:",
        (startingWhale - token.balanceOf(whale)) / 1e18,
        "Percentage:",
        (startingWhale - token.balanceOf(whale)) / startingWhale,
    )
    print("Share price:", vault.pricePerShare() / 1e18)


def test_weird_reverts(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
):

    # only vault can call this
    with brownie.reverts():
        strategy.migrate(whale, {"from": gov})

    # can't migrate to a different vault
    with brownie.reverts():
        vault.migrateStrategy(strategy, destination_strategy, {"from": gov})

    # can't withdraw from a non-vault address
    with brownie.reverts():
        strategy.withdraw(1e18, {"from": gov})


# this test makes sure we can still harvest without any assets but still get our profits
# can also test here whether we claim rewards from an empty strategy, some protocols will revert
def test_odds_and_ends_empty_strat(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
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

    # send all funds away, need to update this based on strategy
    staking = Contract(strategy.lqtyStaking())
    staking.unstake(staking.stakes(strategy), {"from": strategy})
    token.transfer(gov, token.balanceOf(strategy), {"from": strategy})
    assert strategy.estimatedTotalAssets() == 0

    # accept our losses, sad day
    strategy.setDoHealthCheck(False, {"from": gov})
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

    # some profits fall from the heavens
    token.transfer(strategy, profit_amount, {"from": profit_whale})
    strategy.setDoHealthCheck(False, {"from": gov})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )
    assert profit > 0
    share_price = vault.pricePerShare()
    assert share_price > 0
    print("Share price:", share_price)


# this test makes sure we can still harvest without any profit and not revert
def test_odds_and_ends_no_profit(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    old_vault,
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

    # if we don't want profit, don't use yswaps
    (profit, loss) = harvest_strategy(
        False,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )
    assert profit == 0
    share_price = vault.pricePerShare()
    assert share_price == 10 ** token.decimals()

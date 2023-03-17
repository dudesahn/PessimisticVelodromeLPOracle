import math
import pytest
import brownie
from utils import harvest_strategy

# test changing the debtRatio on a strategy and then harvesting it
def test_change_debt(
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
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
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

    # evaluate our current total assets
    old_assets = vault.totalAssets()
    startingStrategy = strategy.estimatedTotalAssets()

    # debtRatio is in BPS (aka, max is 10,000, which represents 100%), and is a fraction of the funds that can be in the strategy
    currentDebt = vault.strategies(strategy)["debtRatio"]
    vault.updateStrategyDebtRatio(strategy, currentDebt / 2, {"from": gov})
    chain.sleep(sleep_time)
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    assert strategy.estimatedTotalAssets() <= startingStrategy

    # simulate earnings
    chain.sleep(sleep_time)
    chain.mine(1)

    # set DebtRatio back to 100%
    vault.updateStrategyDebtRatio(strategy, currentDebt, {"from": gov})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # evaluate our current total assets
    new_assets = vault.totalAssets()

    # confirm we made money, or at least that we have about the same
    assert new_assets >= old_assets or math.isclose(new_assets, old_assets, abs_tol=5)

    # simulate five days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and confirm we made money, or at least that we have about the same (profit whale has to be different from normal whale)
    vault.withdraw({"from": whale})
    if is_slippery and no_profit:
        assert (
            math.isclose(token.balanceOf(whale), startingWhale, abs_tol=10)
            or token.balanceOf(whale) >= startingWhale
        )
    else:
        assert token.balanceOf(whale) >= startingWhale


# test changing the debtRatio on a strategy, donating some assets, and then harvesting it
def test_change_debt_with_profit(
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
    profit_whale,
    profit_amount,
    destination_strategy,
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

    # store our values before we start doing weird stuff
    prev_params = vault.strategies(strategy)
    currentDebt = vault.strategies(strategy)["debtRatio"]
    vault.updateStrategyDebtRatio(strategy, currentDebt / 2, {"from": gov})
    assert vault.strategies(strategy)["debtRatio"] == currentDebt / 2

    # our whale donates dust to the vault, what a nice person!
    donation = amount
    token.transfer(strategy, donation, {"from": whale})

    # turn off health check since we just took big profit
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
    new_params = vault.strategies(strategy)

    # sleep 5 days hours to allow share price to normalize
    chain.sleep(5 * 86400)
    chain.mine(1)

    # check to make sure that our debtRatio is about half of our previous debt
    assert new_params["debtRatio"] == currentDebt / 2

    # specifically check that our gain is greater than our donation or at least no more than 10 wei if we get slippage on deposit/withdrawal
    # yswaps also will not have seen profit from the first donation after only one harvest
    profit = new_params["totalGain"] - prev_params["totalGain"]
    if is_slippery and no_profit or use_yswaps:
        assert math.isclose(profit, donation, abs_tol=10) or profit >= donation
    else:
        assert profit > donation
        assert profit > 0

    # check that we didn't add any more loss, or at least no more than 10 wei if we get slippage on deposit/withdrawal
    if is_slippery:
        assert math.isclose(
            new_params["totalLoss"], prev_params["totalLoss"], abs_tol=10
        )
    else:
        assert new_params["totalLoss"] == prev_params["totalLoss"]

    # assert that our vault total assets, multiplied by our debtRatio, is about equal to our estimated total assets plus credit available (within 10 wei)
    # we multiply this by the debtRatio of our strategy out of 10_000 total
    # a vault only knows it has assets if the strategy has reported. yswaps has extra profit donated to the strategy as well.
    if use_yswaps:
        assert math.isclose(
            vault.totalAssets() * new_params["debtRatio"] / 10_000 + profit_amount,
            strategy.estimatedTotalAssets() + vault.creditAvailable(strategy),
            abs_tol=10,
        )
    else:
        assert math.isclose(
            vault.totalAssets() * new_params["debtRatio"] / 10_000,
            strategy.estimatedTotalAssets() + vault.creditAvailable(strategy),
            abs_tol=10,
        )

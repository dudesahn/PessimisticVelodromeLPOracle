import pytest
from utils import harvest_strategy
from brownie import chain

# test reducing the debtRatio on a strategy and then harvesting it
def test_change_debt(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    sleep_time,
    is_slippery,
    no_profit,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    RELATIVE_APPROX,
):
    ## deposit to the vault after approving
    starting_whale = token.balanceOf(whale)
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

    # make sure we reduced our debt properly
    assert (
        pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX)
        == startingStrategy / 2 + profit_amount
    )

    # simulate earnings
    chain.sleep(sleep_time)

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
    if is_slippery and no_profit:
        assert pytest.approx(new_assets, rel=RELATIVE_APPROX) == old_assets
    else:
        new_assets >= old_assets

    # simulate five days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and confirm we made money, or at least that we have about the same (profit whale has to be different from normal whale)
    vault.withdraw({"from": whale})
    if is_slippery and no_profit:
        assert (
            pytest.approx(token.balanceOf(whale), rel=RELATIVE_APPROX) == starting_whale
        )
    else:
        assert token.balanceOf(whale) >= starting_whale


# test changing the debtRatio on a strategy, donating some assets, and then harvesting it
def test_change_debt_with_profit(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    sleep_time,
    is_slippery,
    no_profit,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    RELATIVE_APPROX,
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

    # turn off health check since we just took big profit from our donation
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

    # record our new strategy params
    new_params = vault.strategies(strategy)

    # sleep 5 days hours to allow share price to normalize
    chain.sleep(5 * 86400)
    chain.mine(1)

    # check to make sure that our debtRatio is about half of our previous debt
    assert new_params["debtRatio"] == currentDebt / 2

    # specifically check that our profit is greater than our donation or at least no more than 10 wei if we get slippage on deposit/withdrawal
    # yswaps also will not have seen profit from the first donation after only one harvest
    profit = new_params["totalGain"] - prev_params["totalGain"]
    if is_slippery and no_profit or use_yswaps:
        assert pytest.approx(profit, rel=RELATIVE_APPROX) == donation
    else:
        assert profit > donation
        assert profit > 0

    # check that we didn't add any more loss, and if we did only a little bit if slippery
    if is_slippery:
        assert (
            pytest.approx(new_params["totalLoss"], rel=RELATIVE_APPROX)
            == prev_params["totalLoss"]
        )
    else:
        assert new_params["totalLoss"] == prev_params["totalLoss"]

    # assert that our vault total assets, multiplied by our debtRatio, is about equal to our estimated total assets plus credit available
    # we multiply this by the debtRatio of our strategy out of 10_000 total
    # a vault only knows it has assets if the strategy has reported. yswaps has extra profit donated to the strategy as well that has not yet been reported.
    if use_yswaps:
        assert (
            pytest.approx(
                vault.totalAssets() * new_params["debtRatio"] / 10_000 + profit_amount,
                rel=RELATIVE_APPROX,
            )
            == strategy.estimatedTotalAssets() + vault.creditAvailable(strategy)
        )
    else:
        assert pytest.approx(
            vault.totalAssets() * new_params["debtRatio"] / 10_000, rel=RELATIVE_APPROX
        ) == strategy.estimatedTotalAssets() + vault.creditAvailable(strategy)

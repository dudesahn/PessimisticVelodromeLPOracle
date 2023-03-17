import pytest
from brownie import Contract, chain
from utils import harvest_strategy

# test that emergency exit works properly
def test_emergency_exit(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
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

    # simulate earnings
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

    # set emergency and exit, then confirm that the strategy has no funds
    strategy.setEmergencyExit({"from": gov})
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

    # strategy should be completely empty now
    assert strategy.estimatedTotalAssets() == 0

    # simulate 5 days of waiting for share price to bump back up
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


# test emergency exit, but with a donation (profit)
def test_emergency_exit_with_profit(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
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

    # simulate earnings
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

    # turn off health check since this will be a big profit from the donation
    donation = amount / 2
    token.transfer(strategy, donation, {"from": profit_whale})
    strategy.setDoHealthCheck(False, {"from": gov})

    # set emergency and exit
    strategy.setEmergencyExit({"from": gov})
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

    # confirm that the strategy has no funds
    assert strategy.estimatedTotalAssets() == 0

    # simulate 5 days of waiting for share price to bump back up
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


# test emergency exit, but after somehow losing all of our assets (oopsie)
def test_emergency_exit_with_loss(
    gov,
    token,
    vault,
    whale,
    strategy,
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

    ################# SEND ALL FUNDS AWAY. ADJUST AS NEEDED PER STRATEGY. #################
    staking = Contract(strategy.lqtyStaking())
    to_send = staking.stakes(strategy)
    staking.unstake(to_send, {"from": strategy})
    token.transfer(gov, to_send, {"from": strategy})

    # confirm we emptied the strategy
    assert strategy.estimatedTotalAssets() == 0

    # our whale donates 1 wei to the vault so we don't divide by zero (needed for older vaults)
    if old_vault:
        token.transfer(strategy, 1, {"from": whale})

    # set emergency and exit, but turn off health check since we're taking a huge L
    strategy.setEmergencyExit({"from": gov})
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

    # confirm that the strategy has no funds
    assert strategy.estimatedTotalAssets() == 0

    # vault should also have no assets, except old ones will have 1 wei
    if old_vault:
        assert vault.totalAssets() == 1
    else:
        assert vault.totalAssets() == 0

    # simulate 5 days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and see how down bad we are, confirming we can withdraw from an empty (or mostly empty) vault
    vault.withdraw({"from": whale})
    print(
        "Raw loss:",
        (starting_whale - token.balanceOf(whale)) / 1e18,
        "Percentage:",
        (starting_whale - token.balanceOf(whale)) / starting_whale,
    )
    print("Share price:", vault.pricePerShare() / 1e18)


# test emergency exit, after somehow losing all of our assets but miraculously getting them recovered 🍀
def test_emergency_exit_with_no_loss(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
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

    ################# SEND ALL FUNDS AWAY. ADJUST AS NEEDED PER STRATEGY. #################
    staking = Contract(strategy.lqtyStaking())
    to_send = staking.stakes(strategy)
    staking.unstake(to_send, {"from": strategy})
    token.transfer(gov, to_send, {"from": strategy})

    # confirm we emptied the strategy
    assert strategy.estimatedTotalAssets() == 0

    # gov sends it back
    token.transfer(strategy, to_send, {"from": gov})
    assert strategy.estimatedTotalAssets() > 0

    # set emergency and exit, then confirm that the strategy has no funds
    strategy.setEmergencyExit({"from": gov})
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

    # confirm we didn't lose anything, or at worst just dust
    if is_slippery and no_profit:
        assert pytest.approx(loss, rel=RELATIVE_APPROX) == 0
    else:
        assert loss == 0

    # simulate 5 days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and confirm we made money, or at least that we have about the same
    vault.withdraw({"from": whale})
    if is_slippery and no_profit or use_yswaps:
        assert (
            pytest.approx(token.balanceOf(whale), rel=RELATIVE_APPROX) == starting_whale
        )
    else:
        assert token.balanceOf(whale) >= starting_whale


# test calling emergency shutdown from the vault, harvesting to ensure we can get all assets out
def test_emergency_shutdown_from_vault(
    gov,
    token,
    vault,
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

    # simulate earnings
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

    # simulate earnings
    chain.sleep(sleep_time)

    # set emergency and exit, then confirm that the strategy has no funds
    vault.setEmergencyShutdown(True, {"from": gov})
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # harvest again to get the last of our profit with ySwaps
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

    # shouldn't have any assets
    assert strategy.estimatedTotalAssets() == 0

    # confirm we didn't lose anything, or at worst just dust
    if is_slippery and no_profit:
        assert pytest.approx(loss, rel=RELATIVE_APPROX) == 0
    else:
        assert loss == 0

    # simulate 5 days of waiting for share price to bump back up
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

import math

# test revoking a strategy from the vault
def test_revoke_strategy_from_vault(
    gov,
    token,
    vault,
    whale,
    chain,
    strategy,
    amount,
    is_slippery,
    no_profit,
    sleep_time,
    strategy_harvest,
):

    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    harvest_tx = strategy_harvest()

    # sleep to earn some yield
    chain.sleep(sleep_time)
    chain.mine(1)

    # harvest after revoking
    vaultAssets_starting = vault.totalAssets()
    vault_holdings_starting = token.balanceOf(vault)
    strategy_starting = strategy.estimatedTotalAssets()
    vault.revokeStrategy(strategy.address, {"from": gov})
    harvest_tx = strategy_harvest()
    vaultAssets_after_revoke = vault.totalAssets()

    # confirm we made money, or at least that we have about the same
    assert vaultAssets_after_revoke >= vaultAssets_starting or math.isclose(
        vaultAssets_after_revoke, vaultAssets_starting, abs_tol=5
    )
    assert math.isclose(strategy.estimatedTotalAssets(), 0, abs_tol=5)
    assert token.balanceOf(vault) >= vault_holdings_starting + strategy_starting

    # simulate five days of waiting for share price to bump back up
    chain.sleep(86400 * 5)
    chain.mine(1)

    # withdraw and confirm we made money, or at least that we have about the same
    vault.withdraw({"from": whale})
    if is_slippery and no_profit:
        assert (
            math.isclose(token.balanceOf(whale), startingWhale, abs_tol=10)
            or token.balanceOf(whale) >= startingWhale
        )
    else:
        assert token.balanceOf(whale) >= startingWhale

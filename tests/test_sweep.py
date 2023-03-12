import brownie

# test sweeping out tokens
def test_sweep(
    gov,
    token,
    vault,
    strategist,
    whale,
    strategy,
    chain,
    to_sweep,
    amount,
    strategy_harvest,
):
    # deposit to the vault after approving
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    harvest_tx = strategy_harvest()
    strategy.sweep(to_sweep, {"from": gov})

    # Strategy want token doesn't work
    token.transfer(strategy.address, amount, {"from": whale})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})
    with brownie.reverts():
        strategy.sweep(to_sweep, {"from": whale})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

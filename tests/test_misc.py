import math
from utils import harvest_strategy
import brownie

# test removing a strategy from the withdrawal queue
def test_remove_from_withdrawal_queue(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    amount,
    sleep_time,
    profit_whale,
    profit_amount,
    destination_strategy,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )

    # simulate earnings
    chain.sleep(sleep_time)
    chain.mine(1)
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )
    before = strategy.estimatedTotalAssets()

    # set emergency and exit, then confirm that the strategy has no funds
    vault.removeStrategyFromQueue(strategy, {"from": gov})
    after = strategy.estimatedTotalAssets()
    assert before == after

    # check that our strategy is no longer in the withdrawal queue's 20 addresses
    addresses = []
    for x in range(19):
        address = vault.withdrawalQueue(x)
        addresses.append(address)
    print(
        "Strategy Address: ",
        strategy.address,
        "\nWithdrawal Queue Addresses: ",
        addresses,
    )
    assert not strategy.address in addresses


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
    profit_whale,
    profit_amount,
    destination_strategy,
):

    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )

    # sleep to earn some yield
    chain.sleep(sleep_time)
    chain.mine(1)

    # harvest after revoking
    vaultAssets_starting = vault.totalAssets()
    vault_holdings_starting = token.balanceOf(vault)
    strategy_starting = strategy.estimatedTotalAssets()
    vault.revokeStrategy(strategy.address, {"from": gov})
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )
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


# test the setters on our strategy
def test_setters(
    gov,
    token,
    vault,
    whale,
    strategy,
    amount,
    base_fee_oracle,
    management,
    profit_whale,
    profit_amount,
    destination_strategy,
):
    # deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})

    # test our setters in baseStrategy and our main strategy
    strategy.setMaxReportDelay(0, {"from": gov})
    strategy.setMaxReportDelay(1e18, {"from": gov})
    strategy.setMetadataURI(0, {"from": gov})
    strategy.setMinReportDelay(100, {"from": gov})
    strategy.setRewards(gov, {"from": gov})
    strategy.setStrategist(gov, {"from": gov})
    name = strategy.name()
    print("Strategy Name:", name)


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
    profit_whale,
    profit_amount,
    destination_strategy,
):
    # deposit to the vault after approving
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    (profit, loss) = harvest_strategy(
        True, strategy, token, gov, profit_whale, profit_amount, destination_strategy
    )
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

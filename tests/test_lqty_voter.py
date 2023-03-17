import brownie
from brownie import Contract, config, accounts, chain, interface
import math
from utils import harvest_strategy

# test the our strategy's ability to deposit, harvest, and withdraw, with different optimal deposit tokens if we have them
# turn on keepLQTY for this
def test_simple_harvest_keep(
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
    voter,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    newWhale = token.balanceOf(whale)

    # harvest, store asset amount
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )
    old_assets = vault.totalAssets()
    assert old_assets > 0
    assert token.balanceOf(strategy) == 0
    assert strategy.estimatedTotalAssets() > 0
    print("Starting Assets: ", old_assets / 1e18)

    # turn on keeping some LQTY for our voter
    strategy.setVoter(voter, {"from": gov})

    # simulate profits
    chain.sleep(sleep_time)
    chain.mine(1)

    # check our name
    name = voter.name()
    print("Name:", name)

    # re-set strategy
    voter.setStrategy(strategy, {"from": gov})

    # harvest, store new asset amount
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # need second harvest to get some profits sent to voter (ySwaps)
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # check that our voter got its lqty
    assert voter.stakedBalance() > 0

    ################# GENERATE CLAIMABLE PROFIT HERE AS NEEDED #################
    # we simulate minting LUSD fees from liquity's borrower operations to the staking contract
    lusd_borrower = accounts.at(
        "0xaC5406AEBe35A27691D62bFb80eeFcD7c0093164", force=True
    )
    borrower_operations = accounts.at(
        "0x24179CD81c9e782A4096035f7eC97fB8B783e007", force=True
    )
    staking = Contract("0x4f9Fbb3f1E99B56e0Fe2892e623Ed36A76Fc605d")
    before = staking.getPendingLUSDGain(lusd_borrower)
    staking.increaseF_LUSD(100_000e18, {"from": borrower_operations})
    after = staking.getPendingLUSDGain(lusd_borrower)
    assert after > before

    # check that we have claimable profit on our voter
    claimable_profit = voter.claimableProfitInUsdc()
    assert claimable_profit > 0
    claimable_lusd = staking.getPendingLUSDGain(voter)
    print("Claimable LUSD:", claimable_lusd / 1e18)
    print("Claimable Profit in USDC:", claimable_profit / 1e6)

    # simulate profits
    chain.sleep(sleep_time)
    chain.mine(1)

    # need second harvest to get some profits sent to voter (ySwaps)
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # set our keep to zero
    strategy.setKeepLqty(0, {"from": gov})

    # simulate profits
    chain.sleep(sleep_time)
    chain.mine(1)

    # harvest so we get one with no keep
    (profit, loss) = harvest_strategy(
        use_yswaps,
        strategy,
        token,
        gov,
        profit_whale,
        profit_amount,
        destination_strategy,
    )

    # sleep for 5 days to fully realize profits
    chain.sleep(5 * 86400)
    chain.mine(1)
    new_assets = vault.totalAssets()
    assert new_assets >= old_assets
    print("\nAssets after sleep time: ", new_assets / 1e18)

    # Display estimated APR
    print(
        "\nEstimated APR: ",
        "{:.2%}".format(
            ((new_assets - old_assets) * (365 * 86400 / sleep_time))
            / (strategy.estimatedTotalAssets())
        ),
    )

    # withdraw and confirm we made money, or at least that we have about the same
    tx = vault.withdraw({"from": whale})
    if is_slippery and no_profit:
        assert (
            math.isclose(token.balanceOf(whale), startingWhale, abs_tol=10)
            or token.balanceOf(whale) >= startingWhale
        )
    else:
        assert token.balanceOf(whale) >= startingWhale


# test sweeping out tokens
def test_sweeps(
    gov,
    token,
    vault,
    whale,
    strategy,
    chain,
    to_sweep,
    amount,
    profit_whale,
    profit_amount,
    destination_strategy,
    use_yswaps,
    lusd_whale,
    voter,
):
    # collect our tokens
    lqty = interface.IERC20(strategy.lqty())
    lusd = interface.IERC20(strategy.lusd())

    # lusd whale sends lusd to our voter
    lusd.transfer(voter, 2000e18, {"from": lusd_whale})

    # we can sweep out any non-want
    voter.sweep(strategy.lusd(), {"from": gov})

    # lusd whale sends ether and lusd to our voter
    lusd.transfer(voter, 2000e18, {"from": lusd_whale})
    lusd_whale.transfer(voter, 1e18)
    lqty.transfer(voter, 100e18, {"from": profit_whale})

    # we can sweep out any non-want
    voter.sweep(strategy.lusd(), {"from": gov})

    # can't sweep lqty
    with brownie.reverts():
        voter.sweep(strategy.lqty(), {"from": gov})

    # only gov can sweep
    with brownie.reverts():
        voter.sweep(strategy.lusd(), {"from": whale})

    # lusd whale sends more lusd to our voter
    lusd.transfer(voter, 2000e18, {"from": lusd_whale})

    # queue our sweep
    voter.queueSweep({"from": gov})
    chain.sleep(86400 * 15)

    # sweep!
    voter.unstakeAndSweep(voter.stakedBalance(), {"from": gov})

    # only gov can sweep
    with brownie.reverts():
        voter.unstakeAndSweep(voter.stakedBalance(), {"from": whale})

    chain.sleep(1)
    chain.mine(1)

    # check
    assert voter.stakedBalance() == 0

    # sweep again!
    voter.unstakeAndSweep(voter.stakedBalance(), {"from": gov})

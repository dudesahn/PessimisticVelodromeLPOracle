import pytest
import brownie
from brownie import config, Contract, ZERO_ADDRESS, chain, interface, accounts
from eth_abi import encode_single
import requests


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass


# set this for if we want to use tenderly or not; mostly helpful because with brownie.reverts fails in tenderly forks.
use_tenderly = False

# use this to set what chain we use. 1 for ETH, 250 for fantom, 10 optimism, 42161 arbitrum
chain_used = 10


################################################## TENDERLY DEBUGGING ##################################################

# change autouse to True if we want to use this fork to help debug tests
@pytest.fixture(scope="session", autouse=use_tenderly)
def tenderly_fork(web3, chain):
    fork_base_url = "https://simulate.yearn.network/fork"
    payload = {"network_id": str(chain.id)}
    resp = requests.post(fork_base_url, headers={}, json=payload)
    fork_id = resp.json()["simulation_fork"]["id"]
    fork_rpc_url = f"https://rpc.tenderly.co/fork/{fork_id}"
    print(fork_rpc_url)
    tenderly_provider = web3.HTTPProvider(fork_rpc_url, {"timeout": 600})
    web3.provider = tenderly_provider
    print(f"https://dashboard.tenderly.co/yearn/yearn-web/fork/{fork_id}")


################################################ UPDATE THINGS BELOW HERE ################################################

#################### FIXTURES BELOW NEED TO BE ADJUSTED FOR THIS REPO ####################


# if we want to make harvests public, then we should prevent same-block reward claiming and minting to be safe, but realistically just put it on a gelato job that scream tops up from time to time


# use this to set the standard amount of time we sleep between harvests.
# generally 1 day, but can be less if dealing with smaller windows (oracles) or longer if we need to trigger weekly earnings.
@pytest.fixture(scope="session")
def sleep_time():
    hour = 3600

    # change this one right here
    hours_to_sleep = 24

    sleep_time = hour * hours_to_sleep
    yield sleep_time


#################### FIXTURES ABOVE NEED TO BE ADJUSTED FOR THIS REPO ####################

#################### FIXTURES BELOW SHOULDN'T NEED TO BE ADJUSTED FOR THIS REPO ####################


@pytest.fixture(scope="session")
def tests_using_tenderly():
    yes_or_no = use_tenderly
    yield yes_or_no


@pytest.fixture(
    params=[
        True,
        False,
    ],
    ids=["useAdjustedPrice", "dontUseAdjustedPrice"],
    scope="function",
)
def use_adjusted_price(request):
    yield request.param


@pytest.fixture(
    params=[
        True,
        False,
    ],
    ids=["three_days", "two_days"],
    scope="function",
)
def use_three_days(request):
    yield request.param


@pytest.fixture(scope="session")
def gov():
    yield accounts.at("0xF5d9D6133b698cE29567a90Ab35CfB874204B3A7", force=True)


@pytest.fixture(scope="session")
def weth():
    yield interface.IERC20("0x4200000000000000000000000000000000000006")


# our oracle
@pytest.fixture(scope="function")
def oracle(PessimisticVelodromeLPOracle, gov, use_three_days, use_adjusted_price):
    oracle = gov.deploy(
        PessimisticVelodromeLPOracle,
        gov,
    )
    # set our chainlink feeds, 10 day heartbeat
    # WETH
    feed = "0x13e3Ee699D1909E989722E753853AE30b17e08c5"
    token = "0x4200000000000000000000000000000000000006"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # LDO
    feed = "0x221618871470f78D8a3391d35B77dFb3C0fbc383"
    token = "0xFdb794692724153d1488CcdBE0C56c252596735F"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # LUSD
    feed = "0x9dfc79Aaeb5bb0f96C6e9402671981CdFc424052"
    token = "0xc40F949F8a4e094D1b49a23ea9241D289B7b2819"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # OP
    feed = "0x0D276FC14719f9292D5C1eA2198673d1f4269246"
    token = "0x4200000000000000000000000000000000000042"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # SNX
    feed = "0x2FCF37343e916eAEd1f1DdaaF84458a359b53877"
    token = "0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # USDC
    feed = "0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3"
    token = "0x7F5c764cBc14f9669B88837ca1490cCa17c31607"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # WBTC
    feed = "0x718A5788b89454aAE3A028AE9c111A29Be6c2a6F"
    token = "0x68f180fcCe6836688e9084f035309E29Bf0A2095"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # wstETH
    feed = "0x698B585CbC4407e2D54aa898B2600B53C68958f7"
    token = "0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # FRAX
    feed = "0xc7d132becabe7dcc4204841f33bae45841e41d9c"
    token = "0x2E3D870790dC77A83DD1d18184Acc7439A53f475"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # USDT
    feed = "0xecef79e109e997bca29c1c0897ec9d7b03647f5e"
    token = "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # DAI
    feed = "0x8dba75e83da73cc766a7e5a0ee71f656bab470d6"
    token = "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # sUSD
    feed = "0x7f99817d87bad03ea21e05112ca799d715730efe"
    token = "0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # PERP
    feed = "0xa12cddd8e986af9288ab31e58c60e65f2987fb13"
    token = "0x9e1028F5F1D5eDE59748FFceE5532509976840E0"
    oracle.setFeed(token, feed, 864000, {"from": gov})

    # just run it again
    if not use_adjusted_price and use_three_days:
        with brownie.reverts():
            oracle.setUseAdjustedPrice(use_adjusted_price, use_three_days)
        use_three_days = False

    # setup our pricing preferences
    oracle.setUseAdjustedPrice(use_adjusted_price, use_three_days)

    # rETH-WETH exchange rate: 0x22F3727be377781d1579B7C9222382b21c9d1a8f
    yield oracle


# midas' oracle, returns values in ETH
@pytest.fixture(scope="function")
def midas_oracle(SolidlyLpTokenPriceOracle, gov, weth):
    midas_oracle = gov.deploy(
        SolidlyLpTokenPriceOracle,
        weth,
    )
    yield midas_oracle

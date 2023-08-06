import pytest
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


@pytest.fixture(scope="session")
def token():
    token_address = "0x7D46aee42de131AFa80Acd72094Cf98f3242b926"  # this should be the address of the ERC-20 used by the strategy/vault (sMLP)
    yield interface.IERC20(token_address)


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


@pytest.fixture(scope="session")
def gov():
    yield accounts.at("0xF5d9D6133b698cE29567a90Ab35CfB874204B3A7", force=True)


# our oracle
@pytest.fixture(scope="function")
def oracle(PessimisticVelodromeLPOracle, gov):
    oracle = gov.deploy(
        PessimisticVelodromeLPOracle,
        gov,
    )
    yield oracle

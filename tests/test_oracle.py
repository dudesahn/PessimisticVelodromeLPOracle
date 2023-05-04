import pytest
from brownie import accounts, Contract, chain

# test removing a strategy from the withdrawal queue
def test_oracle(
    gov,
    oracle,
):

    # check our pricing
    result = oracle.latestRoundData({"from": gov})
    print("Result:", result[1] / 1e18)

    # update our price
    oracle.updatePrice({"from": gov})

    # donate some FTM to the LP, price should go up
    wftm_whale = accounts.at("0x3E923747cA2675E096d812c3b24846aC39aeD645", force=True)
    wftm = Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")
    morphex_vault = Contract("0x3CB54f0eB62C371065D739A34a775CC16f46563e")
    wftm.transfer(morphex_vault, 100_000e18, {"from": wftm_whale})
    morphex_vault.directPoolDeposit(wftm, {"from": wftm_whale})

    # check our new price
    after_wftm_donation = oracle.latestRoundData({"from": gov})
    print("After WFTM Donation:", after_wftm_donation[1] / 1e18)
    assert result[1] == after_wftm_donation[1]
    after_wftm_donation_real = oracle.getLivePrice({"from": gov})
    print("After WFTM Donation Live:", after_wftm_donation_real / 1e18)
    assert after_wftm_donation_real > after_wftm_donation[1]

    # send in lots of BTC
    btc_whale = accounts.at("0x38aca5484b8603373acc6961ecd57a6a594510a3", force=True)
    btc = Contract("0x321162Cd933E2Be498Cd2267a90534A804051b11")
    btc.transfer(morphex_vault, 390e8, {"from": btc_whale})
    morphex_vault.directPoolDeposit(btc, {"from": btc_whale})
    assert oracle.getLivePrice({"from": gov}) > after_wftm_donation_real
    assert oracle.getLivePrice({"from": gov}) > oracle.manualPriceCap()
    new_result = oracle.latestRoundData({"from": gov})
    print("After BTC Donation:", new_result[1] / 1e18)
    assert new_result[1] == result[1]
    after_btc_donation_real = oracle.getLivePrice({"from": gov})
    print("After BTC Donation Live:", after_btc_donation_real / 1e18)

    # wait >48 hours so we take new values, we must checkpoint the price every day
    chain.sleep(86400)
    oracle.updatePrice({"from": gov})
    chain.sleep(86400)
    oracle.updatePrice({"from": gov})
    chain.sleep(86400)
    oracle.updatePrice({"from": gov})
    result_after_sleep = oracle.latestRoundData({"from": gov})

    # make sure that our price cap protects us
    assert result_after_sleep[1] == oracle.manualPriceCap()
    after_sleep_real = oracle.getLivePrice({"from": gov})
    print("After Sleep Reported:", result_after_sleep[1] / 1e18)
    print("After Sleep Live:", after_sleep_real / 1e18)

    # below doesn't work, get safemath errors
    # send away all of the BTC and WFTM! Now price is lower than ever
    # btc.transfer(gov, btc.balanceOf(morphex_vault), {"from": morphex_vault})
    # wftm.transfer(gov, wftm.balanceOf(morphex_vault), {"from": morphex_vault})

    # mint some LP to update pricing
    # wftm.approve(oracle.mlpManager(), 2**256 - 1, {"from": wftm_whale})
    # router = Contract("0x20De7f8283D377fA84575A26c9D484Ee40f55877")
    # router.mintAndStakeGlp(wftm, 100e18, 0, 0, {"from": wftm_whale})

    # assert oracle.getLivePrice({"from": gov}) < result[1]
    # assert (
    #    oracle.getLivePrice({"from": gov}) == oracle.latestRoundData({"from": gov})[1]
    # )

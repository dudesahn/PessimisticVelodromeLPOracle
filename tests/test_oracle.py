import pytest
from brownie import accounts, Contract, chain

# test removing a strategy from the withdrawal queue
def test_oracle(
    gov,
    oracle,
):
    # set our chainlink feeds
    weth_feed = "0x13e3Ee699D1909E989722E753853AE30b17e08c5"
    weth = "0x4200000000000000000000000000000000000006"
    oracle.setFeed(weth, weth_feed, {"from": gov})

    # LDO
    feed = "0x221618871470f78D8a3391d35B77dFb3C0fbc383"
    token = "0xFdb794692724153d1488CcdBE0C56c252596735F"
    oracle.setFeed(token, feed, {"from": gov})

    # LUSD
    feed = "0x9dfc79Aaeb5bb0f96C6e9402671981CdFc424052"
    token = "0xc40F949F8a4e094D1b49a23ea9241D289B7b2819"
    oracle.setFeed(token, feed, {"from": gov})

    # OP
    feed = "0x0D276FC14719f9292D5C1eA2198673d1f4269246"
    token = "0x4200000000000000000000000000000000000042"
    oracle.setFeed(token, feed, {"from": gov})

    # SNX
    feed = "0x2FCF37343e916eAEd1f1DdaaF84458a359b53877"
    token = "0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4"
    oracle.setFeed(token, feed, {"from": gov})

    # USDC
    feed = "0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3"
    token = "0x7F5c764cBc14f9669B88837ca1490cCa17c31607"
    oracle.setFeed(token, feed, {"from": gov})

    # WBTC
    feed = "0x718A5788b89454aAE3A028AE9c111A29Be6c2a6F"
    token = "0x68f180fcCe6836688e9084f035309E29Bf0A2095"
    oracle.setFeed(token, feed, {"from": gov})

    # wstETH
    feed = "0x698B585CbC4407e2D54aa898B2600B53C68958f7"
    token = "0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb"
    oracle.setFeed(token, feed, {"from": gov})

    # rETH-WETH exchange rate: 0x22F3727be377781d1579B7C9222382b21c9d1a8f

    reth = "0x9Bcef72be871e61ED4fBbc7630889beE758eb81D"
    weth_reth_pool = "0x7e0F65FAB1524dA9E2E5711D160541cf1199912E"
    price1, price2 = oracle.getTokenPrices(weth_reth_pool)
    print("WETH, rETH Prices:", price1 / 1e8, price2 / 1e8)

    price = oracle.getCurrentPrice(weth_reth_pool)
    print("rETH/WETH Price:", price / 1e8)

    # SNX-USDC
    pool = "0x71d53B5B7141E1ec9A3Fc9Cc48b4766102d14A4A"
    price1, price2 = oracle.getTokenPrices(pool)
    print("USDC, SNX Prices:", price1 / 1e8, price2 / 1e8)

    price = oracle.getCurrentPrice(pool)
    print("USDC/SNX Price:", price / 1e8)


#     # check our pricing
#     result = oracle.latestRoundData({"from": gov})
#     print("Result:", result[1] / 1e18)
#
#     # update our price
#     oracle.updatePrice({"from": gov})
#
#     # donate some FTM to the LP, price should go up
#     wftm_whale = accounts.at("0x3E923747cA2675E096d812c3b24846aC39aeD645", force=True)
#     wftm = Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")
#     morphex_vault = Contract("0x3CB54f0eB62C371065D739A34a775CC16f46563e")
#     wftm.transfer(morphex_vault, 100_000e18, {"from": wftm_whale})
#     morphex_vault.directPoolDeposit(wftm, {"from": wftm_whale})
#
#     # check our new price
#     after_wftm_donation = oracle.latestRoundData({"from": gov})
#     print("After WFTM Donation:", after_wftm_donation[1] / 1e18)
#     assert result[1] == after_wftm_donation[1]
#     after_wftm_donation_real = oracle.getLivePrice({"from": gov})
#     print("After WFTM Donation Live:", after_wftm_donation_real / 1e18)
#     assert after_wftm_donation_real > after_wftm_donation[1]
#
#     # send in lots of BTC
#     btc_whale = accounts.at("0x38aca5484b8603373acc6961ecd57a6a594510a3", force=True)
#     btc = Contract("0x321162Cd933E2Be498Cd2267a90534A804051b11")
#     btc.transfer(morphex_vault, 390e8, {"from": btc_whale})
#     morphex_vault.directPoolDeposit(btc, {"from": btc_whale})
#     assert oracle.getLivePrice({"from": gov}) > after_wftm_donation_real
#     assert oracle.getLivePrice({"from": gov}) > oracle.manualPriceCap()
#     new_result = oracle.latestRoundData({"from": gov})
#     print("After BTC Donation:", new_result[1] / 1e18)
#     assert new_result[1] == result[1]
#     after_btc_donation_real = oracle.getLivePrice({"from": gov})
#     print("After BTC Donation Live:", after_btc_donation_real / 1e18)
#
#     # wait >48 hours so we take new values, we must checkpoint the price every day
#     chain.sleep(86400)
#     oracle.updatePrice({"from": gov})
#     chain.sleep(86400)
#     oracle.updatePrice({"from": gov})
#     chain.sleep(86400)
#     oracle.updatePrice({"from": gov})
#     result_after_sleep = oracle.latestRoundData({"from": gov})
#
#     # make sure that our price cap protects us
#     assert result_after_sleep[1] == oracle.manualPriceCap()
#     after_sleep_real = oracle.getLivePrice({"from": gov})
#     print("After Sleep Reported:", result_after_sleep[1] / 1e18)
#     print("After Sleep Live:", after_sleep_real / 1e18)

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

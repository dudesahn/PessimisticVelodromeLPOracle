import pytest
from brownie import accounts, Contract, chain, interface

# test under normal circumstances
def test_normal_oracle(
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
    print(
        "WETH, rETH Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(weth_reth_pool)
    print("rETH/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # SNX-USDC
    pool = "0x71d53B5B7141E1ec9A3Fc9Cc48b4766102d14A4A"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, SNX Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/SNX LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # VELO-USDC
    pool = "0x8134A2fDC127549480865fB8E5A9E8A8a95a54c5"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, VELO Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/VELO LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # MAI-USDC
    pool = "0xE54e4020d1C3afDB312095D90054103E68fe34B0"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, MAI Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/MAI LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-USDC
    pool = "0x0df083de449F75691fc5A36477a6f3284C269108"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "OP, USDC Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # DOLA-USDC
    pool = "0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/DOLA LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # WETH-frxETH
    pool = "0x3f42Dc59DC4dF5cD607163bC620168f7FF7aB970"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, frxETH Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("WETH-frxETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-WETH
    # 🤑 Price per pool token: $112.15 Address: 0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3
    pool = "0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("WETH-OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")


def test_oracle_price_manipulation(
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
    print(
        "WETH, rETH Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(weth_reth_pool)
    print("rETH/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # SNX-USDC
    pool = "0x71d53B5B7141E1ec9A3Fc9Cc48b4766102d14A4A"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, SNX Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/SNX LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # VELO-USDC
    pool = "0x8134A2fDC127549480865fB8E5A9E8A8a95a54c5"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, VELO Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/VELO LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # MAI-USDC
    pool = "0xE54e4020d1C3afDB312095D90054103E68fe34B0"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, MAI Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/MAI LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-USDC
    pool = "0x0df083de449F75691fc5A36477a6f3284C269108"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "OP, USDC Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # WETH-frxETH
    pool = "0x3f42Dc59DC4dF5cD607163bC620168f7FF7aB970"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, frxETH Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("WETH-frxETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-WETH
    # 🤑 Price per pool token: $112.15 Address: 0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3
    pool = interface.IVeloPoolV2("0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3")
    price1, price2 = oracle.getTokenPrices(pool)
    op = Contract("0x4200000000000000000000000000000000000042")
    weth = Contract("0x4200000000000000000000000000000000000006")
    print(
        "WETH, OP Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    weth_price = price1 / 1e8
    op_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print("WETH-OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # op whale swaps in a lot, should tank price of OP
    whale = accounts.at("0x790b4086D106Eafd913e71843AED987eFE291c92", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    op.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [op.address, weth, False, pool_factory],
    ]
    router.swapExactTokensForTokens(
        1e26, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # OP-WETH
    # 🤑 Price per pool token: $112.15 Address: 0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print(
        "WETH-OP Reserve LP Price after manipulation:",
        "${:,.2f}".format(price / 1e8),
        "\n",
    )

    chain.sleep(86400)
    chain.mine(1)
    print("Sleep one day")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print(
        "WETH-OP Reserve LP Price after manipulation:",
        "${:,.2f}".format(price / 1e8),
        "\n",
    )

    # DOLA-USDC
    pool = "0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPrice(pool)
    print("USDC/DOLA LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    pool = interface.IVeloPoolV2("0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645")
    price1, price2 = oracle.getTokenPrices(pool)
    dola = Contract("0x8aE125E8653821E851F12A49F7765db9a9ce7384")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    print(
        "USDC, DOLA Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    dola_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print("USDC/DOLA LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # dola whale swaps in a lot, should tank price of DOLA
    whale = accounts.at("0x8Bbd036d018657E454F679E7C4726F7a8ECE2773", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    dola.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [dola.address, usdc, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        9e24, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # DOLA-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print(
        "USDC-DOLA Reserve LP Price after manipulation:",
        "${:,.2f}".format(price / 1e8),
        "\n",
    )

    # do this so we have enough checkpoints after the big swap
    chain.sleep(3600)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(3600)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(3600)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(3600)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(3600)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Sleep one day")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool)
    print(
        "USDC-DOLA Reserve LP Price after manipulation:",
        "${:,.2f}".format(price / 1e8),
        "\n",
    )


def test_setters(
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

    # MAI-USDC
    pool = "0xE54e4020d1C3afDB312095D90054103E68fe34B0"
    oracle.updatePrice(pool, {"from": gov})
    price = oracle.getCurrentPrice(pool)
    print("USDC/MAI LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-USDC
    pool = "0x0df083de449F75691fc5A36477a6f3284C269108"
    # WETH-frxETH
    pool_2 = "0x3f42Dc59DC4dF5cD607163bC620168f7FF7aB970"
    oracle.updateManyPrices([pool, pool_2], {"from": gov})
    price = oracle.getCurrentPrice(pool)
    print("USDC/MAI LP Price:", "${:,.2f}".format(price / 1e8), "\n")
    price = oracle.getCurrentPrice(pool_2)
    print("USDC/OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")


#     # check our pricing
#     result = oracle.latestRoundData({"from": gov})
#     print("Result:", result[1] / 1e18)
#
#     # update our price
#     oracle.updatePrice({"from": gov})
#
#     # donate some FTM to the LP, price should go up
#     wftm_whale = accounts.at("0x3E923747cA2675E096d812c3b24846aC39aeD645", force=True)
#     wftm = Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83n")
#     morphex_vault = Contract("0x3CB54f0eB62C371065D739A34a775CC16f46563en")
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
#     btc = Contract("0x321162Cd933E2Be498Cd2267a90534A804051b11n")
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
# router = Contract("0x20De7f8283D377fA84575A26c9D484Ee40f55877n")
# router.mintAndStakeGlp(wftm, 100e18, 0, 0, {"from": wftm_whale})

# assert oracle.getLivePrice({"from": gov}) < result[1]
# assert (
#    oracle.getLivePrice({"from": gov}) == oracle.latestRoundData({"from": gov})[1]
# )

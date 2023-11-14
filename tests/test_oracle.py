import pytest
from brownie import accounts, Contract, chain, interface

# test under normal circumstances
def test_normal_oracle(
    gov,
    oracle,
):
    # rETH-WETH, one chainlink
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

    # SNX-USDC, both chainlink
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

    # VELO-USDC, one chainlink
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

    # MAI-USDC, one chainlink
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

    # DOLA-USDC, one chainlink
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

    # WETH-frxETH, one chainlink
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

    # OP-WETH, both chainlink
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
    # snapshot our chain before we do everything
    chain.snapshot()

    # OP-WETH (same decimals, volatile, both chainlink)
    # since these are both chainlink, should be very resilient to any manipulation
    pool = interface.IVeloPoolV2("0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3")
    price1, price2 = oracle.getTokenPrices(pool)
    op = Contract("0x4200000000000000000000000000000000000042")
    weth = Contract("0x4200000000000000000000000000000000000006")
    print("\n🚨🚨 For WETH-OP, price shouldn't change with any manipulation 🚨🚨\n")
    print(
        "\nWETH, OP Prices:",
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

    price = oracle.getCurrentPrice(pool) / 1e8
    print("WETH-OP LP Price:", "${:,.2f}".format(price))
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves OP-WETH:",
        "${:,.5f}".format(price_diff),
        "\n",
    )

    # op whale swaps in a lot, should tank price of OP
    whale = accounts.at("0x790b4086D106Eafd913e71843AED987eFE291c92", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    op.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [op.address, weth, False, pool_factory],
    ]
    router.swapExactTokensForTokens(
        200e24, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # price again after whale swap
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-OP Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )
    assert manipulation_price == price

    # sleep to see if that affects price at all (it shouldn't)
    chain.sleep(7200)
    chain.mine(1)
    print("Sleep 2 hours")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    sleep_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-OP Reserve LP Price after sleep:",
        "${:,.2f}".format(sleep_price),
        "\n",
    )
    assert sleep_price == price

    # do this so we have enough checkpoints after the big swap (>4 point, >2 hours)
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    # check price again, still should be resilient to manipulation
    swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-OP Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    assert swap_manipulation_price == price

    # increase our lookback twap window for this pair, shouldn't change things since both chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-OP Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # we could a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # however, I prefer to not do this and instead see just how far off someone could drive the pricing.

    # tBTC-WETH (same decimals, volatile, one chainlink)
    tbtc = Contract("0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40")
    weth = Contract("0x4200000000000000000000000000000000000006")
    pool = interface.IVeloPoolV2("0xadBB23Bcc3C1B9810491897cb0690Cf645B858b1")
    price1, price2 = oracle.getTokenPrices(pool)
    print("\n🚨🚨 For WETH-tBTC, price should only change with TWAP 🚨🚨\n")
    print(
        "\nWETH, tBTC Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    weth_price = price1 / 1e8
    tbtc_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool) / 1e8
    print("WETH-tBTC LP Price:", "${:,.2f}".format(price))
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves tBTC-WETH:",
        "${:,.5f}".format(price_diff),
        "\n",
    )

    # tbtc whale swaps in a lot, should tank price of tBTC
    whale = accounts.at("0x6e57B9E54ea043a829584B22182ad22bF446926C", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    tbtc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [tbtc.address, weth, False, pool_factory],
    ]
    router.swapExactTokensForTokens(
        13e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )
    assert pytest.approx(price, 0.001) == manipulation_price

    # sleeping still shouldn't really do anything
    chain.sleep(7200)
    chain.mine(1)
    print("Sleep 2 hours")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    sleep_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after sleep:",
        "${:,.2f}".format(sleep_price),
        "\n",
    )
    assert pytest.approx(price, 0.001) == sleep_price

    # do this so we have enough checkpoints after the big swap (>2 hours, >4 points)
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    # now that we've had enough swaps/time for our TWAP, prices should be rekt
    swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    assert pytest.approx(price, 0.001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
        "\n",
    )
    # adjusting the TWAP window should change our pricing, and it should still be different from the real price
    assert pytest.approx(price, 0.001) != window_swap_manipulation_price
    assert swap_manipulation_price != window_swap_manipulation_price

    # increasing the window should decrease the distance between rekt price and correct price
    assert abs(swap_manipulation_price - price) > abs(
        window_swap_manipulation_price - price
    )

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # we could a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # however, I prefer to not do this and instead see just how far off someone could drive the pricing.

    # DOLA-USDC (DOLA is TWAP, different decimals, stable)
    pool = interface.IVeloPoolV2("0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645")
    dola = Contract("0x8aE125E8653821E851F12A49F7765db9a9ce7384")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\n🚨🚨 For USDC-DOLA, price should change with TWAP and drift with swaps (stable pool) 🚨🚨\n"
    )
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

    price = oracle.getCurrentPrice(pool) / 1e8
    print("USDC/DOLA LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves DOLA-USDC:", "${:,.5f}".format(price_diff))

    # dola whale swaps in a lot, should tank price of DOLA
    whale = accounts.at("0xBA12222222228d8Ba445958a75a0704d566BF2C8", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    dola.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [dola.address, usdc, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        1e24, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # DOLA-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )

    # just make sure we're within 0.1% of each other
    assert pytest.approx(price, 0.001) == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nUSDC, DOLA Prices after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(tiny_swap_manipulation_price),
        "\n",
    )
    # just make sure we're within 0.1% of each other
    assert pytest.approx(price, 0.001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nUSDC, DOLA Prices after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )

    # just make sure we're NOT within 0.01% of each other
    assert pytest.approx(price, 0.0001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
        "\n",
    )
    # adjusting the TWAP window should change our pricing, and it should still be different from the real price
    assert pytest.approx(price, 0.001) != window_swap_manipulation_price
    assert swap_manipulation_price != window_swap_manipulation_price

    # increasing the window should decrease the distance between rekt price and correct price
    assert abs(swap_manipulation_price - price) > abs(
        window_swap_manipulation_price - price
    )

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # LUSD-USDC (18 vs 6 decimals, both chainlink)
    pool = interface.IVeloPoolV2("0xf04458f7B21265b80FC340dE7Ee598e24485c5bB")
    price1, price2 = oracle.getTokenPrices(pool)
    lusd = Contract("0xc40F949F8a4e094D1b49a23ea9241D289B7b2819")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    print(
        "\n🚨🚨 For USDC-LUSD, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing 🚨🚨\n"
    )
    print(
        "USDC, LUSD Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    lusd_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool) / 1e8
    print("USDC/LUSD LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves LUSD-USDC:", "${:,.5f}".format(price_diff))

    # lusd whale swaps in a lot, should tank price of LUSD
    whale = accounts.at("0xAFdf91f120DEC93c65fd63DBD5ec372e5dcA5f82", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    lusd.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [lusd.address, usdc, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        1e23, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # LUSD-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )
    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )

    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # USDT-USDC (both 6 decimals, both chainlink)
    pool = interface.IVeloPoolV2("0x2B47C794c3789f499D8A54Ec12f949EeCCE8bA16")
    price1, price2 = oracle.getTokenPrices(pool)
    usdt = Contract("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    print(
        "\n🚨🚨 For USDC-USDT, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing 🚨🚨\n"
    )
    print(
        "USDC, USDT Prices:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    usdt_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    price = oracle.getCurrentPrice(pool) / 1e8
    print("USDC/USDT LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference USDT-USDC:", "${:,.5f}".format(price_diff))

    # usdt whale swaps in a lot, should tank price of USDT
    whale = accounts.at("0xacD03D601e5bB1B275Bb94076fF46ED9D753435A", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    usdt.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    routes = [
        [usdt.address, usdc, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        6e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    # USDT-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Prices after manipulation:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )
    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, routes, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Pricese after manipulation + swaps/sleeps:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(price1 / 1e8),
        ",",
        "${:,.2f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(swap_manipulation_price),
        "\n",
    )
    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price


def test_setters(
    gov,
    oracle,
):
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

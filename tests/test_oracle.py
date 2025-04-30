import pytest
from brownie import accounts, Contract, chain, interface, ZERO_ADDRESS
import time

# NOTE: Make sure to run these tests in ganache (with an older version of brownie, like 1.19.2) as anvil crashes out
#  when simulating >75 or so transactions in a fork

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
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(weth_reth_pool)
    print("rETH/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # alETH-WETH, one chainlink
    pool = "0xa1055762336F92b4B8d2eDC032A0Ce45ead6280a"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("alETH-WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # tBTC-WETH, one chainlink
    weth_tbtc_pool = "0xadBB23Bcc3C1B9810491897cb0690Cf645B858b1"
    price1, price2 = oracle.getTokenPrices(weth_tbtc_pool)
    print(
        "WETH, tBTC Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(weth_tbtc_pool)
    print("tBTC/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # SNX-USDC, both chainlink
    pool = "0x71d53B5B7141E1ec9A3Fc9Cc48b4766102d14A4A"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, SNX Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("USDC/SNX LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # VELO-USDC, one chainlink
    pool = "0x8134A2fDC127549480865fB8E5A9E8A8a95a54c5"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, VELO Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("USDC/VELO LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # MAI-USDC, one chainlink
    pool = "0xE54e4020d1C3afDB312095D90054103E68fe34B0"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, MAI Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("USDC/MAI LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-USDC
    pool = "0x0df083de449F75691fc5A36477a6f3284C269108"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "OP, USDC Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("USDC/OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # DOLA-USDC, one chainlink
    pool = "0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("USDC/DOLA LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # WETH-frxETH, one chainlink
    pool = "0x3f42Dc59DC4dF5cD607163bC620168f7FF7aB970"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, frxETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("WETH-frxETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-WETH, both chainlink
    pool = "0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3"
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(pool)
    print("WETH-OP LP Price:", "${:,.2f}".format(price / 1e8), "\n")


# test under normal circumstances
def test_normal_oracle_single(
    gov,
    PessimisticVeloSingleOracle,
):

    # set our chainlink feeds, 10 day heartbeat
    # WETH
    feed0 = "0x13e3Ee699D1909E989722E753853AE30b17e08c5"
    feed1 = ZERO_ADDRESS
    heartbeat0 = 864000
    heartbeat1 = 864000
    both_chainlink = False
    twap_points = 4
    use_pessimistic = False

    # rETH-WETH, one chainlink
    pool = "0x7e0F65FAB1524dA9E2E5711D160541cf1199912E"

    oracle = gov.deploy(
        PessimisticVeloSingleOracle,
        pool,
        both_chainlink,
        feed0,
        feed1,
        heartbeat0,
        heartbeat1,
        twap_points,
        gov,
    )

    price1, price2 = oracle.getTokenPrices()
    print(
        "WETH, rETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )

    price = oracle.getCurrentPoolPrice(use_pessimistic)
    print("rETH/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # update some prices
    oracle.setOperator(gov, True, {"from": gov})
    oracle.updatePrice({"from": gov})
    price = oracle.getCurrentPoolPrice(True)
    print("rETH/WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")


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
    whale = accounts.at("0x2A82Ae142b2e62Cb7D10b55E323ACB1Cab663a26", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    op.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    route = [
        [op.address, weth, False, pool_factory],
    ]

    print("\n✅  For WETH-OP, price shouldn't change with any manipulation ✅ \n")
    print(
        "\nWETH, OP Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    weth_price = price1 / 1e8
    op_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # check the vault token price!
    op_weth_vault = Contract("0xDdDCAeE873f2D9Df0E18a80709ef2B396d4a6EA5")
    vault_price = oracle.getCurrentVaultPriceV2(op_weth_vault) / 1e8
    print("🏦 Vault token price:", "${:,.2f}".format(vault_price))
    print("Vault pricePerShare", op_weth_vault.pricePerShare() / 1e18)
    print(
        "Vault PPS * LP spot price:", spot_price * op_weth_vault.pricePerShare() / 1e18
    )

    # swap in 200M OP
    amount_to_swap = 200e24

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * op_price / 1e18))
    ratio = amount_to_swap * op_price / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("WETH-OP LP Price:", "${:,.2f}".format(price))
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves OP-WETH:",
        "${:,.5f}".format(price_diff),
        "\n",
    )

    # op whale swaps in a lot, should tank price of OP
    router.swapExactTokensForTokens(
        amount_to_swap, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    # price again after whale swap
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    sleep_price = oracle.getCurrentPoolPrice(pool) / 1e8
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
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, OP Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    # check price again, still should be resilient to manipulation
    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price + op.balanceOf(pool) / 1e18 * op_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "WETH-OP Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
        "\n",
    )
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # tBTC-WETH (same decimals, volatile, one chainlink)
    tbtc = Contract("0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40")
    weth = Contract("0x4200000000000000000000000000000000000006")
    pool = interface.IVeloPoolV2("0xadBB23Bcc3C1B9810491897cb0690Cf645B858b1")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at("0x6e57B9E54ea043a829584B22182ad22bF446926C", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    tbtc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    route = [
        [tbtc.address, weth, False, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("\n✅  For WETH-tBTC, price should only change with TWAP ✅ \n")
    print(
        "\nWETH, tBTC Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    weth_price = price1 / 1e8
    tbtc_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in 13 tBTC
    amount_to_swap = 13e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * tbtc_price / 1e18))
    ratio = amount_to_swap * tbtc_price / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("WETH-tBTC LP Price:", "${:,.2f}".format(price))
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves tBTC-WETH:",
        "${:,.5f}".format(price_diff),
        "\n",
    )

    # tbtc whale swaps in a lot, should tank price of tBTC
    router.swapExactTokensForTokens(
        amount_to_swap, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    assert price == manipulation_price

    # sleeping still shouldn't really do anything
    chain.sleep(7200)
    chain.mine(1)
    print("Sleep 2 hours")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    sleep_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after sleep:",
        "${:,.2f}".format(sleep_price),
        "\n",
    )

    # similarly to our manipulation price, sleeping should have no impact on the reserve price either. need more TWAPs.
    assert price == sleep_price

    # do this so we have enough checkpoints after the big swap (>2 hours, >4 points)
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e17, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
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
    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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

    # tBTC-WETH (same decimals, volatile, one chainlink)
    tbtc = Contract("0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40")
    weth = Contract("0x4200000000000000000000000000000000000006")
    pool = interface.IVeloPoolV2("0xadBB23Bcc3C1B9810491897cb0690Cf645B858b1")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at("0x6e57B9E54ea043a829584B22182ad22bF446926C", force=True)
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    tbtc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    route = [
        [tbtc.address, weth, False, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("\n✅  For WETH-tBTC, price should only change with TWAP ✅ \n")
    print(
        "Doing a second run here to test out only swapping for TWAP\nPrevious run tested only sleeping"
    )
    print(
        "\nWETH, tBTC Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    weth_price = price1 / 1e8
    tbtc_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in 13 tBTC
    amount_to_swap = 13e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * tbtc_price / 1e18))
    ratio = amount_to_swap * tbtc_price / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("WETH-tBTC LP Price:", "${:,.2f}".format(price))
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves tBTC-WETH:",
        "${:,.5f}".format(price_diff),
        "\n",
    )

    # tbtc whale swaps in a lot, should tank price of tBTC
    router.swapExactTokensForTokens(
        amount_to_swap, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    assert price == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "WETH-tBTC Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(tiny_swap_manipulation_price),
    )

    # more tiny swaps shouldn't move the price if we don't trigger a new TWAP period
    assert price == tiny_swap_manipulation_price

    # do this so we have enough checkpoints after the big swap (>2 hours, >4 points)
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e16, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("\nSwap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "WETH, tBTC Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
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
    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + tbtc.balanceOf(pool) / 1e18 * tbtc_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
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

    # alETH-WETH (alETH is TWAP, stable)
    pool = interface.IVeloPoolV2(
        "0xa1055762336F92b4B8d2eDC032A0Ce45ead6280a"
    )  # ~$2.5M as of 4/28/25
    aleth = Contract("0x3E29D3A9316dAB217754d13b28646B76607c5f04")
    weth = Contract("0x4200000000000000000000000000000000000006")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at(
        "0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8", force=True
    )  # weth
    other_whale = accounts.at(
        "0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a", force=True
    )  # aleth
    aleth.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    weth.approve(router, 2**256 - 1, {"from": whale})
    aleth.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [weth, aleth, True, pool_factory],
    ]
    route = [
        [aleth, weth, True, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    print(
        "⏳  Latest TWAP observation before start:", pool.lastObservation()["timestamp"]
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before start:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print(
        "\n✅  For alETH-WETH, price should change with TWAP and drift with swaps (stable pool) ✅ \n"
    )
    print(
        "alETH, WETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    aleth_price = price1 / 1e8
    weth_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in 4,000 WETH (~$6.8M)
    amount_to_swap = 4_000e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * weth_price / 1e18))
    ratio = amount_to_swap / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price_timestamp = pool.lastObservation()["timestamp"]
    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("alETH/WETH LP Price:", "${:,.8f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves alETH-WETH:", "${:,.5f}".format(price_diff)
    )

    print(
        "⏳  Latest TWAP observation before big swap:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # weth whale swaps in a lot, should tank price of WETH
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # alETH-WETH
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        (weth.balanceOf(pool) / 1e18 * weth_price)
        + (aleth.balanceOf(pool) / 1e18 * aleth_price)
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation:",
        "${:,.8f}".format(manipulation_price),
    )

    print(
        "⏳  Latest TWAP observation after big swap, before small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    assert price == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after small swaps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.8f}".format(tiny_swap_manipulation_price),
    )

    # tbh not clear why these series of tiny swaps actually move the price a bit if one big one didn't
    # ***** LOOK INTO TWAP CODE AND FIGURE OUT HOW NEW SWAPS IN THE SAME PERIOD AFFECT PRICING RETURNED *******
    # should be able to call pool.lastObservation()["timestamp"] and check if that was within 30 minutes or not
    # if that was within 30 minutes, and we still get the price moving with more swaps...not sure what to do
    # if price_timestamp == pool.lastObservation()["timestamp"]:
    #    assert price == tiny_swap_manipulation_price

    # do this so we have enough checkpoints after the big swap
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after swaps/sleeps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after swaps/sleeps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(swap_manipulation_price),
    )

    # just make sure we're NOT within 0.01% of each other
    assert pytest.approx(price, 0.0001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(window_swap_manipulation_price),
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

    # DOLA-USDC (DOLA is TWAP, different decimals, stable)
    pool = interface.IVeloPoolV2(
        "0xB720FBC32d60BB6dcc955Be86b98D8fD3c4bA645"
    )  # ~$30k as of 2/10/25
    dola = Contract("0x8aE125E8653821E851F12A49F7765db9a9ce7384")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at(
        "0xDecC0c09c3B5f6e92EF4184125D5648a66E35298", force=True
    )  # usdc
    other_whale = accounts.at(
        "0x67C253eB6C2e69F9E1114aEeAD0DB4FA8F417AC3", force=True
    )  # dola
    dola.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    usdc.approve(router, 2**256 - 1, {"from": whale})
    dola.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [usdc, dola, True, pool_factory],
    ]
    route = [
        [dola, usdc, True, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    print(
        "⏳  Latest TWAP observation before start:", pool.lastObservation()["timestamp"]
    )
    twap_price = oracle.getTwapPrice(pool, dola, 1e18)
    print("DOLA TWAP Price before start:", twap_price / 1e6)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print(
        "\n✅  For USDC-DOLA, price should change with TWAP and drift with swaps (stable pool) ✅ \n"
    )
    print(
        "USDC, DOLA Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    dola_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in $6M USDC
    amount_to_swap = 6e12

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * 1e12 / 1e18))
    ratio = amount_to_swap * 1e12 / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price_timestamp = pool.lastObservation()["timestamp"]
    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("USDC/DOLA LP Price:", "${:,.8f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves DOLA-USDC:", "${:,.5f}".format(price_diff))

    print(
        "⏳  Latest TWAP observation before big swap:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, dola, 1e18)
    print("DOLA TWAP Price before big swap:", twap_price / 1e6)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # usdc whale swaps in a lot, should tank price of USDC
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # DOLA-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        (usdc.balanceOf(pool) / 1e6 * usdc_price)
        + (dola.balanceOf(pool) / 1e18 * dola_price)
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation:",
        "${:,.8f}".format(manipulation_price),
    )

    print(
        "⏳  Latest TWAP observation after big swap, before small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, dola, 1e18)
    print("DOLA TWAP Price after big swap:", twap_price / 1e6)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    # assert price == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, dola, 1e18)
    print("DOLA TWAP Price after small swaps:", twap_price / 1e6)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nUSDC, DOLA Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.8f}".format(tiny_swap_manipulation_price),
    )

    # tbh not clear why these series of tiny swaps actually move the price a bit if one big one didn't
    # ***** LOOK INTO TWAP CODE AND FIGURE OUT HOW NEW SWAPS IN THE SAME PERIOD AFFECT PRICING RETURNED *******
    # should be able to call pool.lastObservation()["timestamp"] and check if that was within 30 minutes or not
    # if that was within 30 minutes, and we still get the price moving with more swaps...not sure what to do
    # if price_timestamp == pool.lastObservation()["timestamp"]:
    #    assert price == tiny_swap_manipulation_price

    # do this so we have enough checkpoints after the big swap
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after swaps/sleeps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, dola, 1e18)
    print("DOLA TWAP Price after swaps/sleeps:", twap_price / 1e6)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nUSDC, DOLA Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(swap_manipulation_price),
    )

    # just make sure we're NOT within 0.01% of each other
    assert pytest.approx(price, 0.0001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DOLA Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + dola.balanceOf(pool) / 1e18 * dola_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DOLA Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(window_swap_manipulation_price),
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
    pool = interface.IVeloPoolV2(
        "0xf04458f7B21265b80FC340dE7Ee598e24485c5bB"
    )  # ~$3k as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    lusd = Contract("0xc40F949F8a4e094D1b49a23ea9241D289B7b2819")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    whale = accounts.at(
        "0xDecC0c09c3B5f6e92EF4184125D5648a66E35298", force=True
    )  # usdc
    other_whale = accounts.at(
        "0x0172e05392aba65366C4dbBb70D958BbF43304E4", force=True
    )  # lusd
    lusd.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    lusd.approve(router, 2**256 - 1, {"from": whale})
    usdc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [usdc, lusd, True, pool_factory],
    ]
    route = [
        [lusd, usdc, True, pool_factory],
    ]

    print(
        "\n✅  For USDC-LUSD, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "USDC, LUSD Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    lusd_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in $6M USDC
    amount_to_swap = 6e12

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * 1e12 / 1e18))
    ratio = amount_to_swap * 1e12 / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("USDC/LUSD LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves LUSD-USDC:", "${:,.5f}".format(price_diff))

    # usdc whale swaps in a lot, should tank price of USDC
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # LUSD-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
    )

    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, shouldn't change things since LUSD/USDC is pure chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, LUSD Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + lusd.balanceOf(pool) / 1e18 * lusd_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-LUSD Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # DAI-USDC (18 vs 6 decimals, both chainlink)
    pool = interface.IVeloPoolV2(
        "0x19715771E30c93915A5bbDa134d782b81A820076"
    )  # ~$18k as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    dai = Contract("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    print(
        "\n✅  For USDC-DAI, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "USDC, DAI Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    dai_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in $6M USDC
    amount_to_swap = 6e12

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * 1e12 / 1e18))
    ratio = amount_to_swap * 1e12 / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("USDC/DAI LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves DAI-USDC:", "${:,.5f}".format(price_diff))

    # usdc whale swaps in a lot, should tank price of USDC
    whale = accounts.at(
        "0xDecC0c09c3B5f6e92EF4184125D5648a66E35298", force=True
    )  # usdc
    other_whale = accounts.at(
        "0x1eED63EfBA5f81D95bfe37d82C8E736b974F477b", force=True
    )  # dai
    dai.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    dai.approve(router, 2**256 - 1, {"from": whale})
    usdc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [usdc, dai, True, pool_factory],
    ]
    route = [
        [dai, usdc, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # DAI-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DAI Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DAI Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
    )
    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DAI Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DAI Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, shouldn't change things since DAI/USDC is pure chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, DAI Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-DAI Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # FRAX-USDC (18 vs 6 decimals, both chainlink)
    pool = interface.IVeloPoolV2(
        "0x8542DD4744edEa38b8a9306268b08F4D26d38581"
    )  # ~$73k as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    frax = Contract("0x2E3D870790dC77A83DD1d18184Acc7439A53f475")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    whale = accounts.at(
        "0xDecC0c09c3B5f6e92EF4184125D5648a66E35298", force=True
    )  # usdc
    other_whale = accounts.at(
        "0xCc4Dd8Bc7967D46060bA3fAAA8e525A35625F8b4", force=True
    )  # frax
    frax.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    frax.approve(router, 2**256 - 1, {"from": whale})
    usdc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [usdc, frax, True, pool_factory],
    ]
    route = [
        [frax, usdc, True, pool_factory],
    ]

    print(
        "\n✅  For USDC-FRAX, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "USDC, FRAX Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    frax_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in $6M USDC
    amount_to_swap = 6e12

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * 1e12 / 1e18))
    ratio = amount_to_swap * 1e12 / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("USDC/FRAX LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves FRAX-USDC:", "${:,.5f}".format(price_diff))

    # usdc whale swaps in a lot, should tank price of USDC
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # FRAX-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, FRAX Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-FRAX Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
    )
    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        5e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        5e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        5e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        5e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        5e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, FRAX Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-FRAX Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, shouldn't change things since FRAX/USDC is pure chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, FRAX Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-FRAX Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # DAI-LUSD (18 vs 18 decimals, both chainlink)
    pool = interface.IVeloPoolV2(
        "0x0D0F65C63E379263f7CE2713dd012180681D0dc5"
    )  # ~$232 as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    dai = Contract("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1")
    lusd = Contract("0xc40F949F8a4e094D1b49a23ea9241D289B7b2819")
    print(
        "\n✅  For LUSD-DAI, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "LUSD, DAI Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    lusd_price = price1 / 1e8
    dai_price = price2 / 1e8
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in $6M DAI
    amount_to_swap = 6e24

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap / 1e18))
    ratio = amount_to_swap / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("LUSD/DAI LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves DAI-LUSD:", "${:,.5f}".format(price_diff))

    # dai whale swaps in a lot, should tank price of DAI
    whale = accounts.at("0x1eED63EfBA5f81D95bfe37d82C8E736b974F477b", force=True)  # dai
    other_whale = accounts.at(
        "0x0172e05392aba65366C4dbBb70D958BbF43304E4", force=True
    )  # lusd
    lusd.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    dai.approve(router, 2**256 - 1, {"from": whale})
    lusd.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [dai, lusd, True, pool_factory],
    ]
    route = [
        [lusd, dai, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # DAI-LUSD
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, DAI Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-DAI Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )

    # Since we aggressively manipulate here, this won't hold true
    # assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, DAI Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-DAI Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # Since we aggressively manipulate here, this won't hold true
    # assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, shouldn't change things since DAI/LUSD is pure chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, DAI Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + dai.balanceOf(pool) / 1e18 * dai_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-DAI Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(window_swap_manipulation_price),
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # FRAX-LUSD (18 vs 18 decimals, both chainlink) 🚨🚨🚨 VOLATILE!!!!!
    pool = interface.IVeloPoolV2(
        "0xf0dC43BbAe48dd39b97229CEC09894A503Ea230C"
    )  # ~$1> as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    frax = Contract("0x2E3D870790dC77A83DD1d18184Acc7439A53f475")
    lusd = Contract("0xc40F949F8a4e094D1b49a23ea9241D289B7b2819")
    print(
        "\n✅  For this LUSD-FRAX, price should not move since xy=k (vAMM)... Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "LUSD, FRAX Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    lusd_price = price1 / 1e8
    frax_price = price2 / 1e8
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.8f}".format(spot_price))

    # swap in $250k FRAX
    amount_to_swap = 250_000e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap / 1e18))
    ratio = amount_to_swap / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("LUSD/FRAX LP Price:", "${:,.8f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference spot vs reserves FRAX-LUSD:", "${:,.8f}".format(price_diff))

    # frax whale swaps in a lot, should tank price of FRAX
    whale = accounts.at(
        "0xCc4Dd8Bc7967D46060bA3fAAA8e525A35625F8b4", force=True
    )  # frax
    other_whale = accounts.at(
        "0x0172e05392aba65366C4dbBb70D958BbF43304E4", force=True
    )  # lusd
    lusd.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    frax.approve(router, 2**256 - 1, {"from": whale})
    lusd.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [frax, lusd, False, pool_factory],
    ]
    route = [
        [lusd, frax, False, pool_factory],
    ]
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # FRAX-LUSD
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, FRAX Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.8f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-FRAX Reserve LP Price after manipulation:",
        "${:,.8f}".format(manipulation_price),
        "\n",
    )
    assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, FRAX Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-FRAX Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(swap_manipulation_price),
        "\n",
    )

    # Should be the same thing here, slight changes over time, stable pools seem to drift (even with two chainlink feeds)
    assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, shouldn't change things since FRAX/LUSD is pure chainlink
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "LUSD, FRAX Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        lusd.balanceOf(pool) / 1e18 * lusd_price
        + frax.balanceOf(pool) / 1e18 * frax_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "LUSD-FRAX Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(window_swap_manipulation_price),
        "\n",
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price

    ##############################################################################################################

    # revert to our snapshot for the new pair
    chain.revert()

    # USDT-USDC (both 6 decimals, both chainlink)
    pool = interface.IVeloPoolV2(
        "0x2B47C794c3789f499D8A54Ec12f949EeCCE8bA16"
    )  # ~$25k as of 2/10/25
    price1, price2 = oracle.getTokenPrices(pool)
    usdt = Contract("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58")
    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    print(
        "\n✅  For USDC-USDT, price should only drift with swaps (stable pool). Adjusting TWAP length does nothing ✅ \n"
    )
    print(
        "USDC, USDT Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    usdc_price = price1 / 1e8
    usdt_price = price2 / 1e8
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in USDT
    amount_to_swap = 30_000_000e6  # 30M USDT

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * 1e12 / 1e18))
    ratio = amount_to_swap * 1e12 / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("USDC/USDT LP Price:", "${:,.2f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print("Price difference USDT-USDC:", "${:,.5f}".format(price_diff))

    # usdt whale swaps in a lot, should tank price of USDT
    whale = accounts.at(
        "0xacD03D601e5bB1B275Bb94076fF46ED9D753435A", force=True
    )  # usdt
    other_whale = accounts.at(
        "0xDecC0c09c3B5f6e92EF4184125D5648a66E35298", force=True
    )  # usdc
    usdc.transfer(whale, 100e6, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    usdt.approve(router, 2**256 - 1, {"from": whale})
    usdc.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [usdt, usdc, True, pool_factory],
    ]
    route = [
        [usdc, usdt, True, pool_factory],
    ]
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # USDT-USDC
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation:",
        "${:,.2f}".format(manipulation_price),
        "\n",
    )

    # Since we aggressively manipulate here, this won't hold true
    # assert pytest.approx(price, 0.0001) == manipulation_price

    # do this so we have enough checkpoints after the big swap
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e6, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # Since we aggressively manipulate here, this won't hold true
    # assert pytest.approx(price, 0.0001) == swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "USDC, USDT Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        usdc.balanceOf(pool) / 1e6 * usdc_price
        + usdt.balanceOf(pool) / 1e6 * usdt_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "USDC-USDT Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(swap_manipulation_price),
    )

    # adjusting the TWAP window shouldn't change our price at all, drift or not
    assert swap_manipulation_price == window_swap_manipulation_price


def test_price_update(
    gov,
    oracle,
):
    # OP-USDC
    pool = "0x0df083de449F75691fc5A36477a6f3284C269108"
    oracle.updatePrice(pool, {"from": gov})
    price = oracle.getCurrentPoolPrice(pool)
    print("OP-USDC LP Price:", "${:,.2f}".format(price / 1e8), "\n")

    # OP-WETH
    pool = "0xd25711EdfBf747efCE181442Cc1D8F5F8fc8a0D3"

    # WETH-alETH
    pool_2 = "0xa1055762336F92b4B8d2eDC032A0Ce45ead6280a"
    oracle.updateManyPrices([pool, pool_2], {"from": gov})
    price = oracle.getCurrentPoolPrice(pool)
    print("OP-WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")
    price = oracle.getCurrentPoolPrice(pool_2)
    print("alETH-WETH LP Price:", "${:,.2f}".format(price / 1e8), "\n")


def test_aleth_only(
    gov,
    oracle,
):
    # snapshot our chain before we do everything
    chain.snapshot()

    # alETH-WETH (alETH is TWAP, stable)
    pool = interface.IVeloPoolV2(
        "0xa1055762336F92b4B8d2eDC032A0Ce45ead6280a"
    )  # ~$2.5M as of 4/28/25
    aleth = Contract("0x3E29D3A9316dAB217754d13b28646B76607c5f04")
    weth = Contract("0x4200000000000000000000000000000000000006")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at(
        "0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8", force=True
    )  # weth
    other_whale = accounts.at(
        "0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a", force=True
    )  # aleth
    aleth.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    weth.approve(router, 2**256 - 1, {"from": whale})
    aleth.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [weth, aleth, True, pool_factory],
    ]
    route = [
        [aleth, weth, True, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    print(
        "⏳  Latest TWAP observation before start:", pool.lastObservation()["timestamp"]
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before start:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print(
        "\n✅  For alETH-WETH, price should change with TWAP and drift with swaps (stable pool) ✅ \n"
    )
    print(
        "alETH, WETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    aleth_price = price1 / 1e8
    weth_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in 4,000 WETH (~$6.8M)
    amount_to_swap = 4_000e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * weth_price / 1e18))
    ratio = amount_to_swap * weth_price / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price_timestamp = pool.lastObservation()["timestamp"]
    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("alETH/WETH LP Price:", "${:,.8f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves alETH-WETH:", "${:,.5f}".format(price_diff)
    )

    print(
        "⏳  Latest TWAP observation before big swap:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # weth whale swaps in a lot, should tank price of WETH
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # alETH-WETH
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        (weth.balanceOf(pool) / 1e18 * weth_price)
        + (aleth.balanceOf(pool) / 1e18 * aleth_price)
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation:",
        "${:,.8f}".format(manipulation_price),
    )

    print(
        "⏳  Latest TWAP observation after big swap, before small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    assert price == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after small swaps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.8f}".format(tiny_swap_manipulation_price),
    )

    # tbh not clear why these series of tiny swaps actually move the price a bit if one big one didn't
    # ***** LOOK INTO TWAP CODE AND FIGURE OUT HOW NEW SWAPS IN THE SAME PERIOD AFFECT PRICING RETURNED *******
    # should be able to call pool.lastObservation()["timestamp"] and check if that was within 30 minutes or not
    # if that was within 30 minutes, and we still get the price moving with more swaps...not sure what to do
    # if price_timestamp == pool.lastObservation()["timestamp"]:
    #    assert price == tiny_swap_manipulation_price

    # do this so we have enough checkpoints after the big swap
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after swaps/sleeps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after swaps/sleeps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(swap_manipulation_price),
    )

    # just make sure we're NOT within 0.01% of each other
    assert pytest.approx(price, 0.0001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(window_swap_manipulation_price),
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

    # f
    print("\n🔄 Flip the direction of manipulation—overload with alETH this time\n")

    # alETH-WETH (alETH is TWAP, stable)
    pool = interface.IVeloPoolV2(
        "0xa1055762336F92b4B8d2eDC032A0Ce45ead6280a"
    )  # ~$2.5M as of 4/28/25
    aleth = Contract("0x3E29D3A9316dAB217754d13b28646B76607c5f04")
    weth = Contract("0x4200000000000000000000000000000000000006")
    price1, price2 = oracle.getTokenPrices(pool)
    whale = accounts.at(
        "0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a", force=True
    )  # aleth
    other_whale = accounts.at(
        "0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8", force=True
    )  # weth
    weth.transfer(whale, 100e18, {"from": other_whale})
    router = Contract("0xa062aE8A9c5e11aaA026fc2670B0D65cCc8B2858")
    weth.approve(router, 2**256 - 1, {"from": whale})
    aleth.approve(router, 2**256 - 1, {"from": whale})
    pool_factory = "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a"
    main_route = [
        [aleth, weth, True, pool_factory],
    ]
    route = [
        [weth, aleth, True, pool_factory],
    ]

    # do a tiny swap at the beginning of the test to fix our TWAP at a set point for the test (relatively, at least)
    # 🚨 NOTE: in the real world, if a pool isn't very active, this means that any potential large swap will automatically
    #  be counted toward's an LP's price and thus will start at a disadvantage
    print(
        "⏳  Latest TWAP observation before start:", pool.lastObservation()["timestamp"]
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before start:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    print(
        "\n✅  For alETH-WETH, price should change with TWAP and drift with swaps (stable pool) ✅ \n"
    )
    print(
        "alETH, WETH Prices:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    aleth_price = price1 / 1e8
    weth_price = price2 / 1e8
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print("Spot price:", "${:,.2f}".format(spot_price))

    # swap in 450 alETH
    amount_to_swap = 450e18

    # check ratios and TVL
    print("Pool TVL:", "${:,.8f}".format(spot_price * pool.totalSupply() / 1e18))
    print("Whale swap:", "${:,.8f}".format(amount_to_swap * aleth_price / 1e18))
    ratio = amount_to_swap * aleth_price / (spot_price * pool.totalSupply())
    print("Swap to TVL Ratio:", "{:,.2f}x".format(ratio))

    price_timestamp = pool.lastObservation()["timestamp"]
    price = oracle.getCurrentPoolPrice(pool) / 1e8
    print("alETH/WETH LP Price:", "${:,.8f}".format(price), "\n")
    price_diff = abs(price - spot_price)
    print(
        "Price difference spot vs reserves alETH-WETH:", "${:,.5f}".format(price_diff)
    )

    print(
        "⏳  Latest TWAP observation before big swap:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price before big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # weth whale swaps in a lot, should tank price of WETH
    router.swapExactTokensForTokens(
        amount_to_swap, 0, main_route, whale.address, 2**256 - 1, {"from": whale}
    )

    # alETH-WETH
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        (weth.balanceOf(pool) / 1e18 * weth_price)
        + (aleth.balanceOf(pool) / 1e18 * aleth_price)
    ) / (pool.totalSupply() / 1e18)
    print("LP spot price after manipulation:", "${:,.2f}".format(spot_price))

    manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation:",
        "${:,.8f}".format(manipulation_price),
    )

    print(
        "⏳  Latest TWAP observation after big swap, before small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after big swap:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    # note that since we stabilized our TWAP before our manipulation swap, the manipulation should have no effect
    assert price == manipulation_price

    # do 5 swaps but just 5 seconds, shouldn't change prices vs previous swaps significantly
    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e18, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after small swaps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after small swaps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, but don't sleep much")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + tiny swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    tiny_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + tiny swaps/sleeps:",
        "${:,.8f}".format(tiny_swap_manipulation_price),
    )

    # tbh not clear why these series of tiny swaps actually move the price a bit if one big one didn't
    # ***** LOOK INTO TWAP CODE AND FIGURE OUT HOW NEW SWAPS IN THE SAME PERIOD AFFECT PRICING RETURNED *******
    # should be able to call pool.lastObservation()["timestamp"] and check if that was within 30 minutes or not
    # if that was within 30 minutes, and we still get the price moving with more swaps...not sure what to do
    # if price_timestamp == pool.lastObservation()["timestamp"]:
    #    assert price == tiny_swap_manipulation_price

    # do this so we have enough checkpoints after the big swap
    # we do small swaps because the size is not important, it's the checkpointing
    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )

    chain.sleep(1800)
    chain.mine(1)
    router.swapExactTokensForTokens(
        1e12, 0, route, whale.address, 2**256 - 1, {"from": whale}
    )
    print(
        "⏳  Latest TWAP observation after swaps/sleeps:",
        pool.lastObservation()["timestamp"],
    )
    twap_price = oracle.getTwapPrice(pool, aleth, 1e18)
    print("alETH TWAP Price after swaps/sleeps:", twap_price / 1e18)
    print("Reserve0:", pool.reserve0())
    print("Reserve1:", pool.reserve1())

    print("Swap a few times, sleep to wait out our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "\nalETH, WETH Prices after manipulation + swaps/sleeps:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps:",
        "${:,.2f}".format(spot_price),
    )

    swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps:",
        "${:,.8f}".format(swap_manipulation_price),
    )

    # just make sure we're NOT within 0.01% of each other
    assert pytest.approx(price, 0.0001) != swap_manipulation_price

    # increase our lookback twap window for this pair, should change things
    oracle.setPointsOverride(pool, 24, {"from": gov})
    print("Add more points to our TWAP")
    price1, price2 = oracle.getTokenPrices(pool)
    print(
        "alETH, WETH Prices after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(price1 / 1e8),
        ",",
        "${:,.8f}".format(price2 / 1e8),
    )
    spot_price = (
        weth.balanceOf(pool) / 1e18 * weth_price
        + aleth.balanceOf(pool) / 1e18 * aleth_price
    ) / (pool.totalSupply() / 1e18)
    print(
        "LP spot price after manipulation + swaps/sleeps + window increase:",
        "${:,.2f}".format(spot_price),
    )

    window_swap_manipulation_price = oracle.getCurrentPoolPrice(pool) / 1e8
    print(
        "alETH-WETH Reserve LP Price after manipulation + swaps/sleeps + window increase:",
        "${:,.8f}".format(window_swap_manipulation_price),
    )

    # adjusting the TWAP window should change our pricing, and it should still be different from the real price
    assert pytest.approx(price, 0.001) != window_swap_manipulation_price
    assert swap_manipulation_price != window_swap_manipulation_price

    # increasing the window should decrease the distance between rekt price and correct price
    assert abs(swap_manipulation_price - price) > abs(
        window_swap_manipulation_price - price
    )

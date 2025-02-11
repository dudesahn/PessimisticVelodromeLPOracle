# Velodrome LP Pessimistic Oracle

## Use

This oracle may be used to price Velodrome-style LP pools (both vAMM and sAMM) in a manipulation-resistant manner. A pool must contain at least one asset with a Chainlink feed to be valid. If only one asset has a Chainlink feed, an internal TWAP may be used to price the other asset , with a default 2 hour window.

The pessimistic oracle stores daily lows, and prices are checked over the past two (or three) days of stored data when calculating an LP's value. A manual price cap (upper and lower bounds) may be enabled to further limit the impact of manipulations in a given direction. Note that manual price caps (just as the ability to set price feeds) are the main centralization risk of an oracle such as this, and if used, should be treated with great consideration.

With this oracle, price manipulation attacks are substantially more difficult, as an attacker needs to log artificially high lows but still come in under any price cap (if set). Additionally, if three-day lows are used, the oracle becomes more robust for public price updates, as the minimum time covered by all observations jumps from two seconds (two-day window) to 24 hours (three-day window). However, using the pessimistic oracle does have the disadvantage of reducing borrow power of borrowers to a multi-day minimum value of their collateral, where the price also must have been seen by the oracle.

Fora deeper dive into the theory behind this oracle, see the background section below.

## Tests

To run the test suite with detailed printouts

```
brownie test -s
```

## Background

At its core, the value of an LP token is determined by pricing each of the assets, and the reserves of each asset. Credit to [Alpha Homora](https://blog.alphaventuredao.io/fair-lp-token-pricing/) for the first implementation, [cmichel](https://cmichel.io/pricing-lp-tokens/) for expanding on the explanation, and [VMEX](https://vmex.notion.site/Fair-reserves-for-Velo-stable-bb61a5c04eea4d468ed68f61fa809ee5) for consulting on the derivation for sAMM pools. Additional credit to Inverse Finance for the [pessimistic oracle](https://www.inverse.finance/blog/posts/en-US/Why-We-Are-Using-Pessimistic-Price-Oracles).

### Price

- This must come from a trusted source
  - **Decentralized Price Oracle** - E.g. ChainLink, Band Protocol. Asset prices are limited to the assets the oracle supports.
  - **On-chain TWAP** - E.g. Uniswap's TWAP, Keep3r Network. Asset prices are limited to the ones in Uniswap pools (and perhaps ones with sufficiently deep liquidity).
  - **Centralized Feed** - E.g. self-feed the prices on-chain using multiple centralized sources, for example, from CoinGecko, CoinMarketCap, CryptoCompare.

### Reserves

- `getReserves` is subject to manipulation.
- Instead, _only_ use underlying asset reserves to calculate the invariant product `k` - `x * y = k` - `x * y^3 + y * x^3 = k`
- While the relative sizes of asset reserves compared to each other may be altered, the product `k` remains the same (or at least relatively the same)
  - In the absence of fees, and in the absence of add/remove liquidity, `k` would never change
  - Fees gradually increase `k.` Adding liquidity increases `k`, removing liquidity decreases it, [source](https://blockcast.cc/news/technical-analysis-of-the-k-value-design-in-uniswap-constant-product-algorithm/)

### Fair Asset Reserves

- Use standard `getReserves()` to compute `k`
- Calculate the fair price ratio between the underlying assets, `p`
  - **Ex:** If ETH fair price is 650 USDT and BTC fair price is 22,000 USDT, then ETH-to-BTC fair price is 650/22,000 = 0.03.
- The fair asset reserves are then `sqrt(k / p)`​ and `sqrt(k * p)` - Adding and removing liquidity do not affect this formula - `sqrt(k)` will change proportionally with the `totalSupply` in the denominator so pricing does not change
  ![ah_formula](https://github.com/dudesahn/PessimisticVelodromeLPOracle/assets/23222916/9b67319c-e03e-4c19-81f3-ca72d2ff7a05)
  ![cmichel_formula](https://github.com/dudesahn/PessimisticVelodromeLPOracle/assets/23222916/bd34e286-f43c-4757-9c63-5062948f0b41)

### sAMM Pools

- Solidly added sAMM pools in addition to the standard Uniswap `x * y = k` vAMM pools
  - `x * y^3 + y * x^3 = k`
- Because of the new k invariant, we need to re-derive the formula, [source](https://vmex.notion.site/Fair-reserves-for-Velo-stable-bb61a5c04eea4d468ed68f61fa809ee5)
  ![vmex_samm_derivation](https://github.com/dudesahn/PessimisticVelodromeLPOracle/assets/23222916/122f07f2-36b4-4caa-82ce-cb07613ca12a)

#### Notes

- The invariant listed in (1) is the invariant used by solidly stable pairs, which is also the same invariant used in velodrome’s stable pairs.
- r0 is the amount of token 0 in the reserve, r1 is the amount of token 1 in the reserve
- p0 is the fair price of token 0, p1 is the fair price of token 1
- L is the total supply of the LP token
- r0’ is the variable denoting the exact amount of token 0 in the reserve such that the pair is “fair”

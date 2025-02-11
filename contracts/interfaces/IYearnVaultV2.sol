// SPDX-License-Identifier: AGLP-3.0
pragma solidity ^0.8.19;

interface IYearnVaultV2 {
    function token() external view returns (address);

    function pricePerShare() external view returns (uint256);

    function decimals() external view returns (uint256);

    function totalSupply() external view returns (uint);

    function lockedProfitDegradation() external view returns (uint);

    function lastReport() external view returns (uint);

    function totalAssets() external view returns (uint);

    function lockedProfit() external view returns (uint);
}

pragma solidity ^0.8.2;

interface IIbAMM {
    function swap(
        address to,
        uint256 amount,
        uint256 minOut
    ) external returns (bool);

    function quote(address to, uint256 amount) external returns (uint256);
}

pragma solidity ^0.8.2;

interface IRKP3R {
    function redeem(uint256 id) external;

    function claim(uint256 amount) external returns (uint256);

    function claim() external returns (uint256);

    function options(
        uint256
    )
        external
        view
        returns (
            uint256 amount,
            uint256 strike,
            uint256 expiry,
            bool exercised
        );
}

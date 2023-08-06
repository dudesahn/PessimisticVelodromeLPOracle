pragma solidity 0.6.12;

interface IAlphaStaking {
    function STATUS_READY() external view returns (uint256);

    function STATUS_UNBONDING() external view returns (uint256);

    function UNBONDING_DURATION() external view returns (uint256);

    function WITHDRAW_DURATION() external view returns (uint256);

    function setWorker(address) external;

    function setPendingGovernor(address) external;

    function acceptGovernor() external;

    function setMerkle(address) external;

    function getStakeValue(address) external view returns (uint256);

    function stake(address, uint256) external;

    function unbond(uint256) external;

    function withdraw() external;

    function reward(uint256) external;

    function skim(uint256) external;

    function extract(uint256) external;

    function users(
        address
    ) external view returns (uint256, uint256, uint256, uint256);

    function totalAlpha() external view returns (uint256);

    function totalShare() external view returns (uint256);

    function merkle() external view returns (address);
}

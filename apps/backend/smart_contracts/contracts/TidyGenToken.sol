// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

/**
 * @title TidyGenToken
 * @dev ERC20 token for TidyGen ERP ecosystem with governance capabilities
 * @notice This token is used for governance, rewards, and payments within the TidyGen ecosystem
 */
contract TidyGenToken is ERC20, ERC20Burnable, ERC20Pausable, Ownable, ReentrancyGuard, ERC20Votes {
    
    // ==================== STATE VARIABLES ====================
    
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 public constant INITIAL_SUPPLY = 100_000_000 * 10**18; // 100 million tokens
    
    // Token distribution
    uint256 public constant TEAM_ALLOCATION = 20_000_000 * 10**18; // 20%
    uint256 public constant COMMUNITY_ALLOCATION = 30_000_000 * 10**18; // 30%
    uint256 public constant TREASURY_ALLOCATION = 25_000_000 * 10**18; // 25%
    uint256 public constant REWARDS_ALLOCATION = 25_000_000 * 10**18; // 25%
    
    // Vesting
    mapping(address => uint256) public vestingAmount;
    mapping(address => uint256) public vestingStart;
    mapping(address => uint256) public vestingDuration;
    mapping(address => uint256) public vestingClaimed;
    
    // Staking
    struct Stake {
        uint256 amount;
        uint256 startTime;
        uint256 duration;
        uint256 rewards;
    }
    
    mapping(address => Stake[]) public stakes;
    uint256 public stakingRewardRate = 10; // 10% APY
    uint256 public constant MIN_STAKE_DURATION = 30 days;
    uint256 public constant MAX_STAKE_DURATION = 365 days;
    
    // Events
    event TokensVested(address indexed beneficiary, uint256 amount, uint256 duration);
    event VestingClaimed(address indexed beneficiary, uint256 amount);
    event TokensStaked(address indexed staker, uint256 amount, uint256 duration);
    event StakeUnlocked(address indexed staker, uint256 stakeIndex, uint256 amount, uint256 rewards);
    event RewardsDistributed(address indexed recipient, uint256 amount, string reason);
    
    // ==================== CONSTRUCTOR ====================
    
    constructor() ERC20("TidyGen Token", "TGT") ERC20Permit("TidyGen Token") Ownable(msg.sender) {
        // Mint initial supply
        _mint(msg.sender, INITIAL_SUPPLY);
        
        // Set up initial vesting for team
        _setupVesting(msg.sender, TEAM_ALLOCATION, 2 * 365 days); // 2 year vesting
    }
    
    // ==================== VESTING FUNCTIONS ====================
    
    /**
     * @dev Set up vesting for an address
     * @param beneficiary Address to vest tokens to
     * @param amount Amount of tokens to vest
     * @param duration Vesting duration in seconds
     */
    function setupVesting(address beneficiary, uint256 amount, uint256 duration) external onlyOwner {
        require(beneficiary != address(0), "Invalid beneficiary");
        require(amount > 0, "Amount must be greater than 0");
        require(duration > 0, "Duration must be greater than 0");
        require(vestingAmount[beneficiary] == 0, "Vesting already set up");
        
        _setupVesting(beneficiary, amount, duration);
    }
    
    function _setupVesting(address beneficiary, uint256 amount, uint256 duration) internal {
        vestingAmount[beneficiary] = amount;
        vestingStart[beneficiary] = block.timestamp;
        vestingDuration[beneficiary] = duration;
        vestingClaimed[beneficiary] = 0;
        
        emit TokensVested(beneficiary, amount, duration);
    }
    
    /**
     * @dev Claim vested tokens
     */
    function claimVested() external nonReentrant {
        uint256 claimable = getClaimableAmount(msg.sender);
        require(claimable > 0, "No tokens to claim");
        
        vestingClaimed[msg.sender] += claimable;
        _transfer(owner(), msg.sender, claimable);
        
        emit VestingClaimed(msg.sender, claimable);
    }
    
    /**
     * @dev Get claimable amount for an address
     * @param beneficiary Address to check
     * @return claimable Amount of tokens that can be claimed
     */
    function getClaimableAmount(address beneficiary) public view returns (uint256 claimable) {
        if (vestingAmount[beneficiary] == 0) return 0;
        
        uint256 elapsed = block.timestamp - vestingStart[beneficiary];
        if (elapsed >= vestingDuration[beneficiary]) {
            claimable = vestingAmount[beneficiary] - vestingClaimed[beneficiary];
        } else {
            uint256 totalVested = (vestingAmount[beneficiary] * elapsed) / vestingDuration[beneficiary];
            claimable = totalVested - vestingClaimed[beneficiary];
        }
    }

    // ==================== STAKING FUNCTIONS ====================
    
    /**
     * @dev Stake tokens for rewards
     * @param amount Amount of tokens to stake
     * @param duration Staking duration in seconds
     */
    function stake(uint256 amount, uint256 duration) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(duration >= MIN_STAKE_DURATION, "Stake duration too short");
        require(duration <= MAX_STAKE_DURATION, "Stake duration too long");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        // Transfer tokens to contract
        _transfer(msg.sender, address(this), amount);
        
        // Calculate rewards
        uint256 rewards = (amount * stakingRewardRate * duration) / (100 * 365 days);
        
        // Create stake
        stakes[msg.sender].push(Stake({
            amount: amount,
            startTime: block.timestamp,
            duration: duration,
            rewards: rewards
        }));
        
        emit TokensStaked(msg.sender, amount, duration);
    }
    
    /**
     * @dev Unlock a stake
     * @param stakeIndex Index of the stake to unlock
     */
    function unlockStake(uint256 stakeIndex) external nonReentrant {
        require(stakeIndex < stakes[msg.sender].length, "Invalid stake index");
        
        Stake storage stakeInfo = stakes[msg.sender][stakeIndex];
        require(block.timestamp >= stakeInfo.startTime + stakeInfo.duration, "Stake not mature");
        
        uint256 totalAmount = stakeInfo.amount + stakeInfo.rewards;
        
        // Remove stake
        stakes[msg.sender][stakeIndex] = stakes[msg.sender][stakes[msg.sender].length - 1];
        stakes[msg.sender].pop();
        
        // Transfer tokens back
        _transfer(address(this), msg.sender, totalAmount);
        
        emit StakeUnlocked(msg.sender, stakeIndex, stakeInfo.amount, stakeInfo.rewards);
    }
    
    /**
     * @dev Get user's stakes
     * @param staker Address of the staker
     * @return userStakes Array of stakes
     */
    function getUserStakes(address staker) external view returns (Stake[] memory userStakes) {
        return stakes[staker];
    }

    // ==================== REWARD DISTRIBUTION ====================
    
    /**
     * @dev Distribute rewards to community members
     * @param recipients Array of recipient addresses
     * @param amounts Array of amounts to distribute
     * @param reason Reason for distribution
     */
    function distributeRewards(
        address[] calldata recipients,
        uint256[] calldata amounts,
        string calldata reason
    ) external onlyOwner {
        require(recipients.length == amounts.length, "Arrays length mismatch");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "Invalid recipient");
            require(amounts[i] > 0, "Amount must be greater than 0");
            
            _mint(recipients[i], amounts[i]);
            emit RewardsDistributed(recipients[i], amounts[i], reason);
        }
    }
    
    /**
     * @dev Set staking reward rate
     * @param newRate New reward rate (percentage)
     */
    function setStakingRewardRate(uint256 newRate) external onlyOwner {
        require(newRate <= 100, "Rate too high");
        stakingRewardRate = newRate;
    }

    // ==================== OVERRIDES ====================
    
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Pausable, ERC20Votes)
    {
        super._update(from, to, value);
    }
    
    function nonces(address owner)
        public
        view
        override(ERC20Permit, Nonces)
        returns (uint256)
    {
        return super.nonces(owner);
    }
    
    function pause() public onlyOwner {
        _pause();
    }
    
    function unpause() public onlyOwner {
        _unpause();
    }
    
    function mint(address to, uint256 amount) public onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }

    // ==================== VIEW FUNCTIONS ====================
    
    /**
     * @dev Get token information
     * @return name Token name
     * @return symbol Token symbol
     * @return decimals Token decimals
     * @return totalSupply Total supply
     * @return maxSupply Maximum supply
     */
    function getTokenInfo() external view returns (
        string memory name,
        string memory symbol,
        uint8 decimals,
        uint256 totalSupply,
        uint256 maxSupply
    ) {
        return (
            name(),
            symbol(),
            decimals(),
            totalSupply(),
            MAX_SUPPLY
        );
    }
    
    /**
     * @dev Get vesting information for an address
     * @param beneficiary Address to check
     * @return amount Total vesting amount
     * @return start Vesting start time
     * @return duration Vesting duration
     * @return claimed Amount already claimed
     * @return claimable Amount currently claimable
     */
    function getVestingInfo(address beneficiary) external view returns (
        uint256 amount,
        uint256 start,
        uint256 duration,
        uint256 claimed,
        uint256 claimable
    ) {
        return (
            vestingAmount[beneficiary],
            vestingStart[beneficiary],
            vestingDuration[beneficiary],
            vestingClaimed[beneficiary],
            getClaimableAmount(beneficiary)
        );
    }
}

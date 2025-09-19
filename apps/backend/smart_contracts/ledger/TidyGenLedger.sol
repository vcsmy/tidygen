// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title TidyGenLedger
 * @dev Smart contract for logging financial transactions to blockchain
 * @author TidyGen ERP Team
 * @notice This contract provides tamper-proof logging of financial transactions
 *         from the TidyGen ERP system to the blockchain for audit trails.
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract TidyGenLedger is Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    // ============ STRUCTS ============
    
    /**
     * @dev Structure representing a logged transaction
     */
    struct Transaction {
        bytes32 id;                    // Unique transaction ID
        string transactionType;        // Type of transaction (invoice, payment, etc.)
        string sourceModule;           // Source module (finance, sales, etc.)
        string sourceId;               // Original transaction ID in ERP
        string hash;                   // SHA256 hash of transaction data
        uint256 timestamp;             // Block timestamp when logged
        address organization;          // Organization address
        bool verified;                 // Verification status
        uint256 blockNumber;           // Block number when logged
    }
    
    /**
     * @dev Structure representing a batch of transactions
     */
    struct Batch {
        bytes32 batchId;               // Unique batch ID
        bytes32[] transactionIds;      // Array of transaction IDs in batch
        uint256 timestamp;             // Block timestamp when logged
        address organization;          // Organization address
        bool verified;                 // Verification status
    }
    
    /**
     * @dev Structure representing an audit event
     */
    struct AuditEvent {
        bytes32 eventId;               // Unique event ID
        bytes32 transactionId;         // Related transaction ID
        string eventType;              // Type of event
        string eventData;              // Event data as JSON string
        uint256 timestamp;             // Block timestamp
        address triggeredBy;           // Address that triggered the event
    }
    
    // ============ STATE VARIABLES ============
    
    Counters.Counter private _transactionCounter;
    Counters.Counter private _batchCounter;
    Counters.Counter private _eventCounter;
    
    // Mapping from transaction ID to Transaction struct
    mapping(bytes32 => Transaction) public transactions;
    
    // Mapping from batch ID to Batch struct
    mapping(bytes32 => Batch) public batches;
    
    // Mapping from event ID to AuditEvent struct
    mapping(bytes32 => AuditEvent) public auditEvents;
    
    // Mapping from organization to array of transaction IDs
    mapping(address => bytes32[]) public organizationTransactions;
    
    // Mapping from organization to array of batch IDs
    mapping(address => bytes32[]) public organizationBatches;
    
    // Mapping from transaction ID to array of event IDs
    mapping(bytes32 => bytes32[]) public transactionEvents;
    
    // Array of all transaction IDs for enumeration
    bytes32[] public allTransactionIds;
    
    // Array of all batch IDs for enumeration
    bytes32[] public allBatchIds;
    
    // Array of all event IDs for enumeration
    bytes32[] public allEventIds;
    
    // Gas limit for transactions
    uint256 public gasLimit = 1000000;
    
    // Maximum batch size
    uint256 public maxBatchSize = 100;
    
    // Fee for logging transactions (in wei)
    uint256 public loggingFee = 0;
    
    // ============ EVENTS ============
    
    /**
     * @dev Emitted when a transaction is logged
     */
    event TransactionLogged(
        bytes32 indexed transactionId,
        string indexed transactionType,
        address indexed organization,
        string sourceModule,
        string sourceId,
        string hash,
        uint256 timestamp
    );
    
    /**
     * @dev Emitted when a batch of transactions is logged
     */
    event BatchLogged(
        bytes32 indexed batchId,
        address indexed organization,
        bytes32[] transactionIds,
        uint256 timestamp
    );
    
    /**
     * @dev Emitted when a transaction is verified
     */
    event TransactionVerified(
        bytes32 indexed transactionId,
        bool verified,
        uint256 timestamp
    );
    
    /**
     * @dev Emitted when a batch is verified
     */
    event BatchVerified(
        bytes32 indexed batchId,
        bool verified,
        uint256 timestamp
    );
    
    /**
     * @dev Emitted when an audit event is created
     */
    event AuditEventCreated(
        bytes32 indexed eventId,
        bytes32 indexed transactionId,
        string eventType,
        address triggeredBy,
        uint256 timestamp
    );
    
    /**
     * @dev Emitted when gas limit is updated
     */
    event GasLimitUpdated(uint256 oldLimit, uint256 newLimit);
    
    /**
     * @dev Emitted when max batch size is updated
     */
    event MaxBatchSizeUpdated(uint256 oldSize, uint256 newSize);
    
    /**
     * @dev Emitted when logging fee is updated
     */
    event LoggingFeeUpdated(uint256 oldFee, uint256 newFee);
    
    // ============ MODIFIERS ============
    
    /**
     * @dev Modifier to check if transaction exists
     */
    modifier transactionExists(bytes32 _transactionId) {
        require(transactions[_transactionId].id != bytes32(0), "Transaction does not exist");
        _;
    }
    
    /**
     * @dev Modifier to check if batch exists
     */
    modifier batchExists(bytes32 _batchId) {
        require(batches[_batchId].batchId != bytes32(0), "Batch does not exist");
        _;
    }
    
    /**
     * @dev Modifier to check if caller is authorized for organization
     */
    modifier authorizedForOrganization(address _organization) {
        require(
            _organization == msg.sender || 
            _organization == owner() || 
            isAuthorizedCaller(_organization, msg.sender),
            "Not authorized for this organization"
        );
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor() {
        // Initialize counters
        _transactionCounter.increment(); // Start from 1
        _batchCounter.increment();       // Start from 1
        _eventCounter.increment();       // Start from 1
    }
    
    // ============ MAIN FUNCTIONS ============
    
    /**
     * @dev Log a single transaction to the blockchain
     * @param _transactionType Type of transaction (invoice, payment, etc.)
     * @param _sourceModule Source module (finance, sales, etc.)
     * @param _sourceId Original transaction ID in ERP
     * @param _hash SHA256 hash of transaction data
     * @param _organization Organization address
     * @return transactionId The ID of the logged transaction
     */
    function logTransaction(
        string memory _transactionType,
        string memory _sourceModule,
        string memory _sourceId,
        string memory _hash,
        address _organization
    ) 
        external 
        payable 
        nonReentrant 
        whenNotPaused 
        authorizedForOrganization(_organization)
        returns (bytes32 transactionId) 
    {
        // Check fee payment
        require(msg.value >= loggingFee, "Insufficient fee payment");
        
        // Generate unique transaction ID
        transactionId = keccak256(abi.encodePacked(
            _transactionType,
            _sourceModule,
            _sourceId,
            _hash,
            _organization,
            block.timestamp,
            _transactionCounter.current()
        ));
        
        // Check if transaction already exists
        require(transactions[transactionId].id == bytes32(0), "Transaction already exists");
        
        // Create transaction record
        Transaction memory newTransaction = Transaction({
            id: transactionId,
            transactionType: _transactionType,
            sourceModule: _sourceModule,
            sourceId: _sourceId,
            hash: _hash,
            timestamp: block.timestamp,
            organization: _organization,
            verified: false,
            blockNumber: block.number
        });
        
        // Store transaction
        transactions[transactionId] = newTransaction;
        allTransactionIds.push(transactionId);
        organizationTransactions[_organization].push(transactionId);
        
        // Increment counter
        _transactionCounter.increment();
        
        // Create audit event
        _createAuditEvent(
            transactionId,
            "transaction_logged",
            string(abi.encodePacked(
                '{"transactionType":"', _transactionType, 
                '","sourceModule":"', _sourceModule,
                '","sourceId":"', _sourceId,
                '","hash":"', _hash, '"}'
            )),
            msg.sender
        );
        
        // Emit event
        emit TransactionLogged(
            transactionId,
            _transactionType,
            _organization,
            _sourceModule,
            _sourceId,
            _hash,
            block.timestamp
        );
        
        return transactionId;
    }
    
    /**
     * @dev Log multiple transactions in a batch
     * @param _transactionTypes Array of transaction types
     * @param _sourceModules Array of source modules
     * @param _sourceIds Array of source IDs
     * @param _hashes Array of transaction hashes
     * @param _organization Organization address
     * @return batchId The ID of the logged batch
     */
    function logBatch(
        string[] memory _transactionTypes,
        string[] memory _sourceModules,
        string[] memory _sourceIds,
        string[] memory _hashes,
        address _organization
    ) 
        external 
        payable 
        nonReentrant 
        whenNotPaused 
        authorizedForOrganization(_organization)
        returns (bytes32 batchId) 
    {
        // Validate input arrays
        require(_transactionTypes.length > 0, "Empty transaction array");
        require(_transactionTypes.length <= maxBatchSize, "Batch size exceeds limit");
        require(
            _transactionTypes.length == _sourceModules.length &&
            _sourceModules.length == _sourceIds.length &&
            _sourceIds.length == _hashes.length,
            "Array length mismatch"
        );
        
        // Check fee payment (per transaction)
        require(msg.value >= loggingFee * _transactionTypes.length, "Insufficient fee payment");
        
        // Generate unique batch ID
        batchId = keccak256(abi.encodePacked(
            _organization,
            block.timestamp,
            _batchCounter.current()
        ));
        
        // Check if batch already exists
        require(batches[batchId].batchId == bytes32(0), "Batch already exists");
        
        // Create batch record
        bytes32[] memory transactionIds = new bytes32[](_transactionTypes.length);
        
        // Log each transaction in the batch
        for (uint256 i = 0; i < _transactionTypes.length; i++) {
            bytes32 transactionId = keccak256(abi.encodePacked(
                _transactionTypes[i],
                _sourceModules[i],
                _sourceIds[i],
                _hashes[i],
                _organization,
                block.timestamp,
                _transactionCounter.current(),
                i
            ));
            
            // Check if transaction already exists
            require(transactions[transactionId].id == bytes32(0), "Transaction already exists");
            
            // Create transaction record
            Transaction memory newTransaction = Transaction({
                id: transactionId,
                transactionType: _transactionTypes[i],
                sourceModule: _sourceModules[i],
                sourceId: _sourceIds[i],
                hash: _hashes[i],
                timestamp: block.timestamp,
                organization: _organization,
                verified: false,
                blockNumber: block.number
            });
            
            // Store transaction
            transactions[transactionId] = newTransaction;
            allTransactionIds.push(transactionId);
            organizationTransactions[_organization].push(transactionId);
            transactionIds[i] = transactionId;
            
            // Increment counter
            _transactionCounter.increment();
        }
        
        // Create batch record
        Batch memory newBatch = Batch({
            batchId: batchId,
            transactionIds: transactionIds,
            timestamp: block.timestamp,
            organization: _organization,
            verified: false
        });
        
        // Store batch
        batches[batchId] = newBatch;
        allBatchIds.push(batchId);
        organizationBatches[_organization].push(batchId);
        
        // Increment counter
        _batchCounter.increment();
        
        // Create audit event
        _createAuditEvent(
            batchId,
            "batch_logged",
            string(abi.encodePacked(
                '{"batchSize":', _transactionTypes.length.toString(),
                ',"organization":"', _addressToString(_organization), '"}'
            )),
            msg.sender
        );
        
        // Emit event
        emit BatchLogged(
            batchId,
            _organization,
            transactionIds,
            block.timestamp
        );
        
        return batchId;
    }
    
    /**
     * @dev Verify a transaction's hash
     * @param _transactionId ID of the transaction to verify
     * @param _expectedHash Expected hash value
     * @return verified True if hash matches, false otherwise
     */
    function verifyTransaction(
        bytes32 _transactionId,
        string memory _expectedHash
    ) 
        external 
        view 
        transactionExists(_transactionId)
        returns (bool verified) 
    {
        Transaction memory transaction = transactions[_transactionId];
        
        // Compare hashes
        verified = keccak256(abi.encodePacked(transaction.hash)) == 
                  keccak256(abi.encodePacked(_expectedHash));
        
        return verified;
    }
    
    /**
     * @dev Mark a transaction as verified
     * @param _transactionId ID of the transaction to mark as verified
     */
    function markTransactionVerified(bytes32 _transactionId) 
        external 
        onlyOwner 
        transactionExists(_transactionId) 
    {
        transactions[_transactionId].verified = true;
        
        // Create audit event
        _createAuditEvent(
            _transactionId,
            "transaction_verified",
            '{"verified":true}',
            msg.sender
        );
        
        // Emit event
        emit TransactionVerified(
            _transactionId,
            true,
            block.timestamp
        );
    }
    
    /**
     * @dev Mark a batch as verified
     * @param _batchId ID of the batch to mark as verified
     */
    function markBatchVerified(bytes32 _batchId) 
        external 
        onlyOwner 
        batchExists(_batchId) 
    {
        batches[_batchId].verified = true;
        
        // Mark all transactions in batch as verified
        bytes32[] memory transactionIds = batches[_batchId].transactionIds;
        for (uint256 i = 0; i < transactionIds.length; i++) {
            transactions[transactionIds[i]].verified = true;
        }
        
        // Create audit event
        _createAuditEvent(
            _batchId,
            "batch_verified",
            '{"verified":true}',
            msg.sender
        );
        
        // Emit event
        emit BatchVerified(
            _batchId,
            true,
            block.timestamp
        );
    }
    
    // ============ VIEW FUNCTIONS ============
    
    /**
     * @dev Get transaction details
     * @param _transactionId ID of the transaction
     * @return transaction Transaction struct
     */
    function getTransaction(bytes32 _transactionId) 
        external 
        view 
        transactionExists(_transactionId)
        returns (Transaction memory transaction) 
    {
        return transactions[_transactionId];
    }
    
    /**
     * @dev Get batch details
     * @param _batchId ID of the batch
     * @return batch Batch struct
     */
    function getBatch(bytes32 _batchId) 
        external 
        view 
        batchExists(_batchId)
        returns (Batch memory batch) 
    {
        return batches[_batchId];
    }
    
    /**
     * @dev Get audit event details
     * @param _eventId ID of the event
     * @return event AuditEvent struct
     */
    function getAuditEvent(bytes32 _eventId) 
        external 
        view 
        returns (AuditEvent memory event) 
    {
        require(auditEvents[_eventId].eventId != bytes32(0), "Event does not exist");
        return auditEvents[_eventId];
    }
    
    /**
     * @dev Get all transaction IDs for an organization
     * @param _organization Organization address
     * @return transactionIds Array of transaction IDs
     */
    function getOrganizationTransactions(address _organization) 
        external 
        view 
        returns (bytes32[] memory transactionIds) 
    {
        return organizationTransactions[_organization];
    }
    
    /**
     * @dev Get all batch IDs for an organization
     * @param _organization Organization address
     * @return batchIds Array of batch IDs
     */
    function getOrganizationBatches(address _organization) 
        external 
        view 
        returns (bytes32[] memory batchIds) 
    {
        return organizationBatches[_organization];
    }
    
    /**
     * @dev Get all event IDs for a transaction
     * @param _transactionId Transaction ID
     * @return eventIds Array of event IDs
     */
    function getTransactionEvents(bytes32 _transactionId) 
        external 
        view 
        returns (bytes32[] memory eventIds) 
    {
        return transactionEvents[_transactionId];
    }
    
    /**
     * @dev Get total number of transactions
     * @return count Total transaction count
     */
    function getTotalTransactionCount() external view returns (uint256 count) {
        return allTransactionIds.length;
    }
    
    /**
     * @dev Get total number of batches
     * @return count Total batch count
     */
    function getTotalBatchCount() external view returns (uint256 count) {
        return allBatchIds.length;
    }
    
    /**
     * @dev Get total number of events
     * @return count Total event count
     */
    function getTotalEventCount() external view returns (uint256 count) {
        return allEventIds.length;
    }
    
    /**
     * @dev Check if transaction exists
     * @param _transactionId Transaction ID to check
     * @return exists True if transaction exists
     */
    function transactionExists(bytes32 _transactionId) external view returns (bool exists) {
        return transactions[_transactionId].id != bytes32(0);
    }
    
    /**
     * @dev Check if batch exists
     * @param _batchId Batch ID to check
     * @return exists True if batch exists
     */
    function batchExists(bytes32 _batchId) external view returns (bool exists) {
        return batches[_batchId].batchId != bytes32(0);
    }
    
    // ============ ADMIN FUNCTIONS ============
    
    /**
     * @dev Update gas limit
     * @param _newGasLimit New gas limit
     */
    function updateGasLimit(uint256 _newGasLimit) external onlyOwner {
        require(_newGasLimit > 0, "Gas limit must be greater than 0");
        
        uint256 oldLimit = gasLimit;
        gasLimit = _newGasLimit;
        
        emit GasLimitUpdated(oldLimit, _newGasLimit);
    }
    
    /**
     * @dev Update maximum batch size
     * @param _newMaxBatchSize New maximum batch size
     */
    function updateMaxBatchSize(uint256 _newMaxBatchSize) external onlyOwner {
        require(_newMaxBatchSize > 0, "Max batch size must be greater than 0");
        
        uint256 oldSize = maxBatchSize;
        maxBatchSize = _newMaxBatchSize;
        
        emit MaxBatchSizeUpdated(oldSize, _newMaxBatchSize);
    }
    
    /**
     * @dev Update logging fee
     * @param _newLoggingFee New logging fee in wei
     */
    function updateLoggingFee(uint256 _newLoggingFee) external onlyOwner {
        uint256 oldFee = loggingFee;
        loggingFee = _newLoggingFee;
        
        emit LoggingFeeUpdated(oldFee, _newLoggingFee);
    }
    
    /**
     * @dev Pause the contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Withdraw contract balance
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance to withdraw");
        
        payable(owner()).transfer(balance);
    }
    
    // ============ INTERNAL FUNCTIONS ============
    
    /**
     * @dev Create an audit event
     * @param _transactionId Related transaction ID
     * @param _eventType Type of event
     * @param _eventData Event data as JSON string
     * @param _triggeredBy Address that triggered the event
     * @return eventId The ID of the created event
     */
    function _createAuditEvent(
        bytes32 _transactionId,
        string memory _eventType,
        string memory _eventData,
        address _triggeredBy
    ) 
        internal 
        returns (bytes32 eventId) 
    {
        // Generate unique event ID
        eventId = keccak256(abi.encodePacked(
            _transactionId,
            _eventType,
            _eventData,
            _triggeredBy,
            block.timestamp,
            _eventCounter.current()
        ));
        
        // Create audit event record
        AuditEvent memory newEvent = AuditEvent({
            eventId: eventId,
            transactionId: _transactionId,
            eventType: _eventType,
            eventData: _eventData,
            timestamp: block.timestamp,
            triggeredBy: _triggeredBy
        });
        
        // Store event
        auditEvents[eventId] = newEvent;
        allEventIds.push(eventId);
        transactionEvents[_transactionId].push(eventId);
        
        // Increment counter
        _eventCounter.increment();
        
        // Emit event
        emit AuditEventCreated(
            eventId,
            _transactionId,
            _eventType,
            _triggeredBy,
            block.timestamp
        );
        
        return eventId;
    }
    
    /**
     * @dev Check if caller is authorized for organization
     * @param _organization Organization address
     * @param _caller Caller address
     * @return authorized True if authorized
     */
    function isAuthorizedCaller(address _organization, address _caller) 
        internal 
        pure 
        returns (bool authorized) 
    {
        // For now, only allow direct calls from organization or owner
        // In production, implement role-based access control
        return _caller == _organization;
    }
    
    /**
     * @dev Convert address to string
     * @param _address Address to convert
     * @return string String representation of address
     */
    function _addressToString(address _address) 
        internal 
        pure 
        returns (string memory) 
    {
        bytes32 value = bytes32(uint256(uint160(_address)));
        bytes memory alphabet = "0123456789abcdef";
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2 + i * 2] = alphabet[uint8(value[i + 12] >> 4)];
            str[3 + i * 2] = alphabet[uint8(value[i + 12] & 0x0f)];
        }
        return string(str);
    }
}

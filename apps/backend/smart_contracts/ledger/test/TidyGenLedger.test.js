const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

describe("TidyGenLedger", function () {
  let tidygenLedger;
  let owner;
  let organization1;
  let organization2;
  let unauthorizedUser;
  
  const TRANSACTION_TYPE = "invoice";
  const SOURCE_MODULE = "finance";
  const SOURCE_ID = "INV-001";
  const TRANSACTION_HASH = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456";
  
  beforeEach(async function () {
    // Get signers
    [owner, organization1, organization2, unauthorizedUser] = await ethers.getSigners();
    
    // Deploy contract
    const TidyGenLedger = await ethers.getContractFactory("TidyGenLedger");
    tidygenLedger = await TidyGenLedger.deploy();
    await tidygenLedger.deployed();
  });
  
  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await tidygenLedger.owner()).to.equal(owner.address);
    });
    
    it("Should have correct initial values", async function () {
      expect(await tidygenLedger.gasLimit()).to.equal(1000000);
      expect(await tidygenLedger.maxBatchSize()).to.equal(100);
      expect(await tidygenLedger.loggingFee()).to.equal(0);
    });
    
    it("Should have zero initial transaction count", async function () {
      expect(await tidygenLedger.getTotalTransactionCount()).to.equal(0);
    });
  });
  
  describe("Transaction Logging", function () {
    it("Should log a single transaction", async function () {
      const tx = await tidygenLedger.logTransaction(
        TRANSACTION_TYPE,
        SOURCE_MODULE,
        SOURCE_ID,
        TRANSACTION_HASH,
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      await expect(tx)
        .to.emit(tidygenLedger, "TransactionLogged")
        .withArgs(
          await tidygenLedger.transactions(0), // First transaction ID
          TRANSACTION_TYPE,
          organization1.address,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          await time.latest()
        );
      
      expect(await tidygenLedger.getTotalTransactionCount()).to.equal(1);
    });
    
    it("Should not allow duplicate transactions", async function () {
      // Log first transaction
      await tidygenLedger.logTransaction(
        TRANSACTION_TYPE,
        SOURCE_MODULE,
        SOURCE_ID,
        TRANSACTION_HASH,
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      // Try to log duplicate transaction
      await expect(
        tidygenLedger.logTransaction(
          TRANSACTION_TYPE,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          organization1.address,
          { value: await tidygenLedger.loggingFee() }
        )
      ).to.be.revertedWith("Transaction already exists");
    });
    
    it("Should require sufficient fee payment", async function () {
      await tidygenLedger.updateLoggingFee(ethers.utils.parseEther("0.001"));
      
      await expect(
        tidygenLedger.logTransaction(
          TRANSACTION_TYPE,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          organization1.address,
          { value: ethers.utils.parseEther("0.0005") } // Insufficient fee
        )
      ).to.be.revertedWith("Insufficient fee payment");
    });
    
    it("Should only allow authorized callers", async function () {
      await expect(
        tidygenLedger.connect(unauthorizedUser).logTransaction(
          TRANSACTION_TYPE,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          organization1.address,
          { value: await tidygenLedger.loggingFee() }
        )
      ).to.be.revertedWith("Not authorized for this organization");
    });
  });
  
  describe("Batch Logging", function () {
    it("Should log multiple transactions in a batch", async function () {
      const transactionTypes = ["invoice", "payment", "expense"];
      const sourceModules = ["finance", "finance", "finance"];
      const sourceIds = ["INV-001", "PAY-001", "EXP-001"];
      const hashes = [
        "hash1",
        "hash2", 
        "hash3"
      ];
      
      const tx = await tidygenLedger.logBatch(
        transactionTypes,
        sourceModules,
        sourceIds,
        hashes,
        organization1.address,
        { value: (await tidygenLedger.loggingFee()).mul(3) }
      );
      
      await expect(tx)
        .to.emit(tidygenLedger, "BatchLogged")
        .withArgs(
          await tidygenLedger.batches(0), // First batch ID
          organization1.address,
          await tidygenLedger.getOrganizationTransactions(organization1.address),
          await time.latest()
        );
      
      expect(await tidygenLedger.getTotalTransactionCount()).to.equal(3);
      expect(await tidygenLedger.getTotalBatchCount()).to.equal(1);
    });
    
    it("Should not allow empty batch", async function () {
      await expect(
        tidygenLedger.logBatch(
          [],
          [],
          [],
          [],
          organization1.address,
          { value: 0 }
        )
      ).to.be.revertedWith("Empty transaction array");
    });
    
    it("Should not allow batch exceeding max size", async function () {
      const largeArray = new Array(101).fill("test");
      
      await expect(
        tidygenLedger.logBatch(
          largeArray,
          largeArray,
          largeArray,
          largeArray,
          organization1.address,
          { value: (await tidygenLedger.loggingFee()).mul(101) }
        )
      ).to.be.revertedWith("Batch size exceeds limit");
    });
    
    it("Should require array length consistency", async function () {
      await expect(
        tidygenLedger.logBatch(
          ["invoice", "payment"],
          ["finance"],
          ["INV-001", "PAY-001"],
          ["hash1", "hash2"],
          organization1.address,
          { value: (await tidygenLedger.loggingFee()).mul(2) }
        )
      ).to.be.revertedWith("Array length mismatch");
    });
  });
  
  describe("Transaction Verification", function () {
    let transactionId;
    
    beforeEach(async function () {
      const tx = await tidygenLedger.logTransaction(
        TRANSACTION_TYPE,
        SOURCE_MODULE,
        SOURCE_ID,
        TRANSACTION_HASH,
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      const receipt = await tx.wait();
      const event = receipt.events.find(e => e.event === "TransactionLogged");
      transactionId = event.args.transactionId;
    });
    
    it("Should verify correct transaction hash", async function () {
      const isValid = await tidygenLedger.verifyTransaction(transactionId, TRANSACTION_HASH);
      expect(isValid).to.be.true;
    });
    
    it("Should reject incorrect transaction hash", async function () {
      const isValid = await tidygenLedger.verifyTransaction(transactionId, "wrong_hash");
      expect(isValid).to.be.false;
    });
    
    it("Should mark transaction as verified", async function () {
      const tx = await tidygenLedger.markTransactionVerified(transactionId);
      
      await expect(tx)
        .to.emit(tidygenLedger, "TransactionVerified")
        .withArgs(transactionId, true, await time.latest());
      
      const transaction = await tidygenLedger.getTransaction(transactionId);
      expect(transaction.verified).to.be.true;
    });
    
    it("Should only allow owner to mark as verified", async function () {
      await expect(
        tidygenLedger.connect(organization1).markTransactionVerified(transactionId)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });
  
  describe("Batch Verification", function () {
    let batchId;
    
    beforeEach(async function () {
      const transactionTypes = ["invoice", "payment"];
      const sourceModules = ["finance", "finance"];
      const sourceIds = ["INV-001", "PAY-001"];
      const hashes = ["hash1", "hash2"];
      
      const tx = await tidygenLedger.logBatch(
        transactionTypes,
        sourceModules,
        sourceIds,
        hashes,
        organization1.address,
        { value: (await tidygenLedger.loggingFee()).mul(2) }
      );
      
      const receipt = await tx.wait();
      const event = receipt.events.find(e => e.event === "BatchLogged");
      batchId = event.args.batchId;
    });
    
    it("Should mark batch as verified", async function () {
      const tx = await tidygenLedger.markBatchVerified(batchId);
      
      await expect(tx)
        .to.emit(tidygenLedger, "BatchVerified")
        .withArgs(batchId, true, await time.latest());
      
      const batch = await tidygenLedger.getBatch(batchId);
      expect(batch.verified).to.be.true;
    });
    
    it("Should mark all transactions in batch as verified", async function () {
      await tidygenLedger.markBatchVerified(batchId);
      
      const batch = await tidygenLedger.getBatch(batchId);
      for (let i = 0; i < batch.transactionIds.length; i++) {
        const transaction = await tidygenLedger.getTransaction(batch.transactionIds[i]);
        expect(transaction.verified).to.be.true;
      }
    });
  });
  
  describe("View Functions", function () {
    beforeEach(async function () {
      // Log some test transactions
      await tidygenLedger.logTransaction(
        "invoice",
        "finance",
        "INV-001",
        "hash1",
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      await tidygenLedger.logTransaction(
        "payment",
        "finance", 
        "PAY-001",
        "hash2",
        organization2.address,
        { value: await tidygenLedger.loggingFee() }
      );
    });
    
    it("Should return correct transaction details", async function () {
      const transactionId = await tidygenLedger.allTransactionIds(0);
      const transaction = await tidygenLedger.getTransaction(transactionId);
      
      expect(transaction.transactionType).to.equal("invoice");
      expect(transaction.sourceModule).to.equal("finance");
      expect(transaction.sourceId).to.equal("INV-001");
      expect(transaction.hash).to.equal("hash1");
      expect(transaction.organization).to.equal(organization1.address);
    });
    
    it("Should return organization transactions", async function () {
      const org1Transactions = await tidygenLedger.getOrganizationTransactions(organization1.address);
      const org2Transactions = await tidygenLedger.getOrganizationTransactions(organization2.address);
      
      expect(org1Transactions.length).to.equal(1);
      expect(org2Transactions.length).to.equal(1);
    });
    
    it("Should check transaction existence", async function () {
      const transactionId = await tidygenLedger.allTransactionIds(0);
      const exists = await tidygenLedger.transactionExists(transactionId);
      
      expect(exists).to.be.true;
    });
    
    it("Should return false for non-existent transaction", async function () {
      const fakeId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("fake"));
      const exists = await tidygenLedger.transactionExists(fakeId);
      
      expect(exists).to.be.false;
    });
  });
  
  describe("Admin Functions", function () {
    it("Should update gas limit", async function () {
      const newGasLimit = 2000000;
      
      await expect(tidygenLedger.updateGasLimit(newGasLimit))
        .to.emit(tidygenLedger, "GasLimitUpdated")
        .withArgs(1000000, newGasLimit);
      
      expect(await tidygenLedger.gasLimit()).to.equal(newGasLimit);
    });
    
    it("Should update max batch size", async function () {
      const newMaxBatchSize = 200;
      
      await expect(tidygenLedger.updateMaxBatchSize(newMaxBatchSize))
        .to.emit(tidygenLedger, "MaxBatchSizeUpdated")
        .withArgs(100, newMaxBatchSize);
      
      expect(await tidygenLedger.maxBatchSize()).to.equal(newMaxBatchSize);
    });
    
    it("Should update logging fee", async function () {
      const newFee = ethers.utils.parseEther("0.001");
      
      await expect(tidygenLedger.updateLoggingFee(newFee))
        .to.emit(tidygenLedger, "LoggingFeeUpdated")
        .withArgs(0, newFee);
      
      expect(await tidygenLedger.loggingFee()).to.equal(newFee);
    });
    
    it("Should pause and unpause contract", async function () {
      await tidygenLedger.pause();
      expect(await tidygenLedger.paused()).to.be.true;
      
      await expect(
        tidygenLedger.logTransaction(
          TRANSACTION_TYPE,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          organization1.address,
          { value: await tidygenLedger.loggingFee() }
        )
      ).to.be.revertedWith("Pausable: paused");
      
      await tidygenLedger.unpause();
      expect(await tidygenLedger.paused()).to.be.false;
    });
    
    it("Should only allow owner to call admin functions", async function () {
      await expect(
        tidygenLedger.connect(organization1).updateGasLimit(2000000)
      ).to.be.revertedWith("Ownable: caller is not the owner");
      
      await expect(
        tidygenLedger.connect(organization1).pause()
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });
  
  describe("Audit Events", function () {
    it("Should create audit events for transactions", async function () {
      const tx = await tidygenLedger.logTransaction(
        TRANSACTION_TYPE,
        SOURCE_MODULE,
        SOURCE_ID,
        TRANSACTION_HASH,
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      await expect(tx)
        .to.emit(tidygenLedger, "AuditEventCreated");
      
      expect(await tidygenLedger.getTotalEventCount()).to.equal(1);
    });
    
    it("Should return transaction events", async function () {
      const tx = await tidygenLedger.logTransaction(
        TRANSACTION_TYPE,
        SOURCE_MODULE,
        SOURCE_ID,
        TRANSACTION_HASH,
        organization1.address,
        { value: await tidygenLedger.loggingFee() }
      );
      
      const receipt = await tx.wait();
      const event = receipt.events.find(e => e.event === "TransactionLogged");
      const transactionId = event.args.transactionId;
      
      const events = await tidygenLedger.getTransactionEvents(transactionId);
      expect(events.length).to.be.greaterThan(0);
    });
  });
  
  describe("Withdrawal", function () {
    it("Should allow owner to withdraw contract balance", async function () {
      // Send some ETH to contract
      await organization1.sendTransaction({
        to: tidygenLedger.address,
        value: ethers.utils.parseEther("1.0")
      });
      
      const initialBalance = await owner.getBalance();
      await tidygenLedger.withdraw();
      const finalBalance = await owner.getBalance();
      
      expect(finalBalance).to.be.gt(initialBalance);
    });
    
    it("Should not allow non-owner to withdraw", async function () {
      await expect(
        tidygenLedger.connect(organization1).withdraw()
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });
  
  describe("Edge Cases", function () {
    it("Should handle zero fee correctly", async function () {
      await tidygenLedger.updateLoggingFee(0);
      
      await expect(
        tidygenLedger.logTransaction(
          TRANSACTION_TYPE,
          SOURCE_MODULE,
          SOURCE_ID,
          TRANSACTION_HASH,
          organization1.address,
          { value: 0 }
        )
      ).to.not.be.reverted;
    });
    
    it("Should handle maximum batch size", async function () {
      const maxSize = await tidygenLedger.maxBatchSize();
      const largeArray = new Array(maxSize.toNumber()).fill("test");
      
      await expect(
        tidygenLedger.logBatch(
          largeArray,
          largeArray,
          largeArray,
          largeArray,
          organization1.address,
          { value: (await tidygenLedger.loggingFee()).mul(maxSize) }
        )
      ).to.not.be.reverted;
    });
  });
});
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TidyGenERP", function () {
  let tidygenERP;
  let tidygenToken;
  let owner;
  let client;
  let vendor;
  let addr1;
  let addr2;

  beforeEach(async function () {
    [owner, client, vendor, addr1, addr2] = await ethers.getSigners();

    // Deploy TidyGenToken
    const TidyGenToken = await ethers.getContractFactory("TidyGenToken");
    tidygenToken = await TidyGenToken.deploy();
    await tidygenToken.waitForDeployment();

    // Deploy TidyGenERP
    const TidyGenERP = await ethers.getContractFactory("TidyGenERP");
    tidygenERP = await TidyGenERP.deploy();
    await tidygenERP.waitForDeployment();

    // Set up voting power for testing
    await tidygenERP.setVotingPower(owner.address, ethers.parseEther("1000000"));
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await tidygenERP.owner()).to.equal(owner.address);
    });

    it("Should initialize with correct values", async function () {
      expect(await tidygenERP.nextInvoiceId()).to.equal(1);
      expect(await tidygenERP.nextPaymentId()).to.equal(1);
      expect(await tidygenERP.nextProposalId()).to.equal(1);
    });
  });

  describe("Invoice Management", function () {
    it("Should create an invoice", async function () {
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      await expect(
        tidygenERP.createInvoice(
          client.address,
          amount,
          ethers.ZeroAddress, // ETH
          "Test Invoice",
          dueDate,
          dataHash
        )
      )
        .to.emit(tidygenERP, "InvoiceCreated")
        .withArgs(1, client.address, vendor.address, amount);

      const invoice = await tidygenERP.getInvoice(1);
      expect(invoice.client).to.equal(client.address);
      expect(invoice.vendor).to.equal(vendor.address);
      expect(invoice.amount).to.equal(amount);
      expect(invoice.status).to.equal(0); // Draft
    });

    it("Should send an invoice", async function () {
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      await tidygenERP.createInvoice(
        client.address,
        amount,
        ethers.ZeroAddress,
        "Test Invoice",
        dueDate,
        dataHash
      );

      await tidygenERP.sendInvoice(1);

      const invoice = await tidygenERP.getInvoice(1);
      expect(invoice.status).to.equal(1); // Sent
    });

    it("Should pay an invoice with ETH", async function () {
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      await tidygenERP.createInvoice(
        client.address,
        amount,
        ethers.ZeroAddress,
        "Test Invoice",
        dueDate,
        dataHash
      );

      await tidygenERP.sendInvoice(1);

      const initialBalance = await ethers.provider.getBalance(vendor.address);

      await expect(
        tidygenERP.connect(client).payInvoice(1, { value: amount })
      )
        .to.emit(tidygenERP, "InvoicePaid")
        .withArgs(1, 1, amount);

      const finalBalance = await ethers.provider.getBalance(vendor.address);
      expect(finalBalance).to.be.closeTo(initialBalance + amount, ethers.parseEther("0.1"));

      const invoice = await tidygenERP.getInvoice(1);
      expect(invoice.status).to.equal(2); // Paid
    });

    it("Should pay an invoice with ERC20 tokens", async function () {
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      // Transfer tokens to client
      await tidygenToken.transfer(client.address, amount);

      await tidygenERP.createInvoice(
        client.address,
        amount,
        await tidygenToken.getAddress(),
        "Test Invoice",
        dueDate,
        dataHash
      );

      await tidygenERP.sendInvoice(1);

      await tidygenToken.connect(client).approve(await tidygenERP.getAddress(), amount);

      await expect(
        tidygenERP.connect(client).payInvoice(1)
      )
        .to.emit(tidygenERP, "InvoicePaid")
        .withArgs(1, 1, amount);

      const invoice = await tidygenERP.getInvoice(1);
      expect(invoice.status).to.equal(2); // Paid
    });
  });

  describe("Data Anchoring", function () {
    it("Should anchor data to blockchain", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test data"));
      const dataType = "test";

      await expect(
        tidygenERP.anchorData(dataHash, dataType, owner.address)
      )
        .to.emit(tidygenERP, "DataAnchored")
        .withArgs(dataHash, dataType, owner.address);

      const anchor = await tidygenERP.dataAnchors(dataHash);
      expect(anchor.dataHash).to.equal(dataHash);
      expect(anchor.dataType).to.equal(dataType);
      expect(anchor.anchorer).to.equal(owner.address);
      expect(anchor.isVerified).to.be.true;
    });

    it("Should verify data integrity", async function () {
      const data = "test data";
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes(data));

      const isValid = await tidygenERP.verifyData(dataHash, data);
      expect(isValid).to.be.true;

      const invalidData = "different data";
      const isInvalid = await tidygenERP.verifyData(dataHash, invalidData);
      expect(isInvalid).to.be.false;
    });
  });

  describe("Governance", function () {
    it("Should create a proposal", async function () {
      const title = "Test Proposal";
      const description = "This is a test proposal";
      const votingPowerRequired = ethers.parseEther("1000");
      const votingDuration = 86400; // 1 day
      const executionHash = ethers.keccak256(ethers.toUtf8Bytes("execution data"));

      await expect(
        tidygenERP.createProposal(
          title,
          description,
          votingPowerRequired,
          votingDuration,
          executionHash
        )
      )
        .to.emit(tidygenERP, "ProposalCreated")
        .withArgs(1, owner.address, title);

      const proposal = await tidygenERP.getProposal(1);
      expect(proposal.proposer).to.equal(owner.address);
      expect(proposal.title).to.equal(title);
      expect(proposal.description).to.equal(description);
      expect(proposal.status).to.equal(1); // Active
    });

    it("Should cast a vote", async function () {
      const title = "Test Proposal";
      const description = "This is a test proposal";
      const votingPowerRequired = ethers.parseEther("1000");
      const votingDuration = 86400;
      const executionHash = ethers.keccak256(ethers.toUtf8Bytes("execution data"));

      await tidygenERP.createProposal(
        title,
        description,
        votingPowerRequired,
        votingDuration,
        executionHash
      );

      await expect(
        tidygenERP.vote(1, true)
      )
        .to.emit(tidygenERP, "VoteCast")
        .withArgs(1, owner.address, true, ethers.parseEther("1000000"));

      const proposal = await tidygenERP.getProposal(1);
      expect(proposal.votesFor).to.equal(ethers.parseEther("1000000"));
    });

    it("Should execute a proposal", async function () {
      const title = "Test Proposal";
      const description = "This is a test proposal";
      const votingPowerRequired = ethers.parseEther("1000");
      const votingDuration = 1; // 1 second for testing
      const executionHash = ethers.keccak256(ethers.toUtf8Bytes("execution data"));

      await tidygenERP.createProposal(
        title,
        description,
        votingPowerRequired,
        votingDuration,
        executionHash
      );

      await tidygenERP.vote(1, true);

      // Wait for voting to end
      await new Promise(resolve => setTimeout(resolve, 2000));

      await expect(
        tidygenERP.executeProposal(1)
      )
        .to.emit(tidygenERP, "ProposalExecuted")
        .withArgs(1, executionHash);

      const proposal = await tidygenERP.getProposal(1);
      expect(proposal.status).to.equal(3); // Executed
    });
  });

  describe("Access Control", function () {
    it("Should only allow invoice participants to interact with invoices", async function () {
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      await tidygenERP.createInvoice(
        client.address,
        amount,
        ethers.ZeroAddress,
        "Test Invoice",
        dueDate,
        dataHash
      );

      await expect(
        tidygenERP.connect(addr1).sendInvoice(1)
      ).to.be.revertedWith("Not authorized for this invoice");

      await expect(
        tidygenERP.connect(addr1).payInvoice(1, { value: amount })
      ).to.be.revertedWith("Not authorized for this invoice");
    });

    it("Should only allow owner to set voting power", async function () {
      await expect(
        tidygenERP.connect(addr1).setVotingPower(addr1.address, ethers.parseEther("1000"))
      ).to.be.revertedWithCustomError(tidygenERP, "OwnableUnauthorizedAccount");
    });
  });

  describe("Statistics", function () {
    it("Should return correct statistics", async function () {
      const stats = await tidygenERP.getStats();
      expect(stats[0]).to.equal(0); // totalInvoices
      expect(stats[1]).to.equal(0); // totalPayments
      expect(stats[2]).to.equal(0); // totalProposals
      expect(stats[3]).to.equal(0); // totalAnchors

      // Create an invoice
      const amount = ethers.parseEther("100");
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("test invoice data"));

      await tidygenERP.createInvoice(
        client.address,
        amount,
        ethers.ZeroAddress,
        "Test Invoice",
        dueDate,
        dataHash
      );

      const newStats = await tidygenERP.getStats();
      expect(newStats[0]).to.equal(1); // totalInvoices
    });
  });
});

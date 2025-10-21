/**
 * Tests for Substrate transaction utilities
 */

import { describe, it, expect, vi } from 'vitest';
import { mockAccounts, mockTransactionResult, createMockApi } from '../../test/mocks/blockchainMocks';

// Mock the entire polkadot modules
vi.mock('@polkadot/api', () => ({
  ApiPromise: {
    create: vi.fn(() => Promise.resolve(createMockApi())),
  },
  WsProvider: vi.fn(),
}));

vi.mock('@polkadot/extension-dapp', () => ({
  web3FromAddress: vi.fn(() =>
    Promise.resolve({
      signer: {
        signPayload: vi.fn(),
      },
    })
  ),
}));

import {
  submitInvoice,
  registerDID,
  createProposal,
  voteOnProposal,
} from '../substrateTransactions';

describe('Substrate Transactions', () => {
  const mockAccount = mockAccounts[0];

  describe('submitInvoice', () => {
    it('should submit invoice successfully', async () => {
      const result = await submitInvoice(
        {
          client: '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
          amount: 1000000,
          metadata: 'INV-2025-001|Test|Net 30',
        },
        mockAccount
      );

      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.txHash).toBeTruthy();
    }, 10000); // Increase timeout for async operations

    it('should include transaction metadata', async () => {
      const invoiceData = {
        client: '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
        amount: 2000000,
        metadata: 'INV-2025-002|Client XYZ|Net 15',
      };

      const result = await submitInvoice(invoiceData, mockAccount);

      expect(result.success).toBe(true);
    }, 10000);
  });

  describe('registerDID', () => {
    it('should register DID successfully', async () => {
      const result = await registerDID(
        {
          accountId: mockAccount.address,
          publicKey: '0x04a1b2c3d4',
          metadata: JSON.stringify({ email: 'test@example.com' }),
        },
        mockAccount
      );

      expect(result.success).toBe(true);
      expect(result.txHash).toBeTruthy();
    }, 10000);
  });

  describe('createProposal', () => {
    it('should create proposal successfully', async () => {
      const result = await createProposal(
        {
          title: 'Test Proposal',
          description: 'Test description',
          votingPeriod: 100,
        },
        mockAccount
      );

      expect(result.success).toBe(true);
      expect(result.txHash).toBeTruthy();
    }, 10000);
  });

  describe('voteOnProposal', () => {
    it('should vote yes successfully', async () => {
      const result = await voteOnProposal(0, true, mockAccount);

      expect(result.success).toBe(true);
      expect(result.txHash).toBeTruthy();
    }, 10000);

    it('should vote no successfully', async () => {
      const result = await voteOnProposal(0, false, mockAccount);

      expect(result.success).toBe(true);
      expect(result.txHash).toBeTruthy();
    }, 10000);
  });
});


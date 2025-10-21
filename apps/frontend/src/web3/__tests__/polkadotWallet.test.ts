/**
 * Tests for Polkadot wallet utilities
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mockAccounts, mockChainInfo, createMockApi } from '../../test/mocks/blockchainMocks';

// Mock @polkadot/extension-dapp
vi.mock('@polkadot/extension-dapp', () => ({
  web3Enable: vi.fn(() => Promise.resolve([{ name: 'polkadot-js', version: '0.46.0' }])),
  web3Accounts: vi.fn(() => Promise.resolve(mockAccounts)),
  web3FromAddress: vi.fn((address) => Promise.resolve({
    signer: {
      signPayload: vi.fn(),
    },
  })),
}));

// Mock @polkadot/api
vi.mock('@polkadot/api', () => ({
  ApiPromise: {
    create: vi.fn(() => Promise.resolve(createMockApi())),
  },
  WsProvider: vi.fn(),
}));

import {
  connectWallet,
  getAccounts,
  isWalletConnected,
  formatBalance,
  parseBalance,
} from '../polkadotWallet';

describe('Polkadot Wallet Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('connectWallet', () => {
    it('should connect to Polkadot.js extension', async () => {
      const accounts = await connectWallet();
      
      expect(accounts).toHaveLength(2);
      expect(accounts[0].meta.name).toBe('Alice');
      expect(accounts[1].meta.name).toBe('Bob');
    });

    it('should return accounts with addresses', async () => {
      const accounts = await connectWallet();
      
      accounts.forEach(account => {
        expect(account.address).toBeTruthy();
        expect(account.address).toMatch(/^5[A-Za-z0-9]+$/);
      });
    });
  });

  describe('getAccounts', () => {
    it('should return connected accounts', async () => {
      await connectWallet();
      const accounts = getAccounts();
      
      expect(accounts).toHaveLength(2);
    });
  });

  describe('isWalletConnected', () => {
    it('should return false initially', () => {
      expect(isWalletConnected()).toBe(false);
    });

    it('should return true after connection', async () => {
      await connectWallet();
      expect(isWalletConnected()).toBe(true);
    });
  });

  describe('formatBalance', () => {
    it('should format balance correctly', () => {
      expect(formatBalance(1000000000000, 12)).toBe('1');
      expect(formatBalance(1500000000000, 12)).toBe('1.5');
      expect(formatBalance(123456789012, 12)).toBe('0.123456789012');
    });

    it('should handle zero balance', () => {
      expect(formatBalance(0, 12)).toBe('0');
    });

    it('should handle BigInt', () => {
      expect(formatBalance(BigInt('1000000000000'), 12)).toBe('1');
    });
  });

  describe('parseBalance', () => {
    it('should parse balance to smallest unit', () => {
      expect(parseBalance('1', 12)).toBe(BigInt('1000000000000'));
      expect(parseBalance('1.5', 12)).toBe(BigInt('1500000000000'));
      expect(parseBalance('0.123456789012', 12)).toBe(BigInt('123456789012'));
    });

    it('should handle integer amounts', () => {
      expect(parseBalance(1, 12)).toBe(BigInt('1000000000000'));
      expect(parseBalance(100, 12)).toBe(BigInt('100000000000000'));
    });
  });
});


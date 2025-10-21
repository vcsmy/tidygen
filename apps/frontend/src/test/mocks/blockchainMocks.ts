/**
 * Mock blockchain API responses for testing
 */

import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

// Mock Polkadot.js extension accounts
export const mockAccounts: InjectedAccountWithMeta[] = [
  {
    address: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
    meta: {
      name: 'Alice',
      source: 'polkadot-js',
    },
    type: 'sr25519',
  },
  {
    address: '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
    meta: {
      name: 'Bob',
      source: 'polkadot-js',
    },
    type: 'sr25519',
  },
];

// Mock chain info
export const mockChainInfo = {
  chain: 'TidyGen Development',
  nodeName: 'tidygen-node',
  nodeVersion: '1.0.0',
  tokenSymbol: ['UNIT'],
  tokenDecimals: [12],
  ss58Format: 42,
};

// Mock transaction result
export const mockTransactionResult = {
  success: true,
  txHash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
  blockHash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
  events: [
    {
      section: 'ledger',
      method: 'InvoiceCreated',
      data: [0, '5FHneW...', 1000000],
    },
  ],
};

// Mock invoice data
export const mockInvoice = {
  id: 0,
  client: '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty',
  amount: 1000000,
  metadata: 'INV-2025-001|Test Client|Net 30',
  timestamp: 100,
  invoice_hash: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
  created_by: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
};

// Mock DID document
export const mockDidDocument = {
  controller: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
  public_key: '0x04a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
  metadata: '{"username":"alice","email":"alice@example.com"}',
  created_at: 50,
  updated_at: 50,
  status: 'Active',
  did_identifier: 'did:substrate:tidygen:a1b2c3d4e5f6a7b8',
  nonce: 0,
};

// Mock DAO proposal
export const mockProposal = {
  id: 0,
  proposer: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
  title: 'Approve Q4 Budget',
  description: 'Proposal to approve Q4 2025 budget allocation',
  created_at: 100,
  voting_start: 100,
  voting_end: 200,
  status: 'Active',
  votes_for: 3,
  votes_against: 1,
  total_votes: 4,
  executed: false,
  executed_at: null,
};

// Mock Polkadot.js API
export const createMockApi = () => ({
  isConnected: true,
  tx: {
    ledger: {
      createInvoice: vi.fn(() => ({
        signAndSend: vi.fn((address, options, callback) => {
          // Simulate successful transaction
          setTimeout(() => {
            callback({
              status: {
                isFinalized: true,
                asFinalized: {
                  toHex: () => mockTransactionResult.txHash,
                },
                type: 'Finalized',
              },
              events: [],
              dispatchError: null,
            });
          }, 100);
          return Promise.resolve();
        }),
      })),
    },
    did: {
      registerDid: vi.fn(() => ({
        signAndSend: vi.fn((address, options, callback) => {
          setTimeout(() => {
            callback({
              status: {
                isFinalized: true,
                asFinalized: { toHex: () => mockTransactionResult.txHash },
              },
              events: [],
              dispatchError: null,
            });
          }, 100);
          return Promise.resolve();
        }),
      })),
    },
    dao: {
      createProposal: vi.fn(() => ({
        signAndSend: vi.fn((address, options, callback) => {
          setTimeout(() => {
            callback({
              status: {
                isFinalized: true,
                asFinalized: { toHex: () => mockTransactionResult.txHash },
              },
              events: [],
              dispatchError: null,
            });
          }, 100);
          return Promise.resolve();
        }),
      })),
      vote: vi.fn(() => ({
        signAndSend: vi.fn((address, options, callback) => {
          setTimeout(() => {
            callback({
              status: {
                isFinalized: true,
                asFinalized: { toHex: () => mockTransactionResult.txHash },
              },
              events: [],
              dispatchError: null,
            });
          }, 100);
          return Promise.resolve();
        }),
      })),
    },
  },
  query: {
    ledger: {
      invoices: vi.fn(() => ({
        toJSON: () => [mockInvoice],
        value: [mockInvoice],
      })),
    },
    did: {
      didDocuments: vi.fn(() => ({
        toJSON: () => mockDidDocument,
        value: mockDidDocument,
      })),
    },
    dao: {
      proposals: vi.fn(() => ({
        toJSON: () => mockProposal,
        value: mockProposal,
      })),
    },
  },
  rpc: {
    system: {
      chain: vi.fn(() => Promise.resolve({ toString: () => mockChainInfo.chain })),
      name: vi.fn(() => Promise.resolve({ toString: () => mockChainInfo.nodeName })),
      version: vi.fn(() => Promise.resolve({ toString: () => mockChainInfo.nodeVersion })),
      properties: vi.fn(() =>
        Promise.resolve({
          tokenSymbol: { toJSON: () => mockChainInfo.tokenSymbol },
          tokenDecimals: { toJSON: () => mockChainInfo.tokenDecimals },
          ss58Format: { toJSON: () => mockChainInfo.ss58Format },
        })
      ),
    },
    chain: {
      getHeader: vi.fn(() =>
        Promise.resolve({
          number: { toNumber: () => 100 },
        })
      ),
      subscribeNewHeads: vi.fn((callback) => {
        // Simulate new blocks
        const interval = setInterval(() => {
          callback({ number: { toNumber: () => Math.floor(Math.random() * 1000) } });
        }, 1000);
        
        return () => clearInterval(interval);
      }),
    },
    did: {
      getDid: vi.fn(() => Promise.resolve({ toJSON: () => mockDidDocument })),
      isDidActive: vi.fn(() => Promise.resolve(true)),
      getTotalDids: vi.fn(() => Promise.resolve(10)),
    },
  },
  disconnect: vi.fn(() => Promise.resolve()),
});

export default {
  mockAccounts,
  mockChainInfo,
  mockTransactionResult,
  mockInvoice,
  mockDidDocument,
  mockProposal,
  createMockApi,
};


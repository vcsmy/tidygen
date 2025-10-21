/**
 * TidyGen Web3 Integration
 * 
 * Central export for all Web3 functionality
 */

// Wallet utilities
export {
  initializeApi,
  getApi,
  connectWallet,
  getAccounts,
  getAccountByAddress,
  disconnectWallet,
  isWalletConnected,
  getChainInfo,
  getBlockNumber,
  subscribeToNewBlocks,
  formatBalance,
  parseBalance,
} from './polkadotWallet';

// Transaction utilities
export {
  submitInvoice,
  registerDID,
  createProposal,
  voteOnProposal,
  executeProposal,
  queryInvoices,
  queryDID,
  queryProposal,
} from './substrateTransactions';

// Types
export type {
  InvoiceData,
  DIDData,
  ProposalData,
  TransactionResult,
} from './substrateTransactions';

export type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';


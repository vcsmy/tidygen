/**
 * Polkadot Wallet Integration
 * 
 * Utilities for connecting to Polkadot.js extension and managing accounts.
 */

import { ApiPromise, WsProvider } from '@polkadot/api';
import { web3Accounts, web3Enable, web3FromAddress } from '@polkadot/extension-dapp';
import type { InjectedAccountWithMeta } from '@polkadot/extension-inject/types';

const WS_ENDPOINT = import.meta.env.VITE_WS_ENDPOINT || 'ws://127.0.0.1:9944';
const APP_NAME = 'TidyGen ERP';

let apiInstance: ApiPromise | null = null;
let connectedAccounts: InjectedAccountWithMeta[] = [];

/**
 * Initialize connection to Substrate node
 */
export async function initializeApi(): Promise<ApiPromise> {
  if (apiInstance && apiInstance.isConnected) {
    return apiInstance;
  }

  try {
    console.log(`Connecting to Substrate node at ${WS_ENDPOINT}...`);
    
    const provider = new WsProvider(WS_ENDPOINT);
    const api = await ApiPromise.create({ provider });
    
    await api.isReady;
    
    const [chain, nodeName, nodeVersion] = await Promise.all([
      api.rpc.system.chain(),
      api.rpc.system.name(),
      api.rpc.system.version(),
    ]);
    
    console.log(`Connected to ${chain} using ${nodeName} v${nodeVersion}`);
    
    apiInstance = api;
    return api;
  } catch (error) {
    console.error('Failed to connect to Substrate node:', error);
    throw new Error(`Substrate connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get the current API instance
 */
export function getApi(): ApiPromise | null {
  return apiInstance;
}

/**
 * Connect to Polkadot.js browser extension
 * 
 * @returns Promise<InjectedAccountWithMeta[]> - Array of available accounts
 * @throws Error if extension is not installed or user denies access
 */
export async function connectWallet(): Promise<InjectedAccountWithMeta[]> {
  try {
    console.log('Requesting access to Polkadot.js extension...');
    
    // Request access to extension
    const extensions = await web3Enable(APP_NAME);
    
    if (extensions.length === 0) {
      throw new Error(
        'Polkadot.js extension not found. Please install it from polkadot.js.org/extension/'
      );
    }
    
    console.log(`Connected to ${extensions.length} extension(s)`);
    
    // Get all accounts
    const accounts = await web3Accounts();
    
    if (accounts.length === 0) {
      throw new Error('No accounts found in Polkadot.js extension. Please create an account first.');
    }
    
    console.log(`Found ${accounts.length} account(s)`);
    connectedAccounts = accounts;
    
    return accounts;
  } catch (error) {
    console.error('Wallet connection failed:', error);
    throw error;
  }
}

/**
 * Get all available accounts from connected wallet
 * 
 * @returns InjectedAccountWithMeta[] - Array of accounts
 */
export function getAccounts(): InjectedAccountWithMeta[] {
  return connectedAccounts;
}

/**
 * Get a specific account by address
 */
export function getAccountByAddress(address: string): InjectedAccountWithMeta | undefined {
  return connectedAccounts.find(account => account.address === address);
}

/**
 * Disconnect wallet and cleanup
 */
export async function disconnectWallet(): Promise<void> {
  connectedAccounts = [];
  
  if (apiInstance) {
    await apiInstance.disconnect();
    apiInstance = null;
  }
  
  console.log('Wallet disconnected');
}

/**
 * Check if wallet is connected
 */
export function isWalletConnected(): boolean {
  return connectedAccounts.length > 0;
}

/**
 * Get chain information
 */
export async function getChainInfo() {
  const api = await initializeApi();
  
  const [chain, nodeName, nodeVersion, properties] = await Promise.all([
    api.rpc.system.chain(),
    api.rpc.system.name(),
    api.rpc.system.version(),
    api.rpc.system.properties(),
  ]);
  
  return {
    chain: chain.toString(),
    nodeName: nodeName.toString(),
    nodeVersion: nodeVersion.toString(),
    tokenSymbol: properties.tokenSymbol.toJSON() as string[],
    tokenDecimals: properties.tokenDecimals.toJSON() as number[],
    ss58Format: properties.ss58Format.toJSON() as number,
  };
}

/**
 * Get current block number
 */
export async function getBlockNumber(): Promise<number> {
  const api = await initializeApi();
  const header = await api.rpc.chain.getHeader();
  return header.number.toNumber();
}

/**
 * Subscribe to new blocks
 */
export async function subscribeToNewBlocks(
  callback: (blockNumber: number) => void
): Promise<() => void> {
  const api = await initializeApi();
  
  const unsubscribe = await api.rpc.chain.subscribeNewHeads((header) => {
    callback(header.number.toNumber());
  });
  
  return unsubscribe;
}

/**
 * Format balance for display
 */
export function formatBalance(balance: bigint | string | number, decimals: number = 12): string {
  const balanceBigInt = typeof balance === 'bigint' ? balance : BigInt(balance);
  const divisor = BigInt(10 ** decimals);
  const integerPart = balanceBigInt / divisor;
  const fractionalPart = balanceBigInt % divisor;
  
  if (fractionalPart === BigInt(0)) {
    return integerPart.toString();
  }
  
  const fractionalStr = fractionalPart.toString().padStart(decimals, '0');
  const trimmed = fractionalStr.replace(/0+$/, '');
  
  return `${integerPart}.${trimmed}`;
}

/**
 * Parse balance from string to smallest unit
 */
export function parseBalance(amount: string | number, decimals: number = 12): bigint {
  const amountStr = amount.toString();
  const [integerPart, fractionalPart = ''] = amountStr.split('.');
  
  const paddedFractional = fractionalPart.padEnd(decimals, '0').slice(0, decimals);
  const fullAmount = integerPart + paddedFractional;
  
  return BigInt(fullAmount);
}

export default {
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
};


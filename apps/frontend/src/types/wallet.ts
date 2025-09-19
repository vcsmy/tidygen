/**
 * Wallet Types
 * 
 * TypeScript type definitions for wallet-related functionality
 * including MetaMask and Polkadot.js integration.
 */

export interface WalletInfo {
  id: string;
  address: string;
  walletType: 'metamask' | 'polkadot' | 'walletconnect' | 'other';
  chainType: 'ethereum' | 'polygon' | 'bsc' | 'substrate' | 'polkadot' | 'kusama' | 'other';
  chainId: string;
  networkName: string;
  isPrimary: boolean;
  isVerified: boolean;
  isActive: boolean;
  publicKey?: string;
  metadata: Record<string, any>;
  createdAt: string;
  lastUsed: string;
  verifiedAt?: string;
}

export interface WalletSignature {
  id: string;
  walletId: string;
  signatureType: 'authentication' | 'transaction' | 'verification' | 'permission';
  message: string;
  signature?: string;
  nonce: string;
  status: 'pending' | 'signed' | 'verified' | 'expired' | 'failed';
  verified: boolean;
  isExpired: boolean;
  isValid: boolean;
  createdAt: string;
  signedAt?: string;
  verifiedAt?: string;
  expiresAt: string;
  ipAddress?: string;
  userAgent?: string;
  metadata: Record<string, any>;
}

export interface WalletPermission {
  id: string;
  walletId: string;
  permissionType: 'read' | 'write' | 'delete' | 'admin' | 'sign' | 'approve';
  resourceType: 'invoice' | 'payment' | 'expense' | 'user' | 'organization' | 'ledger' | 'wallet' | 'all';
  resourceId?: string;
  granted: boolean;
  isExpired: boolean;
  isActive: boolean;
  reason?: string;
  expiresAt?: string;
  grantedBy: string;
  grantedByUsername: string;
  createdAt: string;
  updatedAt: string;
}

export interface WalletSession {
  id: string;
  walletId: string;
  walletAddress: string;
  walletType: string;
  userId: string;
  username: string;
  sessionKey: string;
  isActive: boolean;
  isExpired: boolean;
  isValid: boolean;
  ipAddress: string;
  userAgent: string;
  createdAt: string;
  lastActivity: string;
  expiresAt: string;
}

export interface NetworkInfo {
  chainId: number | string;
  networkName: string;
  rpcUrl: string;
  blockExplorer: string;
  currency: string;
  decimals?: number;
}

export interface SupportedWallet {
  type: string;
  name: string;
  description: string;
  supportedChains: string[];
  icon: string;
  enabled: boolean;
}

export interface WalletConnectionRequest {
  walletType: string;
  address: string;
  chainId: string;
  networkName: string;
  publicKey?: string;
  metadata?: Record<string, any>;
}

export interface WalletAuthenticationRequest {
  walletId: string;
  signatureType: string;
  userId?: string;
}

export interface WalletAuthenticationResponse {
  signatureId: string;
  walletId: string;
  address: string;
  walletType: string;
  message: string;
  nonce: string;
  timestamp: number;
  expiresAt: string;
  networkInfo?: NetworkInfo;
}

export interface WalletAuthenticationVerify {
  signatureId: string;
  signature: string;
  userId?: string;
}

export interface WalletAuthenticationResult {
  success: boolean;
  userId?: string;
  walletId?: string;
  address?: string;
  walletType?: string;
  accessToken?: string;
  refreshToken?: string;
  sessionId?: string;
  message?: string;
  error?: string;
}

export interface TransactionSignatureRequest {
  walletId: string;
  transactionType: string;
  amount: string;
  currency: string;
  description: string;
  recipient?: string;
  metadata?: Record<string, any>;
}

export interface TransactionSignatureResponse {
  signatureId: string;
  walletId: string;
  address: string;
  walletType: string;
  message: string;
  nonce: string;
  timestamp: number;
  expiresAt: string;
  transactionData: Record<string, any>;
}

export interface WalletStatus {
  connected: boolean;
  walletType: string;
  address: string;
  networkName: string;
  chainId: string;
  balance?: {
    address: string;
    balanceWei: string;
    balanceEth: string;
    currency: string;
  };
  isVerified: boolean;
  lastUsed: string;
}

export interface WalletError {
  code: string;
  message: string;
  details?: any;
}

export interface MetaMaskProvider {
  isMetaMask?: boolean;
  request: (args: { method: string; params?: any[] }) => Promise<any>;
  on: (event: string, callback: (data: any) => void) => void;
  removeListener: (event: string, callback: (data: any) => void) => void;
  selectedAddress?: string;
  chainId?: string;
  networkVersion?: string;
}

export interface PolkadotProvider {
  isPolkadot?: boolean;
  enable: () => Promise<any>;
  signer: {
    signRaw: (args: { address: string; data: string }) => Promise<{ signature: string }>;
  };
  accounts: {
    get: () => Promise<any[]>;
    subscribe: (callback: (accounts: any[]) => void) => () => void;
  };
}

export interface WalletConnectOptions {
  walletType: string;
  onConnect: (wallet: WalletInfo) => void;
  onDisconnect: () => void;
  onError: (error: WalletError) => void;
}

export interface TransactionSignerOptions {
  transaction: Record<string, any>;
  wallet: WalletInfo;
  onSigned: (signature: string) => void;
  onError: (error: WalletError) => void;
}

export interface WalletServiceConfig {
  apiBaseUrl: string;
  supportedWallets: SupportedWallet[];
  defaultNetwork: NetworkInfo;
  signatureTimeout: number;
  retryAttempts: number;
}

// Event types for wallet events
export type WalletEventType = 
  | 'connect'
  | 'disconnect'
  | 'accountChanged'
  | 'chainChanged'
  | 'signatureRequested'
  | 'signatureReceived'
  | 'signatureVerified'
  | 'error';

export interface WalletEvent {
  type: WalletEventType;
  data: any;
  timestamp: number;
}

export interface WalletEventCallback {
  (event: WalletEvent): void;
}

// Hook return types
export interface UseWalletReturn {
  wallet: WalletInfo | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: WalletError | null;
  connect: (walletType: string) => Promise<void>;
  disconnect: () => Promise<void>;
  signMessage: (message: string) => Promise<string>;
  signTransaction: (transaction: Record<string, any>) => Promise<string>;
  switchNetwork: (chainId: string) => Promise<void>;
  getBalance: () => Promise<string>;
  getNetworkInfo: () => Promise<NetworkInfo>;
}

export interface UseMetaMaskReturn {
  isInstalled: boolean;
  isConnected: boolean;
  account: string | null;
  chainId: string | null;
  connect: () => Promise<string[]>;
  disconnect: () => Promise<void>;
  signMessage: (message: string) => Promise<string>;
  signTransaction: (transaction: Record<string, any>) => Promise<string>;
  switchChain: (chainId: string) => Promise<void>;
  addChain: (chain: NetworkInfo) => Promise<void>;
  getBalance: (address: string) => Promise<string>;
}

export interface UsePolkadotReturn {
  isInstalled: boolean;
  isConnected: boolean;
  accounts: any[];
  selectedAccount: any | null;
  connect: () => Promise<any[]>;
  disconnect: () => Promise<void>;
  signMessage: (message: string, account: any) => Promise<string>;
  signTransaction: (transaction: Record<string, any>, account: any) => Promise<string>;
  switchAccount: (account: any) => Promise<void>;
  getBalance: (address: string) => Promise<string>;
}

export interface UseSignatureReturn {
  isSigning: boolean;
  error: WalletError | null;
  signMessage: (message: string) => Promise<string>;
  signTransaction: (transaction: Record<string, any>) => Promise<string>;
  verifySignature: (message: string, signature: string, address: string) => Promise<boolean>;
}

/**
 * Polkadot Service
 * 
 * Service for integrating with Polkadot.js wallet,
 * including connection, signature requests, and transaction handling.
 */

import { 
  UsePolkadotReturn, 
  NetworkInfo, 
  WalletError,
  PolkadotProvider 
} from '../../types/wallet';

declare global {
  interface Window {
    injectedWeb3?: {
      [key: string]: {
        enable: (origin: string) => Promise<PolkadotProvider>;
        version: string;
      };
    };
  }
}

class PolkadotService {
  private provider: PolkadotProvider | null = null;
  private isInstalled: boolean = false;
  private accounts: any[] = [];
  private selectedAccount: any | null = null;

  constructor() {
    this.initializeProvider();
  }

  /**
   * Initialize Polkadot provider
   */
  private initializeProvider(): void {
    if (typeof window !== 'undefined' && window.injectedWeb3) {
      // Check for common Polkadot.js extensions
      const extensions = ['polkadot-js', 'subwallet-js', 'talisman'];
      
      for (const extension of extensions) {
        if (window.injectedWeb3[extension]) {
          this.isInstalled = true;
          break;
        }
      }
    }
  }

  /**
   * Check if Polkadot.js is installed
   */
  getIsInstalled(): boolean {
    return this.isInstalled;
  }

  /**
   * Check if Polkadot.js is connected
   */
  getIsConnected(): boolean {
    return this.provider !== null && this.accounts.length > 0;
  }

  /**
   * Get connected accounts
   */
  getAccounts(): any[] {
    return this.accounts;
  }

  /**
   * Get selected account
   */
  getSelectedAccount(): any | null {
    return this.selectedAccount;
  }

  /**
   * Connect to Polkadot.js
   */
  async connect(): Promise<any[]> {
    if (!this.isInstalled) {
      throw new WalletError('POLKADOT_NOT_INSTALLED', 'Polkadot.js extension is not installed');
    }

    try {
      // Try to enable the first available extension
      const extensions = Object.keys(window.injectedWeb3!);
      const extension = extensions[0];
      
      if (!extension) {
        throw new WalletError('NO_EXTENSION', 'No Polkadot.js extension found');
      }

      this.provider = await window.injectedWeb3![extension].enable('TidyGen ERP');
      
      // Get accounts
      this.accounts = await this.provider.accounts.get();
      
      if (this.accounts.length === 0) {
        throw new WalletError('NO_ACCOUNTS', 'No accounts found in Polkadot.js extension');
      }

      // Select first account by default
      this.selectedAccount = this.accounts[0];

      return this.accounts;
    } catch (error: any) {
      throw new WalletError('CONNECTION_FAILED', error.message || 'Failed to connect to Polkadot.js');
    }
  }

  /**
   * Disconnect from Polkadot.js
   */
  async disconnect(): Promise<void> {
    this.provider = null;
    this.accounts = [];
    this.selectedAccount = null;
  }

  /**
   * Switch to a different account
   */
  async switchAccount(account: any): Promise<void> {
    if (!this.accounts.includes(account)) {
      throw new WalletError('INVALID_ACCOUNT', 'Account not found in connected accounts');
    }

    this.selectedAccount = account;
  }

  /**
   * Sign a message
   */
  async signMessage(message: string, account?: any): Promise<string> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'Polkadot.js is not connected');
    }

    const targetAccount = account || this.selectedAccount;
    if (!targetAccount) {
      throw new WalletError('NO_ACCOUNT', 'No account selected');
    }

    try {
      const result = await this.provider.signer.signRaw({
        address: targetAccount.address,
        data: message,
      });

      return result.signature;
    } catch (error: any) {
      throw new WalletError('SIGNATURE_FAILED', error.message || 'Failed to sign message');
    }
  }

  /**
   * Sign a transaction
   */
  async signTransaction(transaction: Record<string, any>, account?: any): Promise<string> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'Polkadot.js is not connected');
    }

    const targetAccount = account || this.selectedAccount;
    if (!targetAccount) {
      throw new WalletError('NO_ACCOUNT', 'No account selected');
    }

    try {
      // For now, we'll sign the transaction data as a message
      // In a real implementation, you would use the proper transaction signing methods
      const transactionData = JSON.stringify(transaction);
      const result = await this.provider.signer.signRaw({
        address: targetAccount.address,
        data: transactionData,
      });

      return result.signature;
    } catch (error: any) {
      throw new WalletError('TRANSACTION_FAILED', error.message || 'Failed to sign transaction');
    }
  }

  /**
   * Get balance for an address
   */
  async getBalance(address: string): Promise<string> {
    // This would typically require a connection to a Substrate node
    // For now, return a mock balance
    return '0';
  }

  /**
   * Get current network information
   */
  async getNetworkInfo(): Promise<NetworkInfo> {
    // This would typically require a connection to a Substrate node
    // For now, return default Polkadot network info
    return {
      chainId: 'polkadot',
      networkName: 'Polkadot',
      rpcUrl: 'wss://rpc.polkadot.io',
      blockExplorer: 'https://polkadot.subscan.io',
      currency: 'DOT',
      decimals: 10,
    };
  }

  /**
   * Listen for account changes
   */
  onAccountsChanged(callback: (accounts: any[]) => void): () => void {
    if (!this.provider) {
      return () => {};
    }

    const unsubscribe = this.provider.accounts.subscribe((accounts) => {
      this.accounts = accounts;
      if (accounts.length > 0 && !this.selectedAccount) {
        this.selectedAccount = accounts[0];
      }
      callback(accounts);
    });

    return unsubscribe;
  }

  /**
   * Get supported networks
   */
  getSupportedNetworks(): NetworkInfo[] {
    return [
      {
        chainId: 'polkadot',
        networkName: 'Polkadot',
        rpcUrl: 'wss://rpc.polkadot.io',
        blockExplorer: 'https://polkadot.subscan.io',
        currency: 'DOT',
        decimals: 10,
      },
      {
        chainId: 'kusama',
        networkName: 'Kusama',
        rpcUrl: 'wss://kusama-rpc.polkadot.io',
        blockExplorer: 'https://kusama.subscan.io',
        currency: 'KSM',
        decimals: 12,
      },
      {
        chainId: 'westend',
        networkName: 'Westend Testnet',
        rpcUrl: 'wss://westend-rpc.polkadot.io',
        blockExplorer: 'https://westend.subscan.io',
        currency: 'WND',
        decimals: 12,
      },
      {
        chainId: 'rococo',
        networkName: 'Rococo Testnet',
        rpcUrl: 'wss://rococo-rpc.polkadot.io',
        blockExplorer: 'https://rococo.subscan.io',
        currency: 'ROC',
        decimals: 12,
      },
    ];
  }

  /**
   * Validate Substrate address
   */
  validateAddress(address: string): boolean {
    // Basic validation for Substrate addresses
    // In a real implementation, you would use proper SS58 validation
    return address.length >= 40 && address.length <= 50;
  }

  /**
   * Get account display name
   */
  getAccountDisplayName(account: any): string {
    return account.meta?.name || account.address;
  }

  /**
   * Get account short address
   */
  getAccountShortAddress(account: any): string {
    const address = account.address;
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-6)}`;
    }
    return address;
  }

  /**
   * Get account balance (mock implementation)
   */
  async getAccountBalance(account: any): Promise<string> {
    // This would typically require a connection to a Substrate node
    // For now, return a mock balance
    return '0';
  }

  /**
   * Get account metadata
   */
  getAccountMetadata(account: any): Record<string, any> {
    return account.meta || {};
  }

  /**
   * Check if account is hardware wallet
   */
  isHardwareWallet(account: any): boolean {
    return account.meta?.isHardware || false;
  }

  /**
   * Get account source
   */
  getAccountSource(account: any): string {
    return account.meta?.source || 'unknown';
  }
}

// Create singleton instance
export const polkadotService = new PolkadotService();
export default PolkadotService;

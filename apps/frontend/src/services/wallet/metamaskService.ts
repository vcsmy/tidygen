/**
 * MetaMask Service
 * 
 * Service for integrating with MetaMask wallet,
 * including connection, signature requests, and transaction handling.
 */

import { 
  UseMetaMaskReturn, 
  NetworkInfo, 
  WalletError,
  MetaMaskProvider 
} from '../../types/wallet';

declare global {
  interface Window {
    ethereum?: MetaMaskProvider;
  }
}

class MetaMaskService {
  private provider: MetaMaskProvider | null = null;
  private isInstalled: boolean = false;

  constructor() {
    this.initializeProvider();
  }

  /**
   * Initialize MetaMask provider
   */
  private initializeProvider(): void {
    if (typeof window !== 'undefined' && window.ethereum) {
      this.provider = window.ethereum;
      this.isInstalled = true;
    }
  }

  /**
   * Check if MetaMask is installed
   */
  getIsInstalled(): boolean {
    return this.isInstalled;
  }

  /**
   * Check if MetaMask is connected
   */
  getIsConnected(): boolean {
    return this.provider?.selectedAddress !== undefined;
  }

  /**
   * Get current account
   */
  getAccount(): string | null {
    return this.provider?.selectedAddress || null;
  }

  /**
   * Get current chain ID
   */
  getChainId(): string | null {
    return this.provider?.chainId || null;
  }

  /**
   * Connect to MetaMask
   */
  async connect(): Promise<string[]> {
    if (!this.isInstalled) {
      throw new WalletError('METAMASK_NOT_INSTALLED', 'MetaMask is not installed');
    }

    try {
      const accounts = await this.provider!.request({
        method: 'eth_requestAccounts',
      });

      return accounts;
    } catch (error: any) {
      throw new WalletError('CONNECTION_FAILED', error.message || 'Failed to connect to MetaMask');
    }
  }

  /**
   * Disconnect from MetaMask
   */
  async disconnect(): Promise<void> {
    // MetaMask doesn't have a disconnect method
    // The connection is managed by the user in the MetaMask extension
    return Promise.resolve();
  }

  /**
   * Sign a message
   */
  async signMessage(message: string): Promise<string> {
    if (!this.provider || !this.getAccount()) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      const signature = await this.provider.request({
        method: 'personal_sign',
        params: [message, this.getAccount()],
      });

      return signature;
    } catch (error: any) {
      throw new WalletError('SIGNATURE_FAILED', error.message || 'Failed to sign message');
    }
  }

  /**
   * Sign a transaction
   */
  async signTransaction(transaction: Record<string, any>): Promise<string> {
    if (!this.provider || !this.getAccount()) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      const txHash = await this.provider.request({
        method: 'eth_sendTransaction',
        params: [transaction],
      });

      return txHash;
    } catch (error: any) {
      throw new WalletError('TRANSACTION_FAILED', error.message || 'Failed to sign transaction');
    }
  }

  /**
   * Switch to a different chain
   */
  async switchChain(chainId: string): Promise<void> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      await this.provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId }],
      });
    } catch (error: any) {
      // If the chain is not added, try to add it
      if (error.code === 4902) {
        throw new WalletError('CHAIN_NOT_ADDED', 'Chain not added to MetaMask');
      }
      throw new WalletError('CHAIN_SWITCH_FAILED', error.message || 'Failed to switch chain');
    }
  }

  /**
   * Add a new chain to MetaMask
   */
  async addChain(chain: NetworkInfo): Promise<void> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      await this.provider.request({
        method: 'wallet_addEthereumChain',
        params: [{
          chainId: `0x${parseInt(chain.chainId.toString()).toString(16)}`,
          chainName: chain.networkName,
          rpcUrls: [chain.rpcUrl],
          blockExplorerUrls: [chain.blockExplorer],
          nativeCurrency: {
            name: chain.currency,
            symbol: chain.currency,
            decimals: chain.decimals || 18,
          },
        }],
      });
    } catch (error: any) {
      throw new WalletError('CHAIN_ADD_FAILED', error.message || 'Failed to add chain');
    }
  }

  /**
   * Get balance for an address
   */
  async getBalance(address: string): Promise<string> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      const balance = await this.provider.request({
        method: 'eth_getBalance',
        params: [address, 'latest'],
      });

      // Convert from wei to ether
      return this.weiToEther(balance);
    } catch (error: any) {
      throw new WalletError('BALANCE_FAILED', error.message || 'Failed to get balance');
    }
  }

  /**
   * Get current network information
   */
  async getNetworkInfo(): Promise<NetworkInfo> {
    if (!this.provider) {
      throw new WalletError('NOT_CONNECTED', 'MetaMask is not connected');
    }

    try {
      const chainId = await this.provider.request({
        method: 'eth_chainId',
      });

      const networkInfo = this.getNetworkByChainId(chainId);
      return networkInfo;
    } catch (error: any) {
      throw new WalletError('NETWORK_INFO_FAILED', error.message || 'Failed to get network info');
    }
  }

  /**
   * Listen for account changes
   */
  onAccountsChanged(callback: (accounts: string[]) => void): () => void {
    if (!this.provider) {
      return () => {};
    }

    this.provider.on('accountsChanged', callback);

    return () => {
      this.provider?.removeListener('accountsChanged', callback);
    };
  }

  /**
   * Listen for chain changes
   */
  onChainChanged(callback: (chainId: string) => void): () => void {
    if (!this.provider) {
      return () => {};
    }

    this.provider.on('chainChanged', callback);

    return () => {
      this.provider?.removeListener('chainChanged', callback);
    };
  }

  /**
   * Convert wei to ether
   */
  private weiToEther(wei: string): string {
    const weiValue = parseInt(wei, 16);
    const etherValue = weiValue / Math.pow(10, 18);
    return etherValue.toString();
  }

  /**
   * Get network information by chain ID
   */
  private getNetworkByChainId(chainId: string): NetworkInfo {
    const networks: Record<string, NetworkInfo> = {
      '0x1': {
        chainId: 1,
        networkName: 'Ethereum Mainnet',
        rpcUrl: 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
        blockExplorer: 'https://etherscan.io',
        currency: 'ETH',
        decimals: 18,
      },
      '0x5': {
        chainId: 5,
        networkName: 'Goerli Testnet',
        rpcUrl: 'https://goerli.infura.io/v3/YOUR_PROJECT_ID',
        blockExplorer: 'https://goerli.etherscan.io',
        currency: 'ETH',
        decimals: 18,
      },
      '0x89': {
        chainId: 137,
        networkName: 'Polygon Mainnet',
        rpcUrl: 'https://polygon-rpc.com',
        blockExplorer: 'https://polygonscan.com',
        currency: 'MATIC',
        decimals: 18,
      },
      '0x13881': {
        chainId: 80001,
        networkName: 'Polygon Mumbai Testnet',
        rpcUrl: 'https://rpc-mumbai.maticvigil.com',
        blockExplorer: 'https://mumbai.polygonscan.com',
        currency: 'MATIC',
        decimals: 18,
      },
      '0x38': {
        chainId: 56,
        networkName: 'BSC Mainnet',
        rpcUrl: 'https://bsc-dataseed.binance.org',
        blockExplorer: 'https://bscscan.com',
        currency: 'BNB',
        decimals: 18,
      },
      '0x61': {
        chainId: 97,
        networkName: 'BSC Testnet',
        rpcUrl: 'https://data-seed-prebsc-1-s1.binance.org:8545',
        blockExplorer: 'https://testnet.bscscan.com',
        currency: 'BNB',
        decimals: 18,
      },
    };

    return networks[chainId] || {
      chainId: parseInt(chainId, 16),
      networkName: `Unknown Network (${chainId})`,
      rpcUrl: '',
      blockExplorer: '',
      currency: 'ETH',
      decimals: 18,
    };
  }

  /**
   * Get supported networks
   */
  getSupportedNetworks(): NetworkInfo[] {
    return [
      {
        chainId: 1,
        networkName: 'Ethereum Mainnet',
        rpcUrl: 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
        blockExplorer: 'https://etherscan.io',
        currency: 'ETH',
        decimals: 18,
      },
      {
        chainId: 5,
        networkName: 'Goerli Testnet',
        rpcUrl: 'https://goerli.infura.io/v3/YOUR_PROJECT_ID',
        blockExplorer: 'https://goerli.etherscan.io',
        currency: 'ETH',
        decimals: 18,
      },
      {
        chainId: 137,
        networkName: 'Polygon Mainnet',
        rpcUrl: 'https://polygon-rpc.com',
        blockExplorer: 'https://polygonscan.com',
        currency: 'MATIC',
        decimals: 18,
      },
      {
        chainId: 80001,
        networkName: 'Polygon Mumbai Testnet',
        rpcUrl: 'https://rpc-mumbai.maticvigil.com',
        blockExplorer: 'https://mumbai.polygonscan.com',
        currency: 'MATIC',
        decimals: 18,
      },
      {
        chainId: 56,
        networkName: 'BSC Mainnet',
        rpcUrl: 'https://bsc-dataseed.binance.org',
        blockExplorer: 'https://bscscan.com',
        currency: 'BNB',
        decimals: 18,
      },
      {
        chainId: 97,
        networkName: 'BSC Testnet',
        rpcUrl: 'https://data-seed-prebsc-1-s1.binance.org:8545',
        blockExplorer: 'https://testnet.bscscan.com',
        currency: 'BNB',
        decimals: 18,
      },
    ];
  }
}

// Create singleton instance
export const metaMaskService = new MetaMaskService();
export default MetaMaskService;

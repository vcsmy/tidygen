/**
 * useWallet Hook
 * 
 * React hook for wallet management and authentication
 * providing a unified interface for different wallet types.
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  UseWalletReturn, 
  WalletInfo, 
  WalletError,
  WalletEvent,
  WalletEventCallback
} from '../types/wallet';
import { walletService } from '../services/wallet/walletService';
import { metaMaskService } from '../services/wallet/metamaskService';
import { polkadotService } from '../services/wallet/polkadotService';

export const useWallet = (): UseWalletReturn => {
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<WalletError | null>(null);

  // Event listeners
  const [eventListeners, setEventListeners] = useState<Map<string, WalletEventCallback>>(new Map());

  /**
   * Emit wallet event
   */
  const emitEvent = useCallback((event: WalletEvent) => {
    eventListeners.forEach((callback) => {
      try {
        callback(event);
      } catch (err) {
        console.error('Error in wallet event callback:', err);
      }
    });
  }, [eventListeners]);

  /**
   * Add event listener
   */
  const addEventListener = useCallback((eventType: string, callback: WalletEventCallback) => {
    setEventListeners(prev => new Map(prev).set(eventType, callback));
  }, []);

  /**
   * Remove event listener
   */
  const removeEventListener = useCallback((eventType: string) => {
    setEventListeners(prev => {
      const newMap = new Map(prev);
      newMap.delete(eventType);
      return newMap;
    });
  }, []);

  /**
   * Connect to wallet
   */
  const connect = useCallback(async (walletType: string) => {
    setIsConnecting(true);
    setError(null);

    try {
      let address: string;
      let chainId: string;
      let networkName: string;
      let publicKey: string | undefined;

      // Connect to the appropriate wallet service
      if (walletType === 'metamask') {
        if (!metaMaskService.getIsInstalled()) {
          throw new WalletError('METAMASK_NOT_INSTALLED', 'MetaMask is not installed');
        }

        const accounts = await metaMaskService.connect();
        address = accounts[0];
        chainId = metaMaskService.getChainId() || '1';
        networkName = 'Ethereum Mainnet';
      } else if (walletType === 'polkadot') {
        if (!polkadotService.getIsInstalled()) {
          throw new WalletError('POLKADOT_NOT_INSTALLED', 'Polkadot.js extension is not installed');
        }

        const accounts = await polkadotService.connect();
        address = accounts[0].address;
        chainId = 'polkadot';
        networkName = 'Polkadot';
        publicKey = accounts[0].address; // For Substrate, address is the public key
      } else {
        throw new WalletError('UNSUPPORTED_WALLET', `Unsupported wallet type: ${walletType}`);
      }

      // Connect wallet to backend
      const walletInfo = await walletService.connectWallet({
        walletType,
        address,
        chainId,
        networkName,
        publicKey,
        metadata: {},
      });

      setWallet(walletInfo);
      setIsConnected(true);

      emitEvent({
        type: 'connect',
        data: walletInfo,
        timestamp: Date.now(),
      });

    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('CONNECTION_FAILED', err.message);
      setError(walletError);
      
      emitEvent({
        type: 'error',
        data: walletError,
        timestamp: Date.now(),
      });
    } finally {
      setIsConnecting(false);
    }
  }, [emitEvent]);

  /**
   * Disconnect wallet
   */
  const disconnect = useCallback(async () => {
    if (!wallet) return;

    try {
      await walletService.disconnectWallet(wallet.id);
      
      // Disconnect from wallet service
      if (wallet.walletType === 'metamask') {
        await metaMaskService.disconnect();
      } else if (wallet.walletType === 'polkadot') {
        await polkadotService.disconnect();
      }

      setWallet(null);
      setIsConnected(false);

      emitEvent({
        type: 'disconnect',
        data: wallet,
        timestamp: Date.now(),
      });

    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('DISCONNECT_FAILED', err.message);
      setError(walletError);
      
      emitEvent({
        type: 'error',
        data: walletError,
        timestamp: Date.now(),
      });
    }
  }, [wallet, emitEvent]);

  /**
   * Sign message
   */
  const signMessage = useCallback(async (message: string): Promise<string> => {
    if (!wallet) {
      throw new WalletError('NOT_CONNECTED', 'No wallet connected');
    }

    try {
      let signature: string;

      if (wallet.walletType === 'metamask') {
        signature = await metaMaskService.signMessage(message);
      } else if (wallet.walletType === 'polkadot') {
        signature = await polkadotService.signMessage(message);
      } else {
        throw new WalletError('UNSUPPORTED_WALLET', `Unsupported wallet type: ${wallet.walletType}`);
      }

      emitEvent({
        type: 'signatureReceived',
        data: { message, signature },
        timestamp: Date.now(),
      });

      return signature;
    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('SIGNATURE_FAILED', err.message);
      setError(walletError);
      throw walletError;
    }
  }, [wallet, emitEvent]);

  /**
   * Sign transaction
   */
  const signTransaction = useCallback(async (transaction: Record<string, any>): Promise<string> => {
    if (!wallet) {
      throw new WalletError('NOT_CONNECTED', 'No wallet connected');
    }

    try {
      let signature: string;

      if (wallet.walletType === 'metamask') {
        signature = await metaMaskService.signTransaction(transaction);
      } else if (wallet.walletType === 'polkadot') {
        signature = await polkadotService.signTransaction(transaction);
      } else {
        throw new WalletError('UNSUPPORTED_WALLET', `Unsupported wallet type: ${wallet.walletType}`);
      }

      emitEvent({
        type: 'signatureReceived',
        data: { transaction, signature },
        timestamp: Date.now(),
      });

      return signature;
    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('TRANSACTION_FAILED', err.message);
      setError(walletError);
      throw walletError;
    }
  }, [wallet, emitEvent]);

  /**
   * Switch network
   */
  const switchNetwork = useCallback(async (chainId: string): Promise<void> => {
    if (!wallet) {
      throw new WalletError('NOT_CONNECTED', 'No wallet connected');
    }

    try {
      if (wallet.walletType === 'metamask') {
        await metaMaskService.switchChain(chainId);
      } else if (wallet.walletType === 'polkadot') {
        // Polkadot doesn't have network switching in the same way
        // This would typically involve connecting to a different chain
        console.log('Network switching not supported for Polkadot.js');
      }

      emitEvent({
        type: 'chainChanged',
        data: { chainId },
        timestamp: Date.now(),
      });

    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('NETWORK_SWITCH_FAILED', err.message);
      setError(walletError);
      throw walletError;
    }
  }, [wallet, emitEvent]);

  /**
   * Get balance
   */
  const getBalance = useCallback(async (): Promise<string> => {
    if (!wallet) {
      throw new WalletError('NOT_CONNECTED', 'No wallet connected');
    }

    try {
      if (wallet.walletType === 'metamask') {
        return await metaMaskService.getBalance(wallet.address);
      } else if (wallet.walletType === 'polkadot') {
        return await polkadotService.getBalance(wallet.address);
      } else {
        throw new WalletError('UNSUPPORTED_WALLET', `Unsupported wallet type: ${wallet.walletType}`);
      }
    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('BALANCE_FAILED', err.message);
      setError(walletError);
      throw walletError;
    }
  }, [wallet]);

  /**
   * Get network info
   */
  const getNetworkInfo = useCallback(async () => {
    if (!wallet) {
      throw new WalletError('NOT_CONNECTED', 'No wallet connected');
    }

    try {
      if (wallet.walletType === 'metamask') {
        return await metaMaskService.getNetworkInfo();
      } else if (wallet.walletType === 'polkadot') {
        return await polkadotService.getNetworkInfo();
      } else {
        throw new WalletError('UNSUPPORTED_WALLET', `Unsupported wallet type: ${wallet.walletType}`);
      }
    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('NETWORK_INFO_FAILED', err.message);
      setError(walletError);
      throw walletError;
    }
  }, [wallet]);

  /**
   * Load existing wallet connection on mount
   */
  useEffect(() => {
    const loadExistingConnection = async () => {
      try {
        const wallets = await walletService.getUserWallets();
        if (wallets.length > 0) {
          const primaryWallet = wallets.find(w => w.isPrimary) || wallets[0];
          setWallet(primaryWallet);
          setIsConnected(true);
        }
      } catch (err) {
        // Ignore errors when loading existing connections
        console.log('No existing wallet connection found');
      }
    };

    loadExistingConnection();
  }, []);

  /**
   * Set up wallet event listeners
   */
  useEffect(() => {
    if (!wallet) return;

    const cleanupFunctions: (() => void)[] = [];

    if (wallet.walletType === 'metamask') {
      // Listen for account changes
      const cleanupAccounts = metaMaskService.onAccountsChanged((accounts) => {
        if (accounts.length === 0) {
          // User disconnected
          setWallet(null);
          setIsConnected(false);
          emitEvent({
            type: 'disconnect',
            data: wallet,
            timestamp: Date.now(),
          });
        } else {
          // Account changed
          emitEvent({
            type: 'accountChanged',
            data: { accounts },
            timestamp: Date.now(),
          });
        }
      });

      // Listen for chain changes
      const cleanupChain = metaMaskService.onChainChanged((chainId) => {
        emitEvent({
          type: 'chainChanged',
          data: { chainId },
          timestamp: Date.now(),
        });
      });

      cleanupFunctions.push(cleanupAccounts, cleanupChain);
    } else if (wallet.walletType === 'polkadot') {
      // Listen for account changes
      const cleanupAccounts = polkadotService.onAccountsChanged((accounts) => {
        if (accounts.length === 0) {
          // User disconnected
          setWallet(null);
          setIsConnected(false);
          emitEvent({
            type: 'disconnect',
            data: wallet,
            timestamp: Date.now(),
          });
        } else {
          // Account changed
          emitEvent({
            type: 'accountChanged',
            data: { accounts },
            timestamp: Date.now(),
          });
        }
      });

      cleanupFunctions.push(cleanupAccounts);
    }

    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  }, [wallet, emitEvent]);

  return {
    wallet,
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    signMessage,
    signTransaction,
    switchNetwork,
    getBalance,
    getNetworkInfo,
  };
};

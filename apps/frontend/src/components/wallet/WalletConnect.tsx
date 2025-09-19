/**
 * WalletConnect Component
 * 
 * Main component for wallet connection and management
 * providing a unified interface for different wallet types.
 */

import React, { useState, useEffect } from 'react';
import { 
  WalletInfo, 
  SupportedWallet, 
  WalletError,
  WalletConnectionRequest 
} from '../../types/wallet';
import { walletService } from '../../services/wallet/walletService';
import { metaMaskService } from '../../services/wallet/metamaskService';
import { polkadotService } from '../../services/wallet/polkadotService';
import WalletSelector from './WalletSelector';
import WalletStatus from './WalletStatus';
import './WalletConnect.css';

interface WalletConnectProps {
  onConnect?: (wallet: WalletInfo) => void;
  onDisconnect?: () => void;
  onError?: (error: WalletError) => void;
  className?: string;
}

const WalletConnect: React.FC<WalletConnectProps> = ({
  onConnect,
  onDisconnect,
  onError,
  className = ''
}) => {
  const [supportedWallets, setSupportedWallets] = useState<SupportedWallet[]>([]);
  const [connectedWallet, setConnectedWallet] = useState<WalletInfo | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<WalletError | null>(null);
  const [showSelector, setShowSelector] = useState(false);

  /**
   * Load supported wallets on mount
   */
  useEffect(() => {
    const loadSupportedWallets = async () => {
      try {
        const wallets = await walletService.getSupportedWallets();
        setSupportedWallets(wallets);
      } catch (err: any) {
        const walletError = new WalletError('LOAD_FAILED', err.message);
        setError(walletError);
        onError?.(walletError);
      }
    };

    loadSupportedWallets();
  }, [onError]);

  /**
   * Load existing wallet connection
   */
  useEffect(() => {
    const loadExistingConnection = async () => {
      try {
        const wallets = await walletService.getUserWallets();
        if (wallets.length > 0) {
          const primaryWallet = wallets.find(w => w.isPrimary) || wallets[0];
          setConnectedWallet(primaryWallet);
        }
      } catch (err) {
        // Ignore errors when loading existing connections
        console.log('No existing wallet connection found');
      }
    };

    loadExistingConnection();
  }, []);

  /**
   * Handle wallet connection
   */
  const handleConnect = async (walletType: string) => {
    setIsConnecting(true);
    setError(null);
    setShowSelector(false);

    try {
      let address: string;
      let chainId: string;
      let networkName: string;
      let publicKey: string | undefined;

      // Connect to the appropriate wallet service
      if (walletType === 'metamask') {
        if (!metaMaskService.getIsInstalled()) {
          throw new WalletError('METAMASK_NOT_INSTALLED', 'MetaMask is not installed. Please install MetaMask to continue.');
        }

        const accounts = await metaMaskService.connect();
        address = accounts[0];
        chainId = metaMaskService.getChainId() || '1';
        networkName = 'Ethereum Mainnet';
      } else if (walletType === 'polkadot') {
        if (!polkadotService.getIsInstalled()) {
          throw new WalletError('POLKADOT_NOT_INSTALLED', 'Polkadot.js extension is not installed. Please install Polkadot.js to continue.');
        }

        const accounts = await polkadotService.connect();
        address = accounts[0].address;
        chainId = 'polkadot';
        networkName = 'Polkadot';
        publicKey = accounts[0].address;
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

      setConnectedWallet(walletInfo);
      onConnect?.(walletInfo);

    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('CONNECTION_FAILED', err.message);
      setError(walletError);
      onError?.(walletError);
    } finally {
      setIsConnecting(false);
    }
  };

  /**
   * Handle wallet disconnection
   */
  const handleDisconnect = async () => {
    if (!connectedWallet) return;

    try {
      await walletService.disconnectWallet(connectedWallet.id);
      
      // Disconnect from wallet service
      if (connectedWallet.walletType === 'metamask') {
        await metaMaskService.disconnect();
      } else if (connectedWallet.walletType === 'polkadot') {
        await polkadotService.disconnect();
      }

      setConnectedWallet(null);
      onDisconnect?.();

    } catch (err: any) {
      const walletError = err instanceof WalletError ? err : new WalletError('DISCONNECT_FAILED', err.message);
      setError(walletError);
      onError?.(walletError);
    }
  };

  /**
   * Handle wallet selection
   */
  const handleWalletSelect = (walletType: string) => {
    handleConnect(walletType);
  };

  /**
   * Show wallet selector
   */
  const showWalletSelector = () => {
    setShowSelector(true);
    setError(null);
  };

  /**
   * Hide wallet selector
   */
  const hideWalletSelector = () => {
    setShowSelector(false);
  };

  /**
   * Clear error
   */
  const clearError = () => {
    setError(null);
  };

  return (
    <div className={`wallet-connect ${className}`}>
      {error && (
        <div className="wallet-error">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-message">{error.message}</span>
            <button 
              className="error-close" 
              onClick={clearError}
              aria-label="Close error"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {connectedWallet ? (
        <WalletStatus
          wallet={connectedWallet}
          onDisconnect={handleDisconnect}
          onReconnect={() => setShowSelector(true)}
        />
      ) : (
        <div className="wallet-connect-prompt">
          <div className="connect-header">
            <h3>Connect Your Wallet</h3>
            <p>Connect your wallet to access TidyGen ERP features</p>
          </div>
          
          <button
            className="connect-button"
            onClick={showWalletSelector}
            disabled={isConnecting}
          >
            {isConnecting ? (
              <>
                <span className="spinner"></span>
                Connecting...
              </>
            ) : (
              <>
                <span className="wallet-icon">🔗</span>
                Connect Wallet
              </>
            )}
          </button>
        </div>
      )}

      {showSelector && (
        <WalletSelector
          supportedWallets={supportedWallets}
          onSelect={handleWalletSelect}
          onCancel={hideWalletSelector}
          isConnecting={isConnecting}
        />
      )}
    </div>
  );
};

export default WalletConnect;

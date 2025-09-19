/**
 * WalletStatus Component
 * 
 * Component for displaying connected wallet status and information
 * including balance, network, and management options.
 */

import React, { useState, useEffect } from 'react';
import { WalletInfo, WalletError } from '../../types/wallet';
import { walletService } from '../../services/wallet/walletService';
import './WalletStatus.css';

interface WalletStatusProps {
  wallet: WalletInfo;
  onDisconnect: () => void;
  onReconnect: () => void;
}

const WalletStatus: React.FC<WalletStatusProps> = ({
  wallet,
  onDisconnect,
  onReconnect
}) => {
  const [balance, setBalance] = useState<string>('0');
  const [networkInfo, setNetworkInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<WalletError | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  /**
   * Load wallet status information
   */
  useEffect(() => {
    const loadWalletStatus = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const [statusData, accountData] = await Promise.all([
          walletService.getWalletStatus(wallet.id),
          walletService.getWalletAccountInfo(wallet.id)
        ]);

        setBalance(statusData.balance?.balanceEth || '0');
        setNetworkInfo(statusData);
      } catch (err: any) {
        const walletError = err instanceof WalletError ? err : new WalletError('STATUS_FAILED', err.message);
        setError(walletError);
      } finally {
        setIsLoading(false);
      }
    };

    loadWalletStatus();
  }, [wallet.id]);

  /**
   * Get wallet icon
   */
  const getWalletIcon = (walletType: string): string => {
    const icons: Record<string, string> = {
      metamask: '🦊',
      polkadot: '🔴',
      walletconnect: '🔗',
      other: '💼'
    };
    return icons[walletType] || icons.other;
  };

  /**
   * Format address for display
   */
  const formatAddress = (address: string): string => {
    if (address.length > 20) {
      return `${address.slice(0, 6)}...${address.slice(-4)}`;
    }
    return address;
  };

  /**
   * Copy address to clipboard
   */
  const copyAddress = async () => {
    try {
      await navigator.clipboard.writeText(wallet.address);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy address:', err);
    }
  };

  /**
   * Toggle details visibility
   */
  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  /**
   * Handle disconnect
   */
  const handleDisconnect = () => {
    if (window.confirm('Are you sure you want to disconnect this wallet?')) {
      onDisconnect();
    }
  };

  return (
    <div className="wallet-status">
      <div className="status-header">
        <div className="wallet-info">
          <div className="wallet-icon">
            {getWalletIcon(wallet.walletType)}
          </div>
          <div className="wallet-details">
            <div className="wallet-name">
              {wallet.walletType.charAt(0).toUpperCase() + wallet.walletType.slice(1)}
              {wallet.isPrimary && <span className="primary-badge">Primary</span>}
            </div>
            <div className="wallet-address" onClick={copyAddress} title="Click to copy">
              {formatAddress(wallet.address)}
            </div>
          </div>
        </div>
        
        <div className="status-actions">
          <button 
            className="details-button"
            onClick={toggleDetails}
            title="Toggle details"
          >
            {showDetails ? '−' : '+'}
          </button>
          <button 
            className="disconnect-button"
            onClick={handleDisconnect}
            title="Disconnect wallet"
          >
            Disconnect
          </button>
        </div>
      </div>

      {showDetails && (
        <div className="status-details">
          <div className="detail-section">
            <h4>Wallet Information</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{wallet.walletType}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Network:</span>
                <span className="detail-value">{wallet.networkName}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Chain ID:</span>
                <span className="detail-value">{wallet.chainId}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Status:</span>
                <span className={`detail-value status ${wallet.isVerified ? 'verified' : 'unverified'}`}>
                  {wallet.isVerified ? 'Verified' : 'Unverified'}
                </span>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h4>Balance</h4>
            {isLoading ? (
              <div className="balance-loading">
                <span className="spinner"></span>
                Loading balance...
              </div>
            ) : error ? (
              <div className="balance-error">
                <span>⚠️</span>
                Failed to load balance
              </div>
            ) : (
              <div className="balance-info">
                <span className="balance-amount">{balance}</span>
                <span className="balance-currency">
                  {networkInfo?.balance?.currency || 'ETH'}
                </span>
              </div>
            )}
          </div>

          <div className="detail-section">
            <h4>Connection Details</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">Connected:</span>
                <span className="detail-value">
                  {new Date(wallet.createdAt).toLocaleDateString()}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Last Used:</span>
                <span className="detail-value">
                  {new Date(wallet.lastUsed).toLocaleDateString()}
                </span>
              </div>
              {wallet.verifiedAt && (
                <div className="detail-item">
                  <span className="detail-label">Verified:</span>
                  <span className="detail-value">
                    {new Date(wallet.verifiedAt).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="detail-actions">
            <button 
              className="action-button secondary"
              onClick={onReconnect}
            >
              Reconnect
            </button>
            <button 
              className="action-button secondary"
              onClick={copyAddress}
            >
              Copy Address
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="status-error">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error.message}</span>
        </div>
      )}
    </div>
  );
};

export default WalletStatus;

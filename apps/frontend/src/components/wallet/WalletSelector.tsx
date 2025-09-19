/**
 * WalletSelector Component
 * 
 * Component for selecting and connecting to different wallet types
 * including MetaMask and Polkadot.js.
 */

import React from 'react';
import { SupportedWallet } from '../../types/wallet';
import './WalletSelector.css';

interface WalletSelectorProps {
  supportedWallets: SupportedWallet[];
  onSelect: (walletType: string) => void;
  onCancel: () => void;
  isConnecting: boolean;
}

const WalletSelector: React.FC<WalletSelectorProps> = ({
  supportedWallets,
  onSelect,
  onCancel,
  isConnecting
}) => {
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
   * Get wallet description
   */
  const getWalletDescription = (wallet: SupportedWallet): string => {
    if (wallet.type === 'metamask') {
      return 'Connect using MetaMask browser extension';
    } else if (wallet.type === 'polkadot') {
      return 'Connect using Polkadot.js browser extension';
    } else if (wallet.type === 'walletconnect') {
      return 'Connect using WalletConnect protocol';
    }
    return wallet.description;
  };

  /**
   * Check if wallet is available
   */
  const isWalletAvailable = (walletType: string): boolean => {
    if (typeof window === 'undefined') return false;
    
    if (walletType === 'metamask') {
      return !!(window as any).ethereum?.isMetaMask;
    } else if (walletType === 'polkadot') {
      return !!(window as any).injectedWeb3;
    }
    
    return true;
  };

  /**
   * Handle wallet selection
   */
  const handleWalletSelect = (walletType: string) => {
    if (isConnecting) return;
    onSelect(walletType);
  };

  return (
    <div className="wallet-selector-overlay">
      <div className="wallet-selector">
        <div className="selector-header">
          <h3>Select Wallet</h3>
          <button 
            className="close-button" 
            onClick={onCancel}
            disabled={isConnecting}
            aria-label="Close wallet selector"
          >
            ×
          </button>
        </div>

        <div className="selector-content">
          <p className="selector-description">
            Choose a wallet to connect to TidyGen ERP
          </p>

          <div className="wallet-list">
            {supportedWallets.map((wallet) => {
              const isAvailable = isWalletAvailable(wallet.type);
              const isDisabled = !isAvailable || isConnecting;

              return (
                <button
                  key={wallet.type}
                  className={`wallet-option ${isDisabled ? 'disabled' : ''}`}
                  onClick={() => handleWalletSelect(wallet.type)}
                  disabled={isDisabled}
                >
                  <div className="wallet-option-content">
                    <div className="wallet-icon">
                      {getWalletIcon(wallet.type)}
                    </div>
                    <div className="wallet-info">
                      <div className="wallet-name">
                        {wallet.name}
                        {!isAvailable && (
                          <span className="unavailable-badge">Not Available</span>
                        )}
                      </div>
                      <div className="wallet-description">
                        {getWalletDescription(wallet)}
                      </div>
                      <div className="wallet-chains">
                        <span className="chains-label">Supported chains:</span>
                        <span className="chains-list">
                          {wallet.supportedChains.join(', ')}
                        </span>
                      </div>
                    </div>
                    <div className="wallet-arrow">
                      {isConnecting ? (
                        <span className="spinner"></span>
                      ) : (
                        <span>→</span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {supportedWallets.length === 0 && (
            <div className="no-wallets">
              <p>No supported wallets found</p>
            </div>
          )}
        </div>

        <div className="selector-footer">
          <button 
            className="cancel-button"
            onClick={onCancel}
            disabled={isConnecting}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default WalletSelector;

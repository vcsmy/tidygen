/**
 * WalletConnectButton Component
 * 
 * Button to connect/disconnect Polkadot.js wallet
 */

import React, { useState, useEffect } from 'react';
import { Wallet, WalletOff, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { toast } from 'sonner';
import { connectWallet, disconnectWallet, getAccounts, isWalletConnected } from '../../web3/polkadotWallet';
import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

interface WalletConnectButtonProps {
  onAccountSelect?: (account: InjectedAccountWithMeta) => void;
  className?: string;
}

export function WalletConnectButton({ onAccountSelect, className }: WalletConnectButtonProps) {
  const [isConnecting, setIsConnecting] = useState(false);
  const [accounts, setAccounts] = useState<InjectedAccountWithMeta[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<InjectedAccountWithMeta | null>(null);

  useEffect(() => {
    // Check if wallet is already connected
    if (isWalletConnected()) {
      setAccounts(getAccounts());
      if (getAccounts().length > 0) {
        setSelectedAccount(getAccounts()[0]);
      }
    }
  }, []);

  const handleConnect = async () => {
    setIsConnecting(true);
    
    try {
      const connectedAccounts = await connectWallet();
      setAccounts(connectedAccounts);
      
      if (connectedAccounts.length > 0) {
        setSelectedAccount(connectedAccounts[0]);
        if (onAccountSelect) {
          onAccountSelect(connectedAccounts[0]);
        }
        toast.success(`Connected ${connectedAccounts.length} account(s)`);
      }
    } catch (error) {
      console.error('Wallet connection error:', error);
      toast.error(
        error instanceof Error 
          ? error.message 
          : 'Failed to connect wallet. Please install Polkadot.js extension.'
      );
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectWallet();
      setAccounts([]);
      setSelectedAccount(null);
      toast.info('Wallet disconnected');
    } catch (error) {
      console.error('Disconnect error:', error);
      toast.error('Failed to disconnect wallet');
    }
  };

  const handleAccountSelect = (account: InjectedAccountWithMeta) => {
    setSelectedAccount(account);
    if (onAccountSelect) {
      onAccountSelect(account);
    }
    toast.success(`Switched to ${account.meta.name || 'Account'}`);
  };

  // Format address for display
  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-6)}`;
  };

  if (isConnecting) {
    return (
      <Button disabled className={className}>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Connecting...
      </Button>
    );
  }

  if (selectedAccount) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className={className}>
            <Wallet className="mr-2 h-4 w-4" />
            <span className="hidden md:inline">
              {selectedAccount.meta.name || formatAddress(selectedAccount.address)}
            </span>
            <span className="md:hidden">
              {formatAddress(selectedAccount.address)}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64">
          <DropdownMenuLabel>Connected Accounts ({accounts.length})</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {accounts.map((account) => (
            <DropdownMenuItem
              key={account.address}
              onClick={() => handleAccountSelect(account)}
              className="cursor-pointer"
            >
              <div className="flex flex-col">
                <span className="font-medium">{account.meta.name || 'Unnamed'}</span>
                <span className="text-xs text-muted-foreground">
                  {formatAddress(account.address)}
                </span>
              </div>
              {account.address === selectedAccount.address && (
                <span className="ml-auto text-xs text-primary">Selected</span>
              )}
            </DropdownMenuItem>
          ))}
          
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleDisconnect} className="cursor-pointer text-destructive">
            <WalletOff className="mr-2 h-4 w-4" />
            Disconnect
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <Button onClick={handleConnect} className={className}>
      <Wallet className="mr-2 h-4 w-4" />
      Connect Wallet
    </Button>
  );
}

export default WalletConnectButton;


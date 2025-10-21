/**
 * BlockchainDemo Page
 * 
 * Demonstration page for TidyGen blockchain features
 */

import React, { useState, useEffect } from 'react';
import { Link2, Info } from 'lucide-react';
import { WalletConnectButton } from '../components/web3/WalletConnectButton';
import { InvoiceForm } from '../components/web3/InvoiceForm';
import { DAOProposal } from '../components/web3/DAOProposal';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { getChainInfo, getBlockNumber, subscribeToNewBlocks, initializeApi } from '../web3/polkadotWallet';
import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

export function BlockchainDemo() {
  const [selectedAccount, setSelectedAccount] = useState<InjectedAccountWithMeta | null>(null);
  const [chainInfo, setChainInfo] = useState<any>(null);
  const [blockNumber, setBlockNumber] = useState<number>(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize connection to Substrate node
    const initChain = async () => {
      try {
        await initializeApi();
        const info = await getChainInfo();
        const block = await getBlockNumber();
        
        setChainInfo(info);
        setBlockNumber(block);
        setIsConnected(true);
        
        toast.success('Connected to Substrate node', {
          description: `${info.chain} at block #${block}`,
        });
        
        // Subscribe to new blocks
        const unsubscribe = await subscribeToNewBlocks((newBlock) => {
          setBlockNumber(newBlock);
        });
        
        return () => unsubscribe();
      } catch (error) {
        console.error('Failed to connect to Substrate:', error);
        toast.error('Failed to connect to blockchain', {
          description: 'Please ensure Substrate node is running at ws://127.0.0.1:9944',
        });
      }
    };
    
    initChain();
  }, []);

  const handleAccountSelect = (account: InjectedAccountWithMeta) => {
    setSelectedAccount(account);
    toast.info('Account selected', {
      description: account.meta.name || account.address.slice(0, 8) + '...',
    });
  };

  const handleInvoiceSuccess = (txHash: string) => {
    console.log('Invoice submitted successfully:', txHash);
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Link2 className="h-8 w-8" />
            Blockchain Integration Demo
          </h1>
          <p className="text-muted-foreground mt-1">
            Interact with TidyGen Substrate node using Polkadot.js wallet
          </p>
        </div>
        <WalletConnectButton onAccountSelect={handleAccountSelect} />
      </div>

      {/* Connection Status */}
      {chainInfo && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Connected to Blockchain</AlertTitle>
          <AlertDescription className="mt-2 space-y-1">
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Chain: {chainInfo.chain}</Badge>
              <Badge variant="outline">Node: {chainInfo.nodeName}</Badge>
              <Badge variant="outline">Version: {chainInfo.nodeVersion}</Badge>
              <Badge variant="outline">Block: #{blockNumber}</Badge>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Warning if not connected */}
      {!isConnected && (
        <Alert variant="destructive">
          <Info className="h-4 w-4" />
          <AlertTitle>Substrate Node Not Connected</AlertTitle>
          <AlertDescription>
            Please ensure the Substrate node is running:
            <code className="block mt-2 p-2 bg-black/10 rounded">
              cd apps/substrate && make run
            </code>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Invoice Form */}
        <div className="space-y-6">
          <InvoiceForm
            selectedAccount={selectedAccount}
            onSuccess={handleInvoiceSuccess}
          />
          
          {/* Info Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">How It Works</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2 text-muted-foreground">
              <p>
                <strong className="text-foreground">1. Connect Wallet:</strong> Connect your Polkadot.js extension
              </p>
              <p>
                <strong className="text-foreground">2. Create Invoice:</strong> Submit invoices to the blockchain ledger
              </p>
              <p>
                <strong className="text-foreground">3. DAO Voting:</strong> Participate in governance decisions
              </p>
              <p className="text-xs pt-2 border-t">
                All transactions are recorded on-chain for transparency and immutability.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - DAO Proposals */}
        <div className="space-y-6">
          <DAOProposal selectedAccount={selectedAccount} />
        </div>
      </div>

      {/* Selected Account Info */}
      {selectedAccount && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Selected Account</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Name</p>
                <p className="font-medium">{selectedAccount.meta.name || 'Unnamed'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-muted-foreground">Address</p>
                <p className="font-mono text-xs break-all">{selectedAccount.address}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default BlockchainDemo;


/**
 * InvoiceForm Component
 * 
 * Form to create and submit invoices to blockchain
 */

import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { toast } from 'sonner';
import { submitInvoice } from '../../web3/substrateTransactions';
import { getAccounts } from '../../web3/polkadotWallet';
import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

interface InvoiceFormProps {
  onSuccess?: (txHash: string) => void;
  selectedAccount?: InjectedAccountWithMeta | null;
}

export function InvoiceForm({ onSuccess, selectedAccount }: InvoiceFormProps) {
  const [client Address, setClientAddress] = useState('');
  const [amount, setAmount] = useState('');
  const [invoiceNumber, setInvoiceNumber] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!clientAddress || !amount || !invoiceNumber) {
      toast.error('Please fill in all required fields');
      return;
    }

    const account = selectedAccount || getAccounts()[0];
    
    if (!account) {
      toast.error('Please connect your wallet first');
      return;
    }

    setIsSubmitting(true);

    try {
      // Convert amount to smallest unit (assuming 12 decimals)
      const amountInSmallestUnit = Math.floor(parseFloat(amount) * 1_000_000);
      
      // Prepare metadata
      const metadata = `${invoiceNumber}|${description || 'No description'}|Net 30`;
      
      // Submit to blockchain
      const result = await submitInvoice(
        {
          client: clientAddress,
          amount: amountInSmallestUnit,
          metadata,
        },
        account
      );

      if (result.success) {
        toast.success('Invoice submitted to blockchain successfully!', {
          description: `Transaction: ${result.txHash?.slice(0, 10)}...`,
          duration: 5000,
        });
        
        // Reset form
        setClientAddress('');
        setAmount('');
        setInvoiceNumber('');
        setDescription('');
        
        if (onSuccess && result.txHash) {
          onSuccess(result.txHash);
        }
      } else {
        toast.error('Failed to submit invoice', {
          description: result.error || 'Unknown error',
        });
      }
    } catch (error) {
      console.error('Invoice submission error:', error);
      toast.error('Transaction failed', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Send className="h-5 w-5" />
          Create Blockchain Invoice
        </CardTitle>
        <CardDescription>
          Submit an invoice to the Substrate blockchain for tamper-proof storage
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="invoiceNumber">
              Invoice Number <span className="text-destructive">*</span>
            </Label>
            <Input
              id="invoiceNumber"
              placeholder="INV-2025-001"
              value={invoiceNumber}
              onChange={(e) => setInvoiceNumber(e.target.value)}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="clientAddress">
              Client Substrate Address <span className="text-destructive">*</span>
            </Label>
            <Input
              id="clientAddress"
              placeholder="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
              value={clientAddress}
              onChange={(e) => setClientAddress(e.target.value)}
              required
              disabled={isSubmitting}
              className="font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground">
              The client's Substrate account address
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="amount">
              Amount <span className="text-destructive">*</span>
            </Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="1000.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              disabled={isSubmitting}
            />
            <p className="text-xs text-muted-foreground">
              Amount in tokens (will be converted to smallest unit)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="Payment for services rendered in Q4 2025..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isSubmitting}
              rows={3}
            />
          </div>

          {selectedAccount && (
            <div className="rounded-lg bg-muted p-3 text-sm">
              <p className="font-medium">Signing Account:</p>
              <p className="text-muted-foreground font-mono text-xs">
                {selectedAccount.meta.name || 'Account'} ({selectedAccount.address.slice(0, 8)}...{selectedAccount.address.slice(-6)})
              </p>
            </div>
          )}

          <Button
            type="submit"
            disabled={isSubmitting || !selectedAccount}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting to Blockchain...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Submit Invoice to Blockchain
              </>
            )}
          </Button>

          {!selectedAccount && (
            <p className="text-sm text-muted-foreground text-center">
              Please connect your wallet to submit invoices
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}

export default InvoiceForm;


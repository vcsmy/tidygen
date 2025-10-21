/**
 * Substrate Transaction Utilities
 * 
 * Functions for submitting transactions to TidyGen Substrate pallets.
 */

import { ApiPromise } from '@polkadot/api';
import { web3FromAddress } from '@polkadot/extension-dapp';
import type { InjectedAccountWithMeta } from '@polkadot/extension-inject/types';
import { initializeApi } from './polkadotWallet';

export interface InvoiceData {
  client: string;
  amount: number;
  metadata: string;
}

export interface DIDData {
  accountId: string;
  publicKey: string;
  metadata: string;
}

export interface ProposalData {
  title: string;
  description: string;
  votingPeriod?: number;
}

export interface TransactionResult {
  success: boolean;
  txHash?: string;
  blockHash?: string;
  error?: string;
  events?: any[];
}

/**
 * Submit an invoice to the blockchain
 * 
 * @param invoiceData - Invoice data to submit
 * @param account - Account to sign with
 * @returns Transaction result
 */
export async function submitInvoice(
  invoiceData: InvoiceData,
  account: InjectedAccountWithMeta
): Promise<TransactionResult> {
  try {
    console.log('Submitting invoice to blockchain...', invoiceData);
    
    const api = await initializeApi();
    const injector = await web3FromAddress(account.address);
    
    // Create the extrinsic
    const tx = api.tx.ledger.createInvoice(
      invoiceData.client,
      invoiceData.amount,
      invoiceData.metadata
    );
    
    return new Promise((resolve, reject) => {
      tx.signAndSend(
        account.address,
        { signer: injector.signer },
        ({ status, events, dispatchError }) => {
          console.log('Transaction status:', status.type);
          
          if (status.isInBlock) {
            console.log(`Transaction included in block ${status.asInBlock.toHex()}`);
          }
          
          if (status.isFinalized) {
            console.log(`Transaction finalized in block ${status.asFinalized.toHex()}`);
            
            // Check for errors
            if (dispatchError) {
              let errorMessage = 'Transaction failed';
              
              if (dispatchError.isModule) {
                const decoded = api.registry.findMetaError(dispatchError.asModule);
                errorMessage = `${decoded.section}.${decoded.name}: ${decoded.docs}`;
              }
              
              resolve({
                success: false,
                error: errorMessage,
              });
            } else {
              // Success
              const invoiceCreatedEvent = events.find(
                ({ event }) => event.section === 'ledger' && event.method === 'InvoiceCreated'
              );
              
              resolve({
                success: true,
                txHash: status.asFinalized.toHex(),
                blockHash: status.asFinalized.toHex(),
                events: events.map(({ event }) => ({
                  section: event.section,
                  method: event.method,
                  data: event.data.toJSON(),
                })),
              });
            }
          }
        }
      ).catch((error) => {
        console.error('Transaction error:', error);
        reject({
          success: false,
          error: error.message || 'Transaction submission failed',
        });
      });
    });
  } catch (error) {
    console.error('Submit invoice error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Register a DID on the blockchain
 * 
 * @param didData - DID data to register
 * @param account - Account to sign with
 * @returns Transaction result
 */
export async function registerDID(
  didData: DIDData,
  account: InjectedAccountWithMeta
): Promise<TransactionResult> {
  try {
    console.log('Registering DID on blockchain...', didData);
    
    const api = await initializeApi();
    const injector = await web3FromAddress(account.address);
    
    // Convert public key to bytes
    const publicKeyBytes = didData.publicKey.startsWith('0x')
      ? didData.publicKey
      : '0x' + didData.publicKey;
    
    // Create the extrinsic
    const tx = api.tx.did.registerDid(
      didData.accountId,
      publicKeyBytes,
      didData.metadata
    );
    
    return new Promise((resolve, reject) => {
      tx.signAndSend(
        account.address,
        { signer: injector.signer },
        ({ status, events, dispatchError }) => {
          if (status.isFinalized) {
            if (dispatchError) {
              let errorMessage = 'DID registration failed';
              
              if (dispatchError.isModule) {
                const decoded = api.registry.findMetaError(dispatchError.asModule);
                errorMessage = `${decoded.section}.${decoded.name}`;
              }
              
              resolve({ success: false, error: errorMessage });
            } else {
              resolve({
                success: true,
                txHash: status.asFinalized.toHex(),
                blockHash: status.asFinalized.toHex(),
                events: events.map(({ event }) => ({
                  section: event.section,
                  method: event.method,
                  data: event.data.toJSON(),
                })),
              });
            }
          }
        }
      ).catch(reject);
    });
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Create a DAO proposal on the blockchain
 * 
 * @param proposalData - Proposal data
 * @param account - Account to sign with
 * @returns Transaction result
 */
export async function createProposal(
  proposalData: ProposalData,
  account: InjectedAccountWithMeta
): Promise<TransactionResult> {
  try {
    console.log('Creating DAO proposal on blockchain...', proposalData);
    
    const api = await initializeApi();
    const injector = await web3FromAddress(account.address);
    
    // Create the extrinsic
    const tx = api.tx.dao.createProposal(
      proposalData.title,
      proposalData.description,
      proposalData.votingPeriod || null
    );
    
    return new Promise((resolve, reject) => {
      tx.signAndSend(
        account.address,
        { signer: injector.signer },
        ({ status, events, dispatchError }) => {
          if (status.isFinalized) {
            if (dispatchError) {
              let errorMessage = 'Proposal creation failed';
              
              if (dispatchError.isModule) {
                const decoded = api.registry.findMetaError(dispatchError.asModule);
                errorMessage = `${decoded.section}.${decoded.name}`;
              }
              
              resolve({ success: false, error: errorMessage });
            } else {
              resolve({
                success: true,
                txHash: status.asFinalized.toHex(),
                blockHash: status.asFinalized.toHex(),
                events: events.map(({ event }) => ({
                  section: event.section,
                  method: event.method,
                  data: event.data.toJSON(),
                })),
              });
            }
          }
        }
      ).catch(reject);
    });
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Vote on a DAO proposal
 * 
 * @param proposalId - Proposal ID to vote on
 * @param inFavor - true for yes, false for no
 * @param account - Account to sign with
 * @returns Transaction result
 */
export async function voteOnProposal(
  proposalId: number,
  inFavor: boolean,
  account: InjectedAccountWithMeta
): Promise<TransactionResult> {
  try {
    console.log(`Voting on proposal ${proposalId}: ${inFavor ? 'YES' : 'NO'}`);
    
    const api = await initializeApi();
    const injector = await web3FromAddress(account.address);
    
    // Create the extrinsic
    const tx = api.tx.dao.vote(proposalId, inFavor);
    
    return new Promise((resolve, reject) => {
      tx.signAndSend(
        account.address,
        { signer: injector.signer },
        ({ status, events, dispatchError }) => {
          if (status.isFinalized) {
            if (dispatchError) {
              let errorMessage = 'Vote failed';
              
              if (dispatchError.isModule) {
                const decoded = api.registry.findMetaError(dispatchError.asModule);
                errorMessage = `${decoded.section}.${decoded.name}`;
              }
              
              resolve({ success: false, error: errorMessage });
            } else {
              resolve({
                success: true,
                txHash: status.asFinalized.toHex(),
                blockHash: status.asFinalized.toHex(),
                events: events.map(({ event }) => ({
                  section: event.section,
                  method: event.method,
                  data: event.data.toJSON(),
                })),
              });
            }
          }
        }
      ).catch(reject);
    });
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Execute an approved DAO proposal
 * 
 * @param proposalId - Proposal ID to execute
 * @param account - Account to sign with
 * @returns Transaction result
 */
export async function executeProposal(
  proposalId: number,
  account: InjectedAccountWithMeta
): Promise<TransactionResult> {
  try {
    const api = await initializeApi();
    const injector = await web3FromAddress(account.address);
    
    const tx = api.tx.dao.executeProposal(proposalId);
    
    return new Promise((resolve, reject) => {
      tx.signAndSend(
        account.address,
        { signer: injector.signer },
        ({ status, events, dispatchError }) => {
          if (status.isFinalized) {
            if (dispatchError) {
              let errorMessage = 'Execution failed';
              if (dispatchError.isModule) {
                const decoded = api.registry.findMetaError(dispatchError.asModule);
                errorMessage = `${decoded.section}.${decoded.name}`;
              }
              resolve({ success: false, error: errorMessage });
            } else {
              resolve({
                success: true,
                txHash: status.asFinalized.toHex(),
                events: events.map(({ event }) => ({
                  section: event.section,
                  method: event.method,
                  data: event.data.toJSON(),
                })),
              });
            }
          }
        }
      ).catch(reject);
    });
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Query invoices for an account
 */
export async function queryInvoices(accountId: string): Promise<any[]> {
  try {
    const api = await initializeApi();
    const invoices = await api.query.ledger.invoices(accountId);
    return invoices.toJSON() as any[];
  } catch (error) {
    console.error('Query invoices error:', error);
    return [];
  }
}

/**
 * Query DID document for an account via RPC
 */
export async function queryDID(accountId: string): Promise<any | null> {
  try {
    const api = await initializeApi();
    // @ts-ignore - Custom RPC method
    const didDoc = await api.rpc.did.getDid(accountId);
    return didDoc.toJSON();
  } catch (error) {
    console.error('Query DID error:', error);
    return null;
  }
}

/**
 * Query DAO proposal
 */
export async function queryProposal(proposalId: number): Promise<any | null> {
  try {
    const api = await initializeApi();
    const proposal = await api.query.dao.proposals(proposalId);
    return proposal.toJSON();
  } catch (error) {
    console.error('Query proposal error:', error);
    return null;
  }
}

export default {
  submitInvoice,
  registerDID,
  createProposal,
  voteOnProposal,
  executeProposal,
  queryInvoices,
  queryDID,
  queryProposal,
};


"""
DID Registry Sync Service

Handles synchronization between local DID documents and on-chain registries.
"""

import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from web3 import Web3
import json
import time

logger = logging.getLogger(__name__)


class DIDRegistrySyncService:
    """
    Service for synchronizing DID documents with on-chain registries.
    """

    def __init__(self):
        """Initialize the registry sync service."""
        self.web3 = None
        self.registry_contract = None
        self._setup_web3_connection()

    def _setup_web3_connection(self):
        """Setup Web3 connection and registry contract."""
        try:
            # Get Web3 configuration from settings
            web3_config = getattr(settings, 'WEB3_CONFIG', {})
            rpc_url = web3_config.get('RPC_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
            
            # Initialize Web3 connection
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.web3.is_connected():
                logger.warning("Web3 connection failed. Registry sync will be disabled.")
                return
            
            # Registry contract ABI (simplified for DID registry)
            registry_abi = [
                {
                    "inputs": [{"name": "did", "type": "string"}],
                    "name": "resolveDID",
                    "outputs": [{"name": "document", "type": "string"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"name": "did", "type": "string"},
                        {"name": "document", "type": "string"}
                    ],
                    "name": "registerDID",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "did", "type": "string"}],
                    "name": "deactivateDID",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            # Registry contract address (placeholder)
            registry_address = web3_config.get('DID_REGISTRY_ADDRESS', '0x0000000000000000000000000000000000000000')
            
            if registry_address != '0x0000000000000000000000000000000000000000':
                self.registry_contract = self.web3.eth.contract(
                    address=registry_address,
                    abi=registry_abi
                )
                logger.info(f"DID Registry contract initialized at {registry_address}")
            else:
                logger.warning("DID Registry contract address not configured")
                
        except Exception as e:
            logger.error(f"Failed to setup Web3 connection: {e}")
            self.web3 = None
            self.registry_contract = None

    def sync_did_to_registry(self, did_document) -> Dict[str, Any]:
        """
        Sync a DID document to the on-chain registry.
        
        Args:
            did_document: DIDDocument instance to sync
            
        Returns:
            Dict with sync result information
        """
        if not self.registry_contract:
            return {
                'success': False,
                'error': 'Registry contract not available',
                'tx_hash': None
            }
        
        try:
            # Prepare DID document for registration
            document_json = json.dumps(did_document.document)
            
            # Get account for signing transactions
            account = self._get_signing_account()
            if not account:
                return {
                    'success': False,
                    'error': 'No signing account available',
                    'tx_hash': None
                }
            
            # Build transaction
            transaction = self.registry_contract.functions.registerDID(
                did_document.did,
                document_json
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, account.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Update DID document with registry status
                did_document.on_chain_registry_status = 'registered'
                did_document.save()
                
                logger.info(f"DID {did_document.did} successfully registered on-chain")
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'block_number': receipt.blockNumber,
                    'gas_used': receipt.gasUsed
                }
            else:
                return {
                    'success': False,
                    'error': 'Transaction failed',
                    'tx_hash': tx_hash.hex()
                }
                
        except Exception as e:
            logger.error(f"Failed to sync DID {did_document.did} to registry: {e}")
            return {
                'success': False,
                'error': str(e),
                'tx_hash': None
            }

    def sync_did_from_registry(self, did_string: str) -> Dict[str, Any]:
        """
        Sync a DID document from the on-chain registry.
        
        Args:
            did_string: DID string to resolve from registry
            
        Returns:
            Dict with resolved DID document or error
        """
        if not self.registry_contract:
            return {
                'success': False,
                'error': 'Registry contract not available',
                'document': None
            }
        
        try:
            # Call registry contract to resolve DID
            document_json = self.registry_contract.functions.resolveDID(did_string).call()
            
            if document_json:
                document = json.loads(document_json)
                
                return {
                    'success': True,
                    'document': document,
                    'did': did_string
                }
            else:
                return {
                    'success': False,
                    'error': 'DID not found in registry',
                    'document': None
                }
                
        except Exception as e:
            logger.error(f"Failed to resolve DID {did_string} from registry: {e}")
            return {
                'success': False,
                'error': str(e),
                'document': None
            }

    def deactivate_did_on_registry(self, did_document) -> Dict[str, Any]:
        """
        Deactivate a DID on the on-chain registry.
        
        Args:
            did_document: DIDDocument instance to deactivate
            
        Returns:
            Dict with deactivation result
        """
        if not self.registry_contract:
            return {
                'success': False,
                'error': 'Registry contract not available',
                'tx_hash': None
            }
        
        try:
            # Get account for signing transactions
            account = self._get_signing_account()
            if not account:
                return {
                    'success': False,
                    'error': 'No signing account available',
                    'tx_hash': None
                }
            
            # Build transaction
            transaction = self.registry_contract.functions.deactivateDID(
                did_document.did
            ).build_transaction({
                'from': account.address,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, account.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Update DID document status
                did_document.status = 'deactivated'
                did_document.on_chain_registry_status = 'deactivated'
                did_document.save()
                
                logger.info(f"DID {did_document.did} successfully deactivated on-chain")
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'block_number': receipt.blockNumber
                }
            else:
                return {
                    'success': False,
                    'error': 'Transaction failed',
                    'tx_hash': tx_hash.hex()
                }
                
        except Exception as e:
            logger.error(f"Failed to deactivate DID {did_document.did} on registry: {e}")
            return {
                'success': False,
                'error': str(e),
                'tx_hash': None
            }

    def batch_sync_dids(self, did_documents: List) -> Dict[str, Any]:
        """
        Batch sync multiple DID documents to the registry.
        
        Args:
            did_documents: List of DIDDocument instances
            
        Returns:
            Dict with batch sync results
        """
        results = {
            'total': len(did_documents),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for did_doc in did_documents:
            result = self.sync_did_to_registry(did_doc)
            results['details'].append({
                'did': did_doc.did,
                'result': result
            })
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Batch sync completed: {results['successful']}/{results['total']} successful")
        return results

    def get_registry_status(self, did_string: str) -> Dict[str, Any]:
        """
        Get the registry status of a DID.
        
        Args:
            did_string: DID string to check
            
        Returns:
            Dict with registry status information
        """
        if not self.registry_contract:
            return {
                'success': False,
                'error': 'Registry contract not available',
                'status': 'unknown'
            }
        
        try:
            # Try to resolve the DID from registry
            result = self.sync_did_from_registry(did_string)
            
            if result['success']:
                return {
                    'success': True,
                    'status': 'registered',
                    'document': result['document']
                }
            else:
                return {
                    'success': True,
                    'status': 'not_registered',
                    'error': result['error']
                }
                
        except Exception as e:
            logger.error(f"Failed to get registry status for DID {did_string}: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'unknown'
            }

    def _get_signing_account(self):
        """Get the account for signing transactions."""
        try:
            web3_config = getattr(settings, 'WEB3_CONFIG', {})
            private_key = web3_config.get('PRIVATE_KEY')
            
            if not private_key:
                logger.warning("No private key configured for registry transactions")
                return None
            
            # Create account from private key
            account = self.web3.eth.account.from_key(private_key)
            return account
            
        except Exception as e:
            logger.error(f"Failed to get signing account: {e}")
            return None

    def is_registry_available(self) -> bool:
        """Check if the registry is available."""
        return self.web3 is not None and self.registry_contract is not None

    def get_network_info(self) -> Dict[str, Any]:
        """Get information about the connected network."""
        if not self.web3:
            return {'connected': False}
        
        try:
            return {
                'connected': True,
                'chain_id': self.web3.eth.chain_id,
                'latest_block': self.web3.eth.block_number,
                'gas_price': self.web3.eth.gas_price,
                'registry_available': self.is_registry_available()
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {'connected': False, 'error': str(e)}

"""
DID Blockchain Service

Service for blockchain integration with DID operations.
"""

import json
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import DIDDocument, DIDCredential
from .registry_sync_service import DIDRegistrySyncService


class DIDBlockchainService:
    """
    Service for blockchain integration with DID operations.
    """

    def __init__(self, network: str = "ethereum"):
        """
        Initialize the blockchain service.
        
        Args:
            network: The blockchain network to use
        """
        self.network = network
        self.config = self._get_network_config(network)
        self.registry_sync = DIDRegistrySyncService()

    def _get_network_config(self, network: str) -> Dict[str, Any]:
        """
        Get configuration for the specified network.
        
        Args:
            network: The blockchain network
            
        Returns:
            Network configuration dictionary
        """
        configs = {
            "ethereum": {
                "chain_id": 1,
                "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                "contract_address": "0x...",  # DID Registry contract address
                "gas_limit": 200000,
                "gas_price": "20000000000"  # 20 gwei
            },
            "polygon": {
                "chain_id": 137,
                "rpc_url": "https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID",
                "contract_address": "0x...",
                "gas_limit": 200000,
                "gas_price": "30000000000"  # 30 gwei
            },
            "testnet": {
                "chain_id": 5,  # Goerli
                "rpc_url": "https://goerli.infura.io/v3/YOUR_PROJECT_ID",
                "contract_address": "0x...",
                "gas_limit": 200000,
                "gas_price": "10000000000"  # 10 gwei
            }
        }
        
        return configs.get(network, configs["testnet"])

    def store_did_on_chain(
        self,
        did_doc: DIDDocument
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Store a DID document on the blockchain.
        
        Args:
            did_doc: The DID document to store
            
        Returns:
            Tuple of (success, error_message, transaction_info)
        """
        try:
            # In a real implementation, you would:
            # 1. Connect to the blockchain network
            # 2. Deploy or interact with a DID Registry smart contract
            # 3. Store the DID document hash on-chain
            # 4. Return transaction details
            
            # For now, we'll simulate the transaction
            tx_hash = f"0x{''.join([f'{i:02x}' for i in range(32)])}"
            block_number = 12345678
            
            # Update the DID document with on-chain information
            did_doc.on_chain_tx_hash = tx_hash
            did_doc.on_chain_block_number = block_number
            did_doc.save()
            
            transaction_info = {
                "tx_hash": tx_hash,
                "block_number": block_number,
                "network": self.network,
                "timestamp": timezone.now().isoformat()
            }
            
            return True, None, transaction_info
            
        except Exception as e:
            return False, str(e), None

    def store_credential_on_chain(
        self,
        credential: DIDCredential
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Store a credential hash on the blockchain.
        
        Args:
            credential: The credential to store
            
        Returns:
            Tuple of (success, error_message, transaction_info)
        """
        try:
            # In a real implementation, you would:
            # 1. Hash the credential data
            # 2. Store the hash on-chain
            # 3. Return transaction details
            
            # For now, we'll simulate the transaction
            tx_hash = f"0x{''.join([f'{i:02x}' for i in range(32)])}"
            block_number = 12345679
            
            # Update the credential with on-chain information
            credential.on_chain_tx_hash = tx_hash
            credential.save()
            
            transaction_info = {
                "tx_hash": tx_hash,
                "block_number": block_number,
                "network": self.network,
                "timestamp": timezone.now().isoformat()
            }
            
            return True, None, transaction_info
            
        except Exception as e:
            return False, str(e), None

    def verify_did_on_chain(
        self,
        did: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Verify a DID document on the blockchain.
        
        Args:
            did: The DID to verify
            
        Returns:
            Tuple of (is_valid, error_message, verification_info)
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            if not did_doc.on_chain_tx_hash:
                return False, "DID not stored on-chain", None
            
            # In a real implementation, you would:
            # 1. Query the blockchain for the DID document
            # 2. Verify the hash matches
            # 3. Check the transaction is confirmed
            
            # For now, we'll simulate verification
            verification_info = {
                "did": did,
                "tx_hash": did_doc.on_chain_tx_hash,
                "block_number": did_doc.on_chain_block_number,
                "verified": True,
                "timestamp": timezone.now().isoformat()
            }
            
            return True, None, verification_info
            
        except DIDDocument.DoesNotExist:
            return False, "DID not found", None

    def revoke_did_on_chain(
        self,
        did: str,
        revoked_by: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Revoke a DID on the blockchain.
        
        Args:
            did: The DID to revoke
            revoked_by: The DID revoking the document
            
        Returns:
            Tuple of (success, error_message, transaction_info)
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            # In a real implementation, you would:
            # 1. Call the revoke function on the smart contract
            # 2. Update the on-chain registry
            # 3. Return transaction details
            
            # For now, we'll simulate the transaction
            tx_hash = f"0x{''.join([f'{i:02x}' for i in range(32)])}"
            block_number = 12345680
            
            # Update the DID document
            did_doc.status = 'revoked'
            did_doc.on_chain_tx_hash = tx_hash
            did_doc.on_chain_block_number = block_number
            did_doc.save()
            
            transaction_info = {
                "tx_hash": tx_hash,
                "block_number": block_number,
                "network": self.network,
                "revoked_by": revoked_by,
                "timestamp": timezone.now().isoformat()
            }
            
            return True, None, transaction_info
            
        except DIDDocument.DoesNotExist:
            return False, "DID not found", None

    def get_did_from_chain(
        self,
        did: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Retrieve a DID document from the blockchain.
        
        Args:
            did: The DID to retrieve
            
        Returns:
            Tuple of (success, error_message, did_document)
        """
        try:
            # In a real implementation, you would:
            # 1. Query the smart contract for the DID document
            # 2. Parse and return the document
            
            # For now, we'll return a placeholder
            did_document = {
                "did": did,
                "document": {
                    "@context": "https://www.w3.org/ns/did/v1",
                    "id": did,
                    "verificationMethod": []
                },
                "network": self.network,
                "timestamp": timezone.now().isoformat()
            }
            
            return True, None, did_document
            
        except Exception as e:
            return False, str(e), None

    def sync_did_with_chain(
        self,
        did: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Sync a DID document between database and blockchain.
        
        Args:
            did: The DID to sync
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            # Check if DID is already on-chain
            if did_doc.on_chain_tx_hash:
                # Verify on-chain version
                success, error, verification_info = self.verify_did_on_chain(did)
                if not success:
                    return False, f"Verification failed: {error}"
            else:
                # Store on-chain
                success, error, tx_info = self.store_did_on_chain(did_doc)
                if not success:
                    return False, f"Storage failed: {error}"
            
            return True, None
            
        except DIDDocument.DoesNotExist:
            return False, "DID not found"

    def get_network_status(self) -> Dict[str, Any]:
        """
        Get the status of the blockchain network.
        
        Returns:
            Network status information
        """
        # In a real implementation, you would:
        # 1. Check network connectivity
        # 2. Get latest block number
        # 3. Check gas prices
        # 4. Verify contract deployment
        
        return {
            "network": self.network,
            "chain_id": self.config["chain_id"],
            "status": "connected",
            "latest_block": 12345678,
            "gas_price": self.config["gas_price"],
            "contract_deployed": True,
            "timestamp": timezone.now().isoformat()
        }

    def estimate_gas_cost(
        self,
        operation: str,
        data_size: int = 0
    ) -> Dict[str, Any]:
        """
        Estimate gas cost for a blockchain operation.
        
        Args:
            operation: The operation type
            data_size: Size of data to be stored
            
        Returns:
            Gas cost estimation
        """
        base_costs = {
            "store_did": 100000,
            "update_did": 80000,
            "revoke_did": 60000,
            "store_credential": 50000
        }
        
        base_cost = base_costs.get(operation, 50000)
        data_cost = data_size * 100  # 100 gas per byte
        total_gas = base_cost + data_cost
        
        gas_price = int(self.config["gas_price"])
        total_cost_wei = total_gas * gas_price
        total_cost_eth = total_cost_wei / 1e18
        
        return {
            "operation": operation,
            "estimated_gas": total_gas,
            "gas_price_wei": gas_price,
            "total_cost_wei": total_cost_wei,
            "total_cost_eth": total_cost_eth,
            "network": self.network
        }

    def sync_did_to_registry(self, did_document: DIDDocument) -> Dict[str, Any]:
        """
        Sync a DID document to the on-chain registry.
        
        Args:
            did_document: DIDDocument instance to sync
            
        Returns:
            Dict with sync result information
        """
        return self.registry_sync.sync_did_to_registry(did_document)

    def sync_did_from_registry(self, did_string: str) -> Dict[str, Any]:
        """
        Sync a DID document from the on-chain registry.
        
        Args:
            did_string: DID string to resolve from registry
            
        Returns:
            Dict with resolved DID document or error
        """
        return self.registry_sync.sync_did_from_registry(did_string)

    def deactivate_did_on_registry(self, did_document: DIDDocument) -> Dict[str, Any]:
        """
        Deactivate a DID on the on-chain registry.
        
        Args:
            did_document: DIDDocument instance to deactivate
            
        Returns:
            Dict with deactivation result
        """
        return self.registry_sync.deactivate_did_on_registry(did_document)

    def get_registry_status(self, did_string: str) -> Dict[str, Any]:
        """
        Get the registry status of a DID.
        
        Args:
            did_string: DID string to check
            
        Returns:
            Dict with registry status information
        """
        return self.registry_sync.get_registry_status(did_string)

    def is_registry_available(self) -> bool:
        """Check if the registry is available."""
        return self.registry_sync.is_registry_available()

    def get_network_info(self) -> Dict[str, Any]:
        """Get information about the connected network."""
        return self.registry_sync.get_network_info()

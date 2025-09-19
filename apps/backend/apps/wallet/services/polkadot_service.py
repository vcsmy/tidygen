"""
Polkadot Service for Wallet Integration

This module provides services for integrating with Polkadot.js wallets,
including connection management, signature requests, and Substrate transaction handling.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone

from .signature_service import SignatureService

logger = logging.getLogger(__name__)


class PolkadotService:
    """
    Service for Polkadot.js wallet integration.
    
    This service provides methods for connecting to Polkadot.js wallets,
    requesting signatures, and handling Substrate transactions.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialize Polkadot service.
        
        Args:
            rpc_url: RPC URL for Substrate network connection
        """
        self.rpc_url = rpc_url or getattr(settings, 'SUBSTRATE_RPC_URL', 'ws://localhost:9944')
        self.substrate = None
        self._initialize_substrate()
    
    def _initialize_substrate(self):
        """Initialize Substrate connection."""
        try:
            # Try to import substrate-interface
            try:
                from substrateinterface import SubstrateInterface
                self.substrate = SubstrateInterface(url=self.rpc_url)
                logger.info(f"Connected to Substrate network: {self.rpc_url}")
            except ImportError:
                logger.warning("substrate-interface not available, using mock connection")
                self.substrate = MockSubstrateInterface(self.rpc_url)
        except Exception as e:
            logger.error(f"Failed to initialize Substrate: {e}")
            self.substrate = MockSubstrateInterface(self.rpc_url)
    
    def is_connected(self) -> bool:
        """
        Check if connected to Substrate network.
        
        Returns:
            True if connected, False otherwise
        """
        return self.substrate is not None and hasattr(self.substrate, 'connected')
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get current network information.
        
        Returns:
            Dictionary with network information
        """
        if not self.is_connected():
            return {"error": "Not connected to network"}
        
        try:
            # Get chain properties
            chain_properties = self.substrate.get_chain_properties()
            chain_name = self.substrate.get_chain_name()
            chain_version = self.substrate.get_chain_version()
            
            return {
                "chain_name": chain_name,
                "chain_version": chain_version,
                "chain_properties": chain_properties,
                "connected": True,
                "rpc_url": self.rpc_url
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {"error": str(e)}
    
    def validate_address(self, address: str) -> bool:
        """
        Validate a Substrate address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if address is valid, False otherwise
        """
        try:
            # Basic validation for Substrate addresses
            if not address or len(address) < 40:
                return False
            
            # Check if it's a valid SS58 address
            # This is a simplified check - in production, use proper SS58 validation
            return True
        except Exception as e:
            logger.error(f"Failed to validate address {address}: {e}")
            return False
    
    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """
        Get the balance of an address.
        
        Args:
            address: Address to check balance for
            
        Returns:
            Dictionary with balance information
        """
        if not self.validate_address(address):
            return {"error": "Invalid address"}
        
        try:
            # Get account info from Substrate
            account_info = self.substrate.query('System', 'Account', [address])
            
            if account_info:
                balance = account_info.value['data']['free']
                reserved = account_info.value['data']['reserved']
                frozen = account_info.value['data']['frozen']
                
                return {
                    "address": address,
                    "balance": str(balance),
                    "reserved": str(reserved),
                    "frozen": str(frozen),
                    "available": str(balance - frozen),
                    "currency": "DOT"  # or KSM for Kusama
                }
            else:
                return {
                    "address": address,
                    "balance": "0",
                    "reserved": "0",
                    "frozen": "0",
                    "available": "0",
                    "currency": "DOT"
                }
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return {"error": str(e)}
    
    def request_accounts(self) -> List[str]:
        """
        Request accounts from Polkadot.js.
        
        Returns:
            List of connected account addresses
        """
        # This would typically be called from the frontend
        # For backend service, we return empty list
        return []
    
    def request_signature(
        self,
        address: str,
        message: str,
        nonce: str,
        timestamp: int
    ) -> Dict[str, Any]:
        """
        Request a signature from Polkadot.js.
        
        Args:
            address: Wallet address
            message: Message to sign
            nonce: Random nonce
            timestamp: Unix timestamp
            
        Returns:
            Dictionary with signature request details
        """
        if not self.validate_address(address):
            return {"error": "Invalid address"}
        
        # Generate the authentication message
        auth_message = SignatureService.generate_authentication_message(
            address=address,
            nonce=nonce,
            timestamp=timestamp
        )
        
        return {
            "address": address,
            "message": auth_message,
            "nonce": nonce,
            "timestamp": timestamp,
            "chain_name": self.get_network_info().get("chain_name", "Unknown"),
            "network_type": "substrate"
        }
    
    def verify_signature(
        self,
        address: str,
        message: str,
        signature: str,
        public_key: Optional[str] = None
    ) -> bool:
        """
        Verify a Polkadot.js signature.
        
        Args:
            address: Wallet address
            message: Original message
            signature: Signature to verify
            public_key: Optional public key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        return SignatureService.verify_substrate_signature(
            message=message,
            signature=signature,
            address=address,
            public_key=public_key
        )
    
    def prepare_transaction(
        self,
        to_address: str,
        value: str,
        call_data: str = "",
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Prepare a transaction for signing.
        
        Args:
            to_address: Recipient address
            value: Amount to send
            call_data: Transaction call data
            nonce: Transaction nonce
            
        Returns:
            Dictionary with transaction details
        """
        if not self.validate_address(to_address):
            return {"error": "Invalid recipient address"}
        
        try:
            # Get account nonce if not provided
            if nonce is None:
                account_info = self.substrate.query('System', 'Account', [to_address])
                nonce = account_info.value['nonce'] if account_info else 0
            
            transaction = {
                "to": to_address,
                "value": value,
                "data": call_data,
                "nonce": nonce,
                "chain": self.get_network_info().get("chain_name", "Unknown")
            }
            
            return {
                "transaction": transaction,
                "nonce": nonce,
                "estimated_fee": "0.01"  # Simplified fee estimation
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare transaction: {e}")
            return {"error": str(e)}
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get the status of a transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dictionary with transaction status
        """
        try:
            # Get transaction from Substrate
            tx_info = self.substrate.get_block(tx_hash)
            
            if tx_info:
                return {
                    "tx_hash": tx_hash,
                    "status": "success",
                    "block_number": tx_info['header']['number'],
                    "timestamp": tx_info['header']['timestamp']
                }
            else:
                return {
                    "tx_hash": tx_hash,
                    "status": "pending"
                }
        except Exception as e:
            logger.error(f"Failed to get transaction status for {tx_hash}: {e}")
            return {"error": str(e)}
    
    def get_supported_networks(self) -> List[Dict[str, Any]]:
        """
        Get list of supported networks.
        
        Returns:
            List of supported network configurations
        """
        return [
            {
                "chain_id": "polkadot",
                "name": "Polkadot",
                "rpc_url": "wss://rpc.polkadot.io",
                "block_explorer": "https://polkadot.subscan.io",
                "currency": "DOT",
                "decimals": 10
            },
            {
                "chain_id": "kusama",
                "name": "Kusama",
                "rpc_url": "wss://kusama-rpc.polkadot.io",
                "block_explorer": "https://kusama.subscan.io",
                "currency": "KSM",
                "decimals": 12
            },
            {
                "chain_id": "westend",
                "name": "Westend Testnet",
                "rpc_url": "wss://westend-rpc.polkadot.io",
                "block_explorer": "https://westend.subscan.io",
                "currency": "WND",
                "decimals": 12
            },
            {
                "chain_id": "rococo",
                "name": "Rococo Testnet",
                "rpc_url": "wss://rococo-rpc.polkadot.io",
                "block_explorer": "https://rococo.subscan.io",
                "currency": "ROC",
                "decimals": 12
            }
        ]
    
    def switch_network(self, chain_id: str) -> Dict[str, Any]:
        """
        Request Polkadot.js to switch to a different network.
        
        Args:
            chain_id: Target chain ID
            
        Returns:
            Dictionary with network switch request details
        """
        supported_networks = self.get_supported_networks()
        target_network = next(
            (net for net in supported_networks if net["chain_id"] == chain_id),
            None
        )
        
        if not target_network:
            return {"error": f"Unsupported network: {chain_id}"}
        
        return {
            "chain_id": chain_id,
            "network_name": target_network["name"],
            "rpc_url": target_network["rpc_url"],
            "block_explorer": target_network["block_explorer"],
            "currency": target_network["currency"],
            "decimals": target_network["decimals"]
        }
    
    def get_account_info(self, address: str) -> Dict[str, Any]:
        """
        Get comprehensive account information.
        
        Args:
            address: Account address
            
        Returns:
            Dictionary with account information
        """
        if not self.validate_address(address):
            return {"error": "Invalid address"}
        
        try:
            balance_info = self.get_address_balance(address)
            network_info = self.get_network_info()
            
            return {
                "address": address,
                "balance": balance_info,
                "network": network_info,
                "wallet_type": "polkadot",
                "validated": True
            }
        except Exception as e:
            logger.error(f"Failed to get account info for {address}: {e}")
            return {"error": str(e)}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get chain metadata.
        
        Returns:
            Dictionary with chain metadata
        """
        try:
            if not self.is_connected():
                return {"error": "Not connected to network"}
            
            metadata = self.substrate.get_metadata()
            
            return {
                "metadata_version": metadata.version,
                "modules": list(metadata.modules.keys()),
                "extrinsic_version": metadata.extrinsic_version
            }
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return {"error": str(e)}


class MockSubstrateInterface:
    """Mock Substrate interface for development and testing."""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.connected = True
    
    def get_chain_properties(self):
        """Mock chain properties."""
        return {
            "ss58Format": 0,
            "tokenDecimals": 10,
            "tokenSymbol": "DOT"
        }
    
    def get_chain_name(self):
        """Mock chain name."""
        return "Polkadot"
    
    def get_chain_version(self):
        """Mock chain version."""
        return "0.9.0"
    
    def query(self, module: str, function: str, params: list):
        """Mock query response."""
        if module == "System" and function == "Account":
            return MockAccountInfo()
        return None
    
    def get_block(self, block_hash: str):
        """Mock block info."""
        return {
            "header": {
                "number": 12345,
                "timestamp": int(timezone.now().timestamp())
            }
        }
    
    def get_metadata(self):
        """Mock metadata."""
        return MockMetadata()


class MockAccountInfo:
    """Mock account info for testing."""
    
    def __init__(self):
        self.value = {
            "data": {
                "free": 1000000000000,  # 1 DOT
                "reserved": 0,
                "frozen": 0
            },
            "nonce": 0
        }


class MockMetadata:
    """Mock metadata for testing."""
    
    def __init__(self):
        self.version = "0.9.0"
        self.modules = {
            "System": {},
            "Balances": {},
            "Timestamp": {}
        }
        self.extrinsic_version = 4

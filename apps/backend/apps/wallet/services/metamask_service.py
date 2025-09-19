"""
MetaMask Service for Wallet Integration

This module provides services for integrating with MetaMask wallets,
including connection management, signature requests, and transaction handling.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
# Try to import optional dependencies
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

try:
    from eth_account import Account
    ETH_ACCOUNT_AVAILABLE = True
except ImportError:
    ETH_ACCOUNT_AVAILABLE = False

from .signature_service import SignatureService

logger = logging.getLogger(__name__)


class MetaMaskService:
    """
    Service for MetaMask wallet integration.
    
    This service provides methods for connecting to MetaMask wallets,
    requesting signatures, and handling Ethereum-compatible transactions.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialize MetaMask service.
        
        Args:
            rpc_url: RPC URL for Ethereum network connection
        """
        self.rpc_url = rpc_url or getattr(settings, 'ETHEREUM_RPC_URL', 'http://localhost:8545')
        self.web3 = None
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection."""
        if not WEB3_AVAILABLE:
            logger.warning("web3 not available, using mock connection")
            self.web3 = MockWeb3(self.rpc_url)
            return
        
        try:
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if self.web3.is_connected():
                logger.info(f"Connected to Ethereum network: {self.rpc_url}")
            else:
                logger.warning(f"Failed to connect to Ethereum network: {self.rpc_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
            self.web3 = MockWeb3(self.rpc_url)
    
    def is_connected(self) -> bool:
        """
        Check if connected to Ethereum network.
        
        Returns:
            True if connected, False otherwise
        """
        return self.web3 is not None and self.web3.is_connected()
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get current network information.
        
        Returns:
            Dictionary with network information
        """
        if not self.is_connected():
            return {"error": "Not connected to network"}
        
        try:
            chain_id = self.web3.eth.chain_id
            block_number = self.web3.eth.block_number
            gas_price = self.web3.eth.gas_price
            
            # Map chain IDs to network names
            network_names = {
                1: "Ethereum Mainnet",
                3: "Ropsten Testnet",
                4: "Rinkeby Testnet",
                5: "Goerli Testnet",
                42: "Kovan Testnet",
                137: "Polygon Mainnet",
                80001: "Polygon Mumbai Testnet",
                56: "BSC Mainnet",
                97: "BSC Testnet",
            }
            
            return {
                "chain_id": chain_id,
                "network_name": network_names.get(chain_id, f"Unknown Network ({chain_id})"),
                "block_number": block_number,
                "gas_price": gas_price,
                "connected": True
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {"error": str(e)}
    
    def validate_address(self, address: str) -> bool:
        """
        Validate an Ethereum address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if address is valid, False otherwise
        """
        try:
            return self.web3.is_address(address) and self.web3.is_checksum_address(address)
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
            balance_wei = self.web3.eth.get_balance(address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            
            return {
                "address": address,
                "balance_wei": str(balance_wei),
                "balance_eth": str(balance_eth),
                "currency": "ETH"
            }
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return {"error": str(e)}
    
    def request_accounts(self) -> List[str]:
        """
        Request accounts from MetaMask.
        
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
        Request a signature from MetaMask.
        
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
            "chain_id": self.web3.eth.chain_id if self.is_connected() else None,
            "network_name": self.get_network_info().get("network_name", "Unknown")
        }
    
    def verify_signature(
        self,
        address: str,
        message: str,
        signature: str
    ) -> bool:
        """
        Verify a MetaMask signature.
        
        Args:
            address: Wallet address
            message: Original message
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        return SignatureService.verify_ethereum_signature(
            message=message,
            signature=signature,
            address=address
        )
    
    def prepare_transaction(
        self,
        to_address: str,
        value: str,
        data: str = "",
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Prepare a transaction for signing.
        
        Args:
            to_address: Recipient address
            value: Amount to send (in wei)
            data: Transaction data
            gas_limit: Gas limit
            gas_price: Gas price
            
        Returns:
            Dictionary with transaction details
        """
        if not self.validate_address(to_address):
            return {"error": "Invalid recipient address"}
        
        try:
            # Get current gas price if not provided
            if gas_price is None:
                gas_price = self.web3.eth.gas_price
            
            # Estimate gas limit if not provided
            if gas_limit is None:
                gas_limit = self.web3.eth.estimate_gas({
                    'to': to_address,
                    'value': int(value),
                    'data': data
                })
            
            transaction = {
                "to": to_address,
                "value": int(value),
                "data": data,
                "gas": gas_limit,
                "gasPrice": gas_price,
                "chainId": self.web3.eth.chain_id
            }
            
            return {
                "transaction": transaction,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "estimated_cost": gas_limit * gas_price
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
            tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "tx_hash": tx_hash,
                "status": "success" if tx_receipt.status == 1 else "failed",
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "effective_gas_price": tx_receipt.effectiveGasPrice,
                "logs": [dict(log) for log in tx_receipt.logs]
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
                "chain_id": 1,
                "name": "Ethereum Mainnet",
                "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                "block_explorer": "https://etherscan.io",
                "currency": "ETH"
            },
            {
                "chain_id": 5,
                "name": "Goerli Testnet",
                "rpc_url": "https://goerli.infura.io/v3/YOUR_PROJECT_ID",
                "block_explorer": "https://goerli.etherscan.io",
                "currency": "ETH"
            },
            {
                "chain_id": 137,
                "name": "Polygon Mainnet",
                "rpc_url": "https://polygon-rpc.com",
                "block_explorer": "https://polygonscan.com",
                "currency": "MATIC"
            },
            {
                "chain_id": 80001,
                "name": "Polygon Mumbai Testnet",
                "rpc_url": "https://rpc-mumbai.maticvigil.com",
                "block_explorer": "https://mumbai.polygonscan.com",
                "currency": "MATIC"
            },
            {
                "chain_id": 56,
                "name": "BSC Mainnet",
                "rpc_url": "https://bsc-dataseed.binance.org",
                "block_explorer": "https://bscscan.com",
                "currency": "BNB"
            },
            {
                "chain_id": 97,
                "name": "BSC Testnet",
                "rpc_url": "https://data-seed-prebsc-1-s1.binance.org:8545",
                "block_explorer": "https://testnet.bscscan.com",
                "currency": "BNB"
            }
        ]
    
    def switch_network(self, chain_id: int) -> Dict[str, Any]:
        """
        Request MetaMask to switch to a different network.
        
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
            "currency": target_network["currency"]
        }
    
    def add_network(self, network_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request MetaMask to add a new network.
        
        Args:
            network_config: Network configuration
            
        Returns:
            Dictionary with network addition request details
        """
        required_fields = ["chain_id", "name", "rpc_url", "currency"]
        
        for field in required_fields:
            if field not in network_config:
                return {"error": f"Missing required field: {field}"}
        
        return {
            "chain_id": network_config["chain_id"],
            "chain_name": network_config["name"],
            "rpc_urls": [network_config["rpc_url"]],
            "block_explorer_urls": [network_config.get("block_explorer", "")],
            "native_currency": {
                "name": network_config["currency"],
                "symbol": network_config["currency"],
                "decimals": 18
            }
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
                "wallet_type": "metamask",
                "validated": True
            }
        except Exception as e:
            logger.error(f"Failed to get account info for {address}: {e}")
            return {"error": str(e)}


class MockWeb3:
    """Mock Web3 interface for development and testing."""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.connected = True
    
    def is_connected(self):
        """Mock connection status."""
        return True
    
    def is_address(self, address: str):
        """Mock address validation."""
        return address.startswith('0x') and len(address) == 42
    
    def is_checksum_address(self, address: str):
        """Mock checksum validation."""
        return self.is_address(address)
    
    def from_wei(self, value, unit):
        """Mock wei conversion."""
        return value / (10 ** 18)  # Simple ETH conversion
    
    @property
    def eth(self):
        """Mock eth property."""
        return MockEth()


class MockEth:
    """Mock Ethereum interface."""
    
    def __init__(self):
        self.chain_id = 1
        self.block_number = 12345
        self.gas_price = 20000000000  # 20 gwei
    
    def get_balance(self, address: str):
        """Mock balance retrieval."""
        return 1000000000000000000  # 1 ETH in wei
    
    def get_transaction_receipt(self, tx_hash: str):
        """Mock transaction receipt."""
        return MockTransactionReceipt()
    
    def estimate_gas(self, transaction: dict):
        """Mock gas estimation."""
        return 21000  # Standard transfer gas
    
    def get_transaction(self, tx_hash: str):
        """Mock transaction retrieval."""
        return MockTransaction()


class MockTransactionReceipt:
    """Mock transaction receipt."""
    
    def __init__(self):
        self.status = 1
        self.blockNumber = 12345
        self.gasUsed = 21000
        self.effectiveGasPrice = 20000000000
        self.logs = []


class MockTransaction:
    """Mock transaction."""
    
    def __init__(self):
        self.hash = "0x1234567890abcdef"
        self.blockNumber = 12345
        self.gas = 21000
        self.gasPrice = 20000000000

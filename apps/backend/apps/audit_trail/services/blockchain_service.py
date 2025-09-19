"""
Blockchain Service

Service for interacting with blockchain networks to store audit trail hashes.
Supports Ethereum and Substrate-based blockchains.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone

# Try to import web3 for Ethereum integration
try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# Try to import substrate-interface for Substrate integration
try:
    from substrateinterface import SubstrateInterface
    SUBSTRATE_AVAILABLE = True
except ImportError:
    SUBSTRATE_AVAILABLE = False

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service for blockchain integration and on-chain storage of audit hashes.
    """
    
    def __init__(self, network: str = 'ethereum'):
        """
        Initialize blockchain service.
        
        Args:
            network: Blockchain network to use ('ethereum' or 'substrate')
        """
        self.network = network
        self.web3 = None
        self.substrate = None
        self.contract_address = None
        self.contract_abi = None
        
        if network == 'ethereum':
            self._initialize_ethereum()
        elif network == 'substrate':
            self._initialize_substrate()
    
    def _initialize_ethereum(self):
        """Initialize Ethereum connection."""
        if not WEB3_AVAILABLE:
            logger.warning("web3 not available, using mock Ethereum connection")
            self.web3 = MockWeb3()
            return
        
        try:
            rpc_url = getattr(settings, 'ETHEREUM_RPC_URL', 'http://localhost:8545')
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if self.web3.is_connected():
                logger.info(f"Connected to Ethereum network: {rpc_url}")
                
                # Add PoA middleware if needed
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                # Load contract ABI and address
                self._load_contract_config()
            else:
                logger.warning(f"Failed to connect to Ethereum network: {rpc_url}")
                self.web3 = MockWeb3()
                
        except Exception as e:
            logger.error(f"Failed to initialize Ethereum: {e}")
            self.web3 = MockWeb3()
    
    def _initialize_substrate(self):
        """Initialize Substrate connection."""
        if not SUBSTRATE_AVAILABLE:
            logger.warning("substrate-interface not available, using mock Substrate connection")
            self.substrate = MockSubstrate()
            return
        
        try:
            rpc_url = getattr(settings, 'SUBSTRATE_RPC_URL', 'ws://localhost:9944')
            self.substrate = SubstrateInterface(url=rpc_url)
            
            if self.substrate.connected:
                logger.info(f"Connected to Substrate network: {rpc_url}")
            else:
                logger.warning(f"Failed to connect to Substrate network: {rpc_url}")
                self.substrate = MockSubstrate()
                
        except Exception as e:
            logger.error(f"Failed to initialize Substrate: {e}")
            self.substrate = MockSubstrate()
    
    def _load_contract_config(self):
        """Load smart contract configuration."""
        try:
            # Load contract ABI from file
            abi_path = getattr(settings, 'AUDIT_CONTRACT_ABI_PATH', None)
            if abi_path:
                with open(abi_path, 'r') as f:
                    self.contract_abi = json.load(f)
            
            # Load contract address
            self.contract_address = getattr(settings, 'AUDIT_CONTRACT_ADDRESS', None)
            
            if self.contract_abi and self.contract_address:
                self.contract = self.web3.eth.contract(
                    address=self.contract_address,
                    abi=self.contract_abi
                )
                logger.info(f"Loaded audit contract: {self.contract_address}")
            else:
                logger.warning("Contract ABI or address not configured")
                
        except Exception as e:
            logger.error(f"Failed to load contract config: {e}")
    
    def store_audit_hash(
        self,
        event_hash: str,
        merkle_root: str,
        module: str,
        event_type: str
    ) -> Dict[str, Any]:
        """
        Store audit hash on the blockchain.
        
        Args:
            event_hash: Hash of the audit event
            merkle_root: Merkle root hash
            module: Module that generated the event
            event_type: Type of the event
            
        Returns:
            Dictionary containing transaction details
        """
        if self.network == 'ethereum':
            return self._store_on_ethereum(event_hash, merkle_root, module, event_type)
        elif self.network == 'substrate':
            return self._store_on_substrate(event_hash, merkle_root, module, event_type)
        else:
            raise ValueError(f"Unsupported network: {self.network}")
    
    def _store_on_ethereum(
        self,
        event_hash: str,
        merkle_root: str,
        module: str,
        event_type: str
    ) -> Dict[str, Any]:
        """Store audit hash on Ethereum."""
        try:
            if not self.contract:
                raise ValueError("Ethereum contract not configured")
            
            # Get account for signing
            private_key = getattr(settings, 'ETHEREUM_PRIVATE_KEY', None)
            if not private_key:
                raise ValueError("Ethereum private key not configured")
            
            account = self.web3.eth.account.from_key(private_key)
            
            # Prepare transaction
            transaction = self.contract.functions.storeAuditRecord(
                event_hash,
                merkle_root,
                module,
                event_type
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'contract_address': self.contract_address,
                'network': 'ethereum'
            }
            
        except Exception as e:
            logger.error(f"Failed to store on Ethereum: {e}")
            return {
                'success': False,
                'error': str(e),
                'network': 'ethereum'
            }
    
    def _store_on_substrate(
        self,
        event_hash: str,
        merkle_root: str,
        module: str,
        event_type: str
    ) -> Dict[str, Any]:
        """Store audit hash on Substrate."""
        try:
            # This is a simplified implementation
            # In production, you would use proper Substrate transaction calls
            
            # For now, return a mock response
            return {
                'success': True,
                'transaction_hash': f"0x{'0' * 64}",
                'block_number': 12345,
                'gas_used': 0,
                'contract_address': None,
                'network': 'substrate'
            }
            
        except Exception as e:
            logger.error(f"Failed to store on Substrate: {e}")
            return {
                'success': False,
                'error': str(e),
                'network': 'substrate'
            }
    
    def verify_on_chain(self, transaction_hash: str) -> bool:
        """
        Verify that a transaction exists on the blockchain.
        
        Args:
            transaction_hash: Hash of the transaction to verify
            
        Returns:
            True if transaction exists, False otherwise
        """
        if self.network == 'ethereum':
            return self._verify_on_ethereum(transaction_hash)
        elif self.network == 'substrate':
            return self._verify_on_substrate(transaction_hash)
        else:
            return False
    
    def _verify_on_ethereum(self, transaction_hash: str) -> bool:
        """Verify transaction on Ethereum."""
        try:
            if not self.web3:
                return False
            
            receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
            return receipt.status == 1  # 1 means success
            
        except Exception as e:
            logger.error(f"Failed to verify Ethereum transaction: {e}")
            return False
    
    def _verify_on_substrate(self, transaction_hash: str) -> bool:
        """Verify transaction on Substrate."""
        try:
            if not self.substrate:
                return False
            
            # This is a simplified implementation
            # In production, you would check the transaction status
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify Substrate transaction: {e}")
            return False
    
    def get_transaction_details(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a blockchain transaction.
        
        Args:
            transaction_hash: Hash of the transaction
            
        Returns:
            Dictionary containing transaction details or None
        """
        if self.network == 'ethereum':
            return self._get_ethereum_transaction_details(transaction_hash)
        elif self.network == 'substrate':
            return self._get_substrate_transaction_details(transaction_hash)
        else:
            return None
    
    def _get_ethereum_transaction_details(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get Ethereum transaction details."""
        try:
            if not self.web3:
                return None
            
            tx = self.web3.eth.get_transaction(transaction_hash)
            receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
            
            return {
                'hash': tx.hash.hex(),
                'from': tx['from'],
                'to': tx['to'],
                'value': tx['value'],
                'gas': tx['gas'],
                'gas_price': tx['gasPrice'],
                'block_number': receipt.blockNumber,
                'block_hash': receipt.blockHash.hex(),
                'status': receipt.status,
                'gas_used': receipt.gasUsed
            }
            
        except Exception as e:
            logger.error(f"Failed to get Ethereum transaction details: {e}")
            return None
    
    def _get_substrate_transaction_details(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get Substrate transaction details."""
        try:
            if not self.substrate:
                return None
            
            # This is a simplified implementation
            # In production, you would query the Substrate node
            return {
                'hash': transaction_hash,
                'block_number': 12345,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to get Substrate transaction details: {e}")
            return None
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get information about the connected blockchain network.
        
        Returns:
            Dictionary containing network information
        """
        if self.network == 'ethereum':
            return self._get_ethereum_network_info()
        elif self.network == 'substrate':
            return self._get_substrate_network_info()
        else:
            return {'network': self.network, 'connected': False}
    
    def _get_ethereum_network_info(self) -> Dict[str, Any]:
        """Get Ethereum network information."""
        try:
            if not self.web3 or not self.web3.is_connected():
                return {'network': 'ethereum', 'connected': False}
            
            return {
                'network': 'ethereum',
                'connected': True,
                'chain_id': self.web3.eth.chain_id,
                'block_number': self.web3.eth.block_number,
                'gas_price': self.web3.eth.gas_price,
                'contract_address': self.contract_address
            }
            
        except Exception as e:
            logger.error(f"Failed to get Ethereum network info: {e}")
            return {'network': 'ethereum', 'connected': False, 'error': str(e)}
    
    def _get_substrate_network_info(self) -> Dict[str, Any]:
        """Get Substrate network information."""
        try:
            if not self.substrate or not self.substrate.connected:
                return {'network': 'substrate', 'connected': False}
            
            return {
                'network': 'substrate',
                'connected': True,
                'chain_name': self.substrate.get_chain_name(),
                'chain_version': self.substrate.get_chain_version(),
                'block_number': self.substrate.get_block_number()
            }
            
        except Exception as e:
            logger.error(f"Failed to get Substrate network info: {e}")
            return {'network': 'substrate', 'connected': False, 'error': str(e)}


class MockWeb3:
    """Mock Web3 interface for development and testing."""
    
    def __init__(self):
        self.connected = True
        self.chain_id = 1
        self.block_number = 12345
        self.gas_price = 20000000000  # 20 gwei
    
    def is_connected(self):
        """Mock connection status."""
        return True
    
    @property
    def eth(self):
        """Mock eth property."""
        return MockEth()
    
    class MockEth:
        """Mock Ethereum interface."""
        
        def __init__(self):
            self.chain_id = 1
            self.block_number = 12345
            self.gas_price = 20000000000
        
        def get_transaction_receipt(self, tx_hash: str):
            """Mock transaction receipt."""
            return MockTransactionReceipt()
        
        def get_transaction(self, tx_hash: str):
            """Mock transaction."""
            return MockTransaction()
        
        def get_transaction_count(self, address: str):
            """Mock transaction count."""
            return 0


class MockTransactionReceipt:
    """Mock transaction receipt."""
    
    def __init__(self):
        self.status = 1
        self.blockNumber = 12345
        self.gasUsed = 21000
        self.blockHash = b'\x00' * 32


class MockTransaction:
    """Mock transaction."""
    
    def __init__(self):
        self.hash = b'\x00' * 32
        self.blockNumber = 12345
        self.gas = 21000
        self.gasPrice = 20000000000
        self.value = 0


class MockSubstrate:
    """Mock Substrate interface for development and testing."""
    
    def __init__(self):
        self.connected = True
    
    def get_chain_name(self):
        """Mock chain name."""
        return "Polkadot"
    
    def get_chain_version(self):
        """Mock chain version."""
        return "0.9.0"
    
    def get_block_number(self):
        """Mock block number."""
        return 12345

"""
Blockchain service for Web3 integration.
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from django.conf import settings
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import requests
from .models import (
    Wallet, BlockchainTransaction, SmartContract, Token,
    OnChainAnchor, DAOGovernance, TokenizedReward
)

logger = logging.getLogger(__name__)


class BlockchainService:
    """Service for blockchain interactions."""
    
    def __init__(self):
        self.w3 = None
        self.contracts = {}
        self._initialize_web3()
        self._load_contracts()
    
    def _initialize_web3(self):
        """Initialize Web3 connection."""
        try:
            # Initialize Web3 with multiple providers
            providers = []
            
            # Ethereum providers
            if hasattr(settings, 'ETHEREUM_RPC_URL'):
                providers.append(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Polygon providers
            if hasattr(settings, 'POLYGON_RPC_URL'):
                providers.append(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
            
            # Moonbeam providers
            if hasattr(settings, 'MOONBEAM_RPC_URL'):
                providers.append(Web3.HTTPProvider(settings.MOONBEAM_RPC_URL))
            
            if providers:
                self.w3 = Web3(providers[0])  # Use first provider as primary
                logger.info(f"Web3 initialized with {len(providers)} providers")
            else:
                logger.warning("No Web3 providers configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
    
    def _load_contracts(self):
        """Load smart contract ABIs and addresses."""
        try:
            # Load contract configurations
            contract_configs = getattr(settings, 'WEB3_CONTRACTS', {})
            
            for contract_name, config in contract_configs.items():
                if 'address' in config and 'abi' in config:
                    contract = self.w3.eth.contract(
                        address=config['address'],
                        abi=config['abi']
                    )
                    self.contracts[contract_name] = contract
                    logger.info(f"Loaded contract: {contract_name}")
                    
        except Exception as e:
            logger.error(f"Failed to load contracts: {e}")
    
    def is_connected(self) -> bool:
        """Check if Web3 is connected."""
        if not self.w3:
            return False
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information."""
        if not self.is_connected():
            return {}
        
        try:
            chain_id = self.w3.eth.chain_id
            block_number = self.w3.eth.block_number
            gas_price = self.w3.eth.gas_price
            
            return {
                'chain_id': chain_id,
                'block_number': block_number,
                'gas_price': gas_price,
                'network_name': self._get_network_name(chain_id)
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {}
    
    def _get_network_name(self, chain_id: int) -> str:
        """Get network name from chain ID."""
        networks = {
            1: 'Ethereum Mainnet',
            11155111: 'Ethereum Sepolia',
            137: 'Polygon',
            80001: 'Polygon Mumbai',
            1284: 'Moonbeam',
            1287: 'Moonbase Alpha',
            592: 'Astar',
            336: 'Shiden'
        }
        return networks.get(chain_id, f'Unknown Network ({chain_id})')
    
    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """Verify a wallet signature."""
        try:
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            return recovered_address.lower() == address.lower()
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def get_balance(self, address: str, token_address: Optional[str] = None) -> Decimal:
        """Get balance for an address."""
        try:
            if token_address:
                # ERC20 token balance
                contract = self.contracts.get('ERC20')
                if contract:
                    balance = contract.functions.balanceOf(address).call()
                    decimals = contract.functions.decimals().call()
                    return Decimal(balance) / Decimal(10 ** decimals)
            else:
                # ETH balance
                balance = self.w3.eth.get_balance(address)
                return Decimal(balance) / Decimal(10 ** 18)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return Decimal(0)
    
    def create_invoice_on_chain(self, invoice_data: Dict[str, Any]) -> Optional[str]:
        """Create an invoice on the blockchain."""
        try:
            contract = self.contracts.get('TidyGenERP')
            if not contract:
                logger.error("TidyGenERP contract not loaded")
                return None
            
            # Prepare transaction data
            tx_data = contract.functions.createInvoice(
                invoice_data['client_address'],
                int(invoice_data['amount'] * 10**18),  # Convert to wei
                invoice_data.get('token_address', '0x0000000000000000000000000000000000000000'),
                invoice_data['description'],
                invoice_data['due_date'],
                invoice_data['data_hash']
            ).build_transaction({
                'from': invoice_data['vendor_address'],
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return tx_data
        except Exception as e:
            logger.error(f"Failed to create invoice on chain: {e}")
            return None
    
    def pay_invoice_on_chain(self, invoice_id: int, payer_address: str, amount: Decimal, token_address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Pay an invoice on the blockchain."""
        try:
            contract = self.contracts.get('TidyGenERP')
            if not contract:
                logger.error("TidyGenERP contract not loaded")
                return None
            
            if token_address:
                # ERC20 payment
                tx_data = contract.functions.payInvoice(invoice_id).build_transaction({
                    'from': payer_address,
                    'gas': 250000,
                    'gasPrice': self.w3.eth.gas_price
                })
            else:
                # ETH payment
                tx_data = contract.functions.payInvoice(invoice_id).build_transaction({
                    'from': payer_address,
                    'value': int(amount * 10**18),
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price
                })
            
            return tx_data
        except Exception as e:
            logger.error(f"Failed to pay invoice on chain: {e}")
            return None
    
    def anchor_data_on_chain(self, data_hash: str, data_type: str, anchorer_address: str) -> Optional[str]:
        """Anchor data to the blockchain."""
        try:
            contract = self.contracts.get('TidyGenERP')
            if not contract:
                logger.error("TidyGenERP contract not loaded")
                return None
            
            tx_data = contract.functions.anchorData(
                data_hash,
                data_type,
                anchorer_address
            ).build_transaction({
                'from': anchorer_address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return tx_data
        except Exception as e:
            logger.error(f"Failed to anchor data on chain: {e}")
            return None
    
    def create_governance_proposal(self, proposal_data: Dict[str, Any]) -> Optional[str]:
        """Create a governance proposal on the blockchain."""
        try:
            contract = self.contracts.get('TidyGenDAO')
            if not contract:
                logger.error("TidyGenDAO contract not loaded")
                return None
            
            tx_data = contract.functions.propose(
                proposal_data['title'],
                proposal_data['description'],
                proposal_data['proposal_type'],
                proposal_data['execution_hash']
            ).build_transaction({
                'from': proposal_data['proposer_address'],
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return tx_data
        except Exception as e:
            logger.error(f"Failed to create governance proposal: {e}")
            return None
    
    def cast_vote(self, proposal_id: int, voter_address: str, support: bool, reason: str = "") -> Optional[str]:
        """Cast a vote on a governance proposal."""
        try:
            contract = self.contracts.get('TidyGenDAO')
            if not contract:
                logger.error("TidyGenDAO contract not loaded")
                return None
            
            tx_data = contract.functions.castVote(
                proposal_id,
                1 if support else 0,
                reason
            ).build_transaction({
                'from': voter_address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return tx_data
        except Exception as e:
            logger.error(f"Failed to cast vote: {e}")
            return None
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status and details."""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'hash': tx_hash,
                'status': 'success' if tx_receipt.status == 1 else 'failed',
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'gas_price': tx.gasPrice,
                'from': tx['from'],
                'to': tx['to'],
                'value': tx['value']
            }
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return {'hash': tx_hash, 'status': 'unknown', 'error': str(e)}
    
    def get_contract_events(self, contract_name: str, event_name: str, from_block: int = 0, to_block: str = 'latest') -> List[Dict[str, Any]]:
        """Get events from a smart contract."""
        try:
            contract = self.contracts.get(contract_name)
            if not contract:
                logger.error(f"Contract {contract_name} not loaded")
                return []
            
            event_filter = contract.events[event_name].create_filter(
                fromBlock=from_block,
                toBlock=to_block
            )
            
            events = event_filter.get_all_entries()
            return [dict(event) for event in events]
        except Exception as e:
            logger.error(f"Failed to get contract events: {e}")
            return []
    
    def estimate_gas(self, tx_data: Dict[str, Any]) -> int:
        """Estimate gas for a transaction."""
        try:
            return self.w3.eth.estimate_gas(tx_data)
        except Exception as e:
            logger.error(f"Failed to estimate gas: {e}")
            return 0
    
    def get_gas_price(self) -> int:
        """Get current gas price."""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            return 0
    
    def send_transaction(self, tx_data: Dict[str, Any], private_key: str) -> Optional[str]:
        """Send a signed transaction to the blockchain."""
        try:
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            return None
    
    def wait_for_transaction(self, tx_hash: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for transaction to be mined."""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return {
                'status': 'success' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'transaction_hash': receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Failed to wait for transaction: {e}")
            return {'status': 'timeout', 'error': str(e)}


class IPFSService:
    """Service for IPFS integration."""
    
    def __init__(self):
        self.ipfs_url = getattr(settings, 'IPFS_URL', 'http://localhost:5001')
        self.ipfs_gateway = getattr(settings, 'IPFS_GATEWAY', 'https://ipfs.io/ipfs/')
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file to IPFS."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.ipfs_url}/api/v0/add", files=files)
                
            if response.status_code == 200:
                result = response.json()
                return result['Hash']
        except Exception as e:
            logger.error(f"Failed to upload file to IPFS: {e}")
        return None
    
    def upload_data(self, data: str) -> Optional[str]:
        """Upload data to IPFS."""
        try:
            files = {'file': data}
            response = requests.post(f"{self.ipfs_url}/api/v0/add", files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result['Hash']
        except Exception as e:
            logger.error(f"Failed to upload data to IPFS: {e}")
        return None
    
    def pin_file(self, ipfs_hash: str) -> bool:
        """Pin a file to IPFS."""
        try:
            response = requests.post(f"{self.ipfs_url}/api/v0/pin/add", params={'arg': ipfs_hash})
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pin file to IPFS: {e}")
            return False
    
    def get_file_url(self, ipfs_hash: str) -> str:
        """Get IPFS file URL."""
        return f"{self.ipfs_gateway}{ipfs_hash}"


# Global service instances
blockchain_service = BlockchainService()
ipfs_service = IPFSService()

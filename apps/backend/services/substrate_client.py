"""
Substrate RPC Client for TidyGen ERP

This module provides a comprehensive interface to interact with the TidyGen Substrate node,
including invoice ledger, DID management, and DAO governance.
"""

import logging
import time
import json
import hashlib
from typing import Optional, Dict, List, Any, Tuple
from decimal import Decimal

from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException

logger = logging.getLogger(__name__)


class SubstrateConnectionError(Exception):
    """Raised when connection to Substrate node fails"""
    pass


class SubstrateTransactionError(Exception):
    """Raised when a transaction fails"""
    pass


class SubstrateClient:
    """
    Substrate RPC client for TidyGen ERP blockchain integration.
    
    Provides methods to interact with custom pallets:
    - pallet-ledger: Invoice management
    - pallet-did: Decentralized identity
    - pallet-dao: Governance proposals
    
    Features:
    - Automatic retry logic
    - Connection pooling
    - Error handling
    - Transaction verification
    """
    
    def __init__(
        self,
        url: str = "ws://127.0.0.1:9944",
        ss58_format: int = 42,
        type_registry_preset: str = 'substrate-node-template',
        max_retries: int = 3,
        retry_delay: float = 1.0,
        keypair_uri: Optional[str] = None
    ):
        """
        Initialize Substrate client.
        
        Args:
            url: Substrate node WebSocket URL
            ss58_format: SS58 address format (42 for Substrate)
            type_registry_preset: Type registry preset
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            keypair_uri: Default keypair URI (e.g., '//Alice')
        """
        self.url = url
        self.ss58_format = ss58_format
        self.type_registry_preset = type_registry_preset
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.substrate = None
        self.keypair = None
        
        # Initialize connection
        self._connect()
        
        # Initialize default keypair if provided
        if keypair_uri:
            self.keypair = Keypair.create_from_uri(keypair_uri)
    
    def _connect(self) -> None:
        """
        Establish connection to Substrate node with retry logic.
        
        Raises:
            SubstrateConnectionError: If connection fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Connecting to Substrate node at {self.url} (attempt {attempt + 1}/{self.max_retries})")
                
                self.substrate = SubstrateInterface(
                    url=self.url,
                    ss58_format=self.ss58_format,
                    type_registry_preset=self.type_registry_preset
                )
                
                # Test connection
                chain = self.substrate.get_chain()
                logger.info(f"Successfully connected to Substrate node: {chain}")
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise SubstrateConnectionError(
                        f"Failed to connect to Substrate node at {self.url} after {self.max_retries} attempts"
                    ) from e
    
    def _ensure_connected(self) -> None:
        """Ensure connection is alive, reconnect if needed."""
        try:
            # Test connection
            self.substrate.get_block_number(block_hash=None)
        except Exception:
            logger.warning("Connection lost, reconnecting...")
            self._connect()
    
    def _retry_on_failure(self, func, *args, **kwargs):
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    self._ensure_connected()
        
        raise last_exception
    
    # ==========================================
    # LEDGER PALLET METHODS
    # ==========================================
    
    def record_invoice(
        self,
        user_id: int,
        invoice_hash: str,
        client_account: str,
        amount: int,
        metadata: str,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Record an invoice on the blockchain ledger.
        
        Calls: Ledger.create_invoice
        
        Args:
            user_id: Django user ID (for logging)
            invoice_hash: SHA256 hash of invoice data
            client_account: Client's Substrate account ID
            amount: Invoice amount in smallest unit
            metadata: Invoice metadata (invoice number, description, etc.)
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        
        Raises:
            SubstrateTransactionError: If transaction fails
        
        Example:
            >>> client = SubstrateClient()
            >>> tx_hash, receipt = client.record_invoice(
            ...     user_id=1,
            ...     invoice_hash="a1b2c3...",
            ...     client_account="5GrwvaEF...",
            ...     amount=1000000,
            ...     metadata="INV-2025-001|Client XYZ|Net 30"
            ... )
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            logger.info(f"Recording invoice for user {user_id}, client: {client_account}")
            
            # Compose call
            call = self.substrate.compose_call(
                call_module='Ledger',
                call_function='create_invoice',
                call_params={
                    'client': client_account,
                    'amount': amount,
                    'metadata': metadata
                }
            )
            
            # Create and submit signed extrinsic
            extrinsic = self.substrate.create_signed_extrinsic(
                call=call,
                keypair=signer
            )
            
            receipt = self.substrate.submit_extrinsic(
                extrinsic,
                wait_for_inclusion=True
            )
            
            if not receipt.is_success:
                raise SubstrateTransactionError(
                    f"Invoice creation failed: {receipt.error_message}"
                )
            
            logger.info(f"Invoice recorded successfully: {receipt.extrinsic_hash}")
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash,
                'finalized': receipt.finalized,
                'success': receipt.is_success
            }
        
        return self._retry_on_failure(_submit)
    
    def get_invoices(self, user_account: str) -> List[Dict[str, Any]]:
        """
        Get all invoices for a user/client from blockchain.
        
        Queries: Ledger.Invoices
        
        Args:
            user_account: Substrate account ID to query
        
        Returns:
            List of invoice dictionaries
        
        Example:
            >>> client = SubstrateClient()
            >>> invoices = client.get_invoices("5GrwvaEF...")
            >>> for inv in invoices:
            ...     print(f"Invoice {inv['id']}: {inv['amount']}")
        """
        def _query():
            logger.info(f"Querying invoices for account: {user_account}")
            
            result = self.substrate.query(
                module='Ledger',
                storage_function='Invoices',
                params=[user_account]
            )
            
            if result.value is None:
                return []
            
            # Convert to list of dictionaries
            invoices = []
            for invoice_data in result.value:
                invoice = {
                    'id': invoice_data['id'],
                    'client': str(invoice_data['client']),
                    'amount': int(invoice_data['amount']),
                    'metadata': invoice_data['metadata'].decode('utf-8') if isinstance(invoice_data['metadata'], bytes) else invoice_data['metadata'],
                    'timestamp': int(invoice_data['timestamp']),
                    'invoice_hash': invoice_data['invoice_hash'].hex() if isinstance(invoice_data['invoice_hash'], bytes) else invoice_data['invoice_hash'],
                    'created_by': str(invoice_data['created_by'])
                }
                invoices.append(invoice)
            
            logger.info(f"Found {len(invoices)} invoices for account")
            return invoices
        
        return self._retry_on_failure(_query)
    
    def get_invoice_by_hash(self, invoice_hash: str) -> Optional[int]:
        """
        Get invoice ID by its SHA256 hash.
        
        Queries: Ledger.InvoiceByHash
        
        Args:
            invoice_hash: SHA256 hash (hex string or bytes)
        
        Returns:
            Invoice ID if found, None otherwise
        """
        def _query():
            # Convert hex string to bytes if needed
            if isinstance(invoice_hash, str):
                hash_bytes = bytes.fromhex(invoice_hash.replace('0x', ''))
            else:
                hash_bytes = invoice_hash
            
            result = self.substrate.query(
                module='Ledger',
                storage_function='InvoiceByHash',
                params=[hash_bytes]
            )
            
            return result.value if result.value else None
        
        return self._retry_on_failure(_query)
    
    # ==========================================
    # DID PALLET METHODS
    # ==========================================
    
    def register_did(
        self,
        user_id: int,
        account_id: str,
        public_key: str,
        metadata: Optional[Dict[str, Any]] = None,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Register a DID for a user on the blockchain.
        
        Calls: Did.register_did
        
        Args:
            user_id: Django user ID
            account_id: Substrate account ID to register DID for
            public_key: Public key for verification (hex string)
            metadata: Optional metadata dict (will be JSON serialized)
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        
        Raises:
            SubstrateTransactionError: If transaction fails
        
        Example:
            >>> client = SubstrateClient()
            >>> tx_hash, receipt = client.register_did(
            ...     user_id=1,
            ...     account_id="5GrwvaEF...",
            ...     public_key="0x04...",
            ...     metadata={'email': 'alice@example.com', 'role': 'employee'}
            ... )
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            logger.info(f"Registering DID for user {user_id}, account: {account_id}")
            
            # Prepare metadata
            if metadata is None:
                metadata_dict = {'user_id': user_id}
            else:
                metadata_dict = {'user_id': user_id, **metadata}
            
            metadata_json = json.dumps(metadata_dict)
            
            # Convert public key to bytes if hex string
            if isinstance(public_key, str):
                pub_key_bytes = bytes.fromhex(public_key.replace('0x', ''))
            else:
                pub_key_bytes = public_key
            
            # Compose call
            call = self.substrate.compose_call(
                call_module='Did',
                call_function='register_did',
                call_params={
                    'account_id': account_id,
                    'public_key': pub_key_bytes,
                    'metadata': metadata_json
                }
            )
            
            # Create and submit signed extrinsic
            extrinsic = self.substrate.create_signed_extrinsic(
                call=call,
                keypair=signer
            )
            
            receipt = self.substrate.submit_extrinsic(
                extrinsic,
                wait_for_inclusion=True
            )
            
            if not receipt.is_success:
                raise SubstrateTransactionError(
                    f"DID registration failed: {receipt.error_message}"
                )
            
            logger.info(f"DID registered successfully: {receipt.extrinsic_hash}")
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash,
                'finalized': receipt.finalized,
                'success': receipt.is_success
            }
        
        return self._retry_on_failure(_submit)
    
    def get_did(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get DID document for an account via RPC.
        
        RPC: did_getDid
        
        Args:
            account_id: Substrate account ID
        
        Returns:
            DID document dict or None if not found
        
        Example:
            >>> client = SubstrateClient()
            >>> did_doc = client.get_did("5GrwvaEF...")
            >>> print(did_doc['public_key'])
        """
        def _query():
            logger.info(f"Querying DID for account: {account_id}")
            
            try:
                result = self.substrate.rpc_request('did_getDid', [account_id])
                
                if result is None:
                    return None
                
                # Parse result
                did_doc = {
                    'controller': str(result.get('controller')),
                    'public_key': result.get('public_key'),
                    'metadata': result.get('metadata'),
                    'created_at': int(result.get('created_at', 0)),
                    'updated_at': int(result.get('updated_at', 0)),
                    'status': str(result.get('status')),
                    'did_identifier': result.get('did_identifier'),
                    'nonce': int(result.get('nonce', 0))
                }
                
                return did_doc
                
            except Exception as e:
                logger.error(f"Failed to query DID: {e}")
                return None
        
        return self._retry_on_failure(_query)
    
    def is_did_active(self, account_id: str) -> bool:
        """
        Check if a DID is active via RPC.
        
        RPC: did_isDidActive
        
        Args:
            account_id: Substrate account ID
        
        Returns:
            True if DID is active, False otherwise
        """
        def _query():
            try:
                result = self.substrate.rpc_request('did_isDidActive', [account_id])
                return bool(result)
            except Exception as e:
                logger.error(f"Failed to check DID status: {e}")
                return False
        
        return self._retry_on_failure(_query)
    
    def update_did(
        self,
        account_id: str,
        public_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Update a DID document.
        
        Calls: Did.update_did
        
        Args:
            account_id: Substrate account ID
            public_key: New public key (optional)
            metadata: New metadata (optional)
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            # Prepare parameters
            pub_key_param = None
            if public_key:
                pub_key_param = bytes.fromhex(public_key.replace('0x', ''))
            
            metadata_param = None
            if metadata:
                metadata_param = json.dumps(metadata)
            
            # Compose call
            call = self.substrate.compose_call(
                call_module='Did',
                call_function='update_did',
                call_params={
                    'account_id': account_id,
                    'public_key': pub_key_param,
                    'metadata': metadata_param
                }
            )
            
            # Submit extrinsic
            extrinsic = self.substrate.create_signed_extrinsic(call=call, keypair=signer)
            receipt = self.substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
            
            if not receipt.is_success:
                raise SubstrateTransactionError(f"DID update failed: {receipt.error_message}")
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash
            }
        
        return self._retry_on_failure(_submit)
    
    # ==========================================
    # DAO PALLET METHODS
    # ==========================================
    
    def create_proposal(
        self,
        title: str,
        description: str,
        voting_period: Optional[int] = None,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Create a DAO governance proposal.
        
        Calls: Dao.create_proposal
        
        Args:
            title: Proposal title (max 256 bytes)
            description: Proposal description (max 2048 bytes)
            voting_period: Voting period in blocks (optional)
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        
        Example:
            >>> client = SubstrateClient()
            >>> tx_hash, receipt = client.create_proposal(
            ...     title="Approve Q4 Budget",
            ...     description="Allocate $50,000 for Q4 operations",
            ...     voting_period=100
            ... )
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            logger.info(f"Creating DAO proposal: {title}")
            
            # Compose call
            call = self.substrate.compose_call(
                call_module='Dao',
                call_function='create_proposal',
                call_params={
                    'title': title,
                    'description': description,
                    'voting_period': voting_period
                }
            )
            
            # Submit extrinsic
            extrinsic = self.substrate.create_signed_extrinsic(call=call, keypair=signer)
            receipt = self.substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
            
            if not receipt.is_success:
                raise SubstrateTransactionError(
                    f"Proposal creation failed: {receipt.error_message}"
                )
            
            logger.info(f"Proposal created successfully: {receipt.extrinsic_hash}")
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash
            }
        
        return self._retry_on_failure(_submit)
    
    def vote_on_proposal(
        self,
        proposal_id: int,
        in_favor: bool,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Vote on a DAO proposal.
        
        Calls: Dao.vote
        
        Args:
            proposal_id: ID of proposal to vote on
            in_favor: True for yes, False for no
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            logger.info(f"Voting on proposal {proposal_id}: {('yes' if in_favor else 'no')}")
            
            call = self.substrate.compose_call(
                call_module='Dao',
                call_function='vote',
                call_params={
                    'proposal_id': proposal_id,
                    'in_favor': in_favor
                }
            )
            
            extrinsic = self.substrate.create_signed_extrinsic(call=call, keypair=signer)
            receipt = self.substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
            
            if not receipt.is_success:
                raise SubstrateTransactionError(f"Vote failed: {receipt.error_message}")
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash
            }
        
        return self._retry_on_failure(_submit)
    
    def get_proposal(self, proposal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get proposal details from blockchain.
        
        Queries: Dao.Proposals
        
        Args:
            proposal_id: Proposal ID
        
        Returns:
            Proposal dict or None if not found
        """
        def _query():
            result = self.substrate.query(
                module='Dao',
                storage_function='Proposals',
                params=[proposal_id]
            )
            
            if result.value is None:
                return None
            
            proposal = {
                'id': result.value['id'],
                'proposer': str(result.value['proposer']),
                'title': result.value['title'],
                'description': result.value['description'],
                'created_at': int(result.value['created_at']),
                'voting_start': int(result.value['voting_start']),
                'voting_end': int(result.value['voting_end']),
                'status': str(result.value['status']),
                'votes_for': int(result.value['votes_for']),
                'votes_against': int(result.value['votes_against']),
                'total_votes': int(result.value['total_votes']),
                'executed': bool(result.value['executed']),
            }
            
            return proposal
        
        return self._retry_on_failure(_query)
    
    def execute_proposal(
        self,
        proposal_id: int,
        keypair: Optional[Keypair] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute an approved proposal.
        
        Calls: Dao.execute_proposal
        
        Args:
            proposal_id: ID of proposal to execute
            keypair: Keypair for signing (uses default if None)
        
        Returns:
            Tuple of (extrinsic_hash, receipt)
        """
        def _submit():
            signer = keypair or self.keypair
            if not signer:
                raise ValueError("No keypair provided for signing")
            
            call = self.substrate.compose_call(
                call_module='Dao',
                call_function='execute_proposal',
                call_params={'proposal_id': proposal_id}
            )
            
            extrinsic = self.substrate.create_signed_extrinsic(call=call, keypair=signer)
            receipt = self.substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
            
            if not receipt.is_success:
                raise SubstrateTransactionError(
                    f"Proposal execution failed: {receipt.error_message}"
                )
            
            return receipt.extrinsic_hash, {
                'extrinsic_hash': receipt.extrinsic_hash,
                'block_hash': receipt.block_hash
            }
        
        return self._retry_on_failure(_submit)
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_block_number(self) -> int:
        """Get current block number."""
        def _query():
            return self.substrate.get_block_number(block_hash=None)
        
        return self._retry_on_failure(_query)
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get chain information."""
        def _query():
            return {
                'chain': self.substrate.get_chain(),
                'chain_type': self.substrate.chain,
                'version': self.substrate.get_version(),
                'block_number': self.substrate.get_block_number(None),
                'finalized_head': self.substrate.get_block_hash(),
            }
        
        return self._retry_on_failure(_query)
    
    def create_keypair(self, uri: str) -> Keypair:
        """
        Create a keypair from URI.
        
        Args:
            uri: Keypair URI (e.g., '//Alice', mnemonic, or private key)
        
        Returns:
            Keypair instance
        """
        return Keypair.create_from_uri(uri)
    
    def calculate_invoice_hash(self, invoice_data: Dict[str, Any]) -> str:
        """
        Calculate SHA256 hash of invoice data (matches pallet logic).
        
        Args:
            invoice_data: Invoice data dict
        
        Returns:
            SHA256 hash as hex string
        """
        # Prepare data for hashing (must match pallet implementation)
        data = b''
        data += int(invoice_data.get('id', 0)).to_bytes(8, 'little')
        data += str(invoice_data.get('client', '')).encode()
        data += str(invoice_data.get('amount', 0)).encode()
        data += str(invoice_data.get('metadata', '')).encode()
        data += str(invoice_data.get('timestamp', 0)).encode()
        
        return hashlib.sha256(data).hexdigest()
    
    def close(self) -> None:
        """Close connection to Substrate node."""
        if self.substrate:
            try:
                self.substrate.close()
                logger.info("Substrate connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_substrate_client(**kwargs) -> SubstrateClient:
    """
    Get a configured Substrate client instance.
    
    Args:
        **kwargs: Arguments passed to SubstrateClient
    
    Returns:
        SubstrateClient instance
    
    Example:
        >>> client = get_substrate_client(keypair_uri='//Alice')
    """
    return SubstrateClient(**kwargs)


def test_connection(url: str = "ws://127.0.0.1:9944") -> bool:
    """
    Test connection to Substrate node.
    
    Args:
        url: Substrate node URL
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = SubstrateClient(url=url)
        info = client.get_chain_info()
        logger.info(f"Connection test successful: {info['chain']}")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


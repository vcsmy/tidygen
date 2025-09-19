"""
Transaction Service for Smart Contract Ledger

This module provides high-level transaction management services,
coordinating between Django models, hash generation, and blockchain submission.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import LedgerTransaction, LedgerEvent, LedgerBatch, LedgerConfiguration
from .hash_service import HashService
from .blockchain_service import BlockchainService

logger = logging.getLogger(__name__)


class TransactionService:
    """
    High-level service for managing ledger transactions.
    
    This service coordinates the complete transaction lifecycle from creation
    to blockchain confirmation, including hash generation, validation, and
    blockchain submission.
    """
    
    def __init__(self, organization_id: Optional[str] = None):
        """
        Initialize transaction service.
        
        Args:
            organization_id: Organization ID for multi-tenant operations
        """
        self.organization_id = organization_id
        self.blockchain_service = None
        self._initialize_blockchain_service()
    
    def _initialize_blockchain_service(self):
        """Initialize blockchain service with organization configuration."""
        try:
            if self.organization_id:
                config = LedgerConfiguration.objects.get(
                    organization_id=self.organization_id,
                    is_active=True
                )
                
                self.blockchain_service = BlockchainService(
                    network=config.blockchain_network,
                    rpc_endpoint=config.rpc_endpoint
                )
                
                if config.contract_address:
                    self.blockchain_service.set_contract_address(config.contract_address)
                
                if config.private_key:
                    self.blockchain_service.set_private_key(config.private_key)
            else:
                # Use default configuration
                self.blockchain_service = BlockchainService()
                
        except LedgerConfiguration.DoesNotExist:
            logger.warning(f"No ledger configuration found for organization {self.organization_id}")
            self.blockchain_service = BlockchainService()
        except Exception as e:
            logger.error(f"Failed to initialize blockchain service: {e}")
            self.blockchain_service = BlockchainService()
    
    def create_transaction(
        self,
        transaction_type: str,
        source_module: str,
        source_id: str,
        transaction_data: Dict[str, Any],
        organization_id: Optional[str] = None,
        created_by_id: Optional[str] = None
    ) -> LedgerTransaction:
        """
        Create a new ledger transaction.
        
        Args:
            transaction_type: Type of transaction (invoice, payment, etc.)
            source_module: Django app/module that created the transaction
            source_id: ID of the original transaction
            transaction_data: Complete transaction data
            organization_id: Organization ID (defaults to service organization)
            created_by_id: User ID who created the transaction
            
        Returns:
            Created LedgerTransaction instance
            
        Raises:
            ValidationError: If transaction data is invalid
        """
        try:
            logger.info(f"Creating ledger transaction: {source_id}")
            
            # Use service organization if not provided
            if not organization_id:
                organization_id = self.organization_id
            
            if not organization_id:
                raise ValidationError("Organization ID is required")
            
            # Generate transaction hash
            transaction_hash = HashService.generate_transaction_hash(
                transaction_type=transaction_type,
                source_module=source_module,
                source_id=source_id,
                transaction_data=transaction_data,
                organization_id=organization_id
            )
            
            # Create transaction in database
            with transaction.atomic():
                ledger_transaction = LedgerTransaction.objects.create(
                    transaction_type=transaction_type,
                    source_module=source_module,
                    source_id=source_id,
                    transaction_data=transaction_data,
                    hash=transaction_hash,
                    organization_id=organization_id,
                    created_by_id=created_by_id
                )
                
                # Create initial event
                self._create_event(
                    ledger_transaction=ledger_transaction,
                    event_type='transaction_logged',
                    event_data={'status': 'created'}
                )
                
                logger.info(f"Created ledger transaction: {ledger_transaction.id}")
                return ledger_transaction
                
        except Exception as e:
            logger.error(f"Failed to create transaction {source_id}: {e}")
            raise
    
    def submit_transaction(
        self,
        ledger_transaction: LedgerTransaction,
        force_submit: bool = False
    ) -> bool:
        """
        Submit a transaction to the blockchain.
        
        Args:
            ledger_transaction: LedgerTransaction instance to submit
            force_submit: Force submission even if already submitted
            
        Returns:
            True if submission was successful, False otherwise
        """
        try:
            logger.info(f"Submitting transaction to blockchain: {ledger_transaction.id}")
            
            # Check if already submitted
            if ledger_transaction.status in ['submitted', 'confirmed'] and not force_submit:
                logger.info(f"Transaction {ledger_transaction.id} already submitted")
                return True
            
            # Validate transaction
            if not self._validate_transaction(ledger_transaction):
                raise ValidationError("Transaction validation failed")
            
            # Submit to blockchain
            blockchain_result = self.blockchain_service.submit_transaction(
                transaction_type=ledger_transaction.transaction_type,
                source_module=ledger_transaction.source_module,
                source_id=ledger_transaction.source_id,
                transaction_data=ledger_transaction.transaction_data,
                transaction_hash=ledger_transaction.hash
            )
            
            # Update transaction status
            with transaction.atomic():
                if blockchain_result.status == 'submitted':
                    ledger_transaction.mark_submitted(blockchain_result.hash)
                    
                    # Create submission event
                    self._create_event(
                        ledger_transaction=ledger_transaction,
                        event_type='transaction_submitted',
                        event_data={
                            'blockchain_hash': blockchain_result.hash,
                            'status': 'submitted'
                        }
                    )
                    
                    logger.info(f"Transaction {ledger_transaction.id} submitted successfully")
                    return True
                else:
                    ledger_transaction.mark_failed(blockchain_result.error_message)
                    
                    # Create failure event
                    self._create_event(
                        ledger_transaction=ledger_transaction,
                        event_type='transaction_failed',
                        event_data={
                            'error': blockchain_result.error_message,
                            'status': 'failed'
                        }
                    )
                    
                    logger.error(f"Transaction {ledger_transaction.id} submission failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to submit transaction {ledger_transaction.id}: {e}")
            
            # Mark transaction as failed
            ledger_transaction.mark_failed(str(e))
            
            # Create error event
            self._create_event(
                ledger_transaction=ledger_transaction,
                event_type='error_occurred',
                event_data={'error': str(e)}
            )
            
            return False
    
    def confirm_transaction(
        self,
        ledger_transaction: LedgerTransaction,
        block_number: Optional[int] = None,
        transaction_index: Optional[int] = None,
        gas_used: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> bool:
        """
        Confirm a transaction on the blockchain.
        
        Args:
            ledger_transaction: LedgerTransaction instance to confirm
            block_number: Block number where transaction was confirmed
            transaction_index: Transaction index within the block
            gas_used: Gas used for the transaction
            gas_price: Gas price for the transaction
            
        Returns:
            True if confirmation was successful, False otherwise
        """
        try:
            logger.info(f"Confirming transaction: {ledger_transaction.id}")
            
            # Verify transaction on blockchain
            if not self.blockchain_service.verify_transaction(ledger_transaction.blockchain_hash):
                logger.warning(f"Transaction {ledger_transaction.id} not found on blockchain")
                return False
            
            # Get transaction details from blockchain
            tx_details = self.blockchain_service.get_transaction_details(
                ledger_transaction.blockchain_hash
            )
            
            if tx_details:
                block_number = block_number or tx_details.get('block_number')
                transaction_index = transaction_index or tx_details.get('transaction_index')
                gas_used = gas_used or tx_details.get('gas_used')
                gas_price = gas_price or tx_details.get('gas_price')
            
            # Update transaction status
            with transaction.atomic():
                ledger_transaction.mark_confirmed(
                    block_number=block_number,
                    transaction_index=transaction_index,
                    gas_used=gas_used,
                    gas_price=gas_price
                )
                
                # Create confirmation event
                self._create_event(
                    ledger_transaction=ledger_transaction,
                    event_type='transaction_confirmed',
                    event_data={
                        'block_number': block_number,
                        'transaction_index': transaction_index,
                        'gas_used': gas_used,
                        'gas_price': gas_price,
                        'status': 'confirmed'
                    }
                )
                
                logger.info(f"Transaction {ledger_transaction.id} confirmed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to confirm transaction {ledger_transaction.id}: {e}")
            return False
    
    def verify_transaction(
        self,
        ledger_transaction: LedgerTransaction,
        verify_hash: bool = True,
        verify_blockchain: bool = True
    ) -> Dict[str, Any]:
        """
        Verify a transaction's integrity.
        
        Args:
            ledger_transaction: LedgerTransaction instance to verify
            verify_hash: Whether to verify the transaction hash
            verify_blockchain: Whether to verify on blockchain
            
        Returns:
            Dictionary with verification results
        """
        try:
            logger.info(f"Verifying transaction: {ledger_transaction.id}")
            
            verification_result = {
                'transaction_id': str(ledger_transaction.id),
                'hash_valid': True,
                'blockchain_confirmed': False,
                'blockchain_hash': ledger_transaction.blockchain_hash,
                'block_number': ledger_transaction.block_number,
                'verification_timestamp': timezone.now(),
                'error_message': None
            }
            
            # Verify hash
            if verify_hash:
                hash_valid = HashService.verify_transaction_hash(
                    transaction_type=ledger_transaction.transaction_type,
                    source_module=ledger_transaction.source_module,
                    source_id=ledger_transaction.source_id,
                    transaction_data=ledger_transaction.transaction_data,
                    expected_hash=ledger_transaction.hash,
                    organization_id=str(ledger_transaction.organization_id)
                )
                verification_result['hash_valid'] = hash_valid
                
                if not hash_valid:
                    verification_result['error_message'] = "Transaction hash verification failed"
            
            # Verify on blockchain
            if verify_blockchain and ledger_transaction.blockchain_hash:
                blockchain_confirmed = self.blockchain_service.verify_transaction(
                    ledger_transaction.blockchain_hash
                )
                verification_result['blockchain_confirmed'] = blockchain_confirmed
                
                if not blockchain_confirmed:
                    verification_result['error_message'] = "Blockchain verification failed"
            
            # Create verification event
            self._create_event(
                ledger_transaction=ledger_transaction,
                event_type='hash_verified',
                event_data=verification_result
            )
            
            logger.info(f"Transaction {ledger_transaction.id} verification completed")
            return verification_result
            
        except Exception as e:
            logger.error(f"Failed to verify transaction {ledger_transaction.id}: {e}")
            return {
                'transaction_id': str(ledger_transaction.id),
                'hash_valid': False,
                'blockchain_confirmed': False,
                'error_message': str(e),
                'verification_timestamp': timezone.now()
            }
    
    def create_batch(
        self,
        transaction_ids: List[str],
        organization_id: Optional[str] = None
    ) -> LedgerBatch:
        """
        Create a batch of transactions for efficient blockchain submission.
        
        Args:
            transaction_ids: List of transaction IDs to include in batch
            organization_id: Organization ID (defaults to service organization)
            
        Returns:
            Created LedgerBatch instance
        """
        try:
            logger.info(f"Creating batch with {len(transaction_ids)} transactions")
            
            # Use service organization if not provided
            if not organization_id:
                organization_id = self.organization_id
            
            if not organization_id:
                raise ValidationError("Organization ID is required")
            
            # Get transactions
            transactions = LedgerTransaction.objects.filter(
                id__in=transaction_ids,
                organization_id=organization_id,
                status='pending'
            )
            
            if not transactions.exists():
                raise ValidationError("No valid transactions found for batch")
            
            # Generate batch hash
            transaction_hashes = [tx.hash for tx in transactions]
            batch_hash = HashService.generate_batch_hash(transaction_hashes)
            
            # Create batch
            with transaction.atomic():
                batch = LedgerBatch.objects.create(
                    batch_hash=batch_hash,
                    organization_id=organization_id
                )
                
                # Add transactions to batch
                batch.transactions.set(transactions)
                
                logger.info(f"Created batch: {batch.id}")
                return batch
                
        except Exception as e:
            logger.error(f"Failed to create batch: {e}")
            raise
    
    def submit_batch(
        self,
        ledger_batch: LedgerBatch,
        force_submit: bool = False
    ) -> bool:
        """
        Submit a batch of transactions to the blockchain.
        
        Args:
            ledger_batch: LedgerBatch instance to submit
            force_submit: Force submission even if already submitted
            
        Returns:
            True if submission was successful, False otherwise
        """
        try:
            logger.info(f"Submitting batch to blockchain: {ledger_batch.id}")
            
            # Check if already submitted
            if ledger_batch.status in ['submitted', 'confirmed'] and not force_submit:
                logger.info(f"Batch {ledger_batch.id} already submitted")
                return True
            
            # Prepare batch data
            transactions_data = []
            for tx in ledger_batch.transactions.all():
                transactions_data.append({
                    'transaction_type': tx.transaction_type,
                    'source_module': tx.source_module,
                    'source_id': tx.source_id,
                    'transaction_data': tx.transaction_data,
                    'transaction_hash': tx.hash
                })
            
            # Submit to blockchain
            blockchain_results = self.blockchain_service.submit_batch_transactions(
                transactions_data
            )
            
            # Update batch status
            with transaction.atomic():
                if blockchain_results and blockchain_results[0].status == 'submitted':
                    ledger_batch.status = 'submitted'
                    ledger_batch.blockchain_hash = blockchain_results[0].hash
                    ledger_batch.submitted_at = timezone.now()
                    ledger_batch.save()
                    
                    # Update individual transactions
                    for tx in ledger_batch.transactions.all():
                        tx.mark_submitted(blockchain_results[0].hash)
                    
                    logger.info(f"Batch {ledger_batch.id} submitted successfully")
                    return True
                else:
                    error_message = blockchain_results[0].error_message if blockchain_results else "Unknown error"
                    ledger_batch.status = 'failed'
                    ledger_batch.failed_at = timezone.now()
                    ledger_batch.error_message = error_message
                    ledger_batch.save()
                    
                    logger.error(f"Batch {ledger_batch.id} submission failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to submit batch {ledger_batch.id}: {e}")
            
            # Mark batch as failed
            ledger_batch.status = 'failed'
            ledger_batch.failed_at = timezone.now()
            ledger_batch.error_message = str(e)
            ledger_batch.save()
            
            return False
    
    def retry_failed_transactions(
        self,
        organization_id: Optional[str] = None,
        max_retries: int = 3
    ) -> Tuple[int, int]:
        """
        Retry failed transactions that can be retried.
        
        Args:
            organization_id: Organization ID (defaults to service organization)
            max_retries: Maximum number of retries per transaction
            
        Returns:
            Tuple of (successful_retries, failed_retries)
        """
        try:
            logger.info("Retrying failed transactions")
            
            # Use service organization if not provided
            if not organization_id:
                organization_id = self.organization_id
            
            # Get failed transactions that can be retried
            failed_transactions = LedgerTransaction.objects.filter(
                organization_id=organization_id,
                status='failed',
                retry_count__lt=max_retries
            )
            
            successful_retries = 0
            failed_retries = 0
            
            for tx in failed_transactions:
                try:
                    # Reset status to pending
                    tx.status = 'pending'
                    tx.error_message = None
                    tx.save()
                    
                    # Try to submit again
                    if self.submit_transaction(tx):
                        successful_retries += 1
                    else:
                        failed_retries += 1
                        
                except Exception as e:
                    logger.error(f"Failed to retry transaction {tx.id}: {e}")
                    failed_retries += 1
            
            logger.info(f"Retry completed: {successful_retries} successful, {failed_retries} failed")
            return successful_retries, failed_retries
            
        except Exception as e:
            logger.error(f"Failed to retry transactions: {e}")
            return 0, 0
    
    def _validate_transaction(self, ledger_transaction: LedgerTransaction) -> bool:
        """Validate a transaction before submission."""
        try:
            # Check if transaction data is valid
            ledger_transaction.clean()
            
            # Verify hash
            if not ledger_transaction.verify_hash():
                logger.error(f"Transaction {ledger_transaction.id} hash verification failed")
                return False
            
            # Check if blockchain service is available
            if not self.blockchain_service or not self.blockchain_service.is_connected():
                logger.error("Blockchain service not available")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Transaction validation failed: {e}")
            return False
    
    def _create_event(
        self,
        ledger_transaction: LedgerTransaction,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> LedgerEvent:
        """Create a ledger event."""
        return LedgerEvent.objects.create(
            transaction=ledger_transaction,
            event_type=event_type,
            event_data=event_data
        )
    
    def get_transaction_stats(
        self,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get transaction statistics for an organization.
        
        Args:
            organization_id: Organization ID (defaults to service organization)
            
        Returns:
            Dictionary with transaction statistics
        """
        try:
            # Use service organization if not provided
            if not organization_id:
                organization_id = self.organization_id
            
            # Get transactions for organization
            transactions = LedgerTransaction.objects.filter(
                organization_id=organization_id
            )
            
            # Calculate statistics
            stats = {
                'total_transactions': transactions.count(),
                'pending_transactions': transactions.filter(status='pending').count(),
                'submitted_transactions': transactions.filter(status='submitted').count(),
                'confirmed_transactions': transactions.filter(status='confirmed').count(),
                'failed_transactions': transactions.filter(status='failed').count(),
                'rejected_transactions': transactions.filter(status='rejected').count(),
                'total_gas_used': sum(tx.gas_used or 0 for tx in transactions if tx.gas_used),
                'last_updated': timezone.now()
            }
            
            # Calculate average confirmation time
            confirmed_transactions = transactions.filter(
                status='confirmed',
                confirmed_at__isnull=False,
                submitted_at__isnull=False
            )
            
            if confirmed_transactions.exists():
                total_time = sum(
                    (tx.confirmed_at - tx.submitted_at).total_seconds()
                    for tx in confirmed_transactions
                )
                stats['average_confirmation_time'] = total_time / confirmed_transactions.count()
            else:
                stats['average_confirmation_time'] = None
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get transaction stats: {e}")
            return {
                'total_transactions': 0,
                'pending_transactions': 0,
                'submitted_transactions': 0,
                'confirmed_transactions': 0,
                'failed_transactions': 0,
                'rejected_transactions': 0,
                'total_gas_used': 0,
                'average_confirmation_time': None,
                'last_updated': timezone.now()
            }

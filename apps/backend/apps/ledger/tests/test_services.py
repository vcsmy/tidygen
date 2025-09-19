"""
Tests for Ledger Services

This module contains tests for the ledger services including TransactionService,
BlockchainService, and HashService.
"""

import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.ledger.models import (
    LedgerTransaction,
    LedgerEvent,
    LedgerBatch,
    LedgerConfiguration
)
from apps.ledger.services import (
    TransactionService,
    BlockchainService,
    HashService
)
from apps.core.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


class HashServiceTest(TestCase):
    """Test cases for HashService."""
    
    def test_generate_transaction_hash(self):
        """Test transaction hash generation."""
        transaction_type = "invoice"
        source_module = "finance"
        source_id = "INV-001"
        transaction_data = {
            "amount": 1000.00,
            "currency": "USD",
            "description": "Test invoice"
        }
        organization_id = "org-123"
        
        hash1 = HashService.generate_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        # Hash should be deterministic
        hash2 = HashService.generate_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length
    
    def test_generate_batch_hash(self):
        """Test batch hash generation."""
        transaction_hashes = [
            "hash1",
            "hash2",
            "hash3"
        ]
        
        batch_hash = HashService.generate_batch_hash(transaction_hashes)
        
        self.assertIsNotNone(batch_hash)
        self.assertEqual(len(batch_hash), 64)  # SHA256 hash length
        
        # Hash should be deterministic
        batch_hash2 = HashService.generate_batch_hash(transaction_hashes)
        self.assertEqual(batch_hash, batch_hash2)
    
    def test_generate_merkle_root(self):
        """Test Merkle root generation."""
        transaction_hashes = [
            "hash1",
            "hash2",
            "hash3",
            "hash4"
        ]
        
        merkle_root = HashService.generate_merkle_root(transaction_hashes)
        
        self.assertIsNotNone(merkle_root)
        self.assertEqual(len(merkle_root), 64)  # SHA256 hash length
        
        # Empty list should return empty hash
        empty_root = HashService.generate_merkle_root([])
        self.assertEqual(len(empty_root), 64)
    
    def test_verify_transaction_hash(self):
        """Test transaction hash verification."""
        transaction_type = "invoice"
        source_module = "finance"
        source_id = "INV-001"
        transaction_data = {
            "amount": 1000.00,
            "currency": "USD",
            "description": "Test invoice"
        }
        organization_id = "org-123"
        
        expected_hash = HashService.generate_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        # Valid hash should return True
        is_valid = HashService.verify_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            expected_hash=expected_hash,
            organization_id=organization_id
        )
        self.assertTrue(is_valid)
        
        # Invalid hash should return False
        is_valid = HashService.verify_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            expected_hash="invalid_hash",
            organization_id=organization_id
        )
        self.assertFalse(is_valid)
    
    def test_hmac_signature(self):
        """Test HMAC signature generation and verification."""
        data = "test data"
        secret_key = "test_secret"
        
        signature = HashService.generate_hmac_signature(data, secret_key)
        
        self.assertIsNotNone(signature)
        self.assertEqual(len(signature), 64)  # SHA256 hash length
        
        # Verify signature
        is_valid = HashService.verify_hmac_signature(data, signature, secret_key)
        self.assertTrue(is_valid)
        
        # Invalid signature should return False
        is_valid = HashService.verify_hmac_signature(data, "invalid_signature", secret_key)
        self.assertFalse(is_valid)
    
    def test_content_hash(self):
        """Test content hash generation."""
        content = "This is test content"
        
        hash1 = HashService.generate_content_hash(content)
        hash2 = HashService.generate_content_hash(content)
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length
    
    def test_validate_hash_format(self):
        """Test hash format validation."""
        valid_hash = "a" * 64
        invalid_hash = "a" * 63  # Too short
        invalid_hash2 = "g" * 64  # Invalid hex character
        
        self.assertTrue(HashService.validate_hash_format(valid_hash))
        self.assertFalse(HashService.validate_hash_format(invalid_hash))
        self.assertFalse(HashService.validate_hash_format(invalid_hash2))
        self.assertFalse(HashService.validate_hash_format("not_a_string"))


class BlockchainServiceTest(TestCase):
    """Test cases for BlockchainService."""
    
    def setUp(self):
        """Set up test data."""
        self.blockchain_service = BlockchainService(
            network='ethereum',
            rpc_endpoint='http://localhost:8545'
        )
    
    def test_initialization(self):
        """Test blockchain service initialization."""
        self.assertEqual(self.blockchain_service.network, 'ethereum')
        self.assertEqual(self.blockchain_service.rpc_endpoint, 'http://localhost:8545')
        self.assertIsNotNone(self.blockchain_service.client)
    
    def test_set_contract_address(self):
        """Test setting contract address."""
        address = "0x1234567890abcdef"
        self.blockchain_service.set_contract_address(address)
        self.assertEqual(self.blockchain_service.contract_address, address)
    
    def test_set_private_key(self):
        """Test setting private key."""
        private_key = "test_private_key"
        self.blockchain_service.set_private_key(private_key)
        self.assertEqual(self.blockchain_service.private_key, private_key)
    
    @patch('apps.ledger.services.blockchain_service.BlockchainService._submit_ethereum_transaction')
    def test_submit_transaction(self, mock_submit):
        """Test transaction submission."""
        # Mock successful submission
        mock_submit.return_value = Mock(
            hash="0x1234567890abcdef",
            status="submitted"
        )
        
        result = self.blockchain_service.submit_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-001",
            transaction_data={"amount": 100.00, "currency": "USD", "description": "Test"},
            transaction_hash="test_hash"
        )
        
        self.assertEqual(result.hash, "0x1234567890abcdef")
        self.assertEqual(result.status, "submitted")
        mock_submit.assert_called_once()
    
    @patch('apps.ledger.services.blockchain_service.BlockchainService._submit_ethereum_batch')
    def test_submit_batch_transactions(self, mock_submit):
        """Test batch transaction submission."""
        # Mock successful batch submission
        mock_submit.return_value = Mock(
            hash="0xabcdef1234567890",
            status="submitted"
        )
        
        transactions = [
            {
                "transaction_type": "invoice",
                "source_module": "finance",
                "source_id": "INV-001",
                "transaction_data": {"amount": 100.00, "currency": "USD", "description": "Test 1"},
                "transaction_hash": "hash1"
            },
            {
                "transaction_type": "payment",
                "source_module": "finance",
                "source_id": "PAY-001",
                "transaction_data": {"amount": 200.00, "currency": "USD", "description": "Test 2"},
                "transaction_hash": "hash2"
            }
        ]
        
        results = self.blockchain_service.submit_batch_transactions(transactions)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].hash, "0xabcdef1234567890")
        self.assertEqual(results[0].status, "submitted")
        mock_submit.assert_called_once()
    
    @patch('apps.ledger.services.blockchain_service.BlockchainService._verify_ethereum_transaction')
    def test_verify_transaction(self, mock_verify):
        """Test transaction verification."""
        # Mock successful verification
        mock_verify.return_value = True
        
        result = self.blockchain_service.verify_transaction("0x1234567890abcdef")
        
        self.assertTrue(result)
        mock_verify.assert_called_once_with("0x1234567890abcdef")
    
    @patch('apps.ledger.services.blockchain_service.BlockchainService._get_ethereum_transaction_details')
    def test_get_transaction_details(self, mock_get_details):
        """Test getting transaction details."""
        # Mock transaction details
        mock_details = {
            "hash": "0x1234567890abcdef",
            "block_number": 12345,
            "transaction_index": 0,
            "gas_used": 21000,
            "gas_price": 20000000000,
            "status": "confirmed"
        }
        mock_get_details.return_value = mock_details
        
        result = self.blockchain_service.get_transaction_details("0x1234567890abcdef")
        
        self.assertEqual(result, mock_details)
        mock_get_details.assert_called_once_with("0x1234567890abcdef")
    
    def test_estimate_gas(self):
        """Test gas estimation."""
        transaction_data = {
            "amount": 100.00,
            "currency": "USD",
            "description": "Test transaction"
        }
        
        gas_estimate = self.blockchain_service.estimate_gas(transaction_data)
        
        self.assertIsInstance(gas_estimate, int)
        self.assertGreater(gas_estimate, 0)
    
    def test_get_current_block_number(self):
        """Test getting current block number."""
        block_number = self.blockchain_service.get_current_block_number()
        
        self.assertIsInstance(block_number, int)
        self.assertGreater(block_number, 0)
    
    def test_is_connected(self):
        """Test connection status."""
        is_connected = self.blockchain_service.is_connected()
        
        self.assertIsInstance(is_connected, bool)


class TransactionServiceTest(TestCase):
    """Test cases for TransactionService."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        # Create ledger configuration
        self.config = LedgerConfiguration.objects.create(
            organization=self.organization,
            blockchain_network="ethereum",
            rpc_endpoint="http://localhost:8545",
            batch_size=10,
            batch_timeout=300,
            retry_attempts=3,
            gas_limit=1000000,
            auto_confirm=True,
            is_active=True
        )
        
        self.transaction_service = TransactionService(
            organization_id=str(self.organization.id)
        )
        
        self.transaction_data = {
            "amount": 1000.00,
            "currency": "USD",
            "description": "Test invoice payment"
        }
    
    def test_initialization(self):
        """Test transaction service initialization."""
        self.assertEqual(self.transaction_service.organization_id, str(self.organization.id))
        self.assertIsNotNone(self.transaction_service.blockchain_service)
    
    def test_create_transaction(self):
        """Test creating a transaction."""
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-001",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id),
            created_by_id=str(self.user.id)
        )
        
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.transaction_type, "invoice")
        self.assertEqual(transaction.source_module, "finance")
        self.assertEqual(transaction.source_id, "INV-001")
        self.assertEqual(transaction.organization, self.organization)
        self.assertEqual(transaction.created_by, self.user)
        self.assertEqual(transaction.status, "pending")
        self.assertIsNotNone(transaction.hash)
    
    def test_create_transaction_without_organization(self):
        """Test creating a transaction without organization ID."""
        with self.assertRaises(ValidationError):
            self.transaction_service.create_transaction(
                transaction_type="invoice",
                source_module="finance",
                source_id="INV-002",
                transaction_data=self.transaction_data,
                organization_id=None
            )
    
    @patch('apps.ledger.services.transaction_service.BlockchainService.submit_transaction')
    def test_submit_transaction(self, mock_submit):
        """Test submitting a transaction."""
        # Create transaction
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-003",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id)
        )
        
        # Mock successful submission
        mock_submit.return_value = Mock(
            hash="0x1234567890abcdef",
            status="submitted"
        )
        
        success = self.transaction_service.submit_transaction(transaction)
        
        self.assertTrue(success)
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, "submitted")
        self.assertEqual(transaction.blockchain_hash, "0x1234567890abcdef")
        mock_submit.assert_called_once()
    
    @patch('apps.ledger.services.transaction_service.BlockchainService.submit_transaction')
    def test_submit_transaction_failure(self, mock_submit):
        """Test transaction submission failure."""
        # Create transaction
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-004",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id)
        )
        
        # Mock failed submission
        mock_submit.return_value = Mock(
            hash="",
            status="failed",
            error_message="Insufficient gas"
        )
        
        success = self.transaction_service.submit_transaction(transaction)
        
        self.assertFalse(success)
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, "failed")
        self.assertEqual(transaction.error_message, "Insufficient gas")
        self.assertEqual(transaction.retry_count, 1)
    
    @patch('apps.ledger.services.transaction_service.BlockchainService.verify_transaction')
    def test_confirm_transaction(self, mock_verify):
        """Test confirming a transaction."""
        # Create and submit transaction
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-005",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id)
        )
        transaction.mark_submitted("0x1234567890abcdef")
        
        # Mock successful verification
        mock_verify.return_value = True
        
        success = self.transaction_service.confirm_transaction(
            transaction,
            block_number=12345,
            transaction_index=0,
            gas_used=21000,
            gas_price=20000000000
        )
        
        self.assertTrue(success)
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, "confirmed")
        self.assertEqual(transaction.block_number, 12345)
        self.assertEqual(transaction.transaction_index, 0)
        self.assertEqual(transaction.gas_used, 21000)
        self.assertEqual(transaction.gas_price, 20000000000)
    
    def test_verify_transaction(self):
        """Test transaction verification."""
        # Create transaction
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-006",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id)
        )
        
        result = self.transaction_service.verify_transaction(
            transaction,
            verify_hash=True,
            verify_blockchain=False
        )
        
        self.assertIn("transaction_id", result)
        self.assertIn("hash_valid", result)
        self.assertIn("verification_timestamp", result)
        self.assertTrue(result["hash_valid"])
    
    def test_create_batch(self):
        """Test creating a batch."""
        # Create transactions
        transactions = []
        for i in range(3):
            transaction = self.transaction_service.create_transaction(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data=self.transaction_data,
                organization_id=str(self.organization.id)
            )
            transactions.append(transaction)
        
        transaction_ids = [str(tx.id) for tx in transactions]
        
        batch = self.transaction_service.create_batch(
            transaction_ids=transaction_ids,
            organization_id=str(self.organization.id)
        )
        
        self.assertIsNotNone(batch.id)
        self.assertEqual(batch.organization, self.organization)
        self.assertEqual(batch.transaction_count, 3)
        self.assertIsNotNone(batch.batch_hash)
    
    @patch('apps.ledger.services.transaction_service.BlockchainService.submit_batch_transactions')
    def test_submit_batch(self, mock_submit):
        """Test submitting a batch."""
        # Create transactions and batch
        transactions = []
        for i in range(2):
            transaction = self.transaction_service.create_transaction(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data=self.transaction_data,
                organization_id=str(self.organization.id)
            )
            transactions.append(transaction)
        
        transaction_ids = [str(tx.id) for tx in transactions]
        batch = self.transaction_service.create_batch(
            transaction_ids=transaction_ids,
            organization_id=str(self.organization.id)
        )
        
        # Mock successful batch submission
        mock_submit.return_value = [Mock(
            hash="0xabcdef1234567890",
            status="submitted"
        )]
        
        success = self.transaction_service.submit_batch(batch)
        
        self.assertTrue(success)
        batch.refresh_from_db()
        self.assertEqual(batch.status, "submitted")
        self.assertEqual(batch.blockchain_hash, "0xabcdef1234567890")
    
    def test_retry_failed_transactions(self):
        """Test retrying failed transactions."""
        # Create failed transaction
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-007",
            transaction_data=self.transaction_data,
            organization_id=str(self.organization.id)
        )
        transaction.mark_failed("Test error")
        
        # Mock successful retry
        with patch.object(self.transaction_service, 'submit_transaction', return_value=True):
            successful, failed = self.transaction_service.retry_failed_transactions(
                organization_id=str(self.organization.id)
            )
        
        self.assertEqual(successful, 1)
        self.assertEqual(failed, 0)
    
    def test_get_transaction_stats(self):
        """Test getting transaction statistics."""
        # Create some test transactions
        for i in range(5):
            transaction = self.transaction_service.create_transaction(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data=self.transaction_data,
                organization_id=str(self.organization.id)
            )
            
            if i % 2 == 0:
                transaction.mark_confirmed(block_number=12345 + i)
            else:
                transaction.mark_failed("Test error")
        
        stats = self.transaction_service.get_transaction_stats(
            organization_id=str(self.organization.id)
        )
        
        self.assertEqual(stats["total_transactions"], 5)
        self.assertEqual(stats["confirmed_transactions"], 3)
        self.assertEqual(stats["failed_transactions"], 2)
        self.assertIn("average_confirmation_time", stats)
        self.assertIn("last_updated", stats)

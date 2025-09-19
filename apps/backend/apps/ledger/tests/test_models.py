"""
Tests for Ledger Models

This module contains tests for the ledger models including LedgerTransaction,
LedgerEvent, LedgerBatch, and LedgerConfiguration.
"""

import uuid
import json
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.ledger.models import (
    LedgerTransaction,
    LedgerEvent,
    LedgerBatch,
    LedgerConfiguration
)
from apps.core.models import Organization

User = get_user_model()


class LedgerTransactionModelTest(TestCase):
    """Test cases for LedgerTransaction model."""
    
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
        
        self.transaction_data = {
            "amount": 1000.00,
            "currency": "USD",
            "description": "Test invoice payment"
        }
    
    def test_create_ledger_transaction(self):
        """Test creating a ledger transaction."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-001",
            transaction_data=self.transaction_data,
            organization=self.organization,
            created_by=self.user
        )
        
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.transaction_type, "invoice")
        self.assertEqual(transaction.source_module, "finance")
        self.assertEqual(transaction.source_id, "INV-001")
        self.assertEqual(transaction.organization, self.organization)
        self.assertEqual(transaction.created_by, self.user)
        self.assertEqual(transaction.status, "pending")
        self.assertIsNotNone(transaction.hash)
        self.assertEqual(len(transaction.hash), 64)  # SHA256 hash length
    
    def test_transaction_hash_generation(self):
        """Test automatic hash generation."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="payment",
            source_module="finance",
            source_id="PAY-001",
            transaction_data=self.transaction_data,
            organization=self.organization
        )
        
        # Hash should be generated automatically
        self.assertIsNotNone(transaction.hash)
        self.assertEqual(len(transaction.hash), 64)
        
        # Hash should be deterministic
        expected_hash = transaction.generate_hash()
        self.assertEqual(transaction.hash, expected_hash)
    
    def test_transaction_hash_verification(self):
        """Test transaction hash verification."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="expense",
            source_module="finance",
            source_id="EXP-001",
            transaction_data=self.transaction_data,
            organization=self.organization
        )
        
        # Hash should be valid
        self.assertTrue(transaction.verify_hash())
        
        # Modify transaction data
        transaction.transaction_data["amount"] = 2000.00
        transaction.save()
        
        # Hash should now be invalid
        self.assertFalse(transaction.verify_hash())
    
    def test_transaction_status_methods(self):
        """Test transaction status management methods."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-002",
            transaction_data=self.transaction_data,
            organization=self.organization
        )
        
        # Test initial status
        self.assertTrue(transaction.is_pending)
        self.assertFalse(transaction.is_confirmed)
        self.assertFalse(transaction.is_failed)
        
        # Test marking as submitted
        transaction.mark_submitted("0x1234567890abcdef")
        self.assertEqual(transaction.status, "submitted")
        self.assertIsNotNone(transaction.submitted_at)
        self.assertEqual(transaction.blockchain_hash, "0x1234567890abcdef")
        
        # Test marking as confirmed
        transaction.mark_confirmed(
            block_number=12345,
            transaction_index=0,
            gas_used=21000,
            gas_price=20000000000
        )
        self.assertEqual(transaction.status, "confirmed")
        self.assertIsNotNone(transaction.confirmed_at)
        self.assertEqual(transaction.block_number, 12345)
        self.assertEqual(transaction.transaction_index, 0)
        self.assertEqual(transaction.gas_used, 21000)
        self.assertEqual(transaction.gas_price, 20000000000)
        self.assertTrue(transaction.is_confirmed)
        
        # Test marking as failed
        transaction.mark_failed("Insufficient gas")
        self.assertEqual(transaction.status, "failed")
        self.assertIsNotNone(transaction.failed_at)
        self.assertEqual(transaction.error_message, "Insufficient gas")
        self.assertEqual(transaction.retry_count, 1)
        self.assertTrue(transaction.is_failed)
    
    def test_transaction_retry_logic(self):
        """Test transaction retry logic."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-003",
            transaction_data=self.transaction_data,
            organization=self.organization
        )
        
        # Initially can retry
        self.assertTrue(transaction.can_retry)
        
        # Mark as failed multiple times
        for i in range(3):
            transaction.mark_failed(f"Error {i}")
        
        # Should not be able to retry after 3 attempts
        self.assertFalse(transaction.can_retry)
        self.assertEqual(transaction.retry_count, 3)
    
    def test_transaction_validation(self):
        """Test transaction data validation."""
        # Test missing required fields
        with self.assertRaises(ValidationError):
            transaction = LedgerTransaction(
                transaction_type="invoice",
                source_module="finance",
                source_id="INV-004",
                transaction_data={},  # Missing required fields
                organization=self.organization
            )
            transaction.clean()
        
        # Test invalid transaction data type
        with self.assertRaises(ValidationError):
            transaction = LedgerTransaction(
                transaction_type="invoice",
                source_module="finance",
                source_id="INV-005",
                transaction_data="invalid",  # Should be dict
                organization=self.organization
            )
            transaction.clean()
    
    def test_unique_constraint(self):
        """Test unique constraint on source module and ID."""
        # Create first transaction
        LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-006",
            transaction_data=self.transaction_data,
            organization=self.organization
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            LedgerTransaction.objects.create(
                transaction_type="payment",  # Different type
                source_module="finance",
                source_id="INV-006",  # Same source ID
                transaction_data=self.transaction_data,
                organization=self.organization
            )


class LedgerEventModelTest(TestCase):
    """Test cases for LedgerEvent model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        self.transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-007",
            transaction_data={"amount": 100.00, "currency": "USD", "description": "Test"},
            organization=self.organization
        )
    
    def test_create_ledger_event(self):
        """Test creating a ledger event."""
        event = LedgerEvent.objects.create(
            transaction=self.transaction,
            event_type="transaction_logged",
            event_data={"status": "created"},
            blockchain_event_id="event_123"
        )
        
        self.assertIsNotNone(event.id)
        self.assertEqual(event.transaction, self.transaction)
        self.assertEqual(event.event_type, "transaction_logged")
        self.assertEqual(event.event_data, {"status": "created"})
        self.assertEqual(event.blockchain_event_id, "event_123")
        self.assertIsNotNone(event.created_at)


class LedgerBatchModelTest(TestCase):
    """Test cases for LedgerBatch model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test transactions
        self.transactions = []
        for i in range(3):
            transaction = LedgerTransaction.objects.create(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data={"amount": 100.00, "currency": "USD", "description": f"Test {i}"},
                organization=self.organization
            )
            self.transactions.append(transaction)
    
    def test_create_ledger_batch(self):
        """Test creating a ledger batch."""
        batch = LedgerBatch.objects.create(
            batch_hash="test_batch_hash",
            organization=self.organization
        )
        
        # Add transactions to batch
        batch.transactions.set(self.transactions)
        
        self.assertIsNotNone(batch.id)
        self.assertEqual(batch.batch_hash, "test_batch_hash")
        self.assertEqual(batch.organization, self.organization)
        self.assertEqual(batch.status, "pending")
        self.assertEqual(batch.transaction_count, 3)
        self.assertFalse(batch.is_confirmed)
        self.assertFalse(batch.is_failed)
    
    def test_batch_status_methods(self):
        """Test batch status management."""
        batch = LedgerBatch.objects.create(
            batch_hash="test_batch_hash_2",
            organization=self.organization
        )
        batch.transactions.set(self.transactions)
        
        # Test initial status
        self.assertFalse(batch.is_confirmed)
        self.assertFalse(batch.is_failed)
        
        # Test marking as confirmed
        batch.status = "confirmed"
        batch.confirmed_at = timezone.now()
        batch.save()
        
        self.assertTrue(batch.is_confirmed)


class LedgerConfigurationModelTest(TestCase):
    """Test cases for LedgerConfiguration model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
    
    def test_create_ledger_configuration(self):
        """Test creating a ledger configuration."""
        config = LedgerConfiguration.objects.create(
            organization=self.organization,
            blockchain_network="ethereum",
            rpc_endpoint="http://localhost:8545",
            contract_address="0x1234567890abcdef",
            batch_size=10,
            batch_timeout=300,
            retry_attempts=3,
            gas_limit=1000000,
            auto_confirm=True,
            is_active=True
        )
        
        self.assertIsNotNone(config.id)
        self.assertEqual(config.organization, self.organization)
        self.assertEqual(config.blockchain_network, "ethereum")
        self.assertEqual(config.rpc_endpoint, "http://localhost:8545")
        self.assertEqual(config.contract_address, "0x1234567890abcdef")
        self.assertEqual(config.batch_size, 10)
        self.assertEqual(config.batch_timeout, 300)
        self.assertEqual(config.retry_attempts, 3)
        self.assertEqual(config.gas_limit, 1000000)
        self.assertTrue(config.auto_confirm)
        self.assertTrue(config.is_active)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test invalid batch size
        with self.assertRaises(ValidationError):
            config = LedgerConfiguration(
                organization=self.organization,
                batch_size=0,  # Invalid
                batch_timeout=300,
                retry_attempts=3
            )
            config.clean()
        
        # Test invalid batch timeout
        with self.assertRaises(ValidationError):
            config = LedgerConfiguration(
                organization=self.organization,
                batch_size=10,
                batch_timeout=0,  # Invalid
                retry_attempts=3
            )
            config.clean()
        
        # Test invalid retry attempts
        with self.assertRaises(ValidationError):
            config = LedgerConfiguration(
                organization=self.organization,
                batch_size=10,
                batch_timeout=300,
                retry_attempts=0  # Invalid
            )
            config.clean()
    
    def test_one_to_one_relationship(self):
        """Test one-to-one relationship with organization."""
        # Create first configuration
        config1 = LedgerConfiguration.objects.create(
            organization=self.organization,
            blockchain_network="ethereum"
        )
        
        # Try to create second configuration for same organization
        with self.assertRaises(Exception):  # IntegrityError
            LedgerConfiguration.objects.create(
                organization=self.organization,
                blockchain_network="substrate"
            )

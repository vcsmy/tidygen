"""
Tests for Ledger Views

This module contains tests for the ledger API views including transaction management,
verification, and audit trail endpoints.
"""

import json
from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.ledger.models import (
    LedgerTransaction,
    LedgerEvent,
    LedgerBatch,
    LedgerConfiguration
)
from apps.core.models import Organization

User = get_user_model()


class LedgerTransactionViewSetTest(APITestCase):
    """Test cases for LedgerTransactionViewSet."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
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
        
        self.transaction_data = {
            "transaction_type": "invoice",
            "source_module": "finance",
            "source_id": "INV-001",
            "transaction_data": {
                "amount": 1000.00,
                "currency": "USD",
                "description": "Test invoice payment"
            }
        }
    
    def test_create_transaction(self):
        """Test creating a transaction via API."""
        url = reverse('ledger:ledger-transaction-list')
        
        response = self.client.post(url, self.transaction_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('hash', response.data)
        self.assertEqual(response.data['transaction_type'], 'invoice')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_list_transactions(self):
        """Test listing transactions."""
        # Create a transaction
        LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-002",
            transaction_data={
                "amount": 500.00,
                "currency": "USD",
                "description": "Test invoice 2"
            },
            organization=self.organization,
            created_by=self.user
        )
        
        url = reverse('ledger:ledger-transaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_transaction_detail(self):
        """Test getting transaction details."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="payment",
            source_module="finance",
            source_id="PAY-001",
            transaction_data={
                "amount": 750.00,
                "currency": "USD",
                "description": "Test payment"
            },
            organization=self.organization,
            created_by=self.user
        )
        
        url = reverse('ledger:ledger-transaction-detail', kwargs={'pk': transaction.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(transaction.id))
        self.assertEqual(response.data['transaction_type'], 'payment')
    
    @patch('apps.ledger.services.transaction_service.TransactionService.submit_transaction')
    def test_submit_transaction(self, mock_submit):
        """Test submitting a transaction to blockchain."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-003",
            transaction_data={
                "amount": 1200.00,
                "currency": "USD",
                "description": "Test invoice 3"
            },
            organization=self.organization,
            created_by=self.user
        )
        
        # Mock successful submission
        mock_submit.return_value = True
        
        url = reverse('ledger:ledger-transaction-submit', kwargs={'pk': transaction.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('transaction', response.data)
        mock_submit.assert_called_once()
    
    @patch('apps.ledger.services.transaction_service.TransactionService.confirm_transaction')
    def test_confirm_transaction(self, mock_confirm):
        """Test confirming a transaction."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-004",
            transaction_data={
                "amount": 800.00,
                "currency": "USD",
                "description": "Test invoice 4"
            },
            organization=self.organization,
            created_by=self.user
        )
        
        # Mock successful confirmation
        mock_confirm.return_value = True
        
        confirmation_data = {
            "block_number": 12345,
            "transaction_index": 0,
            "gas_used": 21000,
            "gas_price": 20000000000
        }
        
        url = reverse('ledger:ledger-transaction-confirm', kwargs={'pk': transaction.id})
        response = self.client.post(url, confirmation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        mock_confirm.assert_called_once()
    
    @patch('apps.ledger.services.transaction_service.TransactionService.verify_transaction')
    def test_verify_transaction(self, mock_verify):
        """Test verifying a transaction."""
        transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-005",
            transaction_data={
                "amount": 900.00,
                "currency": "USD",
                "description": "Test invoice 5"
            },
            organization=self.organization,
            created_by=self.user
        )
        
        # Mock verification result
        mock_verify.return_value = {
            "transaction_id": str(transaction.id),
            "hash_valid": True,
            "blockchain_confirmed": True,
            "verification_timestamp": "2025-01-XX"
        }
        
        verification_data = {
            "verify_hash": True,
            "verify_blockchain": True
        }
        
        url = reverse('ledger:ledger-transaction-verify', kwargs={'pk': transaction.id})
        response = self.client.post(url, verification_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hash_valid', response.data)
        self.assertIn('blockchain_confirmed', response.data)
        mock_verify.assert_called_once()
    
    @patch('apps.ledger.services.transaction_service.TransactionService.get_transaction_stats')
    def test_get_transaction_stats(self, mock_stats):
        """Test getting transaction statistics."""
        # Mock stats data
        mock_stats.return_value = {
            "total_transactions": 10,
            "pending_transactions": 2,
            "confirmed_transactions": 7,
            "failed_transactions": 1,
            "total_gas_used": 210000,
            "average_confirmation_time": 30.5,
            "last_updated": "2025-01-XX"
        }
        
        url = reverse('ledger:ledger-transaction-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_transactions"], 10)
        self.assertEqual(response.data["confirmed_transactions"], 7)
        mock_stats.assert_called_once()


class LedgerPushViewTest(APITestCase):
    """Test cases for LedgerPushView."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create ledger configuration
        self.config = LedgerConfiguration.objects.create(
            organization=self.organization,
            blockchain_network="ethereum",
            rpc_endpoint="http://localhost:8545",
            batch_size=10,
            batch_timeout=300,
            retry_attempts=3,
            gas_limit=1000000,
            auto_confirm=False,  # Disable auto-confirm for testing
            is_active=True
        )
        
        self.valid_data = {
            "transaction_type": "invoice",
            "source_module": "finance",
            "source_id": "INV-001",
            "transaction_data": {
                "amount": 1000.00,
                "currency": "USD",
                "description": "Test invoice payment"
            }
        }
    
    def test_push_transaction_success(self):
        """Test successful transaction push."""
        url = reverse('ledger:ledger-push')
        
        response = self.client.post(url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('hash', response.data)
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['status'], 'pending')
    
    def test_push_transaction_invalid_data(self):
        """Test pushing transaction with invalid data."""
        url = reverse('ledger:ledger-push')
        
        invalid_data = {
            "transaction_type": "invoice",
            "source_module": "finance",
            "source_id": "INV-002",
            "transaction_data": {
                "amount": "invalid",  # Invalid amount
                "currency": "USD",
                "description": "Test invoice"
            }
        }
        
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_push_transaction_missing_fields(self):
        """Test pushing transaction with missing required fields."""
        url = reverse('ledger:ledger-push')
        
        incomplete_data = {
            "transaction_type": "invoice",
            "source_module": "finance",
            # Missing source_id and transaction_data
        }
        
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_push_transaction_unauthorized(self):
        """Test pushing transaction without authentication."""
        self.client.credentials()  # Remove authentication
        
        url = reverse('ledger:ledger-push')
        response = self.client.post(url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LedgerVerifyViewTest(APITestCase):
    """Test cases for LedgerVerifyView."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create a transaction
        self.transaction = LedgerTransaction.objects.create(
            transaction_type="invoice",
            source_module="finance",
            source_id="INV-001",
            transaction_data={
                "amount": 1000.00,
                "currency": "USD",
                "description": "Test invoice"
            },
            organization=self.organization,
            created_by=self.user
        )
    
    @patch('apps.ledger.services.transaction_service.TransactionService.verify_transaction')
    def test_verify_transaction_success(self, mock_verify):
        """Test successful transaction verification."""
        # Mock verification result
        mock_verify.return_value = {
            "transaction_id": str(self.transaction.id),
            "hash_valid": True,
            "blockchain_confirmed": True,
            "blockchain_hash": "0x1234567890abcdef",
            "block_number": 12345,
            "verification_timestamp": "2025-01-XX"
        }
        
        url = reverse('ledger:ledger-verify', kwargs={'transaction_id': self.transaction.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['hash_valid'])
        self.assertTrue(response.data['blockchain_confirmed'])
        mock_verify.assert_called_once()
    
    def test_verify_nonexistent_transaction(self):
        """Test verifying a non-existent transaction."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        url = reverse('ledger:ledger-verify', kwargs={'transaction_id': fake_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_verify_transaction_unauthorized(self):
        """Test verifying transaction without authentication."""
        self.client.credentials()  # Remove authentication
        
        url = reverse('ledger:ledger-verify', kwargs={'transaction_id': self.transaction.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LedgerAuditTrailViewTest(APITestCase):
    """Test cases for LedgerAuditTrailView."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test transactions
        for i in range(5):
            LedgerTransaction.objects.create(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data={
                    "amount": 100.00 * (i + 1),
                    "currency": "USD",
                    "description": f"Test invoice {i}"
                },
                organization=self.organization,
                created_by=self.user
            )
    
    def test_get_audit_trail(self):
        """Test getting audit trail."""
        url = reverse('ledger:ledger-audit')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transactions', response.data)
        self.assertIn('total_count', response.data)
        self.assertIn('has_next', response.data)
        self.assertIn('has_previous', response.data)
        self.assertEqual(response.data['total_count'], 5)
    
    def test_get_audit_trail_with_filters(self):
        """Test getting audit trail with filters."""
        url = reverse('ledger:ledger-audit')
        params = {
            'transaction_type': 'invoice',
            'status': 'pending',
            'limit': 3
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 3)
        self.assertEqual(response.data['total_count'], 5)
    
    def test_get_audit_trail_pagination(self):
        """Test audit trail pagination."""
        url = reverse('ledger:ledger-audit')
        params = {
            'limit': 2,
            'offset': 2
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 2)
        self.assertTrue(response.data['has_next'])
        self.assertTrue(response.data['has_previous'])
        self.assertEqual(response.data['next_offset'], 4)
        self.assertEqual(response.data['previous_offset'], 0)


class LedgerBatchViewSetTest(APITestCase):
    """Test cases for LedgerBatchViewSet."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test transactions
        self.transactions = []
        for i in range(3):
            transaction = LedgerTransaction.objects.create(
                transaction_type="invoice",
                source_module="finance",
                source_id=f"INV-{i:03d}",
                transaction_data={
                    "amount": 100.00 * (i + 1),
                    "currency": "USD",
                    "description": f"Test invoice {i}"
                },
                organization=self.organization,
                created_by=self.user
            )
            self.transactions.append(transaction)
    
    def test_create_batch(self):
        """Test creating a batch."""
        url = reverse('ledger:ledger-batch-list')
        data = {
            "transaction_ids": [str(tx.id) for tx in self.transactions]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('batch_hash', response.data)
        self.assertEqual(response.data['transaction_count'], 3)
    
    def test_create_batch_invalid_transaction_ids(self):
        """Test creating a batch with invalid transaction IDs."""
        url = reverse('ledger:ledger-batch-list')
        data = {
            "transaction_ids": ["invalid-id-1", "invalid-id-2"]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('apps.ledger.services.transaction_service.TransactionService.submit_batch')
    def test_submit_batch(self, mock_submit):
        """Test submitting a batch."""
        # Create a batch
        batch = LedgerBatch.objects.create(
            batch_hash="test_batch_hash",
            organization=self.organization
        )
        batch.transactions.set(self.transactions)
        
        # Mock successful submission
        mock_submit.return_value = True
        
        url = reverse('ledger:ledger-batch-submit', kwargs={'pk': batch.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('batch', response.data)
        mock_submit.assert_called_once()


class LedgerConfigurationViewSetTest(APITestCase):
    """Test cases for LedgerConfigurationViewSet."""
    
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
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_configuration(self):
        """Test creating a ledger configuration."""
        url = reverse('ledger:ledger-configuration-list')
        data = {
            "blockchain_network": "ethereum",
            "rpc_endpoint": "http://localhost:8545",
            "contract_address": "0x1234567890abcdef",
            "batch_size": 10,
            "batch_timeout": 300,
            "retry_attempts": 3,
            "gas_limit": 1000000,
            "auto_confirm": True,
            "is_active": True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['blockchain_network'], 'ethereum')
        self.assertEqual(response.data['organization'], self.organization.id)
    
    def test_get_configuration(self):
        """Test getting ledger configuration."""
        config = LedgerConfiguration.objects.create(
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
        
        url = reverse('ledger:ledger-configuration-detail', kwargs={'pk': config.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], config.id)
        self.assertEqual(response.data['blockchain_network'], 'ethereum')
    
    @patch('apps.ledger.services.blockchain_service.BlockchainService.is_connected')
    def test_test_connection(self, mock_connected):
        """Test connection test endpoint."""
        config = LedgerConfiguration.objects.create(
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
        
        # Mock connection test
        mock_connected.return_value = True
        
        url = reverse('ledger:ledger-configuration-test-connection', kwargs={'pk': config.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['connected'])
        self.assertIn('message', response.data)

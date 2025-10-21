"""
Tests for freelancer_web3 app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import patch, Mock

from .models import (
    FreelancerNFTBadge, FreelancerNFTInstance, FreelancerSmartContract,
    FreelancerReputationToken, FreelancerWalletConnection, FreelancerWeb3Transaction
)

User = get_user_model()


class FreelancerNFTBadgeModelTests(TestCase):
    """Test cases for FreelancerNFTBadge model."""
    
    @patch('apps.freelancer_web3.models.uuid.uuid4')
    def test_badge_id_generation(self, mock_uuid):
        """Test that badge ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        badge = FreelancerNFTBadge.objects.create(
            name='Quality Expert',
            description='Awarded for consistent quality work',
            badge_type='quality_rating',
            rarity='rare',
            required_rating=Decimal('4.5'),
            required_completed_jobs=50
        )
        
        self.assertTrue(badge.badge_id.startswith('BADGE'))
        self.assertEqual(len(badge.badge_id), 13)  # BADGE + 8 chars
    
    def test_badge_creation(self):
        """Test creating an NFT badge."""
        badge = FreelancerNFTBadge.objects.create(
            name='Completion Milestone',
            description='Completed 100 jobs',
            badge_type='completion_milestone',
            rarity='epic',
            required_completed_jobs=100,
            image_url='https://example.com/badge.png',
            color_hex='#FFD700'
        )
        
        self.assertEqual(badge.name, 'Completion Milestone')
        self.assertEqual(badge.badge_type, 'completion_milestone')
        self.assertEqual(badge.rarity, 'epic')
        self.assertTrue(badge.is_active)


class FreelancerNFTInstanceModelTests(TestCase):
    """Test cases for FreelancerNFTInstance model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        self.badge = FreelancerNFTBadge.objects.create(
            name='Quality Expert',
            description='Quality badge',
            badge_type='quality_rating',
            rarity='rare'
        )
    
    def test_nft_instance_creation(self):
        """Test creating an NFT instance."""
        nft_instance = FreelancerNFTInstance.objects.create(
            freelancer=self.freelancer,
            badge=self.badge,
            token_id=12345,
            nft_contract_address='0x1234567890123456789012345678901234567890',
            current_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            original_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            status='minted',
            minted_at=datetime.now(timezone.utc)
        )
        
        self.assertEqual(nft_instance.freelancer, self.freelancer)
        self.assertEqual(nft_instance.badge, self.badge)
        self.assertEqual(nft_instance.token_id, 12345)
        self.assertEqual(nft_instance.status, 'minted')
    
    def test_nft_instance_unique_constraint(self):
        """Test unique constraint on freelancer, badge, and token_id."""
        # Create first instance
        FreelancerNFTInstance.objects.create(
            freelancer=self.freelancer,
            badge=self.badge,
            token_id=12345,
            nft_contract_address='0x1234567890123456789012345678901234567890',
            current_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            original_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        )
        
        # Try to create second instance with same combination - should fail
        with self.assertRaises(IntegrityError):
            FreelancerNFTInstance.objects.create(
                freelancer=self.freelancer,
                badge=self.badge,
                token_id=12345,
                nft_contract_address='0x1234567890123456789012345678901234567890',
                current_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
                original_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
            )


class FreelancerSmartContractModelTests(TestCase):
    """Test cases for FreelancerSmartContract model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    @patch('apps.freelancer_web3.models.uuid.uuid4')
    def test_contract_id_generation(self, mock_uuid):
        """Test that contract ID is generated automatically."""
        mock_uuid.return_value.hex = '12345678abcdef'
        
        contract = FreelancerSmartContract.objects.create(
            name='Service Agreement Contract',
            contract_type='service_agreement',
            freelancer=self.freelancer,
            deployer_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        )
        
        self.assertTrue(contract.contract_id.startswith('CONTRACT'))
        self.assertEqual(len(contract.contract_id), 15)  # CONTRACT + 8 chars
    
    def test_contract_creation(self):
        """Test creating a smart contract."""
        contract = FreelancerSmartContract.objects.create(
            name='Payment Escrow Contract',
            contract_type='payment_escrow',
            freelancer=self.freelancer,
            deployer_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            contract_address='0x1234567890123456789012345678901234567890',
            status='deployed',
            deployed_at=datetime.now(timezone.utc)
        )
        
        self.assertEqual(contract.freelancer, self.freelancer)
        self.assertEqual(contract.contract_type, 'payment_escrow')
        self.assertEqual(contract.status, 'deployed')


class FreelancerReputationTokenModelTests(TestCase):
    """Test cases for FreelancerReputationToken model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_reputation_token_creation(self):
        """Test creating a reputation token."""
        token = FreelancerReputationToken.objects.create(
            freelancer=self.freelancer,
            token_type='quality',
            token_amount=Decimal('100.50'),
            token_contract_address='0x1234567890123456789012345678901234567890'
        )
        
        self.assertEqual(token.freelancer, self.freelancer)
        self.assertEqual(token.token_type, 'quality')
        self.assertEqual(token.token_amount, Decimal('100.50'))
    
    def test_reputation_token_unique_constraint(self):
        """Test unique constraint on freelancer and token_type."""
        # Create first token
        FreelancerReputationToken.objects.create(
            freelancer=self.freelancer,
            token_type='quality',
            token_amount=Decimal('100.00'),
            token_contract_address='0x1234567890123456789012345678901234567890'
        )
        
        # Try to create second token with same type - should fail
        with self.assertRaises(IntegrityError):
            FreelancerReputationToken.objects.create(
                freelancer=self.freelancer,
                token_type='quality',
                token_amount=Decimal('200.00'),
                token_contract_address='0x1234567890123456789012345678901234567890'
            )


class FreelancerWalletConnectionModelTests(TestCase):
    """Test cases for FreelancerWalletConnection model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_wallet_connection_creation(self):
        """Test creating a wallet connection."""
        connection = FreelancerWalletConnection.objects.create(
            freelancer=self.freelancer,
            user=self.user,
            wallet_type='metamask',
            wallet_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            connection_status='connected',
            connected_at=datetime.now(timezone.utc),
            is_primary=True
        )
        
        self.assertEqual(connection.freelancer, self.freelancer)
        self.assertEqual(connection.user, self.user)
        self.assertEqual(connection.wallet_type, 'metamask')
        self.assertTrue(connection.is_primary)
    
    def test_wallet_connection_unique_constraint(self):
        """Test unique constraint on freelancer, wallet_address, and wallet_type."""
        wallet_address = '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        
        # Create first connection
        FreelancerWalletConnection.objects.create(
            freelancer=self.freelancer,
            user=self.user,
            wallet_type='metamask',
            wallet_address=wallet_address,
            connection_status='connected'
        )
        
        # Try to create second connection with same details - should fail
        with self.assertRaises(IntegrityError):
            FreelancerWalletConnection.objects.create(
                freelancer=self.freelancer,
                user=self.user,
                wallet_type='metamask',
                wallet_address=wallet_address,
                connection_status='pending'
            )


class FreelancerWeb3TransactionModelTests(TestCase):
    """Test cases for FreelancerWeb3Transaction model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
    
    def test_web3_transaction_creation(self):
        """Test creating a Web3 transaction."""
        transaction = FreelancerWeb3Transaction.objects.create(
            freelancer=self.freelancer,
            transaction_type='nft_mint',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc',
            blockchain_network='ethereum',
            from_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            to_address='0x1234567890123456789012345678901234567890',
            value_wei=Decimal('1000000000000000000'),  # 1 ETH
            gas_used=21000,
            status='confirmed'
        )
        
        self.assertEqual(transaction.freelancer, self.freelancer)
        self.assertEqual(transaction.transaction_type, 'nft_mint')
        self.assertEqual(transaction.status, 'confirmed')


class FreelancerWeb3APITests(TestCase):
    """Test cases for FreelancerWeb3 API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create freelancer profile
        from apps.freelancers.models import Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Freelancer',
            date_of_birth='1990-01-01',
            personal_email='john@example.com',
            personal_phone='+1234567890',
            address_line1='123 Freelancer St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            hourly_rate=25.00
        )
        
        self.badge = FreelancerNFTBadge.objects.create(
            name='Test Badge',
            description='Test badge description',
            badge_type='completion_milestone'
        )
    
    def authenticate_user(self, user=None):
        """Helper to authenticate user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_nft_badge_list_unauthenticated(self):
        """Test that unauthenticated users cannot access NFT badge list."""
        response = self.client.get('/api/v1/freelancer-web3/badges/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_nft_badge_list_authenticated(self):
        """Test that authenticated users can access NFT badge list."""
        self.authenticate_user()
        response = self.client.get('/api/v1/freelancer-web3/badges/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_connect_wallet(self):
        """Test wallet connection endpoint."""
        self.authenticate_user()
        
        data = {
            'wallet_address': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            'wallet_type': 'metamask',
            'signature': 'test_signature'
        }
        
        response = self.client.post('/api/v1/freelancer-web3/wallets/connect/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify wallet connection was created
        from apps.freelancer_web3.models import FreelancerWalletConnection
        connection = FreelancerWalletConnection.objects.get(
            freelancer=self.freelancer,
            wallet_address=data['wallet_address']
        )
        self.assertEqual(connection.wallet_type, 'metamask')
    
    def test_connect_wallet_duplicate(self):
        """Test connecting duplicate wallet address."""
        self.authenticate_user()
        
        # Create first connection
        from apps.freelancer_web3.models import FreelancerWalletConnection
        FreelancerWalletConnection.objects.create(
            freelancer=self.freelancer,
            user=self.user,
            wallet_type='metamask',
            wallet_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            connection_status='connected'
        )
        
        data = {
            'wallet_address': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            'wallet_type': 'metamask',
            'signature': 'test_signature'
        }
        
        response = self.client.post('/api/v1/freelancer-web3/wallets/connect/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_freelancer_web3_stats(self):
        """Test freelancer Web3 statistics endpoint."""
        self.authenticate_user()
        
        # Create some Web3 data
        from apps.freelancer_web3.models import FreelancerWalletConnection, FreelancerNFTInstance
        FreelancerWalletConnection.objects.create(
            freelancer=self.freelancer,
            user=self.user,
            wallet_type='metamask',
            wallet_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            connection_status='connected'
        )
        
        FreelancerNFTInstance.objects.create(
            freelancer=self.freelancer,
            badge=self.badge,
            token_id=12345,
            nft_contract_address='0x1234567890123456789012345678901234567890',
            current_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            original_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            status='minted'
        )
        
        response = self.client.get(f'/api/v1/freelancer-web3/freelancers/{self.freelancer.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('nft_badges_count', response.data)
        self.assertIn('connected_wallets_count', response.data)
        self.assertEqual(response.data['connected_wallets_count'], 1)
        self.assertEqual(response.data['nft_badges_count'], 1)


@pytest.mark.django_db
class FreelancerWeb3IntegrationTests:
    """Integration tests for freelancer Web3 workflows."""
    
    def test_complete_nft_badge_workflow(self, freelancer_profile):
        """Test complete NFT badge creation and minting workflow."""
        from apps.freelancer_web3.models import FreelancerNFTBadge, FreelancerNFTInstance
        
        # Create badge template
        badge = FreelancerNFTBadge.objects.create(
            name='Quality Star',
            description='Awarded for 5-star quality work',
            badge_type='quality_rating',
            rarity='rare',
            required_rating=Decimal('5.0'),
            required_completed_jobs=10
        )
        
        assert badge.name == 'Quality Star'
        assert badge.is_active
        
        # Create NFT instance
        nft_instance = FreelancerNFTInstance.objects.create(
            freelancer=freelancer_profile,
            badge=badge,
            token_id=98765,
            nft_contract_address='0x1234567890123456789012345678901234567890',
            current_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            original_owner_address='0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            status='minted',
            minted_at=datetime.now(timezone.utc)
        )
        
        assert nft_instance.freelancer == freelancer_profile
        assert nft_instance.badge == badge
        assert nft_instance.status == 'minted'
        
        # Verify relationship
        assert freelancer_profile.nft_badges.filter(badge=badge).exists()
    
    def test_wallet_connection_workflow(self, freelancer_profile):
        """Test wallet connection and Web3 transaction workflow."""
        from apps.freelancer_web3.models import (
            FreelancerWalletConnection, FreelancerWeb3Transaction
        )
        
        wallet_address = '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        
        # Connect wallet
        connection = FreelancerWalletConnection.objects.create(
            freelancer=freelancer_profile,
            user=freelancer_profile.user,
            wallet_type='metamask',
            wallet_address=wallet_address,
            connection_status='connected',
            connected_at=datetime.now(timezone.utc),
            is_primary=True
        )
        
        assert connection.is_primary
        assert connection.connection_status == 'connected'
        
        # Create Web3 transaction
        transaction = FreelancerWeb3Transaction.objects.create(
            freelancer=freelancer_profile,
            transaction_type='wallet_connection',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc',
            blockchain_network='ethereum',
            from_address=wallet_address,
            value_wei=0,
            status='confirmed'
        )
        
        assert transaction.freelancer == freelancer_profile
        assert transaction.transaction_type == 'wallet_connection'
        
        # Verify stats
        assert freelancer_profile.wallet_connections.filter(
            connection_status='connected'
        ).count() == 1
        assert freelancer_profile.web3_transactions.count() == 1

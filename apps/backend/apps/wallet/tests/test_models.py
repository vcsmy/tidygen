"""
Wallet Models Tests

Test cases for wallet-related models including Wallet, WalletSignature,
WalletPermission, and WalletSession models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.wallet.models import Wallet, WalletSignature, WalletPermission, WalletSession

User = get_user_model()


class WalletModelTest(TestCase):
    """Test cases for Wallet model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_wallet_creation(self):
        """Test wallet creation with valid data."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        self.assertEqual(wallet.address, '0x1234567890123456789012345678901234567890')
        self.assertEqual(wallet.wallet_type, 'metamask')
        self.assertEqual(wallet.chain_type, 'ethereum')
        self.assertEqual(wallet.user, self.user)
        self.assertFalse(wallet.is_primary)
        self.assertFalse(wallet.is_verified)
        self.assertTrue(wallet.is_active)
    
    def test_wallet_primary_constraint(self):
        """Test that only one wallet can be primary per user."""
        # Create first wallet as primary
        wallet1 = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user,
            is_primary=True
        )
        
        # Create second wallet as primary
        wallet2 = Wallet.objects.create(
            address='0x0987654321098765432109876543210987654321',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user,
            is_primary=True
        )
        
        # Refresh from database
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        
        # Only the second wallet should be primary
        self.assertFalse(wallet1.is_primary)
        self.assertTrue(wallet2.is_primary)
    
    def test_wallet_short_address(self):
        """Test short address property."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        expected_short = '0x1234567890...567890'
        self.assertEqual(wallet.short_address, expected_short)
    
    def test_wallet_display_name(self):
        """Test display name property."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        expected_display = 'Metamask (0x1234567890...567890)'
        self.assertEqual(wallet.display_name, expected_display)
    
    def test_wallet_verification_message(self):
        """Test verification message generation."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        message, nonce, timestamp = wallet.generate_verification_message()
        
        self.assertIn('TidyGen ERP Wallet Verification', message)
        self.assertIn(wallet.address, message)
        self.assertIn(nonce, message)
        self.assertIn(str(timestamp), message)
        self.assertIsInstance(nonce, str)
        self.assertIsInstance(timestamp, int)
    
    def test_wallet_clean_validation(self):
        """Test wallet clean validation."""
        # Test invalid Ethereum address
        wallet = Wallet(
            address='invalid_address',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        with self.assertRaises(ValidationError):
            wallet.clean()
    
    def test_wallet_str_representation(self):
        """Test wallet string representation."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        expected_str = 'Metamask - 0x1234567890...567890'
        self.assertEqual(str(wallet), expected_str)


class WalletSignatureModelTest(TestCase):
    """Test cases for WalletSignature model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
    
    def test_signature_creation(self):
        """Test signature creation with valid data."""
        signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        self.assertEqual(signature.wallet, self.wallet)
        self.assertEqual(signature.signature_type, 'authentication')
        self.assertEqual(signature.message, 'Test message')
        self.assertEqual(signature.nonce, 'test_nonce')
        self.assertEqual(signature.status, 'pending')
        self.assertFalse(signature.verified)
    
    def test_signature_expiration(self):
        """Test signature expiration check."""
        # Create expired signature
        expired_signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        # Create valid signature
        valid_signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        self.assertTrue(expired_signature.is_expired)
        self.assertFalse(valid_signature.is_expired)
    
    def test_signature_validity(self):
        """Test signature validity check."""
        # Create valid signature
        valid_signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10),
            verified=True
        )
        
        # Create invalid signature (not verified)
        invalid_signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10),
            verified=False
        )
        
        self.assertTrue(valid_signature.is_valid)
        self.assertFalse(invalid_signature.is_valid)
    
    def test_signature_mark_signed(self):
        """Test marking signature as signed."""
        signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        signature.mark_signed('test_signature')
        
        self.assertEqual(signature.signature, 'test_signature')
        self.assertEqual(signature.status, 'signed')
        self.assertIsNotNone(signature.signed_at)
    
    def test_signature_mark_verified(self):
        """Test marking signature as verified."""
        signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        signature.mark_verified()
        
        self.assertTrue(signature.verified)
        self.assertEqual(signature.status, 'verified')
        self.assertIsNotNone(signature.verified_at)
    
    def test_signature_mark_failed(self):
        """Test marking signature as failed."""
        signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        signature.mark_failed()
        
        self.assertEqual(signature.status, 'failed')
    
    def test_signature_str_representation(self):
        """Test signature string representation."""
        signature = WalletSignature.objects.create(
            wallet=self.wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        expected_str = 'Authentication - 0x1234567890...567890 (pending)'
        self.assertEqual(str(signature), expected_str)


class WalletPermissionModelTest(TestCase):
    """Test cases for WalletPermission model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
    
    def test_permission_creation(self):
        """Test permission creation with valid data."""
        permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user
        )
        
        self.assertEqual(permission.wallet, self.wallet)
        self.assertEqual(permission.permission_type, 'read')
        self.assertEqual(permission.resource_type, 'invoice')
        self.assertTrue(permission.granted)
        self.assertEqual(permission.granted_by, self.user)
    
    def test_permission_expiration(self):
        """Test permission expiration check."""
        # Create expired permission
        expired_permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Create valid permission
        valid_permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        self.assertTrue(expired_permission.is_expired)
        self.assertFalse(valid_permission.is_expired)
    
    def test_permission_activity(self):
        """Test permission activity check."""
        # Create active permission
        active_permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Create inactive permission (expired)
        inactive_permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Create denied permission
        denied_permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=False,
            granted_by=self.user
        )
        
        self.assertTrue(active_permission.is_active)
        self.assertFalse(inactive_permission.is_active)
        self.assertFalse(denied_permission.is_active)
    
    def test_permission_str_representation(self):
        """Test permission string representation."""
        permission = WalletPermission.objects.create(
            wallet=self.wallet,
            permission_type='read',
            resource_type='invoice',
            granted=True,
            granted_by=self.user
        )
        
        expected_str = 'Grant read on invoice for 0x1234567890...567890'
        self.assertEqual(str(permission), expected_str)


class WalletSessionModelTest(TestCase):
    """Test cases for WalletSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
    
    def test_session_creation(self):
        """Test session creation with valid data."""
        session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertEqual(session.wallet, self.wallet)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, 'test_session_key')
        self.assertTrue(session.is_active)
    
    def test_session_expiration(self):
        """Test session expiration check."""
        # Create expired session
        expired_session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create valid session
        valid_session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertTrue(expired_session.is_expired)
        self.assertFalse(valid_session.is_expired)
    
    def test_session_validity(self):
        """Test session validity check."""
        # Create valid session
        valid_session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Create invalid session (inactive)
        invalid_session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24),
            is_active=False
        )
        
        self.assertTrue(valid_session.is_valid)
        self.assertFalse(invalid_session.is_valid)
    
    def test_session_deactivation(self):
        """Test session deactivation."""
        session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        session.deactivate()
        
        self.assertFalse(session.is_active)
    
    def test_session_extension(self):
        """Test session extension."""
        session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        original_expiry = session.expires_at
        session.extend(hours=12)
        
        expected_expiry = original_expiry + timedelta(hours=12)
        self.assertEqual(session.expires_at, expected_expiry)
    
    def test_session_str_representation(self):
        """Test session string representation."""
        session = WalletSession.objects.create(
            wallet=self.wallet,
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        expected_str = f'Session {session.id} - 0x1234567890...567890 (Active)'
        self.assertEqual(str(session), expected_str)

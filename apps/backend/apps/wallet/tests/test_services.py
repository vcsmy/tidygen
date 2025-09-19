"""
Wallet Services Tests

Test cases for wallet-related services including SignatureService,
MetaMaskService, PolkadotService, and WalletService.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone
from datetime import timedelta

from apps.wallet.models import Wallet, WalletSignature, WalletPermission, WalletSession
from apps.wallet.services import (
    SignatureService, 
    MetaMaskService, 
    PolkadotService, 
    WalletService
)

User = get_user_model()


class SignatureServiceTest(TestCase):
    """Test cases for SignatureService."""
    
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
    
    def test_generate_authentication_message(self):
        """Test authentication message generation."""
        address = '0x1234567890123456789012345678901234567890'
        nonce = 'test_nonce'
        timestamp = 1234567890
        
        message = SignatureService.generate_authentication_message(
            address=address,
            nonce=nonce,
            timestamp=timestamp
        )
        
        self.assertIn('TidyGen ERP Authentication', message)
        self.assertIn(address, message)
        self.assertIn(nonce, message)
        self.assertIn(str(timestamp), message)
    
    def test_generate_transaction_message(self):
        """Test transaction message generation."""
        transaction_data = {
            'type': 'payment',
            'amount': '100.0',
            'currency': 'ETH',
            'description': 'Test payment'
        }
        nonce = 'test_nonce'
        timestamp = 1234567890
        
        message = SignatureService.generate_transaction_message(
            transaction_data=transaction_data,
            nonce=nonce,
            timestamp=timestamp
        )
        
        self.assertIn('TidyGen ERP Transaction Signing', message)
        self.assertIn('payment', message)
        self.assertIn('100.0', message)
        self.assertIn('ETH', message)
        self.assertIn(nonce, message)
        self.assertIn(str(timestamp), message)
    
    def test_validate_message_format(self):
        """Test message format validation."""
        valid_message = """TidyGen ERP Authentication

Please sign this message to authenticate with your wallet.

Address: 0x1234567890123456789012345678901234567890
Nonce: test_nonce
Timestamp: 1234567890

This request will not trigger a blockchain transaction or cost any gas fees."""
        
        invalid_message = "Invalid message"
        
        self.assertTrue(SignatureService.validate_message_format(valid_message))
        self.assertFalse(SignatureService.validate_message_format(invalid_message))
    
    def test_extract_message_components(self):
        """Test message component extraction."""
        message = """TidyGen ERP Authentication

Address: 0x1234567890123456789012345678901234567890
Nonce: test_nonce
Timestamp: 1234567890"""
        
        components = SignatureService.extract_message_components(message)
        
        self.assertEqual(components['address'], '0x1234567890123456789012345678901234567890')
        self.assertEqual(components['nonce'], 'test_nonce')
        self.assertEqual(components['timestamp'], '1234567890')
    
    def test_generate_nonce(self):
        """Test nonce generation."""
        nonce1 = SignatureService.generate_nonce()
        nonce2 = SignatureService.generate_nonce()
        
        self.assertIsInstance(nonce1, str)
        self.assertIsInstance(nonce2, str)
        self.assertNotEqual(nonce1, nonce2)
        self.assertEqual(len(nonce1), 32)  # 16 bytes = 32 hex chars
    
    def test_create_message_hash(self):
        """Test message hash creation."""
        message = "Test message"
        hash1 = SignatureService.create_message_hash(message)
        hash2 = SignatureService.create_message_hash(message)
        
        self.assertIsInstance(hash1, str)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length
    
    def test_verify_message_integrity(self):
        """Test message integrity verification."""
        original_message = "Test message"
        received_message = "Test message"
        modified_message = "Modified message"
        
        self.assertTrue(SignatureService.verify_message_integrity(original_message, received_message))
        self.assertFalse(SignatureService.verify_message_integrity(original_message, modified_message))
    
    def test_check_signature_replay_attack(self):
        """Test replay attack check."""
        nonce = 'test_nonce'
        current_timestamp = int(timezone.now().timestamp())
        
        # Valid timestamp (recent)
        valid_timestamp = current_timestamp - 60  # 1 minute ago
        self.assertTrue(SignatureService.check_signature_replay_attack(nonce, valid_timestamp))
        
        # Invalid timestamp (too old)
        old_timestamp = current_timestamp - 400  # More than 5 minutes ago
        self.assertFalse(SignatureService.check_signature_replay_attack(nonce, old_timestamp))
        
        # Invalid timestamp (future)
        future_timestamp = current_timestamp + 120  # 2 minutes in future
        self.assertFalse(SignatureService.check_signature_replay_attack(nonce, future_timestamp))
    
    @patch('apps.wallet.services.signature_service.ETH_ACCOUNT_AVAILABLE', True)
    def test_verify_ethereum_signature_with_eth_account(self):
        """Test Ethereum signature verification with eth-account available."""
        with patch('apps.wallet.services.signature_service.Account') as mock_account:
            mock_account.recover_message.return_value = '0x1234567890123456789012345678901234567890'
            
            result = SignatureService.verify_ethereum_signature(
                message='Test message',
                signature='test_signature',
                address='0x1234567890123456789012345678901234567890'
            )
            
            self.assertTrue(result)
            mock_account.recover_message.assert_called_once()
    
    @patch('apps.wallet.services.signature_service.ETH_ACCOUNT_AVAILABLE', False)
    def test_verify_ethereum_signature_without_eth_account(self):
        """Test Ethereum signature verification without eth-account."""
        result = SignatureService.verify_ethereum_signature(
            message='Test message',
            signature='test_signature',
            address='0x1234567890123456789012345678901234567890'
        )
        
        self.assertTrue(result)  # Should return True for mock verification
    
    def test_verify_substrate_signature(self):
        """Test Substrate signature verification."""
        result = SignatureService.verify_substrate_signature(
            message='Test message',
            signature='test_signature',
            address='5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
        )
        
        self.assertTrue(result)  # Mock implementation returns True
    
    def test_verify_signature_metamask(self):
        """Test signature verification for MetaMask."""
        with patch.object(SignatureService, 'verify_ethereum_signature', return_value=True) as mock_verify:
            result = SignatureService.verify_signature(
                wallet_type='metamask',
                message='Test message',
                signature='test_signature',
                address='0x1234567890123456789012345678901234567890'
            )
            
            self.assertTrue(result)
            mock_verify.assert_called_once()
    
    def test_verify_signature_polkadot(self):
        """Test signature verification for Polkadot."""
        with patch.object(SignatureService, 'verify_substrate_signature', return_value=True) as mock_verify:
            result = SignatureService.verify_signature(
                wallet_type='polkadot',
                message='Test message',
                signature='test_signature',
                address='5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
            )
            
            self.assertTrue(result)
            mock_verify.assert_called_once()
    
    def test_verify_signature_unsupported(self):
        """Test signature verification for unsupported wallet type."""
        result = SignatureService.verify_signature(
            wallet_type='unsupported',
            message='Test message',
            signature='test_signature',
            address='test_address'
        )
        
        self.assertFalse(result)


class MetaMaskServiceTest(TestCase):
    """Test cases for MetaMaskService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = MetaMaskService()
    
    @patch('apps.wallet.services.metamask_service.WEB3_AVAILABLE', True)
    def test_initialize_web3_with_web3(self):
        """Test Web3 initialization with web3 available."""
        with patch('apps.wallet.services.metamask_service.Web3') as mock_web3:
            mock_instance = Mock()
            mock_instance.is_connected.return_value = True
            mock_web3.return_value = mock_instance
            
            service = MetaMaskService()
            
            self.assertIsNotNone(service.web3)
            mock_web3.assert_called_once()
    
    @patch('apps.wallet.services.metamask_service.WEB3_AVAILABLE', False)
    def test_initialize_web3_without_web3(self):
        """Test Web3 initialization without web3."""
        service = MetaMaskService()
        
        self.assertIsNotNone(service.web3)
        self.assertTrue(hasattr(service.web3, 'is_connected'))
    
    def test_is_connected(self):
        """Test connection status check."""
        # Mock web3 instance
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = True
        self.service.web3 = mock_web3
        
        self.assertTrue(self.service.is_connected())
    
    def test_validate_address(self):
        """Test address validation."""
        # Mock web3 instance
        mock_web3 = Mock()
        mock_web3.is_address.return_value = True
        mock_web3.is_checksum_address.return_value = True
        self.service.web3 = mock_web3
        
        valid_address = '0x1234567890123456789012345678901234567890'
        invalid_address = 'invalid_address'
        
        self.assertTrue(self.service.validate_address(valid_address))
        self.assertFalse(self.service.validate_address(invalid_address))
    
    def test_get_address_balance(self):
        """Test address balance retrieval."""
        # Mock web3 instance
        mock_web3 = Mock()
        mock_web3.is_address.return_value = True
        mock_web3.is_checksum_address.return_value = True
        mock_web3.from_wei.return_value = 1.0
        mock_web3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
        self.service.web3 = mock_web3
        
        result = self.service.get_address_balance('0x1234567890123456789012345678901234567890')
        
        self.assertEqual(result['balance_eth'], '1.0')
        self.assertEqual(result['currency'], 'ETH')
    
    def test_get_network_info(self):
        """Test network information retrieval."""
        # Mock web3 instance
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = True
        mock_web3.eth.chain_id = 1
        mock_web3.eth.block_number = 12345
        mock_web3.eth.gas_price = 20000000000
        self.service.web3 = mock_web3
        
        result = self.service.get_network_info()
        
        self.assertEqual(result['chain_id'], 1)
        self.assertEqual(result['network_name'], 'Ethereum Mainnet')
        self.assertTrue(result['connected'])
    
    def test_get_supported_networks(self):
        """Test supported networks list."""
        networks = self.service.get_supported_networks()
        
        self.assertIsInstance(networks, list)
        self.assertGreater(len(networks), 0)
        
        # Check for Ethereum mainnet
        ethereum_mainnet = next((net for net in networks if net['chain_id'] == 1), None)
        self.assertIsNotNone(ethereum_mainnet)
        self.assertEqual(ethereum_mainnet['name'], 'Ethereum Mainnet')


class PolkadotServiceTest(TestCase):
    """Test cases for PolkadotService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = PolkadotService()
    
    def test_initialize_substrate_with_substrate_interface(self):
        """Test Substrate initialization with substrate-interface available."""
        with patch('apps.wallet.services.polkadot_service.SubstrateInterface') as mock_substrate:
            mock_instance = Mock()
            mock_substrate.return_value = mock_instance
            
            service = PolkadotService()
            
            self.assertIsNotNone(service.substrate)
    
    def test_initialize_substrate_without_substrate_interface(self):
        """Test Substrate initialization without substrate-interface."""
        with patch('apps.wallet.services.polkadot_service.SubstrateInterface', side_effect=ImportError):
            service = PolkadotService()
            
            self.assertIsNotNone(service.substrate)
            self.assertTrue(hasattr(service.substrate, 'connected'))
    
    def test_is_connected(self):
        """Test connection status check."""
        # Mock substrate instance
        mock_substrate = Mock()
        mock_substrate.connected = True
        self.service.substrate = mock_substrate
        
        self.assertTrue(self.service.is_connected())
    
    def test_validate_address(self):
        """Test address validation."""
        valid_address = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
        invalid_address = 'invalid'
        
        self.assertTrue(self.service.validate_address(valid_address))
        self.assertFalse(self.service.validate_address(invalid_address))
    
    def test_get_network_info(self):
        """Test network information retrieval."""
        # Mock substrate instance
        mock_substrate = Mock()
        mock_substrate.get_chain_name.return_value = 'Polkadot'
        mock_substrate.get_chain_version.return_value = '0.9.0'
        mock_substrate.get_chain_properties.return_value = {'ss58Format': 0}
        self.service.substrate = mock_substrate
        
        result = self.service.get_network_info()
        
        self.assertEqual(result['chain_name'], 'Polkadot')
        self.assertEqual(result['chain_version'], '0.9.0')
        self.assertTrue(result['connected'])
    
    def test_get_supported_networks(self):
        """Test supported networks list."""
        networks = self.service.get_supported_networks()
        
        self.assertIsInstance(networks, list)
        self.assertGreater(len(networks), 0)
        
        # Check for Polkadot mainnet
        polkadot_mainnet = next((net for net in networks if net['chain_id'] == 'polkadot'), None)
        self.assertIsNotNone(polkadot_mainnet)
        self.assertEqual(polkadot_mainnet['name'], 'Polkadot')


class WalletServiceTest(TestCase):
    """Test cases for WalletService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.service = WalletService()
    
    def test_get_supported_wallet_types(self):
        """Test supported wallet types."""
        wallet_types = self.service.get_supported_wallet_types()
        
        self.assertIsInstance(wallet_types, list)
        self.assertGreater(len(wallet_types), 0)
        
        # Check for MetaMask
        metamask = next((wt for wt in wallet_types if wt['type'] == 'metamask'), None)
        self.assertIsNotNone(metamask)
        self.assertEqual(metamask['name'], 'MetaMask')
        
        # Check for Polkadot
        polkadot = next((wt for wt in wallet_types if wt['type'] == 'polkadot'), None)
        self.assertIsNotNone(polkadot)
        self.assertEqual(polkadot['name'], 'Polkadot.js')
    
    def test_connect_wallet_metamask(self):
        """Test MetaMask wallet connection."""
        with patch.object(self.service.metamask_service, 'validate_address', return_value=True):
            result = self.service.connect_wallet(
                wallet_type='metamask',
                address='0x1234567890123456789012345678901234567890',
                chain_id='1',
                network_name='Ethereum Mainnet'
            )
            
            self.assertIn('wallet_id', result)
            self.assertEqual(result['address'], '0x1234567890123456789012345678901234567890')
            self.assertEqual(result['wallet_type'], 'metamask')
    
    def test_connect_wallet_polkadot(self):
        """Test Polkadot wallet connection."""
        with patch.object(self.service.polkadot_service, 'validate_address', return_value=True):
            result = self.service.connect_wallet(
                wallet_type='polkadot',
                address='5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
                chain_id='polkadot',
                network_name='Polkadot'
            )
            
            self.assertIn('wallet_id', result)
            self.assertEqual(result['address'], '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')
            self.assertEqual(result['wallet_type'], 'polkadot')
    
    def test_connect_wallet_unsupported_type(self):
        """Test connection with unsupported wallet type."""
        result = self.service.connect_wallet(
            wallet_type='unsupported',
            address='test_address',
            chain_id='1',
            network_name='Test Network'
        )
        
        self.assertIn('error', result)
        self.assertIn('Unsupported wallet type', result['error'])
    
    def test_connect_wallet_invalid_address(self):
        """Test connection with invalid address."""
        with patch.object(self.service.metamask_service, 'validate_address', return_value=False):
            result = self.service.connect_wallet(
                wallet_type='metamask',
                address='invalid_address',
                chain_id='1',
                network_name='Ethereum Mainnet'
            )
            
            self.assertIn('error', result)
            self.assertIn('Invalid Ethereum address', result['error'])
    
    def test_request_authentication(self):
        """Test authentication request."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        result = self.service.request_authentication(
            wallet_id=str(wallet.id),
            user_id=str(self.user.id)
        )
        
        self.assertIn('signature_id', result)
        self.assertIn('message', result)
        self.assertIn('nonce', result)
        self.assertEqual(result['wallet_id'], str(wallet.id))
    
    def test_verify_authentication(self):
        """Test authentication verification."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        # Create signature request
        signature_request = WalletSignature.objects.create(
            wallet=wallet,
            signature_type='authentication',
            message='Test message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        with patch.object(self.service.signature_service, 'verify_signature', return_value=True):
            result = self.service.verify_authentication(
                signature_id=str(signature_request.id),
                signature='test_signature',
                user_id=str(self.user.id)
            )
            
            self.assertTrue(result['success'])
            self.assertIn('access_token', result)
            self.assertIn('refresh_token', result)
    
    def test_get_user_wallets(self):
        """Test getting user wallets."""
        wallet1 = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        wallet2 = Wallet.objects.create(
            address='0x0987654321098765432109876543210987654321',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        wallets = self.service.get_user_wallets(str(self.user.id))
        
        self.assertEqual(len(wallets), 2)
        self.assertEqual(wallets[0]['address'], wallet1.address)
        self.assertEqual(wallets[1]['address'], wallet2.address)
    
    def test_set_primary_wallet(self):
        """Test setting primary wallet."""
        wallet1 = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user,
            is_primary=True
        )
        
        wallet2 = Wallet.objects.create(
            address='0x0987654321098765432109876543210987654321',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        result = self.service.set_primary_wallet(
            user_id=str(self.user.id),
            wallet_id=str(wallet2.id)
        )
        
        self.assertTrue(result['success'])
        
        # Refresh from database
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        
        self.assertFalse(wallet1.is_primary)
        self.assertTrue(wallet2.is_primary)
    
    def test_disconnect_wallet(self):
        """Test wallet disconnection."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        result = self.service.disconnect_wallet(
            user_id=str(self.user.id),
            wallet_id=str(wallet.id)
        )
        
        self.assertTrue(result['success'])
        
        # Refresh from database
        wallet.refresh_from_db()
        self.assertFalse(wallet.is_active)
    
    def test_request_transaction_signature(self):
        """Test transaction signature request."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        transaction_data = {
            'type': 'payment',
            'amount': '100.0',
            'currency': 'ETH',
            'description': 'Test payment'
        }
        
        result = self.service.request_transaction_signature(
            wallet_id=str(wallet.id),
            transaction_data=transaction_data,
            user_id=str(self.user.id)
        )
        
        self.assertIn('signature_id', result)
        self.assertIn('message', result)
        self.assertIn('transaction_data', result)
        self.assertEqual(result['transaction_data'], transaction_data)
    
    def test_verify_transaction_signature(self):
        """Test transaction signature verification."""
        wallet = Wallet.objects.create(
            address='0x1234567890123456789012345678901234567890',
            wallet_type='metamask',
            chain_type='ethereum',
            chain_id='1',
            network_name='Ethereum Mainnet',
            user=self.user
        )
        
        # Create signature request
        signature_request = WalletSignature.objects.create(
            wallet=wallet,
            signature_type='transaction',
            message='Test transaction message',
            nonce='test_nonce',
            expires_at=timezone.now() + timedelta(minutes=30),
            metadata={'type': 'payment', 'amount': '100.0'}
        )
        
        with patch.object(self.service.signature_service, 'verify_signature', return_value=True):
            result = self.service.verify_transaction_signature(
                signature_id=str(signature_request.id),
                signature='test_signature'
            )
            
            self.assertTrue(result['success'])
            self.assertIn('transaction_data', result)

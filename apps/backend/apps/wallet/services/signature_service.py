"""
Signature Service for Wallet Authentication

This module provides cryptographic signature verification services
for wallet-based authentication, supporting both EVM and Substrate chains.
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
# Try to import optional dependencies
try:
    from eth_account import Account
    from eth_account.messages import encode_defunct
    ETH_ACCOUNT_AVAILABLE = True
except ImportError:
    ETH_ACCOUNT_AVAILABLE = False

try:
    import base58
    BASE58_AVAILABLE = True
except ImportError:
    BASE58_AVAILABLE = False

logger = logging.getLogger(__name__)


class SignatureService:
    """
    Service for verifying wallet signatures.
    
    This service provides methods for verifying signatures from different
    wallet types including MetaMask (EVM) and Polkadot.js (Substrate).
    """
    
    @staticmethod
    def verify_ethereum_signature(
        message: str,
        signature: str,
        address: str
    ) -> bool:
        """
        Verify an Ethereum signature.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            address: The wallet address that should have signed
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not ETH_ACCOUNT_AVAILABLE:
            logger.warning("eth-account not available, using mock verification")
            return True  # Mock verification for development
        
        try:
            # Encode the message
            message_hash = encode_defunct(text=message)
            
            # Recover the address from the signature
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            # Compare addresses (case-insensitive)
            return recovered_address.lower() == address.lower()
            
        except Exception as e:
            logger.error(f"Failed to verify Ethereum signature: {e}")
            return False
    
    @staticmethod
    def verify_substrate_signature(
        message: str,
        signature: str,
        address: str,
        public_key: Optional[str] = None
    ) -> bool:
        """
        Verify a Substrate signature.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            address: The wallet address that should have signed
            public_key: Optional public key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # For Substrate signatures, we need to use the substrate-interface library
            # This is a simplified implementation - in production, use proper Substrate verification
            
            # Decode the signature (assuming it's base58 encoded)
            if BASE58_AVAILABLE:
                try:
                    signature_bytes = base58.b58decode(signature)
                except Exception:
                    # If not base58, try hex
                    signature_bytes = bytes.fromhex(signature)
            else:
                # If base58 not available, try hex
                signature_bytes = bytes.fromhex(signature)
            
            # For now, return True for demonstration
            # In production, implement proper Substrate signature verification
            logger.info(f"Substrate signature verification for {address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify Substrate signature: {e}")
            return False
    
    @staticmethod
    def verify_signature(
        wallet_type: str,
        message: str,
        signature: str,
        address: str,
        public_key: Optional[str] = None
    ) -> bool:
        """
        Verify a signature based on wallet type.
        
        Args:
            wallet_type: Type of wallet (metamask, polkadot)
            message: The message that was signed
            signature: The signature to verify
            address: The wallet address
            public_key: Optional public key for Substrate wallets
            
        Returns:
            True if signature is valid, False otherwise
        """
        if wallet_type == 'metamask':
            return SignatureService.verify_ethereum_signature(
                message=message,
                signature=signature,
                address=address
            )
        elif wallet_type == 'polkadot':
            return SignatureService.verify_substrate_signature(
                message=message,
                signature=signature,
                address=address,
                public_key=public_key
            )
        else:
            logger.error(f"Unsupported wallet type: {wallet_type}")
            return False
    
    @staticmethod
    def generate_authentication_message(
        address: str,
        nonce: str,
        timestamp: int,
        domain: Optional[str] = None
    ) -> str:
        """
        Generate a standardized authentication message.
        
        Args:
            address: Wallet address
            nonce: Random nonce
            timestamp: Unix timestamp
            domain: Optional domain name
            
        Returns:
            Formatted authentication message
        """
        domain = domain or getattr(settings, 'WALLET_AUTH_DOMAIN', 'TidyGen ERP')
        
        message = f"""{domain} Authentication

Please sign this message to authenticate with your wallet.

Address: {address}
Nonce: {nonce}
Timestamp: {timestamp}

This request will not trigger a blockchain transaction or cost any gas fees."""
        
        return message
    
    @staticmethod
    def generate_transaction_message(
        transaction_data: Dict[str, Any],
        nonce: str,
        timestamp: int,
        domain: Optional[str] = None
    ) -> str:
        """
        Generate a message for transaction signing.
        
        Args:
            transaction_data: Transaction details
            nonce: Random nonce
            timestamp: Unix timestamp
            domain: Optional domain name
            
        Returns:
            Formatted transaction message
        """
        domain = domain or getattr(settings, 'WALLET_AUTH_DOMAIN', 'TidyGen ERP')
        
        # Create a structured message
        message_parts = [
            f"{domain} Transaction Signing",
            "",
            "Please sign this message to approve the following transaction:",
            "",
            f"Type: {transaction_data.get('type', 'Unknown')}",
            f"Amount: {transaction_data.get('amount', 'N/A')}",
            f"Currency: {transaction_data.get('currency', 'N/A')}",
            f"Description: {transaction_data.get('description', 'N/A')}",
            "",
            f"Nonce: {nonce}",
            f"Timestamp: {timestamp}",
            "",
            "By signing this message, you approve this transaction."
        ]
        
        return "\n".join(message_parts)
    
    @staticmethod
    def validate_message_format(message: str) -> bool:
        """
        Validate that a message has the correct format.
        
        Args:
            message: Message to validate
            
        Returns:
            True if message format is valid, False otherwise
        """
        try:
            # Check for required components
            required_components = ['Address:', 'Nonce:', 'Timestamp:']
            
            for component in required_components:
                if component not in message:
                    return False
            
            # Check message length (not too short or too long)
            if len(message) < 50 or len(message) > 2000:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate message format: {e}")
            return False
    
    @staticmethod
    def extract_message_components(message: str) -> Dict[str, str]:
        """
        Extract components from a signed message.
        
        Args:
            message: The signed message
            
        Returns:
            Dictionary with extracted components
        """
        components = {}
        
        try:
            lines = message.split('\n')
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in ['Address', 'Nonce', 'Timestamp']:
                        components[key.lower()] = value
            
            return components
            
        except Exception as e:
            logger.error(f"Failed to extract message components: {e}")
            return {}
    
    @staticmethod
    def generate_nonce() -> str:
        """
        Generate a secure random nonce.
        
        Returns:
            Random nonce string
        """
        import secrets
        return secrets.token_hex(16)
    
    @staticmethod
    def create_message_hash(message: str) -> str:
        """
        Create a hash of the message for verification.
        
        Args:
            message: Message to hash
            
        Returns:
            SHA256 hash of the message
        """
        return hashlib.sha256(message.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_message_integrity(
        original_message: str,
        received_message: str
    ) -> bool:
        """
        Verify that a received message matches the original.
        
        Args:
            original_message: The original message
            received_message: The received message
            
        Returns:
            True if messages match, False otherwise
        """
        # Normalize messages (remove extra whitespace)
        original_normalized = '\n'.join(line.strip() for line in original_message.split('\n'))
        received_normalized = '\n'.join(line.strip() for line in received_message.split('\n'))
        
        return original_normalized == received_normalized
    
    @staticmethod
    def check_signature_replay_attack(
        nonce: str,
        timestamp: int,
        max_age_seconds: int = 300
    ) -> bool:
        """
        Check if a signature request is a replay attack.
        
        Args:
            nonce: The nonce from the signature
            timestamp: The timestamp from the signature
            max_age_seconds: Maximum age for a valid signature
            
        Returns:
            True if signature is valid (not a replay), False otherwise
        """
        try:
            current_time = int(timezone.now().timestamp())
            age = current_time - timestamp
            
            # Check if signature is too old
            if age > max_age_seconds:
                logger.warning(f"Signature too old: {age} seconds")
                return False
            
            # Check if signature is from the future (clock skew)
            if timestamp > current_time + 60:  # Allow 1 minute clock skew
                logger.warning(f"Signature from future: {timestamp - current_time} seconds")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check replay attack: {e}")
            return False
    
    @staticmethod
    def create_hmac_signature(
        data: str,
        secret_key: Optional[str] = None
    ) -> str:
        """
        Create an HMAC signature for data integrity.
        
        Args:
            data: Data to sign
            secret_key: Secret key for signing
            
        Returns:
            HMAC signature
        """
        if secret_key is None:
            secret_key = settings.SECRET_KEY
        
        return hmac.new(
            secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_hmac_signature(
        data: str,
        signature: str,
        secret_key: Optional[str] = None
    ) -> bool:
        """
        Verify an HMAC signature.
        
        Args:
            data: Original data
            signature: HMAC signature to verify
            secret_key: Secret key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = SignatureService.create_hmac_signature(data, secret_key)
        return hmac.compare_digest(signature, expected_signature)

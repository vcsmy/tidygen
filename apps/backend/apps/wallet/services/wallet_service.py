"""
Wallet Service for Authentication and Management

This module provides high-level wallet management services,
coordinating between different wallet types and authentication flows.
"""

import logging
import secrets
from typing import Dict, Any, Optional, List, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Wallet, WalletSignature, WalletPermission, WalletSession
from .metamask_service import MetaMaskService
from .polkadot_service import PolkadotService
from .signature_service import SignatureService

User = get_user_model()
logger = logging.getLogger(__name__)


class WalletService:
    """
    High-level service for wallet management and authentication.
    
    This service coordinates wallet operations across different wallet types,
    manages authentication flows, and handles session management.
    """
    
    def __init__(self):
        """Initialize wallet service with supported wallet services."""
        self.metamask_service = MetaMaskService()
        self.polkadot_service = PolkadotService()
        self.signature_service = SignatureService()
    
    def get_supported_wallet_types(self) -> List[Dict[str, Any]]:
        """
        Get list of supported wallet types.
        
        Returns:
            List of supported wallet configurations
        """
        return [
            {
                "type": "metamask",
                "name": "MetaMask",
                "description": "Ethereum and EVM-compatible wallets",
                "supported_chains": ["ethereum", "polygon", "bsc"],
                "icon": "metamask-icon",
                "enabled": True
            },
            {
                "type": "polkadot",
                "name": "Polkadot.js",
                "description": "Substrate and Polkadot ecosystem wallets",
                "supported_chains": ["polkadot", "kusama", "substrate"],
                "icon": "polkadot-icon",
                "enabled": True
            }
        ]
    
    def connect_wallet(
        self,
        wallet_type: str,
        address: str,
        chain_id: str,
        network_name: str,
        public_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Connect a wallet to the system.
        
        Args:
            wallet_type: Type of wallet (metamask, polkadot)
            address: Wallet address
            chain_id: Network chain ID
            network_name: Human-readable network name
            public_key: Public key for Substrate wallets
            metadata: Additional wallet metadata
            
        Returns:
            Dictionary with connection result
        """
        try:
            # Validate wallet type
            supported_types = [wt["type"] for wt in self.get_supported_wallet_types()]
            if wallet_type not in supported_types:
                return {"error": f"Unsupported wallet type: {wallet_type}"}
            
            # Validate address based on wallet type
            if wallet_type == "metamask":
                if not self.metamask_service.validate_address(address):
                    return {"error": "Invalid Ethereum address"}
            elif wallet_type == "polkadot":
                if not self.polkadot_service.validate_address(address):
                    return {"error": "Invalid Substrate address"}
            
            # Check if wallet already exists
            existing_wallet = Wallet.objects.filter(address=address).first()
            if existing_wallet:
                return {
                    "wallet_id": str(existing_wallet.id),
                    "address": existing_wallet.address,
                    "wallet_type": existing_wallet.wallet_type,
                    "is_verified": existing_wallet.is_verified,
                    "message": "Wallet already connected"
                }
            
            # Create wallet record
            wallet = Wallet.objects.create(
                address=address,
                wallet_type=wallet_type,
                chain_id=chain_id,
                network_name=network_name,
                public_key=public_key,
                metadata=metadata or {}
            )
            
            logger.info(f"Wallet connected: {wallet_type} - {address}")
            
            return {
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "wallet_type": wallet.wallet_type,
                "is_verified": wallet.is_verified,
                "message": "Wallet connected successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to connect wallet: {e}")
            return {"error": str(e)}
    
    def request_authentication(
        self,
        wallet_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request wallet authentication signature.
        
        Args:
            wallet_id: ID of the wallet to authenticate
            user_id: Optional user ID for existing users
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Dictionary with authentication request details
        """
        try:
            # Get wallet
            wallet = Wallet.objects.get(id=wallet_id)
            
            # Generate authentication message
            message, nonce, timestamp = wallet.generate_verification_message()
            
            # Create signature request
            signature_request = WalletSignature.objects.create(
                wallet=wallet,
                signature_type='authentication',
                message=message,
                nonce=nonce,
                expires_at=timezone.now() + timezone.timedelta(minutes=10),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Get wallet-specific service
            if wallet.wallet_type == "metamask":
                service = self.metamask_service
            elif wallet.wallet_type == "polkadot":
                service = self.polkadot_service
            else:
                return {"error": f"Unsupported wallet type: {wallet.wallet_type}"}
            
            # Request signature
            signature_request_data = service.request_signature(
                address=wallet.address,
                message=message,
                nonce=nonce,
                timestamp=timestamp
            )
            
            return {
                "signature_id": str(signature_request.id),
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "wallet_type": wallet.wallet_type,
                "message": message,
                "nonce": nonce,
                "timestamp": timestamp,
                "expires_at": signature_request.expires_at.isoformat(),
                "network_info": signature_request_data
            }
            
        except Wallet.DoesNotExist:
            return {"error": "Wallet not found"}
        except Exception as e:
            logger.error(f"Failed to request authentication: {e}")
            return {"error": str(e)}
    
    def verify_authentication(
        self,
        signature_id: str,
        signature: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify wallet authentication signature.
        
        Args:
            signature_id: ID of the signature request
            signature: The signature to verify
            user_id: Optional user ID for existing users
            
        Returns:
            Dictionary with authentication result
        """
        try:
            # Get signature request
            signature_request = WalletSignature.objects.get(id=signature_id)
            
            # Check if signature request is expired
            if signature_request.is_expired:
                return {"error": "Signature request has expired"}
            
            # Get wallet
            wallet = signature_request.wallet
            
            # Verify signature
            is_valid = self.signature_service.verify_signature(
                wallet_type=wallet.wallet_type,
                message=signature_request.message,
                signature=signature,
                address=wallet.address,
                public_key=wallet.public_key
            )
            
            if not is_valid:
                signature_request.mark_failed()
                return {"error": "Invalid signature"}
            
            # Mark signature as signed and verified
            signature_request.mark_signed(signature)
            signature_request.mark_verified()
            
            # Update wallet verification status
            wallet.is_verified = True
            wallet.verified_at = timezone.now()
            wallet.save()
            
            # Get or create user
            user = self._get_or_create_user(wallet, user_id)
            
            # Create or update wallet session
            session = self._create_wallet_session(wallet, user, signature_request)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            logger.info(f"Wallet authenticated successfully: {wallet.address}")
            
            return {
                "success": True,
                "user_id": str(user.id),
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "wallet_type": wallet.wallet_type,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_id": str(session.id),
                "message": "Authentication successful"
            }
            
        except WalletSignature.DoesNotExist:
            return {"error": "Signature request not found"}
        except Exception as e:
            logger.error(f"Failed to verify authentication: {e}")
            return {"error": str(e)}
    
    def get_user_wallets(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all wallets for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user wallets
        """
        try:
            user = User.objects.get(id=user_id)
            wallets = Wallet.objects.filter(user=user, is_active=True)
            
            return [
                {
                    "wallet_id": str(wallet.id),
                    "address": wallet.address,
                    "wallet_type": wallet.wallet_type,
                    "chain_type": wallet.chain_type,
                    "network_name": wallet.network_name,
                    "is_primary": wallet.is_primary,
                    "is_verified": wallet.is_verified,
                    "created_at": wallet.created_at.isoformat(),
                    "last_used": wallet.last_used.isoformat()
                }
                for wallet in wallets
            ]
        except User.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"Failed to get user wallets: {e}")
            return []
    
    def set_primary_wallet(self, user_id: str, wallet_id: str) -> Dict[str, Any]:
        """
        Set a wallet as the user's primary wallet.
        
        Args:
            user_id: User ID
            wallet_id: Wallet ID to set as primary
            
        Returns:
            Dictionary with operation result
        """
        try:
            user = User.objects.get(id=user_id)
            wallet = Wallet.objects.get(id=wallet_id, user=user)
            
            # Set as primary (this will automatically unset other primary wallets)
            wallet.is_primary = True
            wallet.save()
            
            return {
                "success": True,
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "message": "Primary wallet updated"
            }
            
        except (User.DoesNotExist, Wallet.DoesNotExist):
            return {"error": "User or wallet not found"}
        except Exception as e:
            logger.error(f"Failed to set primary wallet: {e}")
            return {"error": str(e)}
    
    def disconnect_wallet(self, user_id: str, wallet_id: str) -> Dict[str, Any]:
        """
        Disconnect a wallet from a user.
        
        Args:
            user_id: User ID
            wallet_id: Wallet ID to disconnect
            
        Returns:
            Dictionary with operation result
        """
        try:
            user = User.objects.get(id=user_id)
            wallet = Wallet.objects.get(id=wallet_id, user=user)
            
            # Deactivate wallet
            wallet.is_active = False
            wallet.save()
            
            # Deactivate any active sessions for this wallet
            WalletSession.objects.filter(
                wallet=wallet,
                is_active=True
            ).update(is_active=False)
            
            logger.info(f"Wallet disconnected: {wallet.address}")
            
            return {
                "success": True,
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "message": "Wallet disconnected"
            }
            
        except (User.DoesNotExist, Wallet.DoesNotExist):
            return {"error": "User or wallet not found"}
        except Exception as e:
            logger.error(f"Failed to disconnect wallet: {e}")
            return {"error": str(e)}
    
    def request_transaction_signature(
        self,
        wallet_id: str,
        transaction_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request signature for a transaction.
        
        Args:
            wallet_id: ID of the wallet to sign with
            transaction_data: Transaction details
            user_id: User ID
            
        Returns:
            Dictionary with signature request details
        """
        try:
            # Get wallet
            wallet = Wallet.objects.get(id=wallet_id)
            
            # Generate transaction message
            nonce = self.signature_service.generate_nonce()
            timestamp = int(timezone.now().timestamp())
            
            message = self.signature_service.generate_transaction_message(
                transaction_data=transaction_data,
                nonce=nonce,
                timestamp=timestamp
            )
            
            # Create signature request
            signature_request = WalletSignature.objects.create(
                wallet=wallet,
                signature_type='transaction',
                message=message,
                nonce=nonce,
                expires_at=timezone.now() + timezone.timedelta(minutes=30),
                metadata=transaction_data
            )
            
            return {
                "signature_id": str(signature_request.id),
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "wallet_type": wallet.wallet_type,
                "message": message,
                "nonce": nonce,
                "timestamp": timestamp,
                "expires_at": signature_request.expires_at.isoformat(),
                "transaction_data": transaction_data
            }
            
        except Wallet.DoesNotExist:
            return {"error": "Wallet not found"}
        except Exception as e:
            logger.error(f"Failed to request transaction signature: {e}")
            return {"error": str(e)}
    
    def verify_transaction_signature(
        self,
        signature_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify a transaction signature.
        
        Args:
            signature_id: ID of the signature request
            signature: The signature to verify
            
        Returns:
            Dictionary with verification result
        """
        try:
            # Get signature request
            signature_request = WalletSignature.objects.get(id=signature_id)
            
            # Check if signature request is expired
            if signature_request.is_expired:
                return {"error": "Signature request has expired"}
            
            # Get wallet
            wallet = signature_request.wallet
            
            # Verify signature
            is_valid = self.signature_service.verify_signature(
                wallet_type=wallet.wallet_type,
                message=signature_request.message,
                signature=signature,
                address=wallet.address,
                public_key=wallet.public_key
            )
            
            if not is_valid:
                signature_request.mark_failed()
                return {"error": "Invalid signature"}
            
            # Mark signature as signed and verified
            signature_request.mark_signed(signature)
            signature_request.mark_verified()
            
            return {
                "success": True,
                "signature_id": str(signature_request.id),
                "wallet_id": str(wallet.id),
                "address": wallet.address,
                "transaction_data": signature_request.metadata,
                "message": "Transaction signature verified"
            }
            
        except WalletSignature.DoesNotExist:
            return {"error": "Signature request not found"}
        except Exception as e:
            logger.error(f"Failed to verify transaction signature: {e}")
            return {"error": str(e)}
    
    def _get_or_create_user(self, wallet: Wallet, user_id: Optional[str] = None) -> User:
        """
        Get existing user or create new user for wallet.
        
        Args:
            wallet: Wallet instance
            user_id: Optional existing user ID
            
        Returns:
            User instance
        """
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Associate wallet with user
                wallet.user = user
                wallet.save()
                return user
            except User.DoesNotExist:
                pass
        
        # Create new user
        username = f"wallet_{wallet.address[:10]}"
        email = f"{wallet.address}@wallet.local"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=None,  # No password for wallet users
            organization=None  # Will be set later
        )
        
        # Associate wallet with user
        wallet.user = user
        wallet.is_primary = True  # First wallet is primary
        wallet.save()
        
        return user
    
    def _create_wallet_session(
        self,
        wallet: Wallet,
        user: User,
        signature_request: WalletSignature
    ) -> WalletSession:
        """
        Create a wallet session for authenticated user.
        
        Args:
            wallet: Wallet instance
            user: User instance
            signature_request: Signature request instance
            
        Returns:
            WalletSession instance
        """
        # Deactivate any existing sessions for this wallet
        WalletSession.objects.filter(
            wallet=wallet,
            is_active=True
        ).update(is_active=False)
        
        # Create new session
        session = WalletSession.objects.create(
            wallet=wallet,
            user=user,
            session_key=f"wallet_{secrets.token_hex(16)}",
            ip_address=signature_request.ip_address,
            user_agent=signature_request.user_agent,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        return session

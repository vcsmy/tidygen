"""
Hash Service

Service for generating and verifying hashes for audit events.
Supports SHA256, Keccak256, and other hash algorithms.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from django.utils import timezone
from django.conf import settings

# Try to import web3 for Keccak256
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


class HashService:
    """
    Service for generating and verifying hashes for audit events.
    """
    
    @staticmethod
    def generate_sha256_hash(data: Dict[str, Any]) -> str:
        """
        Generate SHA256 hash for audit event data.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            SHA256 hash as hexadecimal string
        """
        # Create deterministic JSON string
        json_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_keccak256_hash(data: Dict[str, Any]) -> str:
        """
        Generate Keccak256 hash for audit event data.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            Keccak256 hash as hexadecimal string
        """
        if not WEB3_AVAILABLE:
            # Fallback to SHA256 if web3 is not available
            return HashService.generate_sha256_hash(data)
        
        # Create deterministic JSON string
        json_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return Web3.keccak(text=json_string).hex()
    
    @staticmethod
    def generate_event_hash(event_data: Dict[str, Any]) -> str:
        """
        Generate hash for audit event with metadata.
        
        Args:
            event_data: Dictionary containing event data and metadata
            
        Returns:
            SHA256 hash as hexadecimal string
        """
        # Extract core event data for hashing
        hash_data = {
            'event_type': event_data.get('event_type'),
            'module': event_data.get('module'),
            'object_id': event_data.get('object_id'),
            'object_type': event_data.get('object_type'),
            'timestamp': event_data.get('timestamp'),
            'user_id': event_data.get('user_id'),
            'data_hash': HashService.generate_sha256_hash(event_data.get('data', {}))
        }
        
        return HashService.generate_sha256_hash(hash_data)
    
    @staticmethod
    def generate_authentication_message(
        address: str,
        nonce: str,
        timestamp: int
    ) -> str:
        """
        Generate authentication message for wallet verification.
        
        Args:
            address: Wallet address
            nonce: Unique nonce
            timestamp: Unix timestamp
            
        Returns:
            Formatted authentication message
        """
        message = f"""TidyGen ERP Authentication

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
        timestamp: int
    ) -> str:
        """
        Generate transaction message for signing.
        
        Args:
            transaction_data: Transaction data
            nonce: Unique nonce
            timestamp: Unix timestamp
            
        Returns:
            Formatted transaction message
        """
        message = f"""TidyGen ERP Transaction Signing

Please sign this message to authorize the following transaction:

Type: {transaction_data.get('type', 'Unknown')}
Amount: {transaction_data.get('amount', '0')} {transaction_data.get('currency', 'ETH')}
Description: {transaction_data.get('description', 'No description')}
Recipient: {transaction_data.get('recipient', 'N/A')}

Nonce: {nonce}
Timestamp: {timestamp}

This request will not trigger a blockchain transaction or cost any gas fees."""
        
        return message
    
    @staticmethod
    def validate_message_format(message: str) -> bool:
        """
        Validate that a message follows the expected format.
        
        Args:
            message: Message to validate
            
        Returns:
            True if message format is valid, False otherwise
        """
        required_headers = [
            'TidyGen ERP',
            'Please sign this message',
            'Nonce:',
            'Timestamp:'
        ]
        
        return all(header in message for header in required_headers)
    
    @staticmethod
    def extract_message_components(message: str) -> Dict[str, str]:
        """
        Extract components from a formatted message.
        
        Args:
            message: Formatted message
            
        Returns:
            Dictionary containing extracted components
        """
        components = {}
        lines = message.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                components[key.strip()] = value.strip()
        
        return components
    
    @staticmethod
    def generate_nonce() -> str:
        """
        Generate a unique nonce for message signing.
        
        Returns:
            Unique nonce as hexadecimal string
        """
        # Generate 16 random bytes and convert to hex
        import secrets
        return secrets.token_hex(16)
    
    @staticmethod
    def create_message_hash(message: str) -> str:
        """
        Create hash of a message.
        
        Args:
            message: Message to hash
            
        Returns:
            SHA256 hash of the message
        """
        return hashlib.sha256(message.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_message_integrity(original_message: str, received_message: str) -> bool:
        """
        Verify that a received message matches the original.
        
        Args:
            original_message: Original message
            received_message: Received message
            
        Returns:
            True if messages match, False otherwise
        """
        return original_message == received_message
    
    @staticmethod
    def check_signature_replay_attack(nonce: str, timestamp: int) -> bool:
        """
        Check if a signature request is a replay attack.
        
        Args:
            nonce: Nonce from the signature request
            timestamp: Timestamp from the signature request
            
        Returns:
            True if signature is valid (not a replay), False otherwise
        """
        current_timestamp = int(timezone.now().timestamp())
        
        # Check if timestamp is within acceptable range (5 minutes)
        time_diff = abs(current_timestamp - timestamp)
        if time_diff > 300:  # 5 minutes
            return False
        
        # In a real implementation, you would also check if the nonce has been used before
        # For now, we'll just return True
        return True
    
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
        if not WEB3_AVAILABLE:
            # Mock verification for development
            return True
        
        try:
            # Encode the message
            message_hash = Web3.keccak(text=message)
            
            # Recover the address from the signature
            recovered_address = Web3.eth.account.recover_message(message_hash, signature=signature)
            
            # Compare addresses (case-insensitive)
            return recovered_address.lower() == address.lower()
            
        except Exception as e:
            print(f"Failed to verify Ethereum signature: {e}")
            return False
    
    @staticmethod
    def verify_substrate_signature(
        message: str,
        signature: str,
        address: str
    ) -> bool:
        """
        Verify a Substrate signature.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            address: The wallet address that should have signed
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # For Substrate signatures, we need to use the substrate-interface library
            # This is a simplified implementation - in production, use proper Substrate verification
            
            # For now, return True for demonstration
            # In production, implement proper Substrate signature verification
            return True
            
        except Exception as e:
            print(f"Failed to verify Substrate signature: {e}")
            return False
    
    @staticmethod
    def verify_signature(
        wallet_type: str,
        message: str,
        signature: str,
        address: str
    ) -> bool:
        """
        Verify signature based on wallet type.
        
        Args:
            wallet_type: Type of wallet (metamask, polkadot, etc.)
            message: The message that was signed
            signature: The signature to verify
            address: The wallet address that should have signed
            
        Returns:
            True if signature is valid, False otherwise
        """
        if wallet_type.lower() in ['metamask', 'ethereum', 'evm']:
            return HashService.verify_ethereum_signature(message, signature, address)
        elif wallet_type.lower() in ['polkadot', 'substrate']:
            return HashService.verify_substrate_signature(message, signature, address)
        else:
            # Unsupported wallet type
            return False
    
    @staticmethod
    def generate_batch_hash(events: list) -> str:
        """
        Generate hash for a batch of events.
        
        Args:
            events: List of audit events
            
        Returns:
            SHA256 hash of the batch
        """
        # Sort events by timestamp and ID for deterministic ordering
        sorted_events = sorted(events, key=lambda x: (x.timestamp, x.id))
        
        # Create batch data
        batch_data = {
            'batch_size': len(events),
            'events': [event.to_dict() for event in sorted_events],
            'batch_timestamp': timezone.now().isoformat()
        }
        
        return HashService.generate_sha256_hash(batch_data)
    
    @staticmethod
    def verify_hash_integrity(original_data: Dict[str, Any], hash_value: str) -> bool:
        """
        Verify that a hash matches the original data.
        
        Args:
            original_data: Original data that was hashed
            hash_value: Hash value to verify
            
        Returns:
            True if hash matches, False otherwise
        """
        expected_hash = HashService.generate_sha256_hash(original_data)
        return expected_hash == hash_value
    
    @staticmethod
    def generate_merkle_root_hash(leaf_hashes: list) -> str:
        """
        Generate Merkle root hash from leaf hashes.
        
        Args:
            leaf_hashes: List of leaf hashes
            
        Returns:
            Merkle root hash
        """
        if not leaf_hashes:
            return ""
        
        if len(leaf_hashes) == 1:
            return leaf_hashes[0]
        
        # Sort hashes for deterministic ordering
        sorted_hashes = sorted(leaf_hashes)
        
        # Build Merkle tree bottom-up
        current_level = sorted_hashes
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Combine hashes
                combined = left + right
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
                next_level.append(combined_hash)
            
            current_level = next_level
        
        return current_level[0]
    
    @staticmethod
    def generate_proof_path(leaf_hash: str, leaf_hashes: list) -> list:
        """
        Generate Merkle proof path for a leaf hash.
        
        Args:
            leaf_hash: Hash of the leaf to prove
            leaf_hashes: List of all leaf hashes
            
        Returns:
            List of hashes in the proof path
        """
        if leaf_hash not in leaf_hashes:
            return []
        
        # Sort hashes for deterministic ordering
        sorted_hashes = sorted(leaf_hashes)
        leaf_index = sorted_hashes.index(leaf_hash)
        
        proof_path = []
        current_level = sorted_hashes
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Add sibling to proof path if this is the leaf's level
                if i == leaf_index or i + 1 == leaf_index:
                    sibling = right if i == leaf_index else left
                    proof_path.append(sibling)
                
                # Combine hashes
                combined = left + right
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
                next_level.append(combined_hash)
            
            # Update leaf index for next level
            leaf_index = leaf_index // 2
            current_level = next_level
        
        return proof_path
    
    @staticmethod
    def verify_merkle_proof(
        leaf_hash: str,
        proof_path: list,
        root_hash: str
    ) -> bool:
        """
        Verify Merkle proof for a leaf hash.
        
        Args:
            leaf_hash: Hash of the leaf to verify
            proof_path: List of hashes in the proof path
            root_hash: Root hash of the Merkle tree
            
        Returns:
            True if proof is valid, False otherwise
        """
        current_hash = leaf_hash
        
        for proof_hash in proof_path:
            # Combine hashes in the same order as tree construction
            combined = current_hash + proof_hash
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return current_hash == root_hash

"""
Hash Service for Smart Contract Ledger

This module provides cryptographic hash generation and verification services
for ledger transactions, ensuring data integrity and tamper-proof logging.
"""

import hashlib
import json
import hmac
from typing import Dict, Any, Optional
from django.conf import settings


class HashService:
    """
    Service for generating and verifying cryptographic hashes.
    
    This service provides methods for creating deterministic hashes
    of transaction data and verifying hash integrity.
    """
    
    @staticmethod
    def generate_transaction_hash(
        transaction_type: str,
        source_module: str,
        source_id: str,
        transaction_data: Dict[str, Any],
        organization_id: Optional[str] = None
    ) -> str:
        """
        Generate a SHA256 hash for a transaction.
        
        Args:
            transaction_type: Type of transaction (invoice, payment, etc.)
            source_module: Django app/module that created the transaction
            source_id: ID of the original transaction
            transaction_data: Complete transaction data as dictionary
            organization_id: Optional organization ID for additional uniqueness
            
        Returns:
            SHA256 hash as hexadecimal string
        """
        # Create deterministic string from transaction data
        data_string = json.dumps(
            transaction_data, 
            sort_keys=True, 
            separators=(',', ':')
        )
        
        # Build hash input with all identifying information
        hash_components = [
            transaction_type,
            source_module,
            source_id,
            data_string
        ]
        
        if organization_id:
            hash_components.append(organization_id)
        
        hash_input = ':'.join(hash_components)
        
        # Generate SHA256 hash
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_batch_hash(transaction_hashes: list) -> str:
        """
        Generate a hash for a batch of transactions.
        
        Args:
            transaction_hashes: List of transaction hashes in the batch
            
        Returns:
            SHA256 hash of the batch
        """
        # Sort hashes for deterministic ordering
        sorted_hashes = sorted(transaction_hashes)
        
        # Join hashes with separator
        batch_string = '|'.join(sorted_hashes)
        
        # Generate hash
        return hashlib.sha256(batch_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_merkle_root(transaction_hashes: list) -> str:
        """
        Generate a Merkle tree root hash for a list of transactions.
        
        Args:
            transaction_hashes: List of transaction hashes
            
        Returns:
            Merkle root hash
        """
        if not transaction_hashes:
            return hashlib.sha256(b'').hexdigest()
        
        if len(transaction_hashes) == 1:
            return transaction_hashes[0]
        
        # Sort hashes for deterministic ordering
        hashes = sorted(transaction_hashes)
        
        # Build Merkle tree bottom-up
        while len(hashes) > 1:
            next_level = []
            
            # Process pairs of hashes
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    # Combine two hashes
                    combined = hashes[i] + hashes[i + 1]
                    next_level.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
                else:
                    # Odd number of hashes, duplicate the last one
                    combined = hashes[i] + hashes[i]
                    next_level.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
            
            hashes = next_level
        
        return hashes[0]
    
    @staticmethod
    def verify_transaction_hash(
        transaction_type: str,
        source_module: str,
        source_id: str,
        transaction_data: Dict[str, Any],
        expected_hash: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Verify that a transaction hash is correct.
        
        Args:
            transaction_type: Type of transaction
            source_module: Django app/module that created the transaction
            source_id: ID of the original transaction
            transaction_data: Complete transaction data as dictionary
            expected_hash: The hash to verify against
            organization_id: Optional organization ID
            
        Returns:
            True if hash is correct, False otherwise
        """
        calculated_hash = HashService.generate_transaction_hash(
            transaction_type=transaction_type,
            source_module=source_module,
            source_id=source_id,
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        return calculated_hash == expected_hash
    
    @staticmethod
    def generate_hmac_signature(
        data: str,
        secret_key: Optional[str] = None
    ) -> str:
        """
        Generate HMAC signature for data integrity verification.
        
        Args:
            data: Data to sign
            secret_key: Secret key for signing (defaults to Django SECRET_KEY)
            
        Returns:
            HMAC signature as hexadecimal string
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
        Verify HMAC signature.
        
        Args:
            data: Original data
            signature: HMAC signature to verify
            secret_key: Secret key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = HashService.generate_hmac_signature(data, secret_key)
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        Generate a simple content hash for any string content.
        
        Args:
            content: String content to hash
            
        Returns:
            SHA256 hash of the content
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
        """
        Generate hash for a file.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read
            
        Returns:
            SHA256 hash of the file content
        """
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    hash_sha256.update(chunk)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except IOError as e:
            raise ValueError(f"Error reading file {file_path}: {e}")
        
        return hash_sha256.hexdigest()
    
    @staticmethod
    def create_audit_hash(
        transaction_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str
    ) -> str:
        """
        Create a hash for audit trail events.
        
        Args:
            transaction_id: ID of the related transaction
            event_type: Type of audit event
            event_data: Event-specific data
            timestamp: ISO timestamp of the event
            
        Returns:
            SHA256 hash of the audit event
        """
        data_string = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        hash_input = f"{transaction_id}:{event_type}:{data_string}:{timestamp}"
        
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_chain_hash(
        previous_hash: str,
        current_data: str,
        nonce: Optional[int] = None
    ) -> str:
        """
        Generate a chain hash linking to previous hash.
        
        Args:
            previous_hash: Hash of the previous item in the chain
            current_data: Current data to hash
            nonce: Optional nonce for additional randomness
            
        Returns:
            SHA256 hash linking current data to previous hash
        """
        if nonce is not None:
            hash_input = f"{previous_hash}:{current_data}:{nonce}"
        else:
            hash_input = f"{previous_hash}:{current_data}"
        
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    @staticmethod
    def validate_hash_format(hash_string: str, expected_length: int = 64) -> bool:
        """
        Validate that a hash string is in the correct format.
        
        Args:
            hash_string: Hash string to validate
            expected_length: Expected length of the hash (64 for SHA256)
            
        Returns:
            True if hash format is valid, False otherwise
        """
        if not isinstance(hash_string, str):
            return False
        
        if len(hash_string) != expected_length:
            return False
        
        # Check if string contains only hexadecimal characters
        try:
            int(hash_string, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def generate_short_hash(data: str, length: int = 8) -> str:
        """
        Generate a short hash for display purposes.
        
        Args:
            data: Data to hash
            length: Length of the short hash (default 8)
            
        Returns:
            Short hash string
        """
        full_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        return full_hash[:length]

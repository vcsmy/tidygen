"""
Audit Service

High-level service for managing audit trail functionality including
event capture, hashing, Merkle tree creation, and on-chain storage.
"""

import logging
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.audit_trail.models import AuditEvent
from .hash_service import HashService
from .merkle_service import MerkleService
from .blockchain_service import BlockchainService
from .ipfs_service import IPFSService

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditService:
    """
    High-level service for audit trail management.
    """
    
    def __init__(self):
        """Initialize audit service."""
        self.config = {
            'blockchain_network': 'ethereum',
            'ipfs_enabled': True,
            'auto_hash_events': True,
            'auto_store_on_chain': False,
            'auto_store_ipfs': False
        }
        self.blockchain_service = BlockchainService(self.config['blockchain_network'])
        self.ipfs_service = IPFSService() if self.config['ipfs_enabled'] else None
    
    def capture_event(
        self,
        event_type: str,
        module: str,
        object_id: str,
        object_type: str,
        data: Dict[str, Any],
        user: Optional[User] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Capture an audit event.
        
        Args:
            event_type: Type of the event
            module: Module that generated the event
            object_id: ID of the object that triggered the event
            object_type: Type of the object
            data: Event data payload
            user: User who triggered the event
            session_id: Session ID
            ip_address: IP address
            user_agent: User agent string
            metadata: Additional metadata
            
        Returns:
            AuditEvent instance
        """
        try:
            with transaction.atomic():
                # Create audit event
                audit_event = AuditEvent.objects.create(
                    event_type=event_type,
                    module=module,
                    object_id=object_id,
                    object_type=object_type,
                    data=data,
                    metadata=metadata or {},
                    user=user,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=timezone.now()
                )
                
                # Auto-hash if configured
                if self.config['auto_hash_events']:
                    self._hash_event(audit_event)
                
                # Auto-store on-chain if configured
                if self.config['auto_store_on_chain']:
                    self._store_event_on_chain(audit_event)
                
                # Auto-store in IPFS if configured
                if self.config['auto_store_ipfs'] and self.ipfs_service:
                    self._store_event_in_ipfs(audit_event)
                
                logger.info(f"Captured audit event: {event_type} - {module} - {object_id}")
                return audit_event
                
        except Exception as e:
            logger.error(f"Failed to capture audit event: {e}")
            raise
    
    def _hash_event(self, audit_event: AuditEvent) -> str:
        """
        Generate hash for an audit event.
        
        Args:
            audit_event: AuditEvent instance
            
        Returns:
            Hash value
        """
        try:
            # Generate hash
            hash_value = audit_event.generate_hash()
            
            # Update the event with the hash
            audit_event.hash = hash_value
            audit_event.save()
            
            logger.info(f"Generated hash for event {audit_event.id}: {hash_value}")
            return hash_value
            
        except Exception as e:
            logger.error(f"Failed to hash event {audit_event.id}: {e}")
            raise
    
    def _store_event_on_chain(self, audit_event: AuditEvent) -> Optional[Dict[str, Any]]:
        """
        Store audit event on blockchain.
        
        Args:
            audit_event: AuditEvent instance
            
        Returns:
            Transaction details or None
        """
        try:
            # Store on blockchain
            result = self.blockchain_service.store_audit_hash(
                event_hash=audit_event.hash,
                merkle_root="",  # Will be updated when Merkle tree is created
                module=audit_event.module,
                event_type=audit_event.event_type
            )
            
            if result.get('success'):
                # Create on-chain record
                OnChainRecord.objects.create(
                    audit_event=audit_event,
                    transaction_hash=result['transaction_hash'],
                    block_number=result['block_number'],
                    block_hash="",  # Will be updated if available
                    gas_used=result.get('gas_used', 0),
                    gas_price=0,  # Will be updated if available
                    contract_address=result.get('contract_address'),
                    function_name='storeAuditRecord'
                )
                
                # Mark event as on-chain
                audit_event.mark_on_chain(
                    tx_hash=result['transaction_hash'],
                    block_number=result['block_number'],
                    on_chain_timestamp=timezone.now()
                )
                
                logger.info(f"Stored event {audit_event.id} on-chain: {result['transaction_hash']}")
                return result
            else:
                logger.error(f"Failed to store event {audit_event.id} on-chain: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to store event {audit_event.id} on-chain: {e}")
            return None
    
    def _store_event_in_ipfs(self, audit_event: AuditEvent) -> Optional[str]:
        """
        Store audit event in IPFS.
        
        Args:
            audit_event: AuditEvent instance
            
        Returns:
            IPFS hash or None
        """
        try:
            if not self.ipfs_service:
                return None
            
            # Store in IPFS
            ipfs_hash = self.ipfs_service.store_audit_log(audit_event.to_dict())
            
            if ipfs_hash:
                # Update audit event with IPFS hash
                audit_event.ipfs_hash = ipfs_hash
                audit_event.save(update_fields=['ipfs_hash'])
                
                logger.info(f"Stored event {audit_event.id} in IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"Failed to store event {audit_event.id} in IPFS")
                return None
                
        except Exception as e:
            logger.error(f"Failed to store event {audit_event.id} in IPFS: {e}")
            return None
    
    def create_merkle_tree_batch(self, batch_size: int = None) -> Optional[Dict[str, Any]]:
        """
        Create a Merkle tree for a batch of events.
        
        Args:
            batch_size: Number of events per batch
            
        Returns:
            Dict[str, Any] instance or None
        """
        try:
            batch_size = batch_size or self.config.merkle_batch_size
            events = MerkleService.get_events_for_batch(batch_size)
            
            if not events:
                logger.info("No events available for Merkle tree batch")
                return None
            
            # Create Merkle tree
            merkle_tree = MerkleService.create_merkle_tree(events)
            
            # Store Merkle tree in IPFS if enabled
            if self.ipfs_service:
                ipfs_hash = self.ipfs_service.store_merkle_tree(merkle_tree.tree_data)
                if ipfs_hash:
                    logger.info(f"Stored Merkle tree {merkle_tree.id} in IPFS: {ipfs_hash}")
            
            logger.info(f"Created Merkle tree batch: {merkle_tree.id} with {len(events)} events")
            return merkle_tree
            
        except Exception as e:
            logger.error(f"Failed to create Merkle tree batch: {e}")
            return None
    
    def store_merkle_tree_on_chain(self, merkle_tree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Store Merkle tree root hash on blockchain.
        
        Args:
            merkle_tree: Dict[str, Any] instance
            
        Returns:
            Transaction details or None
        """
        try:
            # Store Merkle root on blockchain
            result = self.blockchain_service.store_audit_hash(
                event_hash=merkle_tree.root_hash,
                merkle_root=merkle_tree.root_hash,
                module='audit_trail',
                event_type='merkle_tree'
            )
            
            if result.get('success'):
                # Update Merkle tree with on-chain information
                merkle_tree.on_chain_tx_hash = result['transaction_hash']
                merkle_tree.on_chain_block_number = result['block_number']
                merkle_tree.save(update_fields=['on_chain_tx_hash', 'on_chain_block_number'])
                
                logger.info(f"Stored Merkle tree {merkle_tree.id} on-chain: {result['transaction_hash']}")
                return result
            else:
                logger.error(f"Failed to store Merkle tree {merkle_tree.id} on-chain: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to store Merkle tree {merkle_tree.id} on-chain: {e}")
            return None
    
    def verify_event(self, event_id: int) -> Dict[str, Any]:
        """
        Verify an audit event.
        
        Args:
            event_id: ID of the audit event
            
        Returns:
            Dictionary containing verification results
        """
        try:
            audit_event = AuditEvent.objects.get(id=event_id)
            
            # Verify hash
            expected_hash = audit_event.generate_hash()
            hash_valid = audit_event.hash == expected_hash
            
            # Verify on-chain status if available
            on_chain_valid = False
            on_chain_hash = None
            
            if audit_event.on_chain_tx_hash:
                on_chain_valid = self.blockchain_service.verify_on_chain(audit_event.on_chain_tx_hash)
                on_chain_hash = audit_event.on_chain_tx_hash
            
            # Verify IPFS status if available
            ipfs_valid = False
            if audit_event.ipfs_hash and self.ipfs_service:
                ipfs_valid = self.ipfs_service.verify_file_exists(audit_event.ipfs_hash)
            
            # Overall verification
            verified = hash_valid and (on_chain_valid or not audit_event.on_chain_tx_hash)
            
            if verified:
                audit_event.mark_verified()
            
            return {
                'verified': verified,
                'hash_valid': hash_valid,
                'on_chain_valid': on_chain_valid,
                'ipfs_valid': ipfs_valid,
                'on_chain_hash': on_chain_hash,
                'ipfs_hash': audit_event.ipfs_hash,
                'event_id': event_id
            }
            
        except AuditEvent.DoesNotExist:
            return {
                'verified': False,
                'error': 'Event not found',
                'event_id': event_id
            }
        except Exception as e:
            logger.error(f"Failed to verify event {event_id}: {e}")
            return {
                'verified': False,
                'error': str(e),
                'event_id': event_id
            }
    
    def get_audit_events(
        self,
        module: Optional[str] = None,
        event_type: Optional[str] = None,
        user: Optional[User] = None,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEvent]:
        """
        Get audit events with filtering.
        
        Args:
            module: Filter by module
            event_type: Filter by event type
            user: Filter by user
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of events
            offset: Number of events to skip
            
        Returns:
            List of AuditEvent instances
        """
        try:
            queryset = AuditEvent.objects.all()
            
            if module:
                queryset = queryset.filter(module=module)
            
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            
            if user:
                queryset = queryset.filter(user=user)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            return list(queryset.order_by('-timestamp')[offset:offset + limit])
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Get audit trail statistics.
        
        Returns:
            Dictionary containing statistics
        """
        try:
            total_events = AuditEvent.objects.count()
            hashed_events = AuditEvent.objects.filter(status='hashed').count()
            on_chain_events = AuditEvent.objects.filter(status='on_chain').count()
            verified_events = AuditEvent.objects.filter(status='verified').count()
            failed_events = AuditEvent.objects.filter(status='failed').count()
            
            # Get Merkle tree statistics
            merkle_stats = MerkleService.get_merkle_tree_statistics()
            
            # Get network information
            network_info = self.blockchain_service.get_network_info()
            
            return {
                'total_events': total_events,
                'hashed_events': hashed_events,
                'on_chain_events': on_chain_events,
                'verified_events': verified_events,
                'failed_events': failed_events,
                'merkle_trees': merkle_stats,
                'network_info': network_info,
                'ipfs_enabled': self.config.ipfs_enabled,
                'auto_hash_events': self.config.auto_hash_events,
                'auto_store_on_chain': self.config.auto_store_on_chain,
                'auto_store_ipfs': self.config.auto_store_ipfs
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {}
    
    def export_audit_log(
        self,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export audit log data.
        
        Args:
            start_date: Start date for export
            end_date: End date for export
            module: Filter by module
            
        Returns:
            Dictionary containing exported audit data
        """
        try:
            events = self.get_audit_events(
                module=module,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Large limit for export
            )
            
            export_data = {
                'export_info': {
                    'exported_at': timezone.now().isoformat(),
                    'total_events': len(events),
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'module': module
                },
                'events': [event.to_dict() for event in events]
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export audit log: {e}")
            return {}
    
    def cleanup_old_events(self, days: int = None) -> int:
        """
        Clean up old audit events.
        
        Args:
            days: Number of days to keep events
            
        Returns:
            Number of events deleted
        """
        try:
            days = days or self.config.retention_days
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            
            old_events = AuditEvent.objects.filter(timestamp__lt=cutoff_date)
            count = old_events.count()
            old_events.delete()
            
            logger.info(f"Cleaned up {count} old audit events")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0
    
    def get_event_by_hash(self, hash_value: str) -> Optional[AuditEvent]:
        """
        Get audit event by hash.
        
        Args:
            hash_value: Hash value of the event
            
        Returns:
            AuditEvent instance or None
        """
        try:
            return AuditEvent.objects.get(hash=hash_value)
        except AuditEvent.DoesNotExist:
            return None
    
    def get_events_by_object(self, object_type: str, object_id: str) -> List[AuditEvent]:
        """
        Get audit events for a specific object.
        
        Args:
            object_type: Type of the object
            object_id: ID of the object
            
        Returns:
            List of AuditEvent instances
        """
        try:
            return list(
                AuditEvent.objects.filter(
                    object_type=object_type,
                    object_id=object_id
                ).order_by('-timestamp')
            )
        except Exception as e:
            logger.error(f"Failed to get events by object: {e}")
            return []
    
    def get_user_activity(self, user: User, days: int = 30) -> List[AuditEvent]:
        """
        Get audit events for a specific user.
        
        Args:
            user: User instance
            days: Number of days to look back
            
        Returns:
            List of AuditEvent instances
        """
        try:
            start_date = timezone.now() - timezone.timedelta(days=days)
            return list(
                AuditEvent.objects.filter(
                    user=user,
                    timestamp__gte=start_date
                ).order_by('-timestamp')
            )
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []

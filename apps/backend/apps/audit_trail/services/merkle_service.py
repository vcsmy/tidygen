"""
Merkle Tree Service

Service for creating and managing Merkle trees for batch verification
of audit events.
"""

import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from django.utils import timezone
from django.db import transaction

from apps.audit_trail.models import AuditEvent
from .hash_service import HashService


@dataclass
class MerkleNode:
    """Represents a node in the Merkle tree."""
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = False
    data: Optional[Dict[str, Any]] = None


class MerkleTree:
    """
    Merkle tree implementation for batch verification of audit events.
    """
    
    def __init__(self, events: List[AuditEvent]):
        """
        Initialize Merkle tree with audit events.
        
        Args:
            events: List of AuditEvent instances
        """
        self.events = events
        self.leaves = [self._create_leaf(event) for event in events]
        self.root = self._build_tree()
        self.proofs = self._generate_proofs()
    
    def _create_leaf(self, event: AuditEvent) -> MerkleNode:
        """
        Create a leaf node from an audit event.
        
        Args:
            event: AuditEvent instance
            
        Returns:
            MerkleNode representing the leaf
        """
        event_hash = event.hash
        return MerkleNode(
            hash=event_hash,
            is_leaf=True,
            data=event.to_dict()
        )
    
    def _build_tree(self) -> Optional[MerkleNode]:
        """
        Build Merkle tree from leaves.
        
        Returns:
            Root node of the Merkle tree
        """
        if not self.leaves:
            return None
        
        current_level = self.leaves.copy()
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Combine hashes
                combined_hash = hashlib.sha256(
                    (left.hash + right.hash).encode('utf-8')
                ).hexdigest()
                
                parent = MerkleNode(
                    hash=combined_hash,
                    left=left,
                    right=right
                )
                next_level.append(parent)
            
            current_level = next_level
        
        return current_level[0]
    
    def get_root_hash(self) -> str:
        """
        Get the root hash of the Merkle tree.
        
        Returns:
            Root hash as hexadecimal string
        """
        return self.root.hash if self.root else ""
    
    def get_leaf_count(self) -> int:
        """
        Get the number of leaves in the tree.
        
        Returns:
            Number of leaves
        """
        return len(self.leaves)
    
    def generate_proof(self, event_index: int) -> List[str]:
        """
        Generate Merkle proof for a specific event.
        
        Args:
            event_index: Index of the event in the leaves list
            
        Returns:
            List of hashes in the proof path
        """
        if event_index >= len(self.leaves):
            return []
        
        return self.proofs.get(event_index, [])
    
    def _generate_proofs(self) -> Dict[int, List[str]]:
        """
        Generate proofs for all leaves.
        
        Returns:
            Dictionary mapping leaf index to proof path
        """
        proofs = {}
        
        for i, leaf in enumerate(self.leaves):
            proof = self._generate_proof_for_leaf(leaf, i)
            proofs[i] = proof
        
        return proofs
    
    def _generate_proof_for_leaf(self, leaf: MerkleNode, leaf_index: int) -> List[str]:
        """
        Generate proof for a specific leaf.
        
        Args:
            leaf: Leaf node
            leaf_index: Index of the leaf
            
        Returns:
            List of hashes in the proof path
        """
        proof = []
        current_level = self.leaves.copy()
        current_index = leaf_index
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Add sibling to proof if this is the leaf's level
                if i == current_index or i + 1 == current_index:
                    sibling = right if i == current_index else left
                    proof.append(sibling.hash)
                
                # Combine hashes
                combined_hash = hashlib.sha256(
                    (left.hash + right.hash).encode('utf-8')
                ).hexdigest()
                
                parent = MerkleNode(hash=combined_hash)
                next_level.append(parent)
            
            # Update index for next level
            current_index = current_index // 2
            current_level = next_level
        
        return proof
    
    def verify_proof(self, event_hash: str, proof: List[str], root_hash: str) -> bool:
        """
        Verify Merkle proof for an event.
        
        Args:
            event_hash: Hash of the event to verify
            proof: List of hashes in the proof path
            root_hash: Root hash of the Merkle tree
            
        Returns:
            True if proof is valid, False otherwise
        """
        current_hash = event_hash
        
        for proof_hash in proof:
            # Combine hashes in the same order as tree construction
            combined = hashlib.sha256(
                (current_hash + proof_hash).encode('utf-8')
            ).hexdigest()
            current_hash = combined
        
        return current_hash == root_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Merkle tree to dictionary representation.
        
        Returns:
            Dictionary representation of the tree
        """
        return {
            'root_hash': self.get_root_hash(),
            'leaf_count': self.get_leaf_count(),
            'leaves': [leaf.hash for leaf in self.leaves],
            'proofs': self.proofs,
            'created_at': timezone.now().isoformat()
        }


class MerkleService:
    """
    Service for managing Merkle trees in the database.
    """
    
    @staticmethod
    def create_merkle_tree(events: List[AuditEvent]) -> Dict[str, Any]:
        """
        Create a Merkle tree from audit events and save to database.
        
        Args:
            events: List of AuditEvent instances
            
        Returns:
            Dict[str, Any] instance
        """
        if not events:
            raise ValueError("Cannot create Merkle tree with no events")
        
        # Create Merkle tree
        merkle_tree = MerkleTree(events)
        
        # Save to database
        with transaction.atomic():
            merkle_tree_model = Dict[str, Any].objects.create(
                root_hash=merkle_tree.get_root_hash(),
                leaf_count=merkle_tree.get_leaf_count(),
                batch_size=len(events),
                tree_data=merkle_tree.to_dict(),
                leaf_hashes=[leaf.hash for leaf in merkle_tree.leaves]
            )
        
        return merkle_tree_model
    
    @staticmethod
    def get_merkle_tree(tree_id: int) -> Optional[MerkleTree]:
        """
        Get Merkle tree from database.
        
        Args:
            tree_id: ID of the Merkle tree
            
        Returns:
            MerkleTree instance or None if not found
        """
        try:
            tree_model = Dict[str, Any].objects.get(id=tree_id)
            
            # Reconstruct Merkle tree from stored data
            events = []
            for leaf_hash in tree_model.leaf_hashes:
                try:
                    event = AuditEvent.objects.get(hash=leaf_hash)
                    events.append(event)
                except AuditEvent.DoesNotExist:
                    continue
            
            return MerkleTree(events)
            
        except Dict[str, Any].DoesNotExist:
            return None
    
    @staticmethod
    def verify_event_in_tree(event: AuditEvent, tree_id: int) -> bool:
        """
        Verify that an event is included in a Merkle tree.
        
        Args:
            event: AuditEvent to verify
            tree_id: ID of the Merkle tree
            
        Returns:
            True if event is in tree, False otherwise
        """
        try:
            tree_model = Dict[str, Any].objects.get(id=tree_id)
            
            # Check if event hash is in leaf hashes
            if event.hash not in tree_model.leaf_hashes:
                return False
            
            # Get Merkle tree and verify proof
            merkle_tree = MerkleService.get_merkle_tree(tree_id)
            if not merkle_tree:
                return False
            
            # Find event index
            event_index = tree_model.leaf_hashes.index(event.hash)
            
            # Generate and verify proof
            proof = merkle_tree.generate_proof(event_index)
            return merkle_tree.verify_proof(event.hash, proof, tree_model.root_hash)
            
        except Dict[str, Any].DoesNotExist:
            return False
    
    @staticmethod
    def get_events_for_batch(batch_size: int = 100) -> List[AuditEvent]:
        """
        Get events that need to be included in a Merkle tree batch.
        
        Args:
            batch_size: Number of events per batch
            
        Returns:
            List of AuditEvent instances
        """
        # Get events that haven't been included in a Merkle tree yet
        events = AuditEvent.objects.filter(
            status__in=['hashed', 'on_chain', 'verified']
        ).order_by('timestamp')[:batch_size]
        
        return list(events)
    
    @staticmethod
    def create_batch_merkle_tree(batch_size: int = 100) -> Optional[Dict[str, Any]]:
        """
        Create a Merkle tree for a batch of events.
        
        Args:
            batch_size: Number of events per batch
            
        Returns:
            Dict[str, Any] instance or None if no events
        """
        events = MerkleService.get_events_for_batch(batch_size)
        
        if not events:
            return None
        
        return MerkleService.create_merkle_tree(events)
    
    @staticmethod
    def get_merkle_trees(
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get Merkle trees from database.
        
        Args:
            limit: Maximum number of trees to return
            offset: Number of trees to skip
            
        Returns:
            List of Dict[str, Any] instances
        """
        return list(
            Dict[str, Any].objects.all()
            .order_by('-created_at')[offset:offset + limit]
        )
    
    @staticmethod
    def get_merkle_tree_by_root_hash(root_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get Merkle tree by root hash.
        
        Args:
            root_hash: Root hash of the Merkle tree
            
        Returns:
            Dict[str, Any] instance or None if not found
        """
        try:
            return Dict[str, Any].objects.get(root_hash=root_hash)
        except Dict[str, Any].DoesNotExist:
            return None
    
    @staticmethod
    def verify_merkle_tree_integrity(tree_id: int) -> bool:
        """
        Verify the integrity of a Merkle tree.
        
        Args:
            tree_id: ID of the Merkle tree
            
        Returns:
            True if tree is valid, False otherwise
        """
        try:
            tree_model = Dict[str, Any].objects.get(id=tree_id)
            merkle_tree = MerkleService.get_merkle_tree(tree_id)
            
            if not merkle_tree:
                return False
            
            # Verify root hash matches
            if merkle_tree.get_root_hash() != tree_model.root_hash:
                return False
            
            # Verify all events are still valid
            for event_hash in tree_model.leaf_hashes:
                try:
                    event = AuditEvent.objects.get(hash=event_hash)
                    # Verify event hash is still valid
                    if event.hash != event.generate_hash():
                        return False
                except AuditEvent.DoesNotExist:
                    return False
            
            return True
            
        except Dict[str, Any].DoesNotExist:
            return False
    
    @staticmethod
    def get_merkle_tree_statistics() -> Dict[str, Any]:
        """
        Get statistics about Merkle trees.
        
        Returns:
            Dictionary containing statistics
        """
        total_trees = Dict[str, Any].objects.count()
        total_events = sum(
            tree.leaf_count for tree in Dict[str, Any].objects.all()
        )
        
        return {
            'total_trees': total_trees,
            'total_events': total_events,
            'average_events_per_tree': total_events / total_trees if total_trees > 0 else 0,
            'latest_tree': Dict[str, Any].objects.order_by('-created_at').first(),
        }
    
    @staticmethod
    def cleanup_old_merkle_trees(days: int = 30) -> int:
        """
        Clean up old Merkle trees.
        
        Args:
            days: Number of days to keep trees
            
        Returns:
            Number of trees deleted
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        old_trees = Dict[str, Any].objects.filter(created_at__lt=cutoff_date)
        count = old_trees.count()
        old_trees.delete()
        
        return count

from rest_framework import serializers
from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditEvent model.
    """
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_email = serializers.CharField(source='actor.email', read_only=True)
    
    class Meta:
        model = AuditEvent
        fields = [
            'id',
            'event_type',
            'actor',
            'actor_username',
            'actor_email',
            'entity_type',
            'entity_id',
            'event_data',
            'data_hash',
            'on_chain_tx_hash',
            'on_chain_block_number',
            'ipfs_cid',
            'merkle_root',
            'merkle_proof',
            'is_verified',
            'verification_timestamp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'data_hash',
            'on_chain_tx_hash',
            'on_chain_block_number',
            'ipfs_cid',
            'merkle_root',
            'merkle_proof',
            'is_verified',
            'verification_timestamp',
            'created_at',
            'updated_at',
        ]


class AuditEventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new audit events.
    """
    
    class Meta:
        model = AuditEvent
        fields = [
            'event_type',
            'actor',
            'entity_type',
            'entity_id',
            'event_data',
        ]


class AuditEventVerificationSerializer(serializers.Serializer):
    """
    Serializer for audit event verification.
    """
    event_id = serializers.IntegerField()
    expected_hash = serializers.CharField(max_length=64)
    merkle_proof = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False
    )
    merkle_root = serializers.CharField(max_length=64, required=False)


class AuditEventBatchSerializer(serializers.Serializer):
    """
    Serializer for batch audit event operations.
    """
    event_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    operation = serializers.ChoiceField(
        choices=['verify', 'anchor_on_chain', 'store_ipfs', 'generate_merkle']
    )


class AuditEventStatsSerializer(serializers.Serializer):
    """
    Serializer for audit event statistics.
    """
    total_events = serializers.IntegerField()
    verified_events = serializers.IntegerField()
    on_chain_events = serializers.IntegerField()
    ipfs_events = serializers.IntegerField()
    events_by_type = serializers.DictField()
    events_by_actor = serializers.DictField()
    recent_events = serializers.ListField(
        child=AuditEventSerializer()
    )

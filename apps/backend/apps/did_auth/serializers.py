"""
DID Authentication Serializers

Django REST Framework serializers for DID-based authentication.
"""

from rest_framework import serializers
from .models import DIDDocument, DIDRole, DIDCredential, DIDSession, DIDPermission


class DIDDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for DID Document model.
    """
    is_active = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    verification_methods = serializers.SerializerMethodField()
    public_keys = serializers.SerializerMethodField()

    class Meta:
        model = DIDDocument
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'on_chain_tx_hash',
            'on_chain_block_number', 'is_active', 'is_expired'
        ]

    def get_verification_methods(self, obj):
        """Get verification methods from the DID document."""
        return obj.get_verification_methods()

    def get_public_keys(self, obj):
        """Get public keys from verification methods."""
        return obj.get_public_keys()


class DIDRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for DID Role model.
    """
    did_display = serializers.CharField(source='did.did', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = DIDRole
        fields = '__all__'
        read_only_fields = ['granted_at']

    def get_role_display(self, obj):
        """Get the display name for the role."""
        if obj.role_name == 'custom':
            return obj.custom_role_name
        return obj.get_role_name_display()


class DIDCredentialSerializer(serializers.ModelSerializer):
    """
    Serializer for DID Credential model.
    """
    did_display = serializers.CharField(source='did.did', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    credential_type_display = serializers.CharField(source='get_credential_type_display', read_only=True)

    class Meta:
        model = DIDCredential
        fields = '__all__'
        read_only_fields = [
            'issued_at', 'revoked_at', 'revoked_by', 'on_chain_tx_hash',
            'is_valid', 'is_expired'
        ]


class DIDSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for DID Session model.
    """
    did_display = serializers.CharField(source='did.did', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = DIDSession
        fields = '__all__'
        read_only_fields = [
            'session_token', 'created_at', 'last_activity',
            'is_valid', 'is_expired'
        ]


class DIDPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for DID Permission model.
    """
    full_permission = serializers.CharField(source='get_full_permission', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = DIDPermission
        fields = '__all__'
        read_only_fields = ['created_at']


class DIDLoginSerializer(serializers.Serializer):
    """
    Serializer for DID-based login.
    """
    did = serializers.CharField(max_length=255)
    signature = serializers.CharField()
    message = serializers.CharField()
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False, allow_blank=True)

    def validate_did(self, value):
        """Validate DID format."""
        if not value.startswith('did:'):
            raise serializers.ValidationError("DID must start with 'did:'")
        return value


class DIDCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new DID.
    """
    did = serializers.CharField(max_length=255, required=False)
    controller = serializers.CharField(max_length=255)
    public_key = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)

    def validate_did(self, value):
        """Validate DID format."""
        if value and not value.startswith('did:'):
            raise serializers.ValidationError("DID must start with 'did:'")
        return value


class DIDRoleAssignSerializer(serializers.Serializer):
    """
    Serializer for assigning roles to DIDs.
    """
    did = serializers.CharField(max_length=255)
    role_name = serializers.ChoiceField(choices=DIDRole.ROLE_TYPES)
    custom_role_name = serializers.CharField(required=False, allow_blank=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    expires_at = serializers.DateTimeField(required=False)

    def validate_did(self, value):
        """Validate DID format."""
        if not value.startswith('did:'):
            raise serializers.ValidationError("DID must start with 'did:'")
        return value


class DIDCredentialIssueSerializer(serializers.Serializer):
    """
    Serializer for issuing credentials to DIDs.
    """
    did = serializers.CharField(max_length=255)
    credential_type = serializers.ChoiceField(choices=DIDCredential.CREDENTIAL_TYPES)
    credential_data = serializers.JSONField()
    expires_at = serializers.DateTimeField(required=False)

    def validate_did(self, value):
        """Validate DID format."""
        if not value.startswith('did:'):
            raise serializers.ValidationError("DID must start with 'did:'")
        return value


class DIDSignatureVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying DID signatures.
    """
    did = serializers.CharField(max_length=255)
    message = serializers.CharField()
    signature = serializers.CharField()
    verification_method = serializers.CharField(required=False, allow_blank=True)

    def validate_did(self, value):
        """Validate DID format."""
        if not value.startswith('did:'):
            raise serializers.ValidationError("DID must start with 'did:'")
        return value


class DIDSessionInfoSerializer(serializers.Serializer):
    """
    Serializer for session information.
    """
    did = serializers.CharField(read_only=True)
    controller = serializers.CharField(read_only=True)
    roles = serializers.ListField(read_only=True)
    permissions = serializers.ListField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)
    ip_address = serializers.IPAddressField(read_only=True)
    user_agent = serializers.CharField(read_only=True)

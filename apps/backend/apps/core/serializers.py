"""
Core serializers for TidyGen ERP platform.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Permission, Role, SystemSettings, AuditLog


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for API responses.
    """
    full_name = serializers.ReadOnlyField()
    organizations = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'timezone', 'language', 'is_verified',
            'wallet_address', 'wallet_verified', 'date_joined', 'last_login',
            'organizations'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']
    
    def get_organizations(self, obj):
        """Get user's organizations."""
        return [
            {
                'id': membership.organization.id,
                'name': membership.organization.name,
                'role': membership.role.name if membership.role else None,
                'is_owner': membership.is_owner
            }
            for membership in obj.get_organizations()
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User creation serializer.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'password', 'password_confirm', 'timezone', 'language'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User update serializer.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar', 'timezone', 'language'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class PermissionSerializer(serializers.ModelSerializer):
    """
    Permission serializer.
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description', 'module', 'is_system']
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    """
    Role serializer.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 'permission_ids',
            'is_system', 'is_active', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def create(self, validated_data):
        """Create role with permissions."""
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role
    
    def update(self, instance, validated_data):
        """Update role with permissions."""
        permission_ids = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        
        return instance


class SystemSettingsSerializer(serializers.ModelSerializer):
    """
    System settings serializer.
    """
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'is_public', 'created', 'modified']
        read_only_fields = ['id', 'created', 'modified']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit log serializer.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model_name', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent', 'created'
        ]
        read_only_fields = ['id', 'created']


class Web3WalletConnectSerializer(serializers.Serializer):
    """
    Web3 wallet connection serializer.
    """
    wallet_address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()
    
    def validate_wallet_address(self, value):
        """Validate wallet address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid wallet address format.")
        return value.lower()
    
    def validate(self, attrs):
        """Validate wallet signature."""
        # TODO: Implement signature verification
        # This would verify that the signature was created by the wallet owner
        return attrs
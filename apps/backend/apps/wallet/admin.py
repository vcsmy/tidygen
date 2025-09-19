"""
Wallet Admin Configuration

This module configures the Django admin interface for wallet-related models,
providing administrative access to wallet management and monitoring.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Wallet, WalletSignature, WalletPermission, WalletSession


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin interface for Wallet model.
    
    Provides comprehensive wallet management and monitoring capabilities.
    """
    
    list_display = [
        'address_short',
        'wallet_type',
        'chain_type',
        'network_name',
        'user_link',
        'is_primary',
        'is_verified',
        'is_active',
        'created_at',
        'last_used'
    ]
    
    list_filter = [
        'wallet_type',
        'chain_type',
        'is_primary',
        'is_verified',
        'is_active',
        'created_at',
        'last_used'
    ]
    
    search_fields = [
        'address',
        'user__username',
        'user__email',
        'network_name'
    ]
    
    readonly_fields = [
        'id',
        'address',
        'created_at',
        'last_used',
        'verified_at',
        'address_short',
        'display_name'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'address',
                'address_short',
                'display_name',
                'wallet_type',
                'chain_type',
                'chain_id',
                'network_name'
            )
        }),
        ('User & Status', {
            'fields': (
                'user',
                'is_primary',
                'is_verified',
                'is_active',
                'verified_at'
            )
        }),
        ('Technical Details', {
            'fields': (
                'public_key',
                'metadata'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'last_used'
            ),
            'classes': ('collapse',)
        })
    )
    
    def address_short(self, obj):
        """Display shortened address."""
        if len(obj.address) > 20:
            return f"{obj.address[:10]}...{obj.address[-6:]}"
        return obj.address
    address_short.short_description = 'Address'
    
    def user_link(self, obj):
        """Display user as a link."""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')
    
    actions = ['verify_wallets', 'deactivate_wallets', 'activate_wallets']
    
    def verify_wallets(self, request, queryset):
        """Mark selected wallets as verified."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} wallets marked as verified.')
    verify_wallets.short_description = 'Mark selected wallets as verified'
    
    def deactivate_wallets(self, request, queryset):
        """Deactivate selected wallets."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} wallets deactivated.')
    deactivate_wallets.short_description = 'Deactivate selected wallets'
    
    def activate_wallets(self, request, queryset):
        """Activate selected wallets."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} wallets activated.')
    activate_wallets.short_description = 'Activate selected wallets'


@admin.register(WalletSignature)
class WalletSignatureAdmin(admin.ModelAdmin):
    """
    Admin interface for WalletSignature model.
    
    Provides monitoring and management of signature requests and verification.
    """
    
    list_display = [
        'signature_id_short',
        'wallet_link',
        'signature_type',
        'status',
        'verified',
        'is_expired',
        'created_at',
        'expires_at'
    ]
    
    list_filter = [
        'signature_type',
        'status',
        'verified',
        'created_at',
        'expires_at',
        'wallet__wallet_type'
    ]
    
    search_fields = [
        'id',
        'wallet__address',
        'wallet__user__username',
        'nonce',
        'message'
    ]
    
    readonly_fields = [
        'id',
        'wallet',
        'signature_type',
        'message',
        'signature',
        'nonce',
        'status',
        'verified',
        'created_at',
        'signed_at',
        'verified_at',
        'expires_at',
        'ip_address',
        'user_agent',
        'is_expired',
        'is_valid'
    ]
    
    fieldsets = (
        ('Signature Information', {
            'fields': (
                'id',
                'wallet',
                'signature_type',
                'status',
                'verified'
            )
        }),
        ('Message & Signature', {
            'fields': (
                'message',
                'signature',
                'nonce'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'signed_at',
                'verified_at',
                'expires_at'
            )
        }),
        ('Request Details', {
            'fields': (
                'ip_address',
                'user_agent',
                'metadata'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (
                'is_expired',
                'is_valid'
            )
        })
    )
    
    def signature_id_short(self, obj):
        """Display shortened signature ID."""
        return str(obj.id)[:8] + '...'
    signature_id_short.short_description = 'Signature ID'
    
    def wallet_link(self, obj):
        """Display wallet as a link."""
        url = reverse('admin:wallet_wallet_change', args=[obj.wallet.id])
        return format_html('<a href="{}">{}</a>', url, obj.wallet.address_short)
    wallet_link.short_description = 'Wallet'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('wallet', 'wallet__user')
    
    actions = ['mark_verified', 'mark_failed']
    
    def mark_verified(self, request, queryset):
        """Mark selected signatures as verified."""
        updated = queryset.update(verified=True, status='verified')
        self.message_user(request, f'{updated} signatures marked as verified.')
    mark_verified.short_description = 'Mark selected signatures as verified'
    
    def mark_failed(self, request, queryset):
        """Mark selected signatures as failed."""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} signatures marked as failed.')
    mark_failed.short_description = 'Mark selected signatures as failed'


@admin.register(WalletPermission)
class WalletPermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for WalletPermission model.
    
    Provides management of wallet-based permissions and access control.
    """
    
    list_display = [
        'permission_display',
        'wallet_link',
        'permission_type',
        'resource_type',
        'resource_id',
        'granted',
        'is_active',
        'expires_at',
        'granted_by_link'
    ]
    
    list_filter = [
        'permission_type',
        'resource_type',
        'granted',
        'created_at',
        'expires_at',
        'wallet__wallet_type'
    ]
    
    search_fields = [
        'wallet__address',
        'wallet__user__username',
        'resource_id',
        'reason',
        'granted_by__username'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'is_expired',
        'is_active'
    ]
    
    fieldsets = (
        ('Permission Information', {
            'fields': (
                'id',
                'wallet',
                'permission_type',
                'resource_type',
                'resource_id',
                'granted'
            )
        }),
        ('Grant Details', {
            'fields': (
                'granted_by',
                'reason',
                'expires_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (
                'is_expired',
                'is_active'
            )
        })
    )
    
    def permission_display(self, obj):
        """Display permission in a readable format."""
        action = "Grant" if obj.granted else "Deny"
        resource = f"{obj.resource_type}"
        if obj.resource_id:
            resource += f":{obj.resource_id}"
        return f"{action} {obj.permission_type} on {resource}"
    permission_display.short_description = 'Permission'
    
    def wallet_link(self, obj):
        """Display wallet as a link."""
        url = reverse('admin:wallet_wallet_change', args=[obj.wallet.id])
        return format_html('<a href="{}">{}</a>', url, obj.wallet.address_short)
    wallet_link.short_description = 'Wallet'
    
    def granted_by_link(self, obj):
        """Display granted by user as a link."""
        if obj.granted_by:
            url = reverse('admin:accounts_user_change', args=[obj.granted_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.granted_by.username)
        return '-'
    granted_by_link.short_description = 'Granted By'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'wallet', 'wallet__user', 'granted_by'
        )
    
    actions = ['grant_permissions', 'revoke_permissions']
    
    def grant_permissions(self, request, queryset):
        """Grant selected permissions."""
        updated = queryset.update(granted=True)
        self.message_user(request, f'{updated} permissions granted.')
    grant_permissions.short_description = 'Grant selected permissions'
    
    def revoke_permissions(self, request, queryset):
        """Revoke selected permissions."""
        updated = queryset.update(granted=False)
        self.message_user(request, f'{updated} permissions revoked.')
    revoke_permissions.short_description = 'Revoke selected permissions'


@admin.register(WalletSession)
class WalletSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for WalletSession model.
    
    Provides monitoring and management of wallet authentication sessions.
    """
    
    list_display = [
        'session_id_short',
        'wallet_link',
        'user_link',
        'is_active',
        'is_expired',
        'ip_address',
        'created_at',
        'last_activity',
        'expires_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'last_activity',
        'expires_at',
        'wallet__wallet_type'
    ]
    
    search_fields = [
        'id',
        'wallet__address',
        'user__username',
        'session_key',
        'ip_address'
    ]
    
    readonly_fields = [
        'id',
        'wallet',
        'user',
        'session_key',
        'jwt_token',
        'ip_address',
        'user_agent',
        'created_at',
        'last_activity',
        'is_expired',
        'is_valid'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'id',
                'wallet',
                'user',
                'session_key',
                'is_active'
            )
        }),
        ('Authentication', {
            'fields': (
                'jwt_token',
            ),
            'classes': ('collapse',)
        }),
        ('Request Details', {
            'fields': (
                'ip_address',
                'user_agent'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'last_activity',
                'expires_at'
            )
        }),
        ('Status', {
            'fields': (
                'is_expired',
                'is_valid'
            )
        })
    )
    
    def session_id_short(self, obj):
        """Display shortened session ID."""
        return str(obj.id)[:8] + '...'
    session_id_short.short_description = 'Session ID'
    
    def wallet_link(self, obj):
        """Display wallet as a link."""
        url = reverse('admin:wallet_wallet_change', args=[obj.wallet.id])
        return format_html('<a href="{}">{}</a>', url, obj.wallet.address_short)
    wallet_link.short_description = 'Wallet'
    
    def user_link(self, obj):
        """Display user as a link."""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('wallet', 'user')
    
    actions = ['deactivate_sessions', 'extend_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """Deactivate selected sessions."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} sessions deactivated.')
    deactivate_sessions.short_description = 'Deactivate selected sessions'
    
    def extend_sessions(self, request, queryset):
        """Extend selected sessions by 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        
        for session in queryset:
            session.expires_at = timezone.now() + timedelta(hours=24)
            session.save()
        
        self.message_user(request, f'{queryset.count()} sessions extended by 24 hours.')
    extend_sessions.short_description = 'Extend selected sessions by 24 hours'

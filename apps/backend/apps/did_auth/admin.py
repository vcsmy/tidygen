from django.contrib import admin
from django.utils.html import format_html
from .models import DIDDocument, DIDRole, DIDCredential, DIDSession, DIDPermission


@admin.register(DIDDocument)
class DIDDocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for DID Document model.
    """
    list_display = [
        'did',
        'controller',
        'status',
        'on_chain_status',
        'is_active',
        'is_expired',
        'created_at',
    ]
    list_filter = [
        'status',
        'created_at',
        'controller',
    ]
    search_fields = [
        'did',
        'controller',
        'on_chain_tx_hash',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'on_chain_tx_hash',
        'on_chain_block_number',
        'is_active',
        'is_expired',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('DID Information', {
            'fields': (
                'did',
                'controller',
                'status',
                'expires_at',
            )
        }),
        ('DID Document', {
            'fields': ('document',),
            'classes': ('collapse',)
        }),
        ('On-Chain Storage', {
            'fields': (
                'on_chain_tx_hash',
                'on_chain_block_number',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def on_chain_status(self, obj):
        """Display on-chain status."""
        if obj.on_chain_tx_hash:
            return format_html(
                '<span style="color: green;">✓ On-Chain</span><br>'
                '<small>{}</small>',
                obj.on_chain_tx_hash[:16] + "..."
            )
        return format_html('<span style="color: red;">✗ Not On-Chain</span>')
    on_chain_status.short_description = "On-Chain Status"


@admin.register(DIDRole)
class DIDRoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for DID Role model.
    """
    list_display = [
        'did_display',
        'role_display',
        'is_active',
        'is_valid',
        'granted_by',
        'granted_at',
    ]
    list_filter = [
        'role_name',
        'is_active',
        'granted_at',
        'granted_by',
    ]
    search_fields = [
        'did__did',
        'role_name',
        'custom_role_name',
        'granted_by',
    ]
    readonly_fields = [
        'granted_at',
        'is_valid',
    ]
    ordering = ['-granted_at']
    date_hierarchy = 'granted_at'

    fieldsets = (
        ('Role Information', {
            'fields': (
                'did',
                'role_name',
                'custom_role_name',
                'permissions',
            )
        }),
        ('Assignment Details', {
            'fields': (
                'granted_by',
                'granted_at',
                'expires_at',
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    def did_display(self, obj):
        """Display DID information."""
        return obj.did.did
    did_display.short_description = "DID"

    def role_display(self, obj):
        """Display role information."""
        if obj.role_name == 'custom':
            return obj.custom_role_name
        return obj.get_role_name_display()
    role_display.short_description = "Role"


@admin.register(DIDCredential)
class DIDCredentialAdmin(admin.ModelAdmin):
    """
    Admin configuration for DID Credential model.
    """
    list_display = [
        'did_display',
        'credential_type',
        'issuer',
        'is_valid',
        'issued_at',
        'on_chain_status',
    ]
    list_filter = [
        'credential_type',
        'revoked',
        'issued_at',
        'issuer',
    ]
    search_fields = [
        'did__did',
        'credential_type',
        'issuer',
        'on_chain_tx_hash',
    ]
    readonly_fields = [
        'issued_at',
        'revoked_at',
        'revoked_by',
        'on_chain_tx_hash',
        'is_valid',
    ]
    ordering = ['-issued_at']
    date_hierarchy = 'issued_at'

    fieldsets = (
        ('Credential Information', {
            'fields': (
                'did',
                'credential_type',
                'issuer',
                'expires_at',
            )
        }),
        ('Credential Data', {
            'fields': ('credential_data',),
            'classes': ('collapse',)
        }),
        ('Revocation', {
            'fields': (
                'revoked',
                'revoked_at',
                'revoked_by',
            ),
            'classes': ('collapse',)
        }),
        ('On-Chain Storage', {
            'fields': ('on_chain_tx_hash',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    def did_display(self, obj):
        """Display DID information."""
        return obj.did.did
    did_display.short_description = "DID"

    def on_chain_status(self, obj):
        """Display on-chain status."""
        if obj.on_chain_tx_hash:
            return format_html(
                '<span style="color: green;">✓ On-Chain</span><br>'
                '<small>{}</small>',
                obj.on_chain_tx_hash[:16] + "..."
            )
        return format_html('<span style="color: red;">✗ Not On-Chain</span>')
    on_chain_status.short_description = "On-Chain Status"


@admin.register(DIDSession)
class DIDSessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for DID Session model.
    """
    list_display = [
        'did_display',
        'session_token_short',
        'is_active',
        'is_valid',
        'created_at',
        'expires_at',
    ]
    list_filter = [
        'is_active',
        'created_at',
        'expires_at',
    ]
    search_fields = [
        'did__did',
        'session_token',
        'ip_address',
    ]
    readonly_fields = [
        'session_token',
        'created_at',
        'last_activity',
        'is_valid',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Session Information', {
            'fields': (
                'did',
                'session_token',
                'is_active',
                'expires_at',
            )
        }),
        ('Client Information', {
            'fields': (
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': (
                'created_at',
                'last_activity',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    def did_display(self, obj):
        """Display DID information."""
        return obj.did.did
    did_display.short_description = "DID"

    def session_token_short(self, obj):
        """Display shortened session token."""
        return f"{obj.session_token[:16]}..."
    session_token_short.short_description = "Session Token"


@admin.register(DIDPermission)
class DIDPermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for DID Permission model.
    """
    list_display = [
        'name',
        'display_name',
        'category',
        'resource',
        'action',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'category',
        'is_active',
        'created_at',
    ]
    search_fields = [
        'name',
        'display_name',
        'description',
        'resource',
        'action',
    ]
    readonly_fields = [
        'created_at',
    ]
    ordering = ['category', 'name']

    fieldsets = (
        ('Permission Information', {
            'fields': (
                'name',
                'display_name',
                'description',
                'category',
            )
        }),
        ('Access Control', {
            'fields': (
                'resource',
                'action',
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
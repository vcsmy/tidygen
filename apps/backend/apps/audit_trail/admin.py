from django.contrib import admin
from django.utils.html import format_html
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for AuditEvent model.
    """
    list_display = [
        'id',
        'event_type',
        'user_display',
        'entity_display',
        'hash_short',
        'status',
        'on_chain_status',
        'ipfs_status',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'status',
        'created_at',
        'user',
    ]
    search_fields = [
        'event_type',
        'object_type',
        'object_id',
        'hash',
        'on_chain_tx_hash',
        'ipfs_hash',
    ]
    readonly_fields = [
        'hash',
        'on_chain_tx_hash',
        'on_chain_block_number',
        'ipfs_hash',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'event_type',
                'user',
                'object_type',
                'object_id',
                'data',
            )
        }),
        ('Hash & Status', {
            'fields': (
                'hash',
                'status',
            )
        }),
        ('On-Chain Storage', {
            'fields': (
                'on_chain_tx_hash',
                'on_chain_block_number',
            ),
            'classes': ('collapse',)
        }),
        ('IPFS Storage', {
            'fields': ('ipfs_hash',),
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

    def user_display(self, obj):
        """Display user information."""
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "System"
    user_display.short_description = "User"

    def entity_display(self, obj):
        """Display entity information."""
        if obj.object_type and obj.object_id:
            return f"{obj.object_type}: {obj.object_id}"
        return "-"
    entity_display.short_description = "Entity"

    def hash_short(self, obj):
        """Display shortened hash."""
        if obj.hash:
            return f"{obj.hash[:8]}...{obj.hash[-8:]}"
        return "-"
    hash_short.short_description = "Hash"

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

    def ipfs_status(self, obj):
        """Display IPFS status."""
        if obj.ipfs_hash:
            return format_html(
                '<span style="color: green;">✓ On IPFS</span><br>'
                '<small>{}</small>',
                obj.ipfs_hash[:16] + "..."
            )
        return format_html('<span style="color: red;">✗ Not on IPFS</span>')
    ipfs_status.short_description = "IPFS Status"

    def has_add_permission(self, request):
        """Disable adding audit events through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable changing audit events through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit events through admin."""
        return False
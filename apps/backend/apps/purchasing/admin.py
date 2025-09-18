"""
Purchasing Management Admin Configuration

This module configures the Django admin interface for the purchasing management system,
providing administrative access to purchase orders, suppliers, procurement, and analytics.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.purchasing.models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReceiptItem,
    ProcurementRequest, ProcurementRequestItem, SupplierPerformance, PurchaseAnalytics
)


class PurchaseOrderItemInline(admin.TabularInline):
    """Inline admin for purchase order items."""
    model = PurchaseOrderItem
    extra = 0
    fields = ['product', 'product_name', 'product_sku', 'quantity_ordered', 
              'quantity_received', 'quantity_pending', 'unit_price', 'total_price']
    readonly_fields = ['product_name', 'product_sku', 'quantity_pending', 'total_price']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin for purchase orders."""
    list_display = [
        'po_number', 'supplier_link', 'status_badge', 'priority_badge',
        'total_amount', 'order_date', 'expected_delivery_date', 'requested_by_link'
    ]
    list_filter = [
        'status', 'priority', 'order_date', 'expected_delivery_date',
        'supplier', 'requested_by', 'approved_by'
    ]
    search_fields = [
        'po_number', 'supplier__name', 'reference_number', 'tracking_number',
        'notes', 'supplier_notes'
    ]
    readonly_fields = [
        'po_number', 'order_date', 'total_amount', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('po_number', 'supplier', 'requested_by', 'approved_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date', 'actual_delivery_date', 'approval_date')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'supplier_notes', 'terms_conditions', 'reference_number', 'tracking_number'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    inlines = [PurchaseOrderItemInline]
    date_hierarchy = 'order_date'
    ordering = ['-order_date']
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        if obj.supplier:
            url = reverse('admin:inventory_supplier_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return '-'
    supplier_link.short_description = 'Supplier'
    
    def requested_by_link(self, obj):
        """Create a link to the user who requested the order."""
        if obj.requested_by:
            url = reverse('admin:accounts_user_change', args=[obj.requested_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.requested_by.get_full_name())
        return '-'
    requested_by_link.short_description = 'Requested By'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'draft': 'gray',
            'pending_approval': 'orange',
            'approved': 'blue',
            'sent': 'purple',
            'partially_received': 'yellow',
            'fully_received': 'green',
            'cancelled': 'red',
            'closed': 'black'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority as a colored badge."""
        colors = {
            'low': 'green',
            'medium': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """Admin for purchase order items."""
    list_display = [
        'purchase_order_link', 'product_name', 'product_sku', 'quantity_ordered',
        'quantity_received', 'quantity_pending', 'unit_price', 'total_price'
    ]
    list_filter = [
        'purchase_order__status', 'purchase_order__supplier', 'expected_delivery_date'
    ]
    search_fields = [
        'purchase_order__po_number', 'product_name', 'product_sku', 'product_description'
    ]
    readonly_fields = ['product_name', 'product_sku', 'total_price', 'quantity_pending']
    
    def purchase_order_link(self, obj):
        """Create a link to the purchase order."""
        url = reverse('admin:purchasing_purchaseorder_change', args=[obj.purchase_order.id])
        return format_html('<a href="{}">{}</a>', url, obj.purchase_order.po_number)
    purchase_order_link.short_description = 'Purchase Order'


class PurchaseReceiptItemInline(admin.TabularInline):
    """Inline admin for purchase receipt items."""
    model = PurchaseReceiptItem
    extra = 0
    fields = ['purchase_order_item', 'quantity_received', 'condition', 'batch_number', 'expiry_date']


@admin.register(PurchaseReceipt)
class PurchaseReceiptAdmin(admin.ModelAdmin):
    """Admin for purchase receipts."""
    list_display = [
        'receipt_number', 'purchase_order_link', 'status_badge', 'received_by_link',
        'receipt_date'
    ]
    list_filter = ['status', 'receipt_date', 'received_by']
    search_fields = [
        'receipt_number', 'purchase_order__po_number', 'notes', 'condition_notes'
    ]
    readonly_fields = ['receipt_number', 'receipt_date', 'created', 'modified']
    inlines = [PurchaseReceiptItemInline]
    date_hierarchy = 'receipt_date'
    ordering = ['-receipt_date']
    
    def purchase_order_link(self, obj):
        """Create a link to the purchase order."""
        url = reverse('admin:purchasing_purchaseorder_change', args=[obj.purchase_order.id])
        return format_html('<a href="{}">{}</a>', url, obj.purchase_order.po_number)
    purchase_order_link.short_description = 'Purchase Order'
    
    def received_by_link(self, obj):
        """Create a link to the user who received the items."""
        if obj.received_by:
            url = reverse('admin:accounts_user_change', args=[obj.received_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.received_by.get_full_name())
        return '-'
    received_by_link.short_description = 'Received By'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': 'orange',
            'partial': 'yellow',
            'complete': 'green',
            'discrepancy': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(PurchaseReceiptItem)
class PurchaseReceiptItemAdmin(admin.ModelAdmin):
    """Admin for purchase receipt items."""
    list_display = [
        'receipt_link', 'purchase_order_item_name', 'quantity_received', 'condition'
    ]
    list_filter = ['condition', 'receipt__status', 'expiry_date']
    search_fields = [
        'receipt__receipt_number', 'purchase_order_item__product_name',
        'batch_number', 'notes'
    ]
    
    def receipt_link(self, obj):
        """Create a link to the receipt."""
        url = reverse('admin:purchasing_purchasereceipt_change', args=[obj.receipt.id])
        return format_html('<a href="{}">{}</a>', url, obj.receipt.receipt_number)
    receipt_link.short_description = 'Receipt'
    
    def purchase_order_item_name(self, obj):
        """Display the purchase order item name."""
        return obj.purchase_order_item.product_name
    purchase_order_item_name.short_description = 'Product'


class ProcurementRequestItemInline(admin.TabularInline):
    """Inline admin for procurement request items."""
    model = ProcurementRequestItem
    extra = 0
    fields = ['product', 'product_name', 'product_sku', 'quantity', 
              'estimated_unit_price', 'estimated_total_price']
    readonly_fields = ['product_name', 'product_sku', 'estimated_total_price']


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    """Admin for procurement requests."""
    list_display = [
        'request_number', 'title', 'status_badge', 'priority_badge',
        'requested_by_link', 'request_date', 'required_date', 'estimated_cost'
    ]
    list_filter = [
        'status', 'priority', 'request_date', 'required_date', 'requested_by', 'reviewed_by'
    ]
    search_fields = [
        'request_number', 'title', 'description', 'justification', 'notes'
    ]
    readonly_fields = [
        'request_number', 'request_date', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('request_number', 'requested_by', 'reviewed_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('request_date', 'required_date', 'review_date')
        }),
        ('Request Details', {
            'fields': ('title', 'description', 'justification')
        }),
        ('Financial', {
            'fields': ('estimated_cost', 'budget_code')
        }),
        ('Additional Information', {
            'fields': ('notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    inlines = [ProcurementRequestItemInline]
    date_hierarchy = 'request_date'
    ordering = ['-request_date']
    
    def requested_by_link(self, obj):
        """Create a link to the user who made the request."""
        if obj.requested_by:
            url = reverse('admin:accounts_user_change', args=[obj.requested_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.requested_by.get_full_name())
        return '-'
    requested_by_link.short_description = 'Requested By'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'under_review': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'converted': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority as a colored badge."""
        colors = {
            'low': 'green',
            'medium': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'


@admin.register(ProcurementRequestItem)
class ProcurementRequestItemAdmin(admin.ModelAdmin):
    """Admin for procurement request items."""
    list_display = [
        'request_link', 'product_name', 'product_sku', 'quantity',
        'estimated_unit_price', 'estimated_total_price'
    ]
    list_filter = ['request__status', 'request__priority']
    search_fields = [
        'request__request_number', 'product_name', 'product_sku', 'product_description'
    ]
    readonly_fields = ['product_name', 'product_sku', 'estimated_total_price']
    
    def request_link(self, obj):
        """Create a link to the procurement request."""
        url = reverse('admin:purchasing_procurementrequest_change', args=[obj.request.id])
        return format_html('<a href="{}">{}</a>', url, obj.request.request_number)
    request_link.short_description = 'Request'


@admin.register(SupplierPerformance)
class SupplierPerformanceAdmin(admin.ModelAdmin):
    """Admin for supplier performance records."""
    list_display = [
        'supplier_link', 'overall_rating_stars', 'on_time_delivery_rate',
        'quality_rating_stars', 'communication_rating_stars', 'evaluation_date'
    ]
    list_filter = [
        'evaluation_date', 'evaluated_by', 'supplier'
    ]
    search_fields = [
        'supplier__name', 'notes'
    ]
    readonly_fields = [
        'overall_rating', 'evaluation_date', 'created', 'modified'
    ]
    fieldsets = (
        ('Supplier Information', {
            'fields': ('supplier', 'evaluated_by')
        }),
        ('Performance Metrics', {
            'fields': ('on_time_delivery_rate', 'quality_rating', 'communication_rating', 'price_competitiveness')
        }),
        ('Overall Rating', {
            'fields': ('overall_rating',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'evaluation_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'evaluation_date'
    ordering = ['-evaluation_date']
    
    def supplier_link(self, obj):
        """Create a link to the supplier."""
        if obj.supplier:
            url = reverse('admin:inventory_supplier_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return '-'
    supplier_link.short_description = 'Supplier'
    
    def overall_rating_stars(self, obj):
        """Display overall rating as stars."""
        return self._rating_stars(obj.overall_rating)
    overall_rating_stars.short_description = 'Overall Rating'
    
    def quality_rating_stars(self, obj):
        """Display quality rating as stars."""
        return self._rating_stars(obj.quality_rating)
    quality_rating_stars.short_description = 'Quality'
    
    def communication_rating_stars(self, obj):
        """Display communication rating as stars."""
        return self._rating_stars(obj.communication_rating)
    communication_rating_stars.short_description = 'Communication'
    
    def _rating_stars(self, rating):
        """Convert rating to star display."""
        if rating is None:
            return '-'
        
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars = '★' * full_stars + '☆' * half_star + '☆' * empty_stars
        return format_html('<span title="{:.1f}/5.0">{}</span>', rating, stars)


@admin.register(PurchaseAnalytics)
class PurchaseAnalyticsAdmin(admin.ModelAdmin):
    """Admin for purchase analytics."""
    list_display = [
        'period_display', 'total_orders', 'total_value', 'average_order_value',
        'active_suppliers', 'on_time_delivery_rate'
    ]
    list_filter = [
        'period_start', 'period_end'
    ]
    search_fields = [
        'name'
    ]
    readonly_fields = [
        'created', 'modified'
    ]
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'total_value', 'average_order_value')
        }),
        ('Supplier Metrics', {
            'fields': ('active_suppliers', 'top_supplier', 'top_supplier_value')
        }),
        ('Performance Metrics', {
            'fields': ('on_time_delivery_rate', 'average_processing_time')
        }),
        ('Cost Analysis', {
            'fields': ('total_savings', 'cost_reduction_percentage')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'period_start'
    ordering = ['-period_end']
    
    def period_display(self, obj):
        """Display the period in a readable format."""
        return f"{obj.period_start.date()} - {obj.period_end.date()}"
    period_display.short_description = 'Period'

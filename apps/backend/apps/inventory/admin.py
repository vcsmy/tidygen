"""
Inventory admin configuration.
"""
from django.contrib import admin
from .models import (
    Product, ProductCategory, StockMovement, Supplier,
    PurchaseOrder, PurchaseOrderItem
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Product category admin."""
    list_display = ['name', 'parent', 'products_count', 'created']
    list_filter = ['parent', 'created']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin."""
    list_display = [
        'name', 'sku', 'category', 'current_stock', 'cost_price',
        'selling_price', 'stock_status', 'is_active'
    ]
    list_filter = [
        'category', 'is_active', 'is_digital', 'created'
    ]
    search_fields = ['name', 'sku', 'description', 'barcode']
    ordering = ['name']
    readonly_fields = ['current_stock']
    
    def stock_status(self, obj):
        if obj.current_stock <= obj.min_stock_level:
            return 'Low Stock'
        elif obj.current_stock >= obj.max_stock_level:
            return 'Overstocked'
        return 'Normal'
    stock_status.short_description = 'Stock Status'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Stock movement admin."""
    list_display = [
        'product', 'movement_type', 'quantity', 'reference_number',
        'created'
    ]
    list_filter = ['movement_type', 'created']
    search_fields = ['product__name', 'reference_number', 'notes']
    ordering = ['-created']
    readonly_fields = ['created', 'modified']
    
    def product_organization(self, obj):
        return obj.product.organization.name
    product_organization.short_description = 'Organization'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Supplier admin."""
    list_display = [
        'name', 'contact_person', 'email', 'phone',
        'purchase_orders_count', 'total_spent'
    ]
    list_filter = ['created']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering = ['name']
    
    def purchase_orders_count(self, obj):
        return obj.purchase_orders.count()
    purchase_orders_count.short_description = 'Orders'
    
    def total_spent(self, obj):
        total = sum(po.total_amount for po in obj.purchase_orders.filter(status='received'))
        return f"${total:,.2f}"
    total_spent.short_description = 'Total Spent'


class PurchaseOrderItemInline(admin.TabularInline):
    """Purchase order item inline admin."""
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Purchase order admin."""
    list_display = [
        'order_number', 'supplier', 'status', 'order_date',
        'expected_delivery', 'total_amount', 'items_count'
    ]
    list_filter = ['status', 'order_date', 'created']
    search_fields = ['order_number', 'supplier__name', 'notes']
    ordering = ['-order_date']
    readonly_fields = ['order_number', 'total_amount', 'created', 'modified']
    inlines = [PurchaseOrderItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """Purchase order item admin."""
    list_display = [
        'purchase_order', 'product', 'quantity', 'unit_price',
        'total_price'
    ]
    list_filter = ['purchase_order__status']
    search_fields = ['product__name', 'purchase_order__order_number']
    ordering = ['purchase_order', 'product']
    readonly_fields = ['total_price']
    
    def organization(self, obj):
        return obj.purchase_order.organization.name
    organization.short_description = 'Organization'

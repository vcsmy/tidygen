"""
Inventory management serializers.
"""
from rest_framework import serializers
from .models import (
    Product, ProductCategory, StockMovement, Supplier,
    PurchaseOrder, PurchaseOrderItem
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """Product category serializer."""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name',
            'products_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'category', 'category_name',
            'cost_price', 'selling_price', 'current_stock', 'min_stock_level',
            'max_stock_level', 'weight', 'dimensions', 'barcode', 'image',
            'is_active', 'is_digital', 'stock_status', 'total_value', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']

    def get_stock_status(self, obj):
        if obj.current_stock <= obj.min_stock_level:
            return 'low_stock'
        elif obj.current_stock >= obj.max_stock_level:
            return 'overstocked'
        else:
            return 'normal'

    def get_total_value(self, obj):
        return float(obj.current_stock * obj.cost_price)


class StockMovementSerializer(serializers.ModelSerializer):
    """Stock movement serializer."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'movement_type',
            'movement_type_display', 'quantity', 'reference_number', 'notes',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer."""
    purchase_orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address',
            'payment_terms', 'purchase_orders_count', 'total_spent', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']

    def get_purchase_orders_count(self, obj):
        return obj.purchase_orders.count()

    def get_total_spent(self, obj):
        total = sum(po.total_amount for po in obj.purchase_orders.filter(status='received'))
        return float(total)


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Purchase order item serializer."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'total_price', 'created', 'modified'
        ]
        read_only_fields = ['id', 'total_price', 'created', 'modified']

    def validate(self, data):
        """Validate and calculate total price."""
        quantity = data.get('quantity', 0)
        unit_price = data.get('unit_price', 0)
        data['total_price'] = quantity * unit_price
        return data


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Purchase order serializer."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'order_number', 'status', 'status_display', 
            'order_date', 'expected_delivery', 'total_amount', 'notes', 'items', 'items_count',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'order_number', 'total_amount', 'created', 'modified']

    def get_items_count(self, obj):
        return obj.items.count()


class InventorySummarySerializer(serializers.Serializer):
    """Inventory summary serializer."""
    total_products = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    low_stock_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    recent_movements = serializers.IntegerField()
    pending_orders = serializers.IntegerField()


class StockAlertSerializer(serializers.Serializer):
    """Stock alert serializer."""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_sku = serializers.CharField()
    current_stock = serializers.IntegerField()
    min_stock_level = serializers.IntegerField()
    alert_type = serializers.CharField()  # 'low_stock', 'out_of_stock'
    days_until_stockout = serializers.IntegerField()
    suggested_order_quantity = serializers.IntegerField()

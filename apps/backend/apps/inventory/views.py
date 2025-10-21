"""
Inventory management views.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsOrganizationMember
from apps.core.views import BaseModelViewSet
from .models import (
    Product, ProductCategory, StockMovement, Supplier,
    PurchaseOrder, PurchaseOrderItem
)
from .serializers import (
    ProductSerializer, ProductCategorySerializer, StockMovementSerializer,
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer,
    InventorySummarySerializer, StockAlertSerializer
)


@extend_schema(tags=['Inventory'])
class ProductCategoryViewSet(BaseModelViewSet):
    """Product category viewset."""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created', 'modified']
    ordering = ['name']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset()

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in a category."""
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure."""
        categories = self.get_queryset().filter(parent=None)
        tree_data = []
        
        for category in categories:
            tree_data.append(self._build_category_tree(category))
        
        return Response(tree_data)

    def _build_category_tree(self, category):
        """Build category tree recursively."""
        children = ProductCategory.objects.filter(parent=category)
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'products_count': category.products.count(),
            'children': [self._build_category_tree(child) for child in children]
        }


@extend_schema(tags=['Inventory'])
class ProductViewSet(BaseModelViewSet):
    """Product viewset."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_digital']
    search_fields = ['name', 'sku', 'description', 'barcode']
    ordering_fields = ['name', 'sku', 'current_stock', 'cost_price', 'selling_price', 'created']
    ordering = ['name']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust product stock."""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('movement_type', 'adjustment')
        notes = request.data.get('notes', '')
        reference = request.data.get('reference_number', '')

        if movement_type == 'in':
            product.current_stock += quantity
        elif movement_type == 'out':
            if product.current_stock < quantity:
                return Response(
                    {'error': 'Insufficient stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.current_stock -= quantity
        elif movement_type == 'adjustment':
            product.current_stock = quantity

        product.save()

        # Create stock movement record
        StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=abs(quantity),
            reference_number=reference,
            notes=notes
        )

        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock."""
        products = self.get_queryset().filter(
            current_stock__lte=models.F('min_stock_level')
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock products."""
        products = self.get_queryset().filter(current_stock=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """Get stock alerts for all products."""
        products = self.get_queryset()
        alerts = []

        for product in products:
            if product.current_stock <= product.min_stock_level:
                alert_type = 'out_of_stock' if product.current_stock == 0 else 'low_stock'
                days_until_stockout = self._calculate_days_until_stockout(product)
                suggested_quantity = max(product.max_stock_level - product.current_stock, 10)

                alerts.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'current_stock': product.current_stock,
                    'min_stock_level': product.min_stock_level,
                    'alert_type': alert_type,
                    'days_until_stockout': days_until_stockout,
                    'suggested_order_quantity': suggested_quantity
                })

        return Response(alerts)

    def _calculate_days_until_stockout(self, product):
        """Calculate days until stockout based on recent movements."""
        recent_movements = StockMovement.objects.filter(
            product=product,
            movement_type='out',
            created__gte=timezone.now() - timedelta(days=30)
        )
        
        if not recent_movements.exists():
            return 999  # No recent outbound movements
        
        avg_daily_out = recent_movements.aggregate(
            avg_quantity=Sum('quantity') / 30
        )['avg_quantity'] or 0
        
        if avg_daily_out <= 0:
            return 999
        
        return int(product.current_stock / avg_daily_out)


@extend_schema(tags=['Inventory'])
class StockMovementViewSet(BaseModelViewSet):
    """Stock movement viewset."""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'movement_type']
    search_fields = ['reference_number', 'notes', 'product__name']
    ordering_fields = ['created', 'quantity', 'movement_type']
    ordering = ['-created']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset().filter(
            product__organization=self.request.user.organization
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock movement summary."""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created__date__lte=end_date)

        summary = {
            'total_movements': queryset.count(),
            'stock_in': queryset.filter(movement_type='in').aggregate(
                total=Sum('quantity')
            )['total'] or 0,
            'stock_out': queryset.filter(movement_type='out').aggregate(
                total=Sum('quantity')
            )['total'] or 0,
            'transfers': queryset.filter(movement_type='transfer').count(),
            'adjustments': queryset.filter(movement_type='adjustment').count(),
        }
        
        return Response(summary)


@extend_schema(tags=['Inventory'])
class SupplierViewSet(BaseModelViewSet):
    """Supplier viewset."""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'created']
    ordering = ['name']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset()

    @action(detail=True, methods=['get'])
    def purchase_orders(self, request, pk=None):
        """Get purchase orders for a supplier."""
        supplier = self.get_object()
        purchase_orders = PurchaseOrder.objects.filter(supplier=supplier)
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get supplier performance metrics."""
        supplier = self.get_object()
        
        # Calculate performance metrics
        total_orders = supplier.purchase_orders.count()
        received_orders = supplier.purchase_orders.filter(status='received').count()
        total_spent = supplier.purchase_orders.filter(status='received').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate on-time delivery
        on_time_deliveries = supplier.purchase_orders.filter(
            status='received',
            expected_delivery__gte=models.F('updated__date')
        ).count()
        
        performance = {
            'total_orders': total_orders,
            'received_orders': received_orders,
            'total_spent': float(total_spent),
            'on_time_delivery_rate': (on_time_deliveries / received_orders * 100) if received_orders > 0 else 0,
            'average_order_value': float(total_spent / received_orders) if received_orders > 0 else 0
        }
        
        return Response(performance)


@extend_schema(tags=['Inventory'])
class PurchaseOrderViewSet(BaseModelViewSet):
    """Purchase order viewset."""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'status']
    search_fields = ['order_number', 'notes', 'supplier__name']
    ordering_fields = ['order_date', 'total_amount', 'created']
    ordering = ['-order_date']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset()

    def perform_create(self, serializer):
        """Generate order number and save."""
        # Generate order number
        last_order = PurchaseOrder.objects.filter(
            organization=self.request.user.organization
        ).order_by('-id').first()
        
        if last_order:
            last_number = int(last_order.order_number.split('-')[1])
            new_number = f"PO-{last_number + 1:06d}"
        else:
            new_number = "PO-000001"
        
        serializer.save(
            organization=self.request.user.organization,
            order_number=new_number
        )

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to purchase order."""
        purchase_order = self.get_object()
        item_data = request.data.copy()
        item_data['purchase_order'] = purchase_order.id
        
        serializer = PurchaseOrderItemSerializer(data=item_data)
        if serializer.is_valid():
            serializer.save()
            
            # Recalculate total amount
            total = purchase_order.items.aggregate(
                total=Sum('total_price')
            )['total'] or 0
            purchase_order.total_amount = total
            purchase_order.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change purchase order status."""
        purchase_order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(PurchaseOrder.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = new_status
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending purchase orders."""
        pending_orders = self.get_queryset().filter(
            status__in=['draft', 'sent', 'confirmed']
        )
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Inventory'])
class PurchaseOrderItemViewSet(BaseModelViewSet):
    """Purchase order item viewset."""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['purchase_order', 'product']
    ordering_fields = ['quantity', 'unit_price', 'total_price']
    ordering = ['id']

    def get_queryset(self):
        """Filter by organization."""
        return super().get_queryset().filter(
            purchase_order__organization=self.request.user.organization
        )


@extend_schema(tags=['Inventory'])
class InventoryDashboardViewSet(viewsets.ViewSet):
    """Inventory dashboard viewset."""
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get inventory summary."""
        organization = request.user.organization
        
        # Calculate summary metrics
        total_products = Product.objects.count()
        total_categories = ProductCategory.objects.count()
        total_suppliers = Supplier.objects.count()
        
        # Calculate total stock value
        products = Product.objects
        total_stock_value = sum(
            product.current_stock * product.cost_price 
            for product in products
        )
        
        # Calculate low stock and out of stock products
        low_stock_products = products.filter(
            current_stock__lte=models.F('min_stock_level')
        ).count()
        out_of_stock_products = products.filter(current_stock=0).count()
        
        # Calculate recent movements
        recent_movements = StockMovement.objects.filter(
            product__organization=organization,
            created__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Calculate pending orders
        pending_orders = PurchaseOrder.objects.filter(
            organization=organization,
            status__in=['draft', 'sent', 'confirmed']
        ).count()
        
        summary = {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_suppliers': total_suppliers,
            'total_stock_value': float(total_stock_value),
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'recent_movements': recent_movements,
            'pending_orders': pending_orders
        }
        
        serializer = InventorySummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """Get stock alerts."""
        organization = request.user.organization
        products = Product.objects
        alerts = []

        for product in products:
            if product.current_stock <= product.min_stock_level:
                alert_type = 'out_of_stock' if product.current_stock == 0 else 'low_stock'
                days_until_stockout = self._calculate_days_until_stockout(product)
                suggested_quantity = max(product.max_stock_level - product.current_stock, 10)

                alerts.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'current_stock': product.current_stock,
                    'min_stock_level': product.min_stock_level,
                    'alert_type': alert_type,
                    'days_until_stockout': days_until_stockout,
                    'suggested_order_quantity': suggested_quantity
                })

        return Response(alerts)

    def _calculate_days_until_stockout(self, product):
        """Calculate days until stockout based on recent movements."""
        recent_movements = StockMovement.objects.filter(
            product=product,
            movement_type='out',
            created__gte=timezone.now() - timedelta(days=30)
        )
        
        if not recent_movements.exists():
            return 999  # No recent outbound movements
        
        avg_daily_out = recent_movements.aggregate(
            avg_quantity=Sum('quantity') / 30
        )['avg_quantity'] or 0
        
        if avg_daily_out <= 0:
            return 999
        
        return int(product.current_stock / avg_daily_out)

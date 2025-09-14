"""
Custom filters for TidyGen ERP platform.
"""

import django_filters
from django.db.models import Q
from .models import User, Role, AuditLog


class UserFilter(django_filters.FilterSet):
    """
    Filter for User model.
    """
    search = django_filters.CharFilter(method='filter_search')
    is_verified = django_filters.BooleanFilter(field_name='is_verified')
    wallet_verified = django_filters.BooleanFilter(field_name='wallet_verified')
    date_joined_after = django_filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_before = django_filters.DateFilter(field_name='date_joined', lookup_expr='lte')
    last_login_after = django_filters.DateFilter(field_name='last_login', lookup_expr='gte')
    last_login_before = django_filters.DateFilter(field_name='last_login', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'is_superuser': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(username__icontains=value) |
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )


class RoleFilter(django_filters.FilterSet):
    """
    Filter for Role model.
    """
    search = django_filters.CharFilter(method='filter_search')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    is_system = django_filters.BooleanFilter(field_name='is_system')
    has_permission = django_filters.CharFilter(method='filter_has_permission')
    
    class Meta:
        model = Role
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_has_permission(self, queryset, name, value):
        """
        Filter roles that have a specific permission.
        """
        if not value:
            return queryset
        
        return queryset.filter(permissions__codename=value)


class AuditLogFilter(django_filters.FilterSet):
    """
    Filter for AuditLog model.
    """
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    action = django_filters.ChoiceFilter(choices=AuditLog.ACTION_CHOICES)
    model_name = django_filters.CharFilter(field_name='model_name', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    ip_address = django_filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    
    class Meta:
        model = AuditLog
        fields = {
            'object_id': ['exact'],
            'object_repr': ['icontains'],
        }

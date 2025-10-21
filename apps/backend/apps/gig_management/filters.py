"""
Filters for gig_management app.
"""
import django_filters
from django.db.models import Q
from .models import GigJob, GigCategory


class GigJobFilter(django_filters.FilterSet):
    """
    Filter set for gig job list view.
    """
    search = django_filters.CharFilter(method='filter_search')
    category = django_filters.ModelChoiceFilter(queryset=GigCategory.objects.filter(is_active=True))
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='state', lookup_expr='icontains')
    client_type = django_filters.ChoiceFilter(choices=GigJob.CLIENT_TYPES)
    status = django_filters.ChoiceFilter(choices=GigJob.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=GigJob.PRIORITY_CHOICES)
    payment_method = django_filters.ChoiceFilter(choices=GigJob.PAYMENT_METHOD_CHOICES)
    
    # Price filters
    min_hourly_rate = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    max_hourly_rate = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    min_fixed_price = django_filters.NumberFilter(field_name='fixed_price', lookup_expr='gte')
    max_fixed_price = django_filters.NumberFilter(field_name='fixed_price', lookup_expr='lte')
    
    # Date filters
    start_date_from = django_filters.DateTimeFilter(field_name='preferred_start_date', lookup_expr='gte')
    start_date_to = django_filters.DateTimeFilter(field_name='preferred_start_date', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    
    # Service filters
    service_type = django_filters.CharFilter(field_name='service_type', lookup_expr='icontains')
    property_type = django_filters.CharFilter(field_name='property_type', lookup_expr='icontains')
    
    # Assignment filters
    has_freelancer = django_filters.BooleanFilter(field_name='assigned_freelancer', lookup_expr='isnull')
    is_urgent = django_filters.BooleanFilter(field_name='is_urgent')
    
    class Meta:
        model = GigJob
        fields = [
            'search', 'category', 'city', 'state', 'client_type', 'status', 'priority',
            'payment_method', 'min_hourly_rate', 'max_hourly_rate', 'min_fixed_price',
            'max_fixed_price', 'start_date_from', 'start_date_to', 'created_from',
            'created_to', 'service_type', 'property_type', 'has_freelancer', 'is_urgent'
        ]
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        if not value:
            return queryset
            
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(job_id__icontains=value) |
            Q(service_type__icontains=value) |
            Q(property_type__icontains=value) |
            Q(city__icontains=value) |
            Q(state__icontains=value) |
            Q(special_requirements__icontains=value)
        )

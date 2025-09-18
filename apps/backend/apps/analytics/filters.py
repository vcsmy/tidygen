"""
Analytics & Reporting Filters

This module contains all the filters for the analytics and reporting system,
providing advanced data querying capabilities for reports, KPIs, dashboards, and analytics components.
"""

import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)


class ReportFilter(django_filters.FilterSet):
    """Filter for reports."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type and status filters
    report_type = django_filters.ChoiceFilter(choices=Report.REPORT_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=Report.REPORT_STATUS_CHOICES)
    format = django_filters.ChoiceFilter(choices=Report.REPORT_FORMAT_CHOICES)
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_run_from = django_filters.DateTimeFilter(field_name='last_run', lookup_expr='gte')
    last_run_to = django_filters.DateTimeFilter(field_name='last_run', lookup_expr='lte')
    next_run_from = django_filters.DateTimeFilter(field_name='next_run', lookup_expr='gte')
    next_run_to = django_filters.DateTimeFilter(field_name='next_run', lookup_expr='lte')
    
    # Related filters
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    
    # Special filters
    scheduled = django_filters.BooleanFilter(field_name='is_scheduled')
    public = django_filters.BooleanFilter(field_name='is_public')
    has_file = django_filters.BooleanFilter(method='filter_has_file')
    overdue = django_filters.BooleanFilter(method='filter_overdue')
    
    class Meta:
        model = Report
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(report_type__icontains=value)
        )
    
    def filter_has_file(self, queryset, name, value):
        """Filter for reports with files."""
        if value:
            return queryset.exclude(file_path='')
        return queryset.filter(file_path='')
    
    def filter_overdue(self, queryset, name, value):
        """Filter for overdue scheduled reports."""
        if value:
            return queryset.filter(
                is_scheduled=True,
                next_run__lt=timezone.now(),
                status__in=['scheduled', 'running']
            )
        return queryset


class KPIFilter(django_filters.FilterSet):
    """Filter for KPIs."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type and status filters
    kpi_type = django_filters.ChoiceFilter(choices=KPI.KPI_TYPE_CHOICES)
    frequency = django_filters.ChoiceFilter(choices=KPI.KPI_FREQUENCY_CHOICES)
    trend = django_filters.ChoiceFilter(choices=KPI.KPI_TREND_CHOICES)
    
    # Value filters
    current_value_min = django_filters.NumberFilter(field_name='current_value', lookup_expr='gte')
    current_value_max = django_filters.NumberFilter(field_name='current_value', lookup_expr='lte')
    target_value_min = django_filters.NumberFilter(field_name='target_value', lookup_expr='gte')
    target_value_max = django_filters.NumberFilter(field_name='target_value', lookup_expr='lte')
    change_percentage_min = django_filters.NumberFilter(field_name='change_percentage', lookup_expr='gte')
    change_percentage_max = django_filters.NumberFilter(field_name='change_percentage', lookup_expr='lte')
    
    # Date filters
    last_calculated_from = django_filters.DateTimeFilter(field_name='last_calculated', lookup_expr='gte')
    last_calculated_to = django_filters.DateTimeFilter(field_name='last_calculated', lookup_expr='lte')
    next_calculation_from = django_filters.DateTimeFilter(field_name='next_calculation', lookup_expr='gte')
    next_calculation_to = django_filters.DateTimeFilter(field_name='next_calculation', lookup_expr='lte')
    
    # Special filters
    active = django_filters.BooleanFilter(field_name='is_active')
    has_data = django_filters.BooleanFilter(method='filter_has_data')
    above_target = django_filters.BooleanFilter(method='filter_above_target')
    below_warning = django_filters.BooleanFilter(method='filter_below_warning')
    below_critical = django_filters.BooleanFilter(method='filter_below_critical')
    overdue_calculation = django_filters.BooleanFilter(method='filter_overdue_calculation')
    
    class Meta:
        model = KPI
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
            'data_source': ['exact', 'icontains'],
            'unit': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(data_source__icontains=value)
        )
    
    def filter_has_data(self, queryset, name, value):
        """Filter for KPIs with data."""
        if value:
            return queryset.exclude(current_value__isnull=True)
        return queryset.filter(current_value__isnull=True)
    
    def filter_above_target(self, queryset, name, value):
        """Filter for KPIs above target."""
        if value:
            return queryset.filter(
                current_value__gte=F('target_value'),
                target_value__isnull=False
            )
        return queryset
    
    def filter_below_warning(self, queryset, name, value):
        """Filter for KPIs below warning threshold."""
        if value:
            return queryset.filter(
                current_value__lte=F('warning_threshold'),
                warning_threshold__isnull=False
            )
        return queryset
    
    def filter_below_critical(self, queryset, name, value):
        """Filter for KPIs below critical threshold."""
        if value:
            return queryset.filter(
                current_value__lte=F('critical_threshold'),
                critical_threshold__isnull=False
            )
        return queryset
    
    def filter_overdue_calculation(self, queryset, name, value):
        """Filter for KPIs with overdue calculations."""
        if value:
            return queryset.filter(
                next_calculation__lt=timezone.now(),
                is_active=True
            )
        return queryset


class DashboardFilter(django_filters.FilterSet):
    """Filter for dashboards."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type and layout filters
    dashboard_type = django_filters.ChoiceFilter(choices=Dashboard.DASHBOARD_TYPE_CHOICES)
    layout = django_filters.ChoiceFilter(choices=Dashboard.DASHBOARD_LAYOUT_CHOICES)
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_updated_from = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='gte')
    last_updated_to = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='lte')
    
    # Related filters
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    
    # Special filters
    active = django_filters.BooleanFilter(field_name='is_active')
    public = django_filters.BooleanFilter(field_name='is_public')
    auto_refresh = django_filters.BooleanFilter(field_name='auto_refresh')
    has_widgets = django_filters.BooleanFilter(method='filter_has_widgets')
    
    class Meta:
        model = Dashboard
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
            'refresh_interval': ['exact', 'gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(dashboard_type__icontains=value)
        )
    
    def filter_has_widgets(self, queryset, name, value):
        """Filter for dashboards with widgets."""
        if value:
            return queryset.filter(widgets__isnull=False).distinct()
        return queryset.filter(widgets__isnull=True)


class DataSourceFilter(django_filters.FilterSet):
    """Filter for data sources."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type filters
    source_type = django_filters.ChoiceFilter(choices=DataSource.SOURCE_TYPE_CHOICES)
    connection_type = django_filters.ChoiceFilter(choices=DataSource.CONNECTION_TYPE_CHOICES)
    connection_status = django_filters.CharFilter(field_name='connection_status')
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_connected_from = django_filters.DateTimeFilter(field_name='last_connected', lookup_expr='gte')
    last_connected_to = django_filters.DateTimeFilter(field_name='last_connected', lookup_expr='lte')
    
    # Special filters
    active = django_filters.BooleanFilter(field_name='is_active')
    connected = django_filters.BooleanFilter(method='filter_connected')
    never_connected = django_filters.BooleanFilter(method='filter_never_connected')
    
    class Meta:
        model = DataSource
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(source_type__icontains=value) |
            Q(connection_type__icontains=value)
        )
    
    def filter_connected(self, queryset, name, value):
        """Filter for connected data sources."""
        if value:
            return queryset.filter(connection_status='connected')
        return queryset.exclude(connection_status='connected')
    
    def filter_never_connected(self, queryset, name, value):
        """Filter for data sources that have never been connected."""
        if value:
            return queryset.filter(last_connected__isnull=True)
        return queryset.exclude(last_connected__isnull=True)


class ReportTemplateFilter(django_filters.FilterSet):
    """Filter for report templates."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type filter
    template_type = django_filters.ChoiceFilter(choices=ReportTemplate.TEMPLATE_TYPE_CHOICES)
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Related filters
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    
    # Special filters
    public = django_filters.BooleanFilter(field_name='is_public')
    popular = django_filters.BooleanFilter(method='filter_popular')
    
    class Meta:
        model = ReportTemplate
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
            'usage_count': ['exact', 'gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(template_type__icontains=value)
        )
    
    def filter_popular(self, queryset, name, value):
        """Filter for popular templates."""
        if value:
            return queryset.filter(usage_count__gte=10)
        return queryset.filter(usage_count__lt=10)


class AnalyticsEventFilter(django_filters.FilterSet):
    """Filter for analytics events."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type filter
    event_type = django_filters.ChoiceFilter(choices=AnalyticsEvent.EVENT_TYPE_CHOICES)
    
    # Date filters
    event_timestamp_from = django_filters.DateTimeFilter(field_name='event_timestamp', lookup_expr='gte')
    event_timestamp_to = django_filters.DateTimeFilter(field_name='event_timestamp', lookup_expr='lte')
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Related filters
    user = django_filters.NumberFilter(field_name='user__id')
    
    # Special filters
    has_user = django_filters.BooleanFilter(method='filter_has_user')
    has_duration = django_filters.BooleanFilter(method='filter_has_duration')
    recent = django_filters.BooleanFilter(method='filter_recent')
    
    class Meta:
        model = AnalyticsEvent
        fields = {
            'event_name': ['exact', 'icontains'],
            'description': ['icontains'],
            'session_id': ['exact', 'icontains'],
            'ip_address': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(event_name__icontains=value) |
            Q(description__icontains=value) |
            Q(event_type__icontains=value)
        )
    
    def filter_has_user(self, queryset, name, value):
        """Filter for events with users."""
        if value:
            return queryset.exclude(user__isnull=True)
        return queryset.filter(user__isnull=True)
    
    def filter_has_duration(self, queryset, name, value):
        """Filter for events with duration."""
        if value:
            return queryset.exclude(duration__isnull=True)
        return queryset.filter(duration__isnull=True)
    
    def filter_recent(self, queryset, name, value):
        """Filter for recent events."""
        if value:
            return queryset.filter(
                event_timestamp__gte=timezone.now() - timedelta(hours=24)
            )
        return queryset


class AlertFilter(django_filters.FilterSet):
    """Filter for alerts."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type and status filters
    alert_type = django_filters.ChoiceFilter(choices=Alert.ALERT_TYPE_CHOICES)
    severity = django_filters.ChoiceFilter(choices=Alert.ALERT_SEVERITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=Alert.ALERT_STATUS_CHOICES)
    
    # Date filters
    triggered_at_from = django_filters.DateTimeFilter(field_name='triggered_at', lookup_expr='gte')
    triggered_at_to = django_filters.DateTimeFilter(field_name='triggered_at', lookup_expr='lte')
    acknowledged_at_from = django_filters.DateTimeFilter(field_name='acknowledged_at', lookup_expr='gte')
    acknowledged_at_to = django_filters.DateTimeFilter(field_name='acknowledged_at', lookup_expr='lte')
    resolved_at_from = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='gte')
    resolved_at_to = django_filters.DateTimeFilter(field_name='resolved_at', lookup_expr='lte')
    
    # Related filters
    acknowledged_by = django_filters.NumberFilter(field_name='acknowledged_by__id')
    related_kpi = django_filters.NumberFilter(field_name='related_kpi__id')
    related_report = django_filters.NumberFilter(field_name='related_report__id')
    related_dashboard = django_filters.NumberFilter(field_name='related_dashboard__id')
    
    # Value filters
    threshold_value_min = django_filters.NumberFilter(field_name='threshold_value', lookup_expr='gte')
    threshold_value_max = django_filters.NumberFilter(field_name='threshold_value', lookup_expr='lte')
    current_value_min = django_filters.NumberFilter(field_name='current_value', lookup_expr='gte')
    current_value_max = django_filters.NumberFilter(field_name='current_value', lookup_expr='lte')
    
    # Special filters
    notified = django_filters.BooleanFilter(field_name='is_notified')
    unacknowledged = django_filters.BooleanFilter(method='filter_unacknowledged')
    unresolved = django_filters.BooleanFilter(method='filter_unresolved')
    old = django_filters.BooleanFilter(method='filter_old')
    
    class Meta:
        model = Alert
        fields = {
            'title': ['exact', 'icontains'],
            'message': ['icontains'],
            'description': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(message__icontains=value) |
            Q(description__icontains=value) |
            Q(alert_type__icontains=value)
        )
    
    def filter_unacknowledged(self, queryset, name, value):
        """Filter for unacknowledged alerts."""
        if value:
            return queryset.filter(acknowledged_by__isnull=True)
        return queryset.exclude(acknowledged_by__isnull=True)
    
    def filter_unresolved(self, queryset, name, value):
        """Filter for unresolved alerts."""
        if value:
            return queryset.filter(resolved_at__isnull=True)
        return queryset.exclude(resolved_at__isnull=True)
    
    def filter_old(self, queryset, name, value):
        """Filter for old alerts."""
        if value:
            return queryset.filter(
                triggered_at__lt=timezone.now() - timedelta(days=7)
            )
        return queryset.filter(
            triggered_at__gte=timezone.now() - timedelta(days=7)
        )


class KPIMeasurementFilter(django_filters.FilterSet):
    """Filter for KPI measurements."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Date filters
    measurement_date_from = django_filters.DateTimeFilter(field_name='measurement_date', lookup_expr='gte')
    measurement_date_to = django_filters.DateTimeFilter(field_name='measurement_date', lookup_expr='lte')
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Value filters
    value_min = django_filters.NumberFilter(field_name='value', lookup_expr='gte')
    value_max = django_filters.NumberFilter(field_name='value', lookup_expr='lte')
    
    # Related filters
    kpi = django_filters.NumberFilter(field_name='kpi__id')
    
    # Special filters
    has_notes = django_filters.BooleanFilter(method='filter_has_notes')
    has_context = django_filters.BooleanFilter(method='filter_has_context')
    recent = django_filters.BooleanFilter(method='filter_recent')
    
    class Meta:
        model = KPIMeasurement
        fields = {
            'notes': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(kpi__name__icontains=value) |
            Q(notes__icontains=value)
        )
    
    def filter_has_notes(self, queryset, name, value):
        """Filter for measurements with notes."""
        if value:
            return queryset.exclude(notes='')
        return queryset.filter(notes='')
    
    def filter_has_context(self, queryset, name, value):
        """Filter for measurements with context data."""
        if value:
            return queryset.exclude(context_data={})
        return queryset.filter(context_data={})
    
    def filter_recent(self, queryset, name, value):
        """Filter for recent measurements."""
        if value:
            return queryset.filter(
                measurement_date__gte=timezone.now() - timedelta(days=7)
            )
        return queryset


class DashboardWidgetFilter(django_filters.FilterSet):
    """Filter for dashboard widgets."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type filters
    widget_type = django_filters.ChoiceFilter(choices=DashboardWidget.WIDGET_TYPE_CHOICES)
    chart_type = django_filters.ChoiceFilter(choices=DashboardWidget.CHART_TYPE_CHOICES)
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_updated_from = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='gte')
    last_updated_to = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='lte')
    
    # Related filters
    dashboard = django_filters.NumberFilter(field_name='dashboard__id')
    
    # Layout filters
    position_x_min = django_filters.NumberFilter(field_name='position_x', lookup_expr='gte')
    position_x_max = django_filters.NumberFilter(field_name='position_x', lookup_expr='lte')
    position_y_min = django_filters.NumberFilter(field_name='position_y', lookup_expr='gte')
    position_y_max = django_filters.NumberFilter(field_name='position_y', lookup_expr='lte')
    width_min = django_filters.NumberFilter(field_name='width', lookup_expr='gte')
    width_max = django_filters.NumberFilter(field_name='width', lookup_expr='lte')
    height_min = django_filters.NumberFilter(field_name='height', lookup_expr='gte')
    height_max = django_filters.NumberFilter(field_name='height', lookup_expr='lte')
    
    # Special filters
    active = django_filters.BooleanFilter(field_name='is_active')
    has_data_source = django_filters.BooleanFilter(method='filter_has_data_source')
    has_query = django_filters.BooleanFilter(method='filter_has_query')
    
    class Meta:
        model = DashboardWidget
        fields = {
            'name': ['exact', 'icontains'],
            'data_source': ['exact', 'icontains'],
            'refresh_interval': ['exact', 'gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(data_source__icontains=value) |
            Q(widget_type__icontains=value)
        )
    
    def filter_has_data_source(self, queryset, name, value):
        """Filter for widgets with data sources."""
        if value:
            return queryset.exclude(data_source='')
        return queryset.filter(data_source='')
    
    def filter_has_query(self, queryset, name, value):
        """Filter for widgets with queries."""
        if value:
            return queryset.exclude(query='')
        return queryset.filter(query='')


class AnalyticsCacheFilter(django_filters.FilterSet):
    """Filter for analytics cache."""
    
    # Text search
    search = django_filters.CharFilter(method='filter_search')
    
    # Type filter
    cache_type = django_filters.ChoiceFilter(choices=AnalyticsCache.CACHE_TYPE_CHOICES)
    
    # Date filters
    expires_at_from = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_at_to = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    last_accessed_from = django_filters.DateTimeFilter(field_name='last_accessed', lookup_expr='gte')
    last_accessed_to = django_filters.DateTimeFilter(field_name='last_accessed', lookup_expr='lte')
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Related filters
    related_kpi = django_filters.NumberFilter(field_name='related_kpi__id')
    related_report = django_filters.NumberFilter(field_name='related_report__id')
    related_dashboard = django_filters.NumberFilter(field_name='related_dashboard__id')
    
    # Special filters
    expired = django_filters.BooleanFilter(method='filter_expired')
    popular = django_filters.BooleanFilter(method='filter_popular')
    unused = django_filters.BooleanFilter(method='filter_unused')
    
    class Meta:
        model = AnalyticsCache
        fields = {
            'cache_key': ['exact', 'icontains'],
            'hit_count': ['exact', 'gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(cache_key__icontains=value) |
            Q(cache_type__icontains=value)
        )
    
    def filter_expired(self, queryset, name, value):
        """Filter for expired cache entries."""
        if value:
            return queryset.filter(expires_at__lt=timezone.now())
        return queryset.filter(expires_at__gte=timezone.now())
    
    def filter_popular(self, queryset, name, value):
        """Filter for popular cache entries."""
        if value:
            return queryset.filter(hit_count__gte=10)
        return queryset.filter(hit_count__lt=10)
    
    def filter_unused(self, queryset, name, value):
        """Filter for unused cache entries."""
        if value:
            return queryset.filter(hit_count=0)
        return queryset.exclude(hit_count=0)

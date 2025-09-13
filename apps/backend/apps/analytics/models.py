"""
Analytics & Reporting Models

This module contains all the models for the analytics and reporting system,
including reports, KPIs, dashboards, and data visualization components.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from decimal import Decimal
import uuid
import json

User = get_user_model()


class Report(BaseModel):
    """
    Report model for storing and managing various types of reports.
    """
    REPORT_TYPE_CHOICES = [
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('inventory', 'Inventory'),
        ('hr', 'Human Resources'),
        ('sales', 'Sales'),
        ('purchasing', 'Purchasing'),
        ('custom', 'Custom'),
    ]
    
    REPORT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    REPORT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="Report name")
    description = models.TextField(blank=True, help_text="Report description")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=REPORT_STATUS_CHOICES, default='draft')
    
    # Report configuration
    query_parameters = models.JSONField(default=dict, help_text="Report query parameters")
    filters = models.JSONField(default=dict, help_text="Report filters")
    columns = models.JSONField(default=list, help_text="Report columns configuration")
    format = models.CharField(max_length=10, choices=REPORT_FORMAT_CHOICES, default='pdf')
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True, help_text="daily, weekly, monthly, quarterly, yearly")
    schedule_time = models.TimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    
    # Access control
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, blank=True, related_name='accessible_reports')
    
    # Metadata
    file_path = models.CharField(max_length=500, blank=True, help_text="Path to generated report file")
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    execution_time = models.DurationField(null=True, blank=True, help_text="Report execution time")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report"
        verbose_name_plural = "Reports"
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class KPI(BaseModel):
    """
    Key Performance Indicator model for tracking business metrics.
    """
    KPI_TYPE_CHOICES = [
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('inventory', 'Inventory'),
        ('sales', 'Sales'),
        ('purchasing', 'Purchasing'),
        ('custom', 'Custom'),
    ]
    
    KPI_FREQUENCY_CHOICES = [
        ('real_time', 'Real Time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    KPI_TREND_CHOICES = [
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable'),
        ('volatile', 'Volatile'),
    ]
    
    kpi_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="KPI name")
    description = models.TextField(blank=True, help_text="KPI description")
    kpi_type = models.CharField(max_length=20, choices=KPI_TYPE_CHOICES)
    
    # KPI configuration
    calculation_method = models.TextField(help_text="KPI calculation method/formula")
    data_source = models.CharField(max_length=100, help_text="Data source for KPI calculation")
    frequency = models.CharField(max_length=15, choices=KPI_FREQUENCY_CHOICES, default='daily')
    
    # Target values
    target_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    warning_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Current values
    current_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    previous_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    change_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    trend = models.CharField(max_length=15, choices=KPI_TREND_CHOICES, default='stable')
    
    # Status
    is_active = models.BooleanField(default=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    next_calculation = models.DateTimeField(null=True, blank=True)
    
    # Visualization
    chart_type = models.CharField(max_length=20, default='line', help_text="Chart type for visualization")
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color for visualization")
    unit = models.CharField(max_length=20, blank=True, help_text="Unit of measurement")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
    
    def __str__(self):
        return f"{self.name} ({self.get_kpi_type_display()})"


class KPIMeasurement(BaseModel):
    """
    KPI measurement model for storing historical KPI values.
    """
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='measurements')
    value = models.DecimalField(max_digits=15, decimal_places=4)
    measurement_date = models.DateTimeField()
    notes = models.TextField(blank=True, help_text="Additional notes about this measurement")
    
    # Context
    context_data = models.JSONField(default=dict, help_text="Additional context data")
    
    class Meta:
        ordering = ['-measurement_date']
        verbose_name = "KPI Measurement"
        verbose_name_plural = "KPI Measurements"
        unique_together = ['kpi', 'measurement_date']
    
    def __str__(self):
        return f"{self.kpi.name} - {self.value} ({self.measurement_date})"


class Dashboard(BaseModel):
    """
    Dashboard model for organizing and displaying analytics data.
    """
    DASHBOARD_TYPE_CHOICES = [
        ('executive', 'Executive'),
        ('operational', 'Operational'),
        ('departmental', 'Departmental'),
        ('custom', 'Custom'),
    ]
    
    DASHBOARD_LAYOUT_CHOICES = [
        ('grid', 'Grid'),
        ('freeform', 'Freeform'),
        ('tabbed', 'Tabbed'),
    ]
    
    dashboard_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="Dashboard name")
    description = models.TextField(blank=True, help_text="Dashboard description")
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPE_CHOICES, default='custom')
    layout = models.CharField(max_length=15, choices=DASHBOARD_LAYOUT_CHOICES, default='grid')
    
    # Configuration
    configuration = models.JSONField(default=dict, help_text="Dashboard configuration")
    refresh_interval = models.IntegerField(default=300, help_text="Refresh interval in seconds")
    auto_refresh = models.BooleanField(default=True)
    
    # Access control
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, blank=True, related_name='accessible_dashboards')
    
    # Status
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"


class DashboardWidget(BaseModel):
    """
    Dashboard widget model for individual dashboard components.
    """
    WIDGET_TYPE_CHOICES = [
        ('kpi', 'KPI'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('gauge', 'Gauge'),
        ('map', 'Map'),
        ('text', 'Text'),
        ('image', 'Image'),
        ('custom', 'Custom'),
    ]
    
    CHART_TYPE_CHOICES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
        ('heatmap', 'Heatmap'),
        ('funnel', 'Funnel Chart'),
        ('gauge', 'Gauge Chart'),
    ]
    
    widget_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(max_length=200, help_text="Widget name")
    widget_type = models.CharField(max_length=15, choices=WIDGET_TYPE_CHOICES)
    
    # Widget configuration
    configuration = models.JSONField(default=dict, help_text="Widget configuration")
    data_source = models.CharField(max_length=100, blank=True, help_text="Data source for widget")
    query = models.TextField(blank=True, help_text="Data query for widget")
    
    # Visualization
    chart_type = models.CharField(max_length=15, choices=CHART_TYPE_CHOICES, blank=True)
    chart_config = models.JSONField(default=dict, help_text="Chart configuration")
    
    # Layout
    position_x = models.IntegerField(default=0, help_text="X position in grid")
    position_y = models.IntegerField(default=0, help_text="Y position in grid")
    width = models.IntegerField(default=4, help_text="Width in grid units")
    height = models.IntegerField(default=3, help_text="Height in grid units")
    
    # Status
    is_active = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=300, help_text="Refresh interval in seconds")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"


class DataSource(BaseModel):
    """
    Data source model for managing analytics data sources.
    """
    SOURCE_TYPE_CHOICES = [
        ('database', 'Database'),
        ('api', 'API'),
        ('file', 'File'),
        ('external', 'External Service'),
        ('custom', 'Custom'),
    ]
    
    CONNECTION_TYPE_CHOICES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
        ('oracle', 'Oracle'),
        ('mssql', 'Microsoft SQL Server'),
        ('mongodb', 'MongoDB'),
        ('redis', 'Redis'),
        ('rest_api', 'REST API'),
        ('graphql', 'GraphQL'),
        ('csv', 'CSV File'),
        ('excel', 'Excel File'),
        ('json', 'JSON File'),
    ]
    
    source_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="Data source name")
    description = models.TextField(blank=True, help_text="Data source description")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPE_CHOICES)
    
    # Connection details
    connection_string = models.TextField(blank=True, help_text="Connection string or URL")
    credentials = models.JSONField(default=dict, help_text="Connection credentials (encrypted)")
    
    # Configuration
    configuration = models.JSONField(default=dict, help_text="Data source configuration")
    is_active = models.BooleanField(default=True)
    
    # Metadata
    last_connected = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=20, default='unknown', help_text="Connection status")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Data Source"
        verbose_name_plural = "Data Sources"
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class ReportTemplate(BaseModel):
    """
    Report template model for reusable report configurations.
    """
    TEMPLATE_TYPE_CHOICES = [
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('inventory', 'Inventory'),
        ('hr', 'Human Resources'),
        ('sales', 'Sales'),
        ('purchasing', 'Purchasing'),
        ('custom', 'Custom'),
    ]
    
    template_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="Template name")
    description = models.TextField(blank=True, help_text="Template description")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template configuration
    template_config = models.JSONField(default=dict, help_text="Template configuration")
    default_parameters = models.JSONField(default=dict, help_text="Default parameters")
    required_parameters = models.JSONField(default=list, help_text="Required parameters")
    
    # Usage
    usage_count = models.IntegerField(default=0, help_text="Number of times template has been used")
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class AnalyticsEvent(BaseModel):
    """
    Analytics event model for tracking user interactions and system events.
    """
    EVENT_TYPE_CHOICES = [
        ('user_action', 'User Action'),
        ('system_event', 'System Event'),
        ('data_change', 'Data Change'),
        ('report_generated', 'Report Generated'),
        ('dashboard_viewed', 'Dashboard Viewed'),
        ('kpi_updated', 'KPI Updated'),
        ('error', 'Error'),
        ('custom', 'Custom'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=200, help_text="Event name")
    description = models.TextField(blank=True, help_text="Event description")
    
    # Event data
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    session_id = models.CharField(max_length=100, blank=True, help_text="User session ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Event context
    context_data = models.JSONField(default=dict, help_text="Event context data")
    metadata = models.JSONField(default=dict, help_text="Additional event metadata")
    
    # Timing
    event_timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True, help_text="Event duration")
    
    class Meta:
        ordering = ['-event_timestamp']
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        indexes = [
            models.Index(fields=['event_type', 'event_timestamp']),
            models.Index(fields=['user', 'event_timestamp']),
            models.Index(fields=['event_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_name} ({self.get_event_type_display()}) - {self.event_timestamp}"


class Alert(BaseModel):
    """
    Alert model for system notifications and threshold monitoring.
    """
    ALERT_TYPE_CHOICES = [
        ('kpi_threshold', 'KPI Threshold'),
        ('data_anomaly', 'Data Anomaly'),
        ('system_error', 'System Error'),
        ('scheduled_report', 'Scheduled Report'),
        ('custom', 'Custom'),
    ]
    
    ALERT_SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    alert_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=ALERT_SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=ALERT_STATUS_CHOICES, default='active')
    
    # Alert details
    title = models.CharField(max_length=200, help_text="Alert title")
    message = models.TextField(help_text="Alert message")
    description = models.TextField(blank=True, help_text="Detailed alert description")
    
    # Related objects
    related_kpi = models.ForeignKey(KPI, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    related_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    related_dashboard = models.ForeignKey(Dashboard, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    
    # Alert data
    alert_data = models.JSONField(default=dict, help_text="Alert-specific data")
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Notification
    is_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type', 'triggered_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) - {self.triggered_at}"


class AnalyticsCache(BaseModel):
    """
    Analytics cache model for storing pre-calculated analytics data.
    """
    CACHE_TYPE_CHOICES = [
        ('kpi', 'KPI'),
        ('report', 'Report'),
        ('dashboard', 'Dashboard'),
        ('query', 'Query'),
        ('aggregation', 'Aggregation'),
    ]
    
    cache_key = models.CharField(max_length=500, unique=True, help_text="Cache key")
    cache_type = models.CharField(max_length=20, choices=CACHE_TYPE_CHOICES)
    
    # Cache data
    data = models.JSONField(help_text="Cached data")
    metadata = models.JSONField(default=dict, help_text="Cache metadata")
    
    # Cache management
    expires_at = models.DateTimeField(help_text="Cache expiration time")
    hit_count = models.IntegerField(default=0, help_text="Number of cache hits")
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Related objects
    related_kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, null=True, blank=True, related_name='cache_entries')
    related_report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True, related_name='cache_entries')
    related_dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, null=True, blank=True, related_name='cache_entries')
    
    class Meta:
        ordering = ['-last_accessed']
        verbose_name = "Analytics Cache"
        verbose_name_plural = "Analytics Cache"
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['cache_type']),
        ]
    
    def __str__(self):
        return f"{self.cache_key} ({self.get_cache_type_display()})"

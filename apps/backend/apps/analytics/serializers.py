"""
Analytics & Reporting Serializers

This module contains all the serializers for the analytics and reporting system,
providing API communication for reports, KPIs, dashboards, and analytics components.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)
from decimal import Decimal
import json

User = get_user_model()


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for reports."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    allowed_users_count = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'report_id', 'organization', 'name', 'description', 'report_type',
            'report_type_display', 'status', 'status_display', 'query_parameters',
            'filters', 'columns', 'format', 'format_display', 'is_scheduled',
            'schedule_frequency', 'schedule_time', 'next_run', 'last_run',
            'created_by', 'created_by_name', 'is_public', 'allowed_users_count',
            'file_path', 'file_size', 'file_size_display', 'execution_time',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'report_id', 'created', 'modified']
    
    def get_allowed_users_count(self, obj):
        return obj.allowed_users.count()
    
    def get_file_size_display(self, obj):
        if obj.file_size:
            # Convert bytes to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.1f} TB"
        return None


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reports."""
    allowed_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    
    class Meta:
        model = Report
        fields = [
            'organization', 'name', 'description', 'report_type', 'query_parameters',
            'filters', 'columns', 'format', 'is_scheduled', 'schedule_frequency',
            'schedule_time', 'is_public', 'allowed_users'
        ]
    
    def create(self, validated_data):
        allowed_users = validated_data.pop('allowed_users', [])
        report = Report.objects.create(**validated_data)
        report.allowed_users.set(allowed_users)
        return report


class KPISerializer(serializers.ModelSerializer):
    """Serializer for KPIs."""
    kpi_type_display = serializers.CharField(source='get_kpi_type_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    trend_display = serializers.CharField(source='get_trend_display', read_only=True)
    change_percentage_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = [
            'id', 'kpi_id', 'organization', 'name', 'description', 'kpi_type',
            'kpi_type_display', 'calculation_method', 'data_source', 'frequency',
            'frequency_display', 'target_value', 'warning_threshold', 'critical_threshold',
            'current_value', 'previous_value', 'change_percentage', 'change_percentage_display',
            'trend', 'trend_display', 'is_active', 'last_calculated', 'next_calculation',
            'chart_type', 'color', 'unit', 'status_display',             'created', 'modified'
        ]
        read_only_fields = ['id', 'kpi_id', 'created', 'modified']
    
    def get_change_percentage_display(self, obj):
        if obj.change_percentage is not None:
            return f"{obj.change_percentage:+.2f}%"
        return None
    
    def get_status_display(self, obj):
        if obj.current_value is None:
            return "No Data"
        elif obj.critical_threshold and obj.current_value <= obj.critical_threshold:
            return "Critical"
        elif obj.warning_threshold and obj.current_value <= obj.warning_threshold:
            return "Warning"
        elif obj.target_value and obj.current_value >= obj.target_value:
            return "Target Met"
        else:
            return "Normal"


class KPICreateSerializer(serializers.ModelSerializer):
    """Serializer for creating KPIs."""
    
    class Meta:
        model = KPI
        fields = [
            'organization', 'name', 'description', 'kpi_type', 'calculation_method',
            'data_source', 'frequency', 'target_value', 'warning_threshold',
            'critical_threshold', 'chart_type', 'color', 'unit'
        ]


class KPIMeasurementSerializer(serializers.ModelSerializer):
    """Serializer for KPI measurements."""
    kpi_name = serializers.CharField(source='kpi.name', read_only=True)
    
    class Meta:
        model = KPIMeasurement
        fields = [
            'id', 'kpi', 'kpi_name', 'value', 'measurement_date', 'notes',
            'context_data', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for dashboards."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    dashboard_type_display = serializers.CharField(source='get_dashboard_type_display', read_only=True)
    layout_display = serializers.CharField(source='get_layout_display', read_only=True)
    allowed_users_count = serializers.SerializerMethodField()
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'dashboard_id', 'organization', 'name', 'description', 'dashboard_type',
            'dashboard_type_display', 'layout', 'layout_display', 'configuration',
            'refresh_interval', 'auto_refresh', 'created_by', 'created_by_name',
            'is_public', 'allowed_users_count', 'is_active', 'last_updated',
            'widgets_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'dashboard_id', 'created', 'modified']
    
    def get_allowed_users_count(self, obj):
        return obj.allowed_users.count()
    
    def get_widgets_count(self, obj):
        return obj.widgets.count()


class DashboardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating dashboards."""
    allowed_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    
    class Meta:
        model = Dashboard
        fields = [
            'organization', 'name', 'description', 'dashboard_type', 'layout',
            'configuration', 'refresh_interval', 'auto_refresh', 'is_public',
            'allowed_users'
        ]
    
    def create(self, validated_data):
        allowed_users = validated_data.pop('allowed_users', [])
        dashboard = Dashboard.objects.create(**validated_data)
        dashboard.allowed_users.set(allowed_users)
        return dashboard


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets."""
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    chart_type_display = serializers.CharField(source='get_chart_type_display', read_only=True)
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'widget_id', 'dashboard', 'dashboard_name', 'name', 'widget_type',
            'widget_type_display', 'configuration', 'data_source', 'query',
            'chart_type', 'chart_type_display', 'chart_config', 'position_x',
            'position_y', 'width', 'height', 'is_active', 'refresh_interval',
            'last_updated', 'created', 'modified'
        ]
        read_only_fields = ['id', 'widget_id', 'created', 'modified']


class DashboardWidgetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating dashboard widgets."""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'dashboard', 'name', 'widget_type', 'configuration', 'data_source',
            'query', 'chart_type', 'chart_config', 'position_x', 'position_y',
            'width', 'height', 'refresh_interval'
        ]


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for data sources."""
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    connection_type_display = serializers.CharField(source='get_connection_type_display', read_only=True)
    connection_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'source_id', 'organization', 'name', 'description', 'source_type',
            'source_type_display', 'connection_type', 'connection_type_display',
            'connection_string', 'configuration', 'is_active', 'last_connected',
            'connection_status', 'connection_status_display', 'created', 'modified'
        ]
        read_only_fields = ['id', 'source_id', 'created', 'modified']
        extra_kwargs = {
            'credentials': {'write_only': True}
        }
    
    def get_connection_status_display(self, obj):
        status_map = {
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'error': 'Error',
            'unknown': 'Unknown'
        }
        return status_map.get(obj.connection_status, 'Unknown')


class DataSourceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating data sources."""
    
    class Meta:
        model = DataSource
        fields = [
            'organization', 'name', 'description', 'source_type', 'connection_type',
            'connection_string', 'credentials', 'configuration'
        ]


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for report templates."""
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'template_id', 'organization', 'name', 'description', 'template_type',
            'template_type_display', 'template_config', 'default_parameters',
            'required_parameters', 'usage_count', 'is_public', 'created_by',
            'created_by_name', 'created', 'modified'
        ]
        read_only_fields = ['id', 'template_id', 'created', 'modified']


class ReportTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating report templates."""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'organization', 'name', 'description', 'template_type', 'template_config',
            'default_parameters', 'required_parameters', 'is_public'
        ]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'event_id', 'organization', 'event_type', 'event_type_display',
            'event_name', 'description', 'user', 'user_name', 'session_id',
            'ip_address', 'user_agent', 'context_data', 'metadata',
            'event_timestamp', 'duration', 'duration_display', 'created', 'modified'
        ]
        read_only_fields = ['id', 'event_id', 'created', 'modified']
    
    def get_duration_display(self, obj):
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.2f}s"
            elif total_seconds < 3600:
                return f"{total_seconds/60:.2f}m"
            else:
                return f"{total_seconds/3600:.2f}h"
        return None


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alerts."""
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    related_kpi_name = serializers.CharField(source='related_kpi.name', read_only=True)
    related_report_name = serializers.CharField(source='related_report.name', read_only=True)
    related_dashboard_name = serializers.CharField(source='related_dashboard.name', read_only=True)
    age_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'organization', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'status', 'status_display', 'title',
            'message', 'description', 'related_kpi', 'related_kpi_name',
            'related_report', 'related_report_name', 'related_dashboard',
            'related_dashboard_name', 'alert_data', 'threshold_value',
            'current_value', 'is_notified', 'notification_sent_at',
            'acknowledged_by', 'acknowledged_by_name', 'acknowledged_at',
            'triggered_at', 'resolved_at', 'age_display', 'created', 'modified'
        ]
        read_only_fields = ['id', 'alert_id', 'created', 'modified']
    
    def get_age_display(self, obj):
        from django.utils import timezone
        now = timezone.now()
        age = now - obj.triggered_at
        
        if age.days > 0:
            return f"{age.days}d {age.seconds//3600}h"
        elif age.seconds > 3600:
            return f"{age.seconds//3600}h {(age.seconds%3600)//60}m"
        else:
            return f"{age.seconds//60}m {age.seconds%60}s"


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating alerts."""
    
    class Meta:
        model = Alert
        fields = [
            'organization', 'alert_type', 'severity', 'title', 'message',
            'description', 'related_kpi', 'related_report', 'related_dashboard',
            'alert_data', 'threshold_value', 'current_value'
        ]


class AnalyticsCacheSerializer(serializers.ModelSerializer):
    """Serializer for analytics cache."""
    cache_type_display = serializers.CharField(source='get_cache_type_display', read_only=True)
    related_kpi_name = serializers.CharField(source='related_kpi.name', read_only=True)
    related_report_name = serializers.CharField(source='related_report.name', read_only=True)
    related_dashboard_name = serializers.CharField(source='related_dashboard.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsCache
        fields = [
            'id', 'cache_key', 'organization', 'cache_type', 'cache_type_display',
            'data', 'metadata', 'expires_at', 'hit_count', 'last_accessed',
            'related_kpi', 'related_kpi_name', 'related_report', 'related_report_name',
            'related_dashboard', 'related_dashboard_name', 'is_expired',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return timezone.now() > obj.expires_at


class KPISummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for KPI summaries."""
    kpi_type_display = serializers.CharField(source='get_kpi_type_display', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = [
            'id', 'kpi_id', 'name', 'kpi_type', 'kpi_type_display', 'current_value',
            'target_value', 'change_percentage', 'trend', 'status_display',
            'last_calculated', 'unit'
        ]
    
    def get_status_display(self, obj):
        if obj.current_value is None:
            return "No Data"
        elif obj.critical_threshold and obj.current_value <= obj.critical_threshold:
            return "Critical"
        elif obj.warning_threshold and obj.current_value <= obj.warning_threshold:
            return "Warning"
        elif obj.target_value and obj.current_value >= obj.target_value:
            return "Target Met"
        else:
            return "Normal"


class DashboardSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for dashboard summaries."""
    dashboard_type_display = serializers.CharField(source='get_dashboard_type_display', read_only=True)
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'dashboard_id', 'name', 'dashboard_type', 'dashboard_type_display',
            'is_active', 'last_updated', 'widgets_count'
        ]
    
    def get_widgets_count(self, obj):
        return obj.widgets.count()


class ReportSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for report summaries."""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'report_id', 'name', 'report_type', 'report_type_display',
            'status', 'status_display', 'format', 'is_scheduled', 'last_run',
            'created_by_name', 'created'
        ]


class AlertSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for alert summaries."""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'alert_type', 'severity', 'severity_display',
            'status', 'status_display', 'title', 'triggered_at', 'age_display'
        ]
    
    def get_age_display(self, obj):
        from django.utils import timezone
        now = timezone.now()
        age = now - obj.triggered_at
        
        if age.days > 0:
            return f"{age.days}d"
        elif age.seconds > 3600:
            return f"{age.seconds//3600}h"
        else:
            return f"{age.seconds//60}m"


class KPIMeasurementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating KPI measurements."""
    
    class Meta:
        model = KPIMeasurement
        fields = [
            'kpi', 'value', 'measurement_date', 'notes', 'context_data'
        ]


class ReportExecutionSerializer(serializers.Serializer):
    """Serializer for report execution requests."""
    parameters = serializers.JSONField(default=dict, help_text="Report parameters")
    format = serializers.ChoiceField(choices=Report.REPORT_FORMAT_CHOICES, default='pdf')
    email_notification = serializers.BooleanField(default=False)
    email_recipients = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        help_text="Email recipients for notification"
    )


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data requests."""
    widget_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific widget IDs to fetch data for"
    )
    refresh_cache = serializers.BooleanField(default=False)


class AnalyticsQuerySerializer(serializers.Serializer):
    """Serializer for analytics query requests."""
    query = serializers.CharField(help_text="Analytics query")
    parameters = serializers.JSONField(default=dict, help_text="Query parameters")
    data_source = serializers.CharField(help_text="Data source identifier")
    cache_duration = serializers.IntegerField(default=300, help_text="Cache duration in seconds")

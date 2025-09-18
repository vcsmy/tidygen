"""
Analytics & Reporting Admin Configuration

This module configures the Django admin interface for the analytics and reporting system,
providing administrative access to reports, KPIs, dashboards, and analytics components.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)


class KPIMeasurementInline(admin.TabularInline):
    """Inline admin for KPI measurements."""
    model = KPIMeasurement
    extra = 0
    fields = ['value', 'measurement_date', 'notes']
    readonly_fields = ['created']


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    """Admin for KPIs."""
    list_display = [
        'name', 'kpi_type_badge', 'current_value_display', 'target_value_display',
        'change_percentage_display', 'trend_badge', 'status_badge', 'last_calculated'
    ]
    list_filter = [
        'kpi_type', 'frequency', 'trend', 'is_active', 'last_calculated'
    ]
    search_fields = [
        'name', 'description', 'data_source', 'calculation_method'
    ]
    readonly_fields = [
        'kpi_id', 'last_calculated', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('kpi_id', 'name', 'description', 'kpi_type')
        }),
        ('Configuration', {
            'fields': ('calculation_method', 'data_source', 'frequency')
        }),
        ('Targets & Thresholds', {
            'fields': ('target_value', 'warning_threshold', 'critical_threshold')
        }),
        ('Current Values', {
            'fields': ('current_value', 'previous_value', 'change_percentage', 'trend')
        }),
        ('Visualization', {
            'fields': ('chart_type', 'color', 'unit')
        }),
        ('Status', {
            'fields': ('is_active', 'last_calculated', 'next_calculation')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    inlines = [KPIMeasurementInline]
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def kpi_type_badge(self, obj):
        """Display KPI type as a colored badge."""
        colors = {
            'financial': 'green',
            'operational': 'blue',
            'customer': 'purple',
            'employee': 'orange',
            'inventory': 'brown',
            'sales': 'red',
            'purchasing': 'teal',
            'custom': 'gray'
        }
        color = colors.get(obj.kpi_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_kpi_type_display()
        )
    kpi_type_badge.short_description = 'Type'
    
    def current_value_display(self, obj):
        """Display current value with unit."""
        if obj.current_value is not None:
            return f"{obj.current_value} {obj.unit or ''}"
        return "No Data"
    current_value_display.short_description = 'Current Value'
    
    def target_value_display(self, obj):
        """Display target value with unit."""
        if obj.target_value is not None:
            return f"{obj.target_value} {obj.unit or ''}"
        return "No Target"
    target_value_display.short_description = 'Target'
    
    def change_percentage_display(self, obj):
        """Display change percentage with color."""
        if obj.change_percentage is not None:
            color = 'green' if obj.change_percentage >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, obj.change_percentage
            )
        return "-"
    change_percentage_display.short_description = 'Change %'
    
    def trend_badge(self, obj):
        """Display trend as a badge."""
        colors = {
            'increasing': 'green',
            'decreasing': 'red',
            'stable': 'blue',
            'volatile': 'orange'
        }
        color = colors.get(obj.trend, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_trend_display()
        )
    trend_badge.short_description = 'Trend'
    
    def status_badge(self, obj):
        """Display status as a badge."""
        if obj.current_value is None:
            return format_html('<span style="background-color: gray; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">No Data</span>')
        elif obj.critical_threshold and obj.current_value <= obj.critical_threshold:
            return format_html('<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Critical</span>')
        elif obj.warning_threshold and obj.current_value <= obj.warning_threshold:
            return format_html('<span style="background-color: orange; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Warning</span>')
        elif obj.target_value and obj.current_value >= obj.target_value:
            return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Target Met</span>')
        else:
            return format_html('<span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Normal</span>')
    status_badge.short_description = 'Status'


@admin.register(KPIMeasurement)
class KPIMeasurementAdmin(admin.ModelAdmin):
    """Admin for KPI measurements."""
    list_display = [
        'kpi_link', 'value_display', 'measurement_date', 'notes_preview'
    ]
    list_filter = [
        'measurement_date', 'kpi__kpi_type'
    ]
    search_fields = [
        'kpi__name', 'notes'
    ]
    readonly_fields = ['created', 'modified']
    date_hierarchy = 'measurement_date'
    ordering = ['-measurement_date']
    
    def kpi_link(self, obj):
        """Create a link to the KPI."""
        url = reverse('admin:analytics_kpi_change', args=[obj.kpi.id])
        return format_html('<a href="{}">{}</a>', url, obj.kpi.name)
    kpi_link.short_description = 'KPI'
    
    def value_display(self, obj):
        """Display value with unit."""
        return f"{obj.value} {obj.kpi.unit or ''}"
    value_display.short_description = 'Value'
    
    def notes_preview(self, obj):
        """Display notes preview."""
        if obj.notes:
            return obj.notes[:50] + "..." if len(obj.notes) > 50 else obj.notes
        return "-"
    notes_preview.short_description = 'Notes'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin for reports."""
    list_display = [
        'name', 'report_type_badge', 'status_badge', 'format_badge',
        'created_by_link', 'is_scheduled_badge', 'last_run', 'file_size_display'
    ]
    list_filter = [
        'report_type', 'status', 'format', 'is_scheduled', 'is_public',
        'created', 'last_run'
    ]
    search_fields = [
        'name', 'description', 'created_by__username', 'created_by__email'
    ]
    readonly_fields = [
        'report_id', 'created', 'modified', 'execution_time'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('report_id', 'name', 'description', 'report_type')
        }),
        ('Status & Format', {
            'fields': ('status', 'format')
        }),
        ('Configuration', {
            'fields': ('query_parameters', 'filters', 'columns'),
            'classes': ('collapse',)
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'schedule_frequency', 'schedule_time', 'next_run', 'last_run')
        }),
        ('Access Control', {
            'fields': ('created_by', 'is_public', 'allowed_users')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'execution_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def report_type_badge(self, obj):
        """Display report type as a badge."""
        colors = {
            'financial': 'green',
            'operational': 'blue',
            'inventory': 'brown',
            'hr': 'purple',
            'sales': 'red',
            'purchasing': 'teal',
            'custom': 'gray'
        }
        color = colors.get(obj.report_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_report_type_display()
        )
    report_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        """Display status as a badge."""
        colors = {
            'draft': 'gray',
            'scheduled': 'blue',
            'running': 'orange',
            'completed': 'green',
            'failed': 'red',
            'archived': 'black'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def format_badge(self, obj):
        """Display format as a badge."""
        colors = {
            'pdf': 'red',
            'excel': 'green',
            'csv': 'blue',
            'json': 'purple',
            'html': 'orange'
        }
        color = colors.get(obj.format, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_format_display()
        )
    format_badge.short_description = 'Format'
    
    def created_by_link(self, obj):
        """Create a link to the user who created the report."""
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.get_full_name())
        return '-'
    created_by_link.short_description = 'Created By'
    
    def is_scheduled_badge(self, obj):
        """Display scheduled status as a badge."""
        if obj.is_scheduled:
            return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Scheduled</span>')
        return format_html('<span style="background-color: gray; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Manual</span>')
    is_scheduled_badge.short_description = 'Scheduled'
    
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        if obj.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.1f} TB"
        return "-"
    file_size_display.short_description = 'File Size'


class DashboardWidgetInline(admin.TabularInline):
    """Inline admin for dashboard widgets."""
    model = DashboardWidget
    extra = 0
    fields = ['name', 'widget_type', 'chart_type', 'position_x', 'position_y', 'width', 'height', 'is_active']
    readonly_fields = ['widget_id']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """Admin for dashboards."""
    list_display = [
        'name', 'dashboard_type_badge', 'layout_badge', 'created_by_link',
        'is_active_badge', 'is_public_badge', 'widgets_count', 'last_updated'
    ]
    list_filter = [
        'dashboard_type', 'layout', 'is_active', 'is_public', 'auto_refresh',
        'created', 'last_updated'
    ]
    search_fields = [
        'name', 'description', 'created_by__username', 'created_by__email'
    ]
    readonly_fields = [
        'dashboard_id', 'last_updated', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('dashboard_id', 'name', 'description', 'dashboard_type')
        }),
        ('Layout & Configuration', {
            'fields': ('layout', 'configuration', 'refresh_interval', 'auto_refresh')
        }),
        ('Access Control', {
            'fields': ('created_by', 'is_public', 'allowed_users')
        }),
        ('Status', {
            'fields': ('is_active', 'last_updated')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    inlines = [DashboardWidgetInline]
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def dashboard_type_badge(self, obj):
        """Display dashboard type as a badge."""
        colors = {
            'executive': 'purple',
            'operational': 'blue',
            'departmental': 'green',
            'custom': 'gray'
        }
        color = colors.get(obj.dashboard_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_dashboard_type_display()
        )
    dashboard_type_badge.short_description = 'Type'
    
    def layout_badge(self, obj):
        """Display layout as a badge."""
        colors = {
            'grid': 'blue',
            'freeform': 'green',
            'tabbed': 'purple'
        }
        color = colors.get(obj.layout, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_layout_display()
        )
    layout_badge.short_description = 'Layout'
    
    def created_by_link(self, obj):
        """Create a link to the user who created the dashboard."""
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.get_full_name())
        return '-'
    created_by_link.short_description = 'Created By'
    
    def is_active_badge(self, obj):
        """Display active status as a badge."""
        if obj.is_active:
            return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>')
        return format_html('<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>')
    is_active_badge.short_description = 'Active'
    
    def is_public_badge(self, obj):
        """Display public status as a badge."""
        if obj.is_public:
            return format_html('<span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Public</span>')
        return format_html('<span style="background-color: gray; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Private</span>')
    is_public_badge.short_description = 'Public'
    
    def widgets_count(self, obj):
        """Display number of widgets."""
        return obj.widgets.count()
    widgets_count.short_description = 'Widgets'


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Admin for dashboard widgets."""
    list_display = [
        'name', 'dashboard_link', 'widget_type_badge', 'chart_type_badge',
        'position_display', 'size_display', 'is_active_badge'
    ]
    list_filter = [
        'widget_type', 'chart_type', 'is_active', 'dashboard__dashboard_type'
    ]
    search_fields = [
        'name', 'data_source', 'dashboard__name'
    ]
    readonly_fields = ['widget_id', 'last_updated', 'created', 'modified']
    date_hierarchy = 'created'
    ordering = ['dashboard', 'position_y', 'position_x']
    
    def dashboard_link(self, obj):
        """Create a link to the dashboard."""
        url = reverse('admin:analytics_dashboard_change', args=[obj.dashboard.id])
        return format_html('<a href="{}">{}</a>', url, obj.dashboard.name)
    dashboard_link.short_description = 'Dashboard'
    
    def widget_type_badge(self, obj):
        """Display widget type as a badge."""
        colors = {
            'kpi': 'green',
            'chart': 'blue',
            'table': 'purple',
            'gauge': 'orange',
            'map': 'red',
            'text': 'gray',
            'image': 'brown',
            'custom': 'black'
        }
        color = colors.get(obj.widget_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_widget_type_display()
        )
    widget_type_badge.short_description = 'Type'
    
    def chart_type_badge(self, obj):
        """Display chart type as a badge."""
        if obj.chart_type:
            colors = {
                'line': 'blue',
                'bar': 'green',
                'pie': 'red',
                'area': 'purple',
                'scatter': 'orange',
                'heatmap': 'brown',
                'funnel': 'teal',
                'gauge': 'pink'
            }
            color = colors.get(obj.chart_type, 'gray')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                color, obj.get_chart_type_display()
            )
        return "-"
    chart_type_badge.short_description = 'Chart Type'
    
    def position_display(self, obj):
        """Display position."""
        return f"({obj.position_x}, {obj.position_y})"
    position_display.short_description = 'Position'
    
    def size_display(self, obj):
        """Display size."""
        return f"{obj.width}×{obj.height}"
    size_display.short_description = 'Size'
    
    def is_active_badge(self, obj):
        """Display active status as a badge."""
        if obj.is_active:
            return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>')
        return format_html('<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>')
    is_active_badge.short_description = 'Active'


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """Admin for data sources."""
    list_display = [
        'name', 'source_type_badge', 'connection_type_badge', 'connection_status_badge',
        'is_active_badge', 'last_connected'
    ]
    list_filter = [
        'source_type', 'connection_type', 'connection_status', 'is_active',
        'created', 'last_connected'
    ]
    search_fields = [
        'name', 'description', 'connection_string'
    ]
    readonly_fields = [
        'source_id', 'last_connected', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_id', 'name', 'description')
        }),
        ('Connection Details', {
            'fields': ('source_type', 'connection_type', 'connection_string', 'credentials')
        }),
        ('Configuration', {
            'fields': ('configuration', 'is_active')
        }),
        ('Status', {
            'fields': ('connection_status', 'last_connected')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def source_type_badge(self, obj):
        """Display source type as a badge."""
        colors = {
            'database': 'blue',
            'api': 'green',
            'file': 'orange',
            'external': 'purple',
            'custom': 'gray'
        }
        color = colors.get(obj.source_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_source_type_display()
        )
    source_type_badge.short_description = 'Source Type'
    
    def connection_type_badge(self, obj):
        """Display connection type as a badge."""
        colors = {
            'postgresql': 'blue',
            'mysql': 'orange',
            'sqlite': 'green',
            'oracle': 'red',
            'mssql': 'purple',
            'mongodb': 'green',
            'redis': 'red',
            'rest_api': 'blue',
            'graphql': 'purple',
            'csv': 'gray',
            'excel': 'green',
            'json': 'orange'
        }
        color = colors.get(obj.connection_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_connection_type_display()
        )
    connection_type_badge.short_description = 'Connection Type'
    
    def connection_status_badge(self, obj):
        """Display connection status as a badge."""
        colors = {
            'connected': 'green',
            'disconnected': 'red',
            'error': 'red',
            'unknown': 'gray'
        }
        color = colors.get(obj.connection_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.connection_status.title()
        )
    connection_status_badge.short_description = 'Status'
    
    def is_active_badge(self, obj):
        """Display active status as a badge."""
        if obj.is_active:
            return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>')
        return format_html('<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>')
    is_active_badge.short_description = 'Active'


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin for report templates."""
    list_display = [
        'name', 'template_type_badge', 'created_by_link', 'usage_count',
        'is_public_badge', 'created'
    ]
    list_filter = [
        'template_type', 'is_public', 'created'
    ]
    search_fields = [
        'name', 'description', 'created_by__username', 'created_by__email'
    ]
    readonly_fields = [
        'template_id', 'usage_count', 'created', 'modified'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('template_id', 'name', 'description', 'template_type')
        }),
        ('Configuration', {
            'fields': ('template_config', 'default_parameters', 'required_parameters'),
            'classes': ('collapse',)
        }),
        ('Usage', {
            'fields': ('usage_count', 'is_public', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def template_type_badge(self, obj):
        """Display template type as a badge."""
        colors = {
            'financial': 'green',
            'operational': 'blue',
            'inventory': 'brown',
            'hr': 'purple',
            'sales': 'red',
            'purchasing': 'teal',
            'custom': 'gray'
        }
        color = colors.get(obj.template_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_template_type_display()
        )
    template_type_badge.short_description = 'Type'
    
    def created_by_link(self, obj):
        """Create a link to the user who created the template."""
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.get_full_name())
        return '-'
    created_by_link.short_description = 'Created By'
    
    def is_public_badge(self, obj):
        """Display public status as a badge."""
        if obj.is_public:
            return format_html('<span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Public</span>')
        return format_html('<span style="background-color: gray; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Private</span>')
    is_public_badge.short_description = 'Public'


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Admin for analytics events."""
    list_display = [
        'event_name', 'event_type_badge', 'user_link', 'event_timestamp',
        'duration_display', 'ip_address'
    ]
    list_filter = [
        'event_type', 'event_timestamp', 'user'
    ]
    search_fields = [
        'event_name', 'description', 'user__username', 'user__email',
        'session_id', 'ip_address'
    ]
    readonly_fields = [
        'event_id', 'event_timestamp', 'created', 'modified'
    ]
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'event_name', 'description')
        }),
        ('User Information', {
            'fields': ('user', 'session_id', 'ip_address', 'user_agent')
        }),
        ('Event Data', {
            'fields': ('context_data', 'metadata', 'duration'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('event_timestamp',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'event_timestamp'
    ordering = ['-event_timestamp']
    
    def event_type_badge(self, obj):
        """Display event type as a badge."""
        colors = {
            'user_action': 'blue',
            'system_event': 'green',
            'data_change': 'orange',
            'report_generated': 'purple',
            'dashboard_viewed': 'teal',
            'kpi_updated': 'brown',
            'error': 'red',
            'custom': 'gray'
        }
        color = colors.get(obj.event_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Type'
    
    def user_link(self, obj):
        """Create a link to the user."""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
        return "-"
    user_link.short_description = 'User'
    
    def duration_display(self, obj):
        """Display duration in human readable format."""
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.2f}s"
            elif total_seconds < 3600:
                return f"{total_seconds/60:.2f}m"
            else:
                return f"{total_seconds/3600:.2f}h"
        return "-"
    duration_display.short_description = 'Duration'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin for alerts."""
    list_display = [
        'title', 'alert_type_badge', 'severity_badge', 'status_badge',
        'acknowledged_by_link', 'triggered_at', 'age_display'
    ]
    list_filter = [
        'alert_type', 'severity', 'status', 'triggered_at', 'acknowledged_at',
        'resolved_at'
    ]
    search_fields = [
        'title', 'message', 'description', 'acknowledged_by__username',
        'acknowledged_by__email'
    ]
    readonly_fields = [
        'alert_id', 'triggered_at', 'created', 'modified'
    ]
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_id', 'alert_type', 'severity', 'status')
        }),
        ('Alert Details', {
            'fields': ('title', 'message', 'description')
        }),
        ('Related Objects', {
            'fields': ('related_kpi', 'related_report', 'related_dashboard')
        }),
        ('Alert Data', {
            'fields': ('alert_data', 'threshold_value', 'current_value'),
            'classes': ('collapse',)
        }),
        ('Notification', {
            'fields': ('is_notified', 'notification_sent_at', 'acknowledged_by', 'acknowledged_at')
        }),
        ('Timing', {
            'fields': ('triggered_at', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'triggered_at'
    ordering = ['-triggered_at']
    
    def alert_type_badge(self, obj):
        """Display alert type as a badge."""
        colors = {
            'kpi_threshold': 'red',
            'data_anomaly': 'orange',
            'system_error': 'red',
            'scheduled_report': 'blue',
            'custom': 'gray'
        }
        color = colors.get(obj.alert_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_alert_type_display()
        )
    alert_type_badge.short_description = 'Type'
    
    def severity_badge(self, obj):
        """Display severity as a badge."""
        colors = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as a badge."""
        colors = {
            'active': 'red',
            'acknowledged': 'orange',
            'resolved': 'green',
            'dismissed': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def acknowledged_by_link(self, obj):
        """Create a link to the user who acknowledged the alert."""
        if obj.acknowledged_by:
            url = reverse('admin:accounts_user_change', args=[obj.acknowledged_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.acknowledged_by.get_full_name())
        return "-"
    acknowledged_by_link.short_description = 'Acknowledged By'
    
    def age_display(self, obj):
        """Display alert age."""
        from django.utils import timezone
        now = timezone.now()
        age = now - obj.triggered_at
        
        if age.days > 0:
            return f"{age.days}d {age.seconds//3600}h"
        elif age.seconds > 3600:
            return f"{age.seconds//3600}h {(age.seconds%3600)//60}m"
        else:
            return f"{age.seconds//60}m {age.seconds%60}s"
    age_display.short_description = 'Age'


@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    """Admin for analytics cache."""
    list_display = [
        'cache_key_short', 'cache_type_badge', 'hit_count', 'expires_at',
        'is_expired_badge', 'last_accessed'
    ]
    list_filter = [
        'cache_type', 'expires_at', 'last_accessed'
    ]
    search_fields = [
        'cache_key', 'related_kpi__name', 'related_report__name', 'related_dashboard__name'
    ]
    readonly_fields = [
        'created', 'modified'
    ]
    fieldsets = (
        ('Cache Information', {
            'fields': ('cache_key', 'cache_type')
        }),
        ('Cache Data', {
            'fields': ('data', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Cache Management', {
            'fields': ('expires_at', 'hit_count', 'last_accessed')
        }),
        ('Related Objects', {
            'fields': ('related_kpi', 'related_report', 'related_dashboard')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'last_accessed'
    ordering = ['-last_accessed']
    
    def cache_key_short(self, obj):
        """Display shortened cache key."""
        if len(obj.cache_key) > 50:
            return obj.cache_key[:50] + "..."
        return obj.cache_key
    cache_key_short.short_description = 'Cache Key'
    
    def cache_type_badge(self, obj):
        """Display cache type as a badge."""
        colors = {
            'kpi': 'green',
            'report': 'blue',
            'dashboard': 'purple',
            'query': 'orange',
            'aggregation': 'brown'
        }
        color = colors.get(obj.cache_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_cache_type_display()
        )
    cache_type_badge.short_description = 'Type'
    
    def is_expired_badge(self, obj):
        """Display expired status as a badge."""
        from django.utils import timezone
        if timezone.now() > obj.expires_at:
            return format_html('<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Expired</span>')
        return format_html('<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Valid</span>')
    is_expired_badge.short_description = 'Status'

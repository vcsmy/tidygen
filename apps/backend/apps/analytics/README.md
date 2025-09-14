# Analytics & Reporting Module

## Overview

The Analytics & Reporting module provides comprehensive business intelligence and data analytics capabilities for the TidyGen ERP system. It enables organizations to create, manage, and analyze business data through reports, KPIs, dashboards, and real-time analytics.

## Features

### 📊 Report Management
- **Report Creation**: Create and manage various types of reports (financial, operational, inventory, HR, sales, purchasing)
- **Report Templates**: Reusable report templates for common reporting needs
- **Scheduled Reports**: Automated report generation with configurable schedules
- **Multiple Formats**: Export reports in PDF, Excel, CSV, JSON, and HTML formats
- **Access Control**: Granular permissions for report access and sharing

### 📈 KPI Management
- **KPI Definition**: Create and manage Key Performance Indicators across different business areas
- **Real-time Calculation**: Automatic KPI calculation with configurable frequencies
- **Threshold Monitoring**: Set warning and critical thresholds with automatic alerts
- **Trend Analysis**: Track KPI trends and performance over time
- **Visualization**: Multiple chart types for KPI visualization

### 🎛️ Dashboard Management
- **Interactive Dashboards**: Create customizable dashboards with drag-and-drop widgets
- **Widget Library**: Rich set of widgets including KPIs, charts, tables, gauges, and maps
- **Real-time Updates**: Auto-refresh capabilities with configurable intervals
- **Layout Options**: Grid, freeform, and tabbed layout options
- **Responsive Design**: Mobile-friendly dashboard layouts

### 🔍 Data Source Management
- **Multiple Data Sources**: Support for databases, APIs, files, and external services
- **Connection Management**: Secure credential management and connection testing
- **Data Integration**: Seamless integration with various data sources
- **Query Builder**: Visual query builder for data exploration
- **Data Validation**: Built-in data validation and quality checks

### 🚨 Alert System
- **Threshold Alerts**: Automatic alerts based on KPI thresholds
- **Anomaly Detection**: Detect unusual patterns in data
- **Notification System**: Email and in-app notifications for alerts
- **Alert Management**: Acknowledge, resolve, and dismiss alerts
- **Escalation Rules**: Configurable alert escalation workflows

### 📱 Analytics Events
- **User Activity Tracking**: Track user interactions and system events
- **Performance Monitoring**: Monitor system performance and usage patterns
- **Audit Trail**: Complete audit trail for compliance and debugging
- **Session Management**: Track user sessions and behavior
- **Custom Events**: Support for custom event tracking

### 💾 Caching System
- **Intelligent Caching**: Smart caching for improved performance
- **Cache Management**: Automatic cache invalidation and refresh
- **Performance Optimization**: Reduce database load with strategic caching
- **Cache Analytics**: Monitor cache hit rates and performance
- **Distributed Caching**: Support for distributed cache systems

## Models

### Core Models

#### Report
- **Purpose**: Main report entity for storing report configurations and metadata
- **Key Fields**: Report ID, name, type, status, format, scheduling, access control
- **Features**: Automatic ID generation, status tracking, file management

#### KPI
- **Purpose**: Key Performance Indicator definition and management
- **Key Fields**: KPI ID, name, type, calculation method, thresholds, current values
- **Features**: Automatic calculation, trend analysis, threshold monitoring

#### KPIMeasurement
- **Purpose**: Historical KPI values and measurements
- **Key Fields**: KPI reference, value, measurement date, context data
- **Features**: Time-series data, context tracking, automatic updates

#### Dashboard
- **Purpose**: Dashboard container for organizing analytics widgets
- **Key Fields**: Dashboard ID, name, type, layout, configuration, access control
- **Features**: Layout management, access control, auto-refresh

#### DashboardWidget
- **Purpose**: Individual dashboard components and visualizations
- **Key Fields**: Widget ID, type, configuration, position, data source
- **Features**: Drag-and-drop positioning, multiple chart types, data binding

#### DataSource
- **Purpose**: Data source configuration and connection management
- **Key Fields**: Source ID, type, connection details, credentials, status
- **Features**: Secure credential storage, connection testing, status monitoring

#### ReportTemplate
- **Purpose**: Reusable report configurations and templates
- **Key Fields**: Template ID, type, configuration, parameters, usage tracking
- **Features**: Template inheritance, parameter validation, usage analytics

#### AnalyticsEvent
- **Purpose**: System and user event tracking
- **Key Fields**: Event ID, type, name, user, timestamp, context data
- **Features**: Event categorization, user tracking, performance monitoring

#### Alert
- **Purpose**: System alerts and notifications
- **Key Fields**: Alert ID, type, severity, status, related objects, thresholds
- **Features**: Severity levels, acknowledgment workflow, escalation rules

#### AnalyticsCache
- **Purpose**: Performance optimization through intelligent caching
- **Key Fields**: Cache key, type, data, expiration, hit count
- **Features**: Automatic expiration, hit tracking, performance optimization

## API Endpoints

### Reports
- `GET /api/v1/analytics/reports/` - List reports
- `POST /api/v1/analytics/reports/` - Create report
- `GET /api/v1/analytics/reports/{id}/` - Get report details
- `PUT /api/v1/analytics/reports/{id}/` - Update report
- `DELETE /api/v1/analytics/reports/{id}/` - Delete report
- `POST /api/v1/analytics/reports/{id}/execute/` - Execute report
- `POST /api/v1/analytics/reports/{id}/schedule/` - Schedule report
- `POST /api/v1/analytics/reports/{id}/unschedule/` - Unschedule report

### KPIs
- `GET /api/v1/analytics/kpis/` - List KPIs
- `POST /api/v1/analytics/kpis/` - Create KPI
- `GET /api/v1/analytics/kpis/{id}/` - Get KPI details
- `PUT /api/v1/analytics/kpis/{id}/` - Update KPI
- `DELETE /api/v1/analytics/kpis/{id}/` - Delete KPI
- `POST /api/v1/analytics/kpis/{id}/calculate/` - Calculate KPI
- `GET /api/v1/analytics/kpis/{id}/measurements/` - Get KPI measurements
- `GET /api/v1/analytics/kpis/dashboard/` - Get KPI dashboard

### KPI Measurements
- `GET /api/v1/analytics/kpi-measurements/` - List KPI measurements
- `POST /api/v1/analytics/kpi-measurements/` - Create KPI measurement
- `GET /api/v1/analytics/kpi-measurements/{id}/` - Get measurement details
- `PUT /api/v1/analytics/kpi-measurements/{id}/` - Update measurement
- `DELETE /api/v1/analytics/kpi-measurements/{id}/` - Delete measurement

### Dashboards
- `GET /api/v1/analytics/dashboards/` - List dashboards
- `POST /api/v1/analytics/dashboards/` - Create dashboard
- `GET /api/v1/analytics/dashboards/{id}/` - Get dashboard details
- `PUT /api/v1/analytics/dashboards/{id}/` - Update dashboard
- `DELETE /api/v1/analytics/dashboards/{id}/` - Delete dashboard
- `GET /api/v1/analytics/dashboards/{id}/data/` - Get dashboard data
- `POST /api/v1/analytics/dashboards/{id}/clone/` - Clone dashboard

### Dashboard Widgets
- `GET /api/v1/analytics/dashboard-widgets/` - List dashboard widgets
- `POST /api/v1/analytics/dashboard-widgets/` - Create dashboard widget
- `GET /api/v1/analytics/dashboard-widgets/{id}/` - Get widget details
- `PUT /api/v1/analytics/dashboard-widgets/{id}/` - Update widget
- `DELETE /api/v1/analytics/dashboard-widgets/{id}/` - Delete widget

### Data Sources
- `GET /api/v1/analytics/data-sources/` - List data sources
- `POST /api/v1/analytics/data-sources/` - Create data source
- `GET /api/v1/analytics/data-sources/{id}/` - Get data source details
- `PUT /api/v1/analytics/data-sources/{id}/` - Update data source
- `DELETE /api/v1/analytics/data-sources/{id}/` - Delete data source
- `POST /api/v1/analytics/data-sources/{id}/test-connection/` - Test connection

### Report Templates
- `GET /api/v1/analytics/report-templates/` - List report templates
- `POST /api/v1/analytics/report-templates/` - Create report template
- `GET /api/v1/analytics/report-templates/{id}/` - Get template details
- `PUT /api/v1/analytics/report-templates/{id}/` - Update template
- `DELETE /api/v1/analytics/report-templates/{id}/` - Delete template
- `POST /api/v1/analytics/report-templates/{id}/create-report/` - Create report from template

### Analytics Events
- `GET /api/v1/analytics/events/` - List analytics events
- `GET /api/v1/analytics/events/{id}/` - Get event details

### Alerts
- `GET /api/v1/analytics/alerts/` - List alerts
- `POST /api/v1/analytics/alerts/` - Create alert
- `GET /api/v1/analytics/alerts/{id}/` - Get alert details
- `PUT /api/v1/analytics/alerts/{id}/` - Update alert
- `DELETE /api/v1/analytics/alerts/{id}/` - Delete alert
- `POST /api/v1/analytics/alerts/{id}/acknowledge/` - Acknowledge alert
- `POST /api/v1/analytics/alerts/{id}/resolve/` - Resolve alert
- `POST /api/v1/analytics/alerts/{id}/dismiss/` - Dismiss alert

### Analytics Query
- `POST /api/v1/analytics/query/` - Execute analytics query

### Analytics Dashboard
- `GET /api/v1/analytics/dashboard/` - Get analytics dashboard

## Usage Examples

### Creating a KPI

```python
from apps.analytics.models import KPI
from decimal import Decimal

# Create a KPI
kpi = KPI.objects.create(
    organization=organization,
    name="Monthly Revenue",
    description="Total monthly revenue",
    kpi_type='financial',
    calculation_method="SUM(revenue)",
    data_source="sales_data",
    frequency='monthly',
    target_value=Decimal('100000.00'),
    warning_threshold=Decimal('80000.00'),
    critical_threshold=Decimal('60000.00'),
    chart_type='line',
    color='#007bff',
    unit='USD'
)

# Add a measurement
from apps.analytics.models import KPIMeasurement
measurement = KPIMeasurement.objects.create(
    kpi=kpi,
    value=Decimal('95000.00'),
    measurement_date=timezone.now(),
    notes="Strong performance this month"
)
```

### Creating a Dashboard

```python
from apps.analytics.models import Dashboard, DashboardWidget

# Create a dashboard
dashboard = Dashboard.objects.create(
    organization=organization,
    name="Executive Dashboard",
    description="High-level business metrics",
    dashboard_type='executive',
    layout='grid',
    refresh_interval=300,
    auto_refresh=True,
    created_by=user
)

# Add a KPI widget
kpi_widget = DashboardWidget.objects.create(
    dashboard=dashboard,
    name="Revenue KPI",
    widget_type='kpi',
    chart_type='gauge',
    data_source='kpi_data',
    query='SELECT * FROM kpi_measurements WHERE kpi_id = 1',
    position_x=0,
    position_y=0,
    width=4,
    height=3
)

# Add a chart widget
chart_widget = DashboardWidget.objects.create(
    dashboard=dashboard,
    name="Revenue Trend",
    widget_type='chart',
    chart_type='line',
    data_source='chart_data',
    query='SELECT date, revenue FROM sales_data ORDER BY date',
    position_x=4,
    position_y=0,
    width=8,
    height=6
)
```

### Creating a Report

```python
from apps.analytics.models import Report

# Create a report
report = Report.objects.create(
    organization=organization,
    name="Monthly Sales Report",
    description="Comprehensive monthly sales analysis",
    report_type='sales',
    format='pdf',
    query_parameters={
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    },
    filters={
        'status': 'completed',
        'region': 'all'
    },
    columns=['date', 'customer', 'product', 'quantity', 'amount'],
    is_scheduled=True,
    schedule_frequency='monthly',
    schedule_time=time(9, 0),  # 9:00 AM
    created_by=user
)

# Execute the report
report.status = 'running'
report.save()

# Report execution logic would go here
# ...

report.status = 'completed'
report.last_run = timezone.now()
report.save()
```

### Setting up Data Sources

```python
from apps.analytics.models import DataSource

# Create a database data source
db_source = DataSource.objects.create(
    organization=organization,
    name="Sales Database",
    description="Primary sales database",
    source_type='database',
    connection_type='postgresql',
    connection_string="postgresql://user:pass@localhost/sales_db",
    credentials={
        'username': 'analytics_user',
        'password': 'encrypted_password'
    },
    configuration={
        'pool_size': 10,
        'timeout': 30
    }
)

# Create an API data source
api_source = DataSource.objects.create(
    organization=organization,
    name="External API",
    description="Third-party data API",
    source_type='api',
    connection_type='rest_api',
    connection_string="https://api.example.com/v1",
    credentials={
        'api_key': 'encrypted_api_key',
        'auth_type': 'bearer'
    },
    configuration={
        'rate_limit': 1000,
        'timeout': 60
    }
)
```

### Creating Alerts

```python
from apps.analytics.models import Alert

# Create a KPI threshold alert
alert = Alert.objects.create(
    organization=organization,
    alert_type='kpi_threshold',
    severity='high',
    title='Revenue Below Target',
    message='Monthly revenue is below the target threshold',
    description='Current revenue is $75,000, which is below the $80,000 warning threshold',
    related_kpi=kpi,
    threshold_value=Decimal('80000.00'),
    current_value=Decimal('75000.00'),
    alert_data={
        'kpi_id': str(kpi.kpi_id),
        'kpi_name': kpi.name,
        'threshold_type': 'warning'
    }
)
```

## Filters

The module provides comprehensive filtering capabilities:

### Report Filters
- **Search**: Search across report name, description, type
- **Type**: Filter by report type (financial, operational, inventory, etc.)
- **Status**: Filter by report status (draft, running, completed, etc.)
- **Format**: Filter by output format (PDF, Excel, CSV, etc.)
- **Scheduling**: Filter by scheduled reports, overdue reports
- **Date Range**: Filter by creation date, last run date
- **Access**: Filter by public/private reports

### KPI Filters
- **Search**: Search across KPI name, description, data source
- **Type**: Filter by KPI type (financial, operational, customer, etc.)
- **Frequency**: Filter by calculation frequency
- **Status**: Filter by active/inactive KPIs
- **Thresholds**: Filter by KPIs above/below targets or thresholds
- **Data**: Filter by KPIs with/without data
- **Trend**: Filter by trend direction (increasing, decreasing, stable)

### Dashboard Filters
- **Search**: Search across dashboard name, description, type
- **Type**: Filter by dashboard type (executive, operational, departmental)
- **Layout**: Filter by layout type (grid, freeform, tabbed)
- **Status**: Filter by active/inactive dashboards
- **Access**: Filter by public/private dashboards
- **Widgets**: Filter by dashboards with/without widgets
- **Auto-refresh**: Filter by auto-refresh enabled/disabled

### Data Source Filters
- **Search**: Search across data source name, description, type
- **Type**: Filter by source type (database, API, file, external)
- **Connection**: Filter by connection type (PostgreSQL, MySQL, REST API, etc.)
- **Status**: Filter by connection status (connected, disconnected, error)
- **Active**: Filter by active/inactive data sources
- **Connection History**: Filter by never connected, recently connected

### Alert Filters
- **Search**: Search across alert title, message, description
- **Type**: Filter by alert type (KPI threshold, data anomaly, system error)
- **Severity**: Filter by severity level (low, medium, high, critical)
- **Status**: Filter by alert status (active, acknowledged, resolved, dismissed)
- **Age**: Filter by alert age (recent, old, overdue)
- **Related Objects**: Filter by related KPI, report, or dashboard

## Signals

The module includes comprehensive Django signals for automation:

### Report Signals
- **Pre-save**: Auto-generate report IDs, set next run times
- **Post-save**: Log report creation/updates, update analytics
- **Post-delete**: Log report deletion, cleanup files

### KPI Signals
- **Pre-save**: Auto-generate KPI IDs, set calculation schedules
- **Post-save**: Log KPI creation/updates, check thresholds
- **Post-delete**: Log KPI deletion, cleanup measurements

### KPI Measurement Signals
- **Post-save**: Update KPI current values, check thresholds, log events
- **Post-delete**: Update KPI values, log measurement deletion

### Dashboard Signals
- **Pre-save**: Auto-generate dashboard IDs
- **Post-save**: Log dashboard creation/updates
- **Post-delete**: Log dashboard deletion, clear cache

### Dashboard Widget Signals
- **Pre-save**: Auto-generate widget IDs
- **Post-save**: Log widget creation/updates, clear cache
- **Post-delete**: Log widget deletion, clear cache

### Data Source Signals
- **Pre-save**: Auto-generate source IDs
- **Post-save**: Log data source creation/updates
- **Post-delete**: Log data source deletion

### Alert Signals
- **Pre-save**: Auto-generate alert IDs
- **Post-save**: Log alert creation/updates, send notifications
- **Post-delete**: Log alert deletion

### Analytics Event Signals
- **Pre-save**: Auto-generate event IDs
- **Post-save**: Update analytics cache, trigger workflows

### Analytics Cache Signals
- **Post-save**: Log cache creation/updates
- **Post-delete**: Log cache deletion

## Admin Interface

The Django admin interface provides comprehensive management capabilities:

### Report Admin
- **List View**: Report name, type, status, format, creator, scheduling, file size
- **Detail View**: Complete report configuration with inline parameters
- **Filters**: Type, status, format, scheduling, creator, dates
- **Search**: Report name, description, creator
- **Actions**: Bulk status updates, export functionality

### KPI Admin
- **List View**: KPI name, type, current value, target, change %, trend, status
- **Detail View**: Complete KPI configuration with inline measurements
- **Filters**: Type, frequency, trend, status, calculation date
- **Search**: KPI name, description, data source
- **Actions**: Bulk calculation, threshold updates

### Dashboard Admin
- **List View**: Dashboard name, type, layout, creator, status, widgets count
- **Detail View**: Complete dashboard configuration with inline widgets
- **Filters**: Type, layout, status, creator, dates
- **Search**: Dashboard name, description, creator
- **Actions**: Bulk status updates, clone functionality

### Data Source Admin
- **List View**: Data source name, type, connection type, status, last connected
- **Detail View**: Complete data source configuration
- **Filters**: Type, connection type, status, connection date
- **Search**: Data source name, description, connection string
- **Actions**: Test connections, bulk status updates

### Alert Admin
- **List View**: Alert title, type, severity, status, age, acknowledged by
- **Detail View**: Complete alert information with related objects
- **Filters**: Type, severity, status, age, acknowledged by
- **Search**: Alert title, message, description
- **Actions**: Bulk acknowledge, resolve, dismiss

## Testing

The module includes comprehensive test coverage:

### Model Tests
- **ReportModelTest**: Test report creation, ID generation, string representation
- **KPIModelTest**: Test KPI creation, ID generation, string representation
- **KPIMeasurementModelTest**: Test measurement creation, string representation
- **DashboardModelTest**: Test dashboard creation, ID generation, string representation
- **DashboardWidgetModelTest**: Test widget creation, ID generation, string representation
- **DataSourceModelTest**: Test data source creation, ID generation, string representation
- **ReportTemplateModelTest**: Test template creation, ID generation, string representation
- **AnalyticsEventModelTest**: Test event creation, ID generation, string representation
- **AlertModelTest**: Test alert creation, ID generation, string representation
- **AnalyticsCacheModelTest**: Test cache creation, string representation

### API Tests
- **ReportAPITest**: Test all report API endpoints, execution, scheduling
- **KPIAPITest**: Test all KPI API endpoints, calculation, measurements, dashboard
- **DashboardAPITest**: Test all dashboard API endpoints, data retrieval, cloning
- **AnalyticsQueryAPITest**: Test analytics query execution, dashboard data

### Integration Tests
- **AnalyticsIntegrationTest**: Test complete analytics workflows, KPI threshold alerts, dashboard widget data generation

## Configuration

### Settings
The module requires the following Django settings:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'apps.analytics',
]

# Add to URL patterns
urlpatterns = [
    # ... other patterns
    path('api/v1/analytics/', include('apps.analytics.urls')),
]

# Cache configuration for analytics
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Analytics-specific settings
ANALYTICS_SETTINGS = {
    'DEFAULT_CACHE_DURATION': 300,  # 5 minutes
    'MAX_CACHE_SIZE': 1000,
    'ALERT_RETENTION_DAYS': 90,
    'EVENT_RETENTION_DAYS': 365,
}
```

### Permissions
The module uses the following permission classes:
- **IsAuthenticated**: User must be logged in
- **IsOrganizationMember**: User must be a member of the organization

### Dependencies
The module depends on:
- **apps.core**: Base models and permissions
- **apps.organizations**: Self-hosted organization support
- **django-filter**: Advanced filtering capabilities
- **django-rest-framework**: API functionality
- **django-cache**: Caching for performance optimization

## Best Practices

### KPI Management
1. **Define Clear KPIs**: Use specific, measurable, achievable, relevant, and time-bound KPIs
2. **Set Appropriate Thresholds**: Configure warning and critical thresholds based on business requirements
3. **Regular Monitoring**: Monitor KPI performance regularly and adjust thresholds as needed
4. **Documentation**: Document KPI calculation methods and data sources
5. **Review and Update**: Regularly review and update KPI definitions and targets

### Dashboard Design
1. **User-Centric Design**: Design dashboards based on user roles and responsibilities
2. **Performance Optimization**: Use caching and efficient queries for dashboard data
3. **Responsive Layout**: Ensure dashboards work well on different screen sizes
4. **Consistent Styling**: Use consistent colors, fonts, and layouts across dashboards
5. **Regular Updates**: Keep dashboard content fresh and relevant

### Report Management
1. **Template Usage**: Use report templates for common reporting needs
2. **Scheduling**: Schedule regular reports to reduce manual effort
3. **Format Selection**: Choose appropriate output formats based on audience needs
4. **Access Control**: Implement proper access controls for sensitive reports
5. **Performance**: Optimize report queries for better performance

### Data Source Management
1. **Security**: Secure credentials and connection strings
2. **Testing**: Regularly test data source connections
3. **Monitoring**: Monitor data source performance and availability
4. **Documentation**: Document data source configurations and schemas
5. **Backup**: Implement backup strategies for critical data sources

### Alert Management
1. **Threshold Tuning**: Fine-tune alert thresholds to reduce false positives
2. **Escalation Rules**: Implement proper escalation workflows
3. **Notification Channels**: Use appropriate notification channels for different alert types
4. **Response Procedures**: Define clear procedures for alert response
5. **Review Process**: Regularly review and update alert configurations

## Troubleshooting

### Common Issues

#### KPI Calculation Failures
- **Issue**: KPIs not calculating or showing incorrect values
- **Solution**: Check calculation methods, data sources, and measurement data

#### Dashboard Performance
- **Issue**: Slow dashboard loading or widget rendering
- **Solution**: Optimize queries, implement caching, reduce widget complexity

#### Report Generation Failures
- **Issue**: Reports failing to generate or showing errors
- **Solution**: Check query parameters, data source connections, and file permissions

#### Alert Spam
- **Issue**: Too many alerts or false positives
- **Solution**: Adjust thresholds, implement alert cooldowns, review alert logic

#### Cache Issues
- **Issue**: Stale data or cache-related errors
- **Solution**: Clear cache, check cache configuration, implement cache invalidation

### Debug Mode
Enable debug logging for detailed analytics information:

```python
LOGGING = {
    'loggers': {
        'apps.analytics': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Machine learning for predictive analytics and anomaly detection
2. **Real-time Streaming**: Real-time data streaming and live dashboard updates
3. **Advanced Visualizations**: More chart types, interactive visualizations, and custom widgets
4. **Data Pipeline**: Automated data pipeline for ETL operations
5. **Mobile App**: Native mobile app for analytics and reporting
6. **Collaboration**: Collaborative dashboard editing and sharing
7. **Advanced Alerts**: Smart alerts with machine learning-based threshold detection
8. **Data Governance**: Data lineage, quality monitoring, and compliance features

### Integration Opportunities
1. **Business Intelligence Tools**: Integration with Power BI, Tableau, and other BI tools
2. **Data Warehouses**: Integration with data warehouses and data lakes
3. **External APIs**: Integration with external data providers and APIs
4. **Notification Systems**: Integration with Slack, Teams, and other notification platforms
5. **Document Management**: Integration with document management systems

## Support

For support and questions:
- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs and feature requests through the issue tracker
- **Community**: Join the community forum for discussions
- **Training**: Access training materials and video tutorials

## License

This module is part of the TidyGen ERP system and follows the same licensing terms.

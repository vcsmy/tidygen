"""
Analytics & Reporting Views

This module contains all the views for the analytics and reporting system,
providing API endpoints for reports, KPIs, dashboards, and analytics components.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg, F, Max, Min
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
from drf_spectacular.utils import extend_schema

from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)
from apps.analytics.serializers import (
    ReportSerializer, ReportCreateSerializer, ReportSummarySerializer,
    KPISerializer, KPICreateSerializer, KPISummarySerializer,
    KPIMeasurementSerializer, KPIMeasurementCreateSerializer,
    DashboardSerializer, DashboardCreateSerializer, DashboardSummarySerializer,
    DashboardWidgetSerializer, DashboardWidgetCreateSerializer,
    DataSourceSerializer, DataSourceCreateSerializer,
    ReportTemplateSerializer, ReportTemplateCreateSerializer,
    AnalyticsEventSerializer, AlertSerializer, AlertCreateSerializer,
    AnalyticsCacheSerializer, ReportExecutionSerializer,
    DashboardDataSerializer, AnalyticsQuerySerializer
)
from apps.analytics.filters import (
    ReportFilter, KPIFilter, DashboardFilter, DataSourceFilter,
    ReportTemplateFilter, AnalyticsEventFilter, AlertFilter
)
from apps.core.permissions import IsOrganizationMember

logger = logging.getLogger(__name__)


@extend_schema(tags=['Analytics'])
class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReportFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        elif self.action == 'list':
            return ReportSummarySerializer
        return ReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(
                Q(organization=user.organization) &
                (Q(is_public=True) | Q(created_by=user) | Q(allowed_users=user))
            ).distinct()
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report."""
        report = self.get_object()
        execution_serializer = ReportExecutionSerializer(data=request.data)
        
        if execution_serializer.is_valid():
            # Update report status
            report.status = 'running'
            report.save()
            
            try:
                # Execute report logic here
                # This would typically involve:
                # 1. Running the report query
                # 2. Generating the report file
                # 3. Updating report status
                
                report.status = 'completed'
                report.last_run = timezone.now()
                report.save()
                
                # Log analytics event
                AnalyticsEvent.objects.create(
                    organization=request.user.organization,
                    event_type='report_generated',
                    event_name=f'Report Generated: {report.name}',
                    user=request.user,
                    context_data={
                        'report_id': str(report.report_id),
                        'format': execution_serializer.validated_data.get('format', 'pdf')
                    }
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Report executed successfully',
                    'report_id': str(report.report_id)
                })
                
            except Exception as e:
                report.status = 'failed'
                report.save()
                logger.error(f"Report execution failed: {str(e)}")
                return Response(
                    {'error': 'Report execution failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(execution_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a report for automatic execution."""
        report = self.get_object()
        
        frequency = request.data.get('frequency')
        schedule_time = request.data.get('schedule_time')
        
        if not frequency:
            return Response(
                {'error': 'Frequency is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.is_scheduled = True
        report.schedule_frequency = frequency
        if schedule_time:
            report.schedule_time = schedule_time
        
        # Calculate next run time
        report.next_run = self._calculate_next_run(frequency, schedule_time)
        report.save()
        
        return Response({'message': 'Report scheduled successfully'})
    
    @action(detail=True, methods=['post'])
    def unschedule(self, request, pk=None):
        """Unschedule a report."""
        report = self.get_object()
        report.is_scheduled = False
        report.schedule_frequency = ''
        report.schedule_time = None
        report.next_run = None
        report.save()
        
        return Response({'message': 'Report unscheduled successfully'})
    
    def _calculate_next_run(self, frequency, schedule_time):
        """Calculate next run time based on frequency."""
        now = timezone.now()
        
        if frequency == 'daily':
            next_run = now + timedelta(days=1)
        elif frequency == 'weekly':
            next_run = now + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_run = now + timedelta(days=30)
        elif frequency == 'quarterly':
            next_run = now + timedelta(days=90)
        elif frequency == 'yearly':
            next_run = now + timedelta(days=365)
        else:
            next_run = now + timedelta(hours=1)
        
        return next_run


@extend_schema(tags=['Analytics'])
class KPIViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KPIs.
    """
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = KPIFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return KPICreateSerializer
        elif self.action == 'list':
            return KPISummarySerializer
        return KPISerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Manually calculate KPI value."""
        kpi = self.get_object()
        
        try:
            # Calculate KPI value based on calculation_method
            # This would typically involve executing the calculation logic
            new_value = self._calculate_kpi_value(kpi)
            
            # Update KPI
            kpi.previous_value = kpi.current_value
            kpi.current_value = new_value
            
            if kpi.previous_value:
                change = ((new_value - kpi.previous_value) / kpi.previous_value) * 100
                kpi.change_percentage = change
                
                if change > 5:
                    kpi.trend = 'increasing'
                elif change < -5:
                    kpi.trend = 'decreasing'
                else:
                    kpi.trend = 'stable'
            
            kpi.last_calculated = timezone.now()
            kpi.save()
            
            # Create measurement record
            KPIMeasurement.objects.create(
                kpi=kpi,
                value=new_value,
                measurement_date=timezone.now()
            )
            
            # Check for alerts
            self._check_kpi_alerts(kpi)
            
            return Response({
                'status': 'success',
                'current_value': new_value,
                'change_percentage': kpi.change_percentage
            })
            
        except Exception as e:
            logger.error(f"KPI calculation failed: {str(e)}")
            return Response(
                {'error': 'KPI calculation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def measurements(self, request, pk=None):
        """Get KPI measurements."""
        kpi = self.get_object()
        
        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        measurements = kpi.measurements.all()
        
        if start_date:
            measurements = measurements.filter(measurement_date__gte=start_date)
        if end_date:
            measurements = measurements.filter(measurement_date__lte=end_date)
        
        serializer = KPIMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get KPI dashboard data."""
        queryset = self.get_queryset().filter(is_active=True)
        
        # Get KPIs by type
        kpis_by_type = {}
        for kpi_type, _ in KPI.KPI_TYPE_CHOICES:
            kpis = queryset.filter(kpi_type=kpi_type)
            serializer = KPISummarySerializer(kpis, many=True)
            kpis_by_type[kpi_type] = serializer.data
        
        # Get alerts
        alerts = Alert.objects.filter(
            organization=request.user.organization,
            status='active',
            related_kpi__isnull=False
        ).order_by('-triggered_at')[:10]
        
        alert_serializer = AlertSerializer(alerts, many=True)
        
        return Response({
            'kpis_by_type': kpis_by_type,
            'recent_alerts': alert_serializer.data,
            'summary': {
                'total_kpis': queryset.count(),
                'active_kpis': queryset.filter(current_value__isnull=False).count(),
                'alerts_count': alerts.count()
            }
        })
    
    def _calculate_kpi_value(self, kpi):
        """Calculate KPI value based on calculation method."""
        # This is a simplified example
        # In a real implementation, this would execute the actual calculation logic
        import random
        return Decimal(str(random.uniform(0, 100)))
    
    def _check_kpi_alerts(self, kpi):
        """Check if KPI triggers any alerts."""
        if kpi.critical_threshold and kpi.current_value <= kpi.critical_threshold:
            Alert.objects.create(
                organization=kpi.organization,
                alert_type='kpi_threshold',
                severity='critical',
                title=f'Critical KPI Alert: {kpi.name}',
                message=f'KPI "{kpi.name}" has reached critical threshold',
                related_kpi=kpi,
                threshold_value=kpi.critical_threshold,
                current_value=kpi.current_value
            )
        elif kpi.warning_threshold and kpi.current_value <= kpi.warning_threshold:
            Alert.objects.create(
                organization=kpi.organization,
                alert_type='kpi_threshold',
                severity='high',
                title=f'Warning KPI Alert: {kpi.name}',
                message=f'KPI "{kpi.name}" has reached warning threshold',
                related_kpi=kpi,
                threshold_value=kpi.warning_threshold,
                current_value=kpi.current_value
            )


@extend_schema(tags=['Analytics'])
class KPIMeasurementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KPI measurements.
    """
    queryset = KPIMeasurement.objects.all()
    serializer_class = KPIMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return KPIMeasurementCreateSerializer
        return KPIMeasurementSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(kpi__organization=user.organization)
        return self.queryset.none()


@extend_schema(tags=['Analytics'])
class DashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboards.
    """
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DashboardFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DashboardCreateSerializer
        elif self.action == 'list':
            return DashboardSummarySerializer
        return DashboardSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(
                Q(organization=user.organization) &
                (Q(is_public=True) | Q(created_by=user) | Q(allowed_users=user))
            ).distinct()
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get dashboard data."""
        dashboard = self.get_object()
        data_serializer = DashboardDataSerializer(data=request.query_params)
        
        if data_serializer.is_valid():
            widget_ids = data_serializer.validated_data.get('widget_ids', [])
            refresh_cache = data_serializer.validated_data.get('refresh_cache', False)
            
            widgets = dashboard.widgets.filter(is_active=True)
            if widget_ids:
                widgets = widgets.filter(widget_id__in=widget_ids)
            
            widget_data = {}
            for widget in widgets:
                cache_key = f"dashboard_widget_{widget.widget_id}"
                
                if refresh_cache:
                    cache.delete(cache_key)
                
                data = cache.get(cache_key)
                if not data:
                    # Generate widget data
                    data = self._generate_widget_data(widget)
                    cache.set(cache_key, data, 300)  # Cache for 5 minutes
                
                widget_data[str(widget.widget_id)] = data
            
            # Log analytics event
            AnalyticsEvent.objects.create(
                organization=request.user.organization,
                event_type='dashboard_viewed',
                event_name=f'Dashboard Viewed: {dashboard.name}',
                user=request.user,
                context_data={
                    'dashboard_id': str(dashboard.dashboard_id),
                    'widget_count': len(widget_data)
                }
            )
            
            return Response({
                'dashboard_id': str(dashboard.dashboard_id),
                'widget_data': widget_data,
                'last_updated': dashboard.last_updated
            })
        
        return Response(data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a dashboard."""
        original_dashboard = self.get_object()
        
        # Create new dashboard
        new_dashboard = Dashboard.objects.create(
            organization=request.user.organization,
            name=f"{original_dashboard.name} (Copy)",
            description=original_dashboard.description,
            dashboard_type=original_dashboard.dashboard_type,
            layout=original_dashboard.layout,
            configuration=original_dashboard.configuration,
            refresh_interval=original_dashboard.refresh_interval,
            auto_refresh=original_dashboard.auto_refresh,
            created_by=request.user
        )
        
        # Clone widgets
        for widget in original_dashboard.widgets.all():
            DashboardWidget.objects.create(
                dashboard=new_dashboard,
                name=widget.name,
                widget_type=widget.widget_type,
                configuration=widget.configuration,
                data_source=widget.data_source,
                query=widget.query,
                chart_type=widget.chart_type,
                chart_config=widget.chart_config,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                refresh_interval=widget.refresh_interval
            )
        
        serializer = DashboardSerializer(new_dashboard)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generate_widget_data(self, widget):
        """Generate data for a widget."""
        # This is a simplified example
        # In a real implementation, this would execute the actual data query
        import random
        
        if widget.widget_type == 'kpi':
            return {
                'value': random.uniform(0, 100),
                'target': 80,
                'trend': 'increasing'
            }
        elif widget.widget_type == 'chart':
            return {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Data',
                    'data': [random.uniform(0, 100) for _ in range(6)]
                }]
            }
        else:
            return {'data': 'Sample data'}


@extend_schema(tags=['Analytics'])
class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboard widgets.
    """
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DashboardWidgetCreateSerializer
        return DashboardWidgetSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(dashboard__organization=user.organization)
        return self.queryset.none()


@extend_schema(tags=['Analytics'])
class DataSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing data sources.
    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DataSourceFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DataSourceCreateSerializer
        return DataSourceSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test data source connection."""
        data_source = self.get_object()
        
        try:
            # Test connection logic here
            # This would typically involve:
            # 1. Establishing connection using credentials
            # 2. Running a simple query
            # 3. Verifying data access
            
            data_source.connection_status = 'connected'
            data_source.last_connected = timezone.now()
            data_source.save()
            
            return Response({
                'status': 'success',
                'message': 'Connection successful'
            })
            
        except Exception as e:
            data_source.connection_status = 'error'
            data_source.save()
            logger.error(f"Data source connection failed: {str(e)}")
            return Response(
                {'error': 'Connection failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['Analytics'])
class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing report templates.
    """
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReportTemplateFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportTemplateCreateSerializer
        return ReportTemplateSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset.filter(
                Q(organization=user.organization) &
                (Q(is_public=True) | Q(created_by=user))
            ).distinct()
        return self.queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['post'])
    def create_report(self, request, pk=None):
        """Create a report from template."""
        template = self.get_object()
        
        # Create report from template
        report = Report.objects.create(
            organization=request.user.organization,
            name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d')}",
            description=template.description,
            report_type=template.template_type,
            query_parameters=template.default_parameters,
            created_by=request.user
        )
        
        # Update usage count
        template.usage_count += 1
        template.save()
        
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Analytics'])
class AnalyticsEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing analytics events.
    """
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsEventFilter
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()


@extend_schema(tags=['Analytics'])
class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing alerts.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AlertFilter
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlertCreateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return self.queryset
        return self.queryset.none()
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({'message': 'Alert acknowledged'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({'message': 'Alert resolved'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss an alert."""
        alert = self.get_object()
        alert.status = 'dismissed'
        alert.save()
        
        return Response({'message': 'Alert dismissed'})


class AnalyticsQueryView(APIView):
    """
    API view for executing analytics queries.
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def post(self, request):
        """Execute an analytics query."""
        serializer = AnalyticsQuerySerializer(data=request.data)
        
        if serializer.is_valid():
            query = serializer.validated_data['query']
            parameters = serializer.validated_data['parameters']
            data_source_id = serializer.validated_data['data_source']
            cache_duration = serializer.validated_data['cache_duration']
            
            # Check cache first
            cache_key = f"analytics_query_{hash(query + str(parameters))}"
            result = cache.get(cache_key)
            
            if not result:
                try:
                    # Execute query logic here
                    # This would typically involve:
                    # 1. Getting data source
                    # 2. Executing query with parameters
                    # 3. Processing results
                    
                    result = {
                        'data': 'Sample query result',
                        'execution_time': '0.123s',
                        'row_count': 100
                    }
                    
                    # Cache result
                    cache.set(cache_key, result, cache_duration)
                    
                    # Log analytics event
                    AnalyticsEvent.objects.create(
                        organization=request.user.organization,
                        event_type='custom',
                        event_name='Analytics Query Executed',
                        user=request.user,
                        context_data={
                            'query': query,
                            'parameters': parameters,
                            'data_source': data_source_id
                        }
                    )
                    
                    return Response(result)
                    
                except Exception as e:
                    logger.error(f"Analytics query failed: {str(e)}")
                    return Response(
                        {'error': 'Query execution failed', 'details': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsDashboardView(APIView):
    """
    API view for analytics dashboard.
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """Get analytics dashboard data."""
        organization = request.user.organization
        
        # Get summary statistics
        summary = {
            'reports': {
                'total': Report.objects.count(),
                'scheduled': Report.objects.count(),
                'completed_today': Report.objects.filter(
                    organization=organization,
                    status='completed',
                    last_run__date=timezone.now().date()
                ).count()
            },
            'kpis': {
                'total': KPI.objects.count(),
                'active': KPI.objects.count(),
                'with_alerts': KPI.objects.filter(
                    organization=organization,
                    alerts__status='active'
                ).distinct().count()
            },
            'dashboards': {
                'total': Dashboard.objects.count(),
                'active': Dashboard.objects.count(),
                'public': Dashboard.objects.count()
            },
            'alerts': {
                'active': Alert.objects.count(),
                'critical': Alert.objects.filter(
                    organization=organization,
                    status='active',
                    severity='critical'
                ).count(),
                'acknowledged_today': Alert.objects.filter(
                    organization=organization,
                    status='acknowledged',
                    acknowledged_at__date=timezone.now().date()
                ).count()
            }
        }
        
        # Get recent activity
        recent_events = AnalyticsEvent.objects.filter(
            organization=organization
        ).order_by('-event_timestamp')[:10]
        
        recent_events_serializer = AnalyticsEventSerializer(recent_events, many=True)
        
        # Get top KPIs by performance
        top_kpis = KPI.objects.filter(
            organization=organization,
            is_active=True,
            current_value__isnull=False
        ).order_by('-current_value')[:5]
        
        top_kpis_serializer = KPISummarySerializer(top_kpis, many=True)
        
        return Response({
            'summary': summary,
            'recent_events': recent_events_serializer.data,
            'top_kpis': top_kpis_serializer.data
        })

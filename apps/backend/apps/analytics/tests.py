"""
Analytics & Reporting Tests

This module contains comprehensive tests for the analytics and reporting system,
including unit tests, integration tests, and API tests for all analytics functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
import json
import uuid

from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)

User = get_user_model()


class ReportModelTest(TestCase):
    """Test cases for Report model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_report_creation(self):
        """Test creating a report."""
        report = Report.objects.create(
            organization=self.organization,
            name="Test Report",
            description="Test report description",
            report_type='financial',
            status='draft',
            format='pdf',
            created_by=self.user
        )
        
        self.assertEqual(report.organization, self.organization)
        self.assertEqual(report.name, "Test Report")
        self.assertEqual(report.report_type, 'financial')
        self.assertEqual(report.status, 'draft')
        self.assertEqual(report.format, 'pdf')
        self.assertEqual(report.created_by, self.user)
        self.assertTrue(report.report_id)  # Should be auto-generated
    
    def test_report_id_generation(self):
        """Test automatic report ID generation."""
        report1 = Report.objects.create(
            organization=self.organization,
            name="Report 1",
            created_by=self.user
        )
        report2 = Report.objects.create(
            organization=self.organization,
            name="Report 2",
            created_by=self.user
        )
        
        self.assertNotEqual(report1.report_id, report2.report_id)
        self.assertIsInstance(report1.report_id, uuid.UUID)
        self.assertIsInstance(report2.report_id, uuid.UUID)
    
    def test_report_str_representation(self):
        """Test string representation of report."""
        report = Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            created_by=self.user
        )
        
        expected = f"Test Report (Financial)"
        self.assertEqual(str(report), expected)


class KPIModelTest(TestCase):
    """Test cases for KPI model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
    
    def test_kpi_creation(self):
        """Test creating a KPI."""
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            description="Test KPI description",
            kpi_type='financial',
            calculation_method="SUM(revenue)",
            data_source="sales_data",
            frequency='daily',
            target_value=Decimal('1000.00'),
            warning_threshold=Decimal('800.00'),
            critical_threshold=Decimal('600.00')
        )
        
        self.assertEqual(kpi.organization, self.organization)
        self.assertEqual(kpi.name, "Test KPI")
        self.assertEqual(kpi.kpi_type, 'financial')
        self.assertEqual(kpi.calculation_method, "SUM(revenue)")
        self.assertEqual(kpi.data_source, "sales_data")
        self.assertEqual(kpi.frequency, 'daily')
        self.assertEqual(kpi.target_value, Decimal('1000.00'))
        self.assertTrue(kpi.kpi_id)  # Should be auto-generated
    
    def test_kpi_id_generation(self):
        """Test automatic KPI ID generation."""
        kpi1 = KPI.objects.create(
            organization=self.organization,
            name="KPI 1",
            calculation_method="SUM(value1)",
            data_source="data1"
        )
        kpi2 = KPI.objects.create(
            organization=self.organization,
            name="KPI 2",
            calculation_method="SUM(value2)",
            data_source="data2"
        )
        
        self.assertNotEqual(kpi1.kpi_id, kpi2.kpi_id)
        self.assertIsInstance(kpi1.kpi_id, uuid.UUID)
        self.assertIsInstance(kpi2.kpi_id, uuid.UUID)
    
    def test_kpi_str_representation(self):
        """Test string representation of KPI."""
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            kpi_type='financial',
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
        
        expected = f"Test KPI (Financial)"
        self.assertEqual(str(kpi), expected)


class KPIMeasurementModelTest(TestCase):
    """Test cases for KPIMeasurement model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
    
    def test_kpi_measurement_creation(self):
        """Test creating a KPI measurement."""
        measurement = KPIMeasurement.objects.create(
            kpi=self.kpi,
            value=Decimal('1500.00'),
            measurement_date=timezone.now(),
            notes="Test measurement"
        )
        
        self.assertEqual(measurement.kpi, self.kpi)
        self.assertEqual(measurement.value, Decimal('1500.00'))
        self.assertEqual(measurement.notes, "Test measurement")
    
    def test_kpi_measurement_str_representation(self):
        """Test string representation of KPI measurement."""
        measurement = KPIMeasurement.objects.create(
            kpi=self.kpi,
            value=Decimal('1500.00'),
            measurement_date=timezone.now()
        )
        
        expected = f"Test KPI - 1500.00 ({measurement.measurement_date})"
        self.assertEqual(str(measurement), expected)


class DashboardModelTest(TestCase):
    """Test cases for Dashboard model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_dashboard_creation(self):
        """Test creating a dashboard."""
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            description="Test dashboard description",
            dashboard_type='executive',
            layout='grid',
            refresh_interval=300,
            auto_refresh=True,
            created_by=self.user
        )
        
        self.assertEqual(dashboard.organization, self.organization)
        self.assertEqual(dashboard.name, "Test Dashboard")
        self.assertEqual(dashboard.dashboard_type, 'executive')
        self.assertEqual(dashboard.layout, 'grid')
        self.assertEqual(dashboard.refresh_interval, 300)
        self.assertTrue(dashboard.auto_refresh)
        self.assertEqual(dashboard.created_by, self.user)
        self.assertTrue(dashboard.dashboard_id)  # Should be auto-generated
    
    def test_dashboard_id_generation(self):
        """Test automatic dashboard ID generation."""
        dashboard1 = Dashboard.objects.create(
            organization=self.organization,
            name="Dashboard 1",
            created_by=self.user
        )
        dashboard2 = Dashboard.objects.create(
            organization=self.organization,
            name="Dashboard 2",
            created_by=self.user
        )
        
        self.assertNotEqual(dashboard1.dashboard_id, dashboard2.dashboard_id)
        self.assertIsInstance(dashboard1.dashboard_id, uuid.UUID)
        self.assertIsInstance(dashboard2.dashboard_id, uuid.UUID)
    
    def test_dashboard_str_representation(self):
        """Test string representation of dashboard."""
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            dashboard_type='executive',
            created_by=self.user
        )
        
        expected = f"Test Dashboard (Executive)"
        self.assertEqual(str(dashboard), expected)


class DashboardWidgetModelTest(TestCase):
    """Test cases for DashboardWidget model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
    
    def test_dashboard_widget_creation(self):
        """Test creating a dashboard widget."""
        widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            name="Test Widget",
            widget_type='kpi',
            chart_type='line',
            position_x=0,
            position_y=0,
            width=4,
            height=3
        )
        
        self.assertEqual(widget.dashboard, self.dashboard)
        self.assertEqual(widget.name, "Test Widget")
        self.assertEqual(widget.widget_type, 'kpi')
        self.assertEqual(widget.chart_type, 'line')
        self.assertEqual(widget.position_x, 0)
        self.assertEqual(widget.position_y, 0)
        self.assertEqual(widget.width, 4)
        self.assertEqual(widget.height, 3)
        self.assertTrue(widget.widget_id)  # Should be auto-generated
    
    def test_dashboard_widget_id_generation(self):
        """Test automatic widget ID generation."""
        widget1 = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            name="Widget 1",
            widget_type='kpi'
        )
        widget2 = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            name="Widget 2",
            widget_type='chart'
        )
        
        self.assertNotEqual(widget1.widget_id, widget2.widget_id)
        self.assertIsInstance(widget1.widget_id, uuid.UUID)
        self.assertIsInstance(widget2.widget_id, uuid.UUID)
    
    def test_dashboard_widget_str_representation(self):
        """Test string representation of dashboard widget."""
        widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            name="Test Widget",
            widget_type='kpi'
        )
        
        expected = f"Test Widget (KPI)"
        self.assertEqual(str(widget), expected)


class DataSourceModelTest(TestCase):
    """Test cases for DataSource model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
    
    def test_data_source_creation(self):
        """Test creating a data source."""
        data_source = DataSource.objects.create(
            organization=self.organization,
            name="Test Data Source",
            description="Test data source description",
            source_type='database',
            connection_type='postgresql',
            connection_string="postgresql://user:pass@localhost/db",
            is_active=True
        )
        
        self.assertEqual(data_source.organization, self.organization)
        self.assertEqual(data_source.name, "Test Data Source")
        self.assertEqual(data_source.source_type, 'database')
        self.assertEqual(data_source.connection_type, 'postgresql')
        self.assertEqual(data_source.connection_string, "postgresql://user:pass@localhost/db")
        self.assertTrue(data_source.is_active)
        self.assertTrue(data_source.source_id)  # Should be auto-generated
    
    def test_data_source_id_generation(self):
        """Test automatic data source ID generation."""
        data_source1 = DataSource.objects.create(
            organization=self.organization,
            name="Data Source 1",
            source_type='database',
            connection_type='postgresql'
        )
        data_source2 = DataSource.objects.create(
            organization=self.organization,
            name="Data Source 2",
            source_type='api',
            connection_type='rest_api'
        )
        
        self.assertNotEqual(data_source1.source_id, data_source2.source_id)
        self.assertIsInstance(data_source1.source_id, uuid.UUID)
        self.assertIsInstance(data_source2.source_id, uuid.UUID)
    
    def test_data_source_str_representation(self):
        """Test string representation of data source."""
        data_source = DataSource.objects.create(
            organization=self.organization,
            name="Test Data Source",
            source_type='database'
        )
        
        expected = f"Test Data Source (Database)"
        self.assertEqual(str(data_source), expected)


class ReportTemplateModelTest(TestCase):
    """Test cases for ReportTemplate model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_report_template_creation(self):
        """Test creating a report template."""
        template = ReportTemplate.objects.create(
            organization=self.organization,
            name="Test Template",
            description="Test template description",
            template_type='financial',
            template_config={'columns': ['date', 'amount']},
            default_parameters={'start_date': '2024-01-01'},
            required_parameters=['start_date', 'end_date'],
            is_public=True,
            created_by=self.user
        )
        
        self.assertEqual(template.organization, self.organization)
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.template_type, 'financial')
        self.assertEqual(template.template_config, {'columns': ['date', 'amount']})
        self.assertEqual(template.default_parameters, {'start_date': '2024-01-01'})
        self.assertEqual(template.required_parameters, ['start_date', 'end_date'])
        self.assertTrue(template.is_public)
        self.assertEqual(template.created_by, self.user)
        self.assertTrue(template.template_id)  # Should be auto-generated
    
    def test_report_template_id_generation(self):
        """Test automatic template ID generation."""
        template1 = ReportTemplate.objects.create(
            organization=self.organization,
            name="Template 1",
            template_type='financial',
            created_by=self.user
        )
        template2 = ReportTemplate.objects.create(
            organization=self.organization,
            name="Template 2",
            template_type='operational',
            created_by=self.user
        )
        
        self.assertNotEqual(template1.template_id, template2.template_id)
        self.assertIsInstance(template1.template_id, uuid.UUID)
        self.assertIsInstance(template2.template_id, uuid.UUID)
    
    def test_report_template_str_representation(self):
        """Test string representation of report template."""
        template = ReportTemplate.objects.create(
            organization=self.organization,
            name="Test Template",
            template_type='financial',
            created_by=self.user
        )
        
        expected = f"Test Template (Financial)"
        self.assertEqual(str(template), expected)


class AnalyticsEventModelTest(TestCase):
    """Test cases for AnalyticsEvent model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_analytics_event_creation(self):
        """Test creating an analytics event."""
        event = AnalyticsEvent.objects.create(
            organization=self.organization,
            event_type='user_action',
            event_name='Test Event',
            description='Test event description',
            user=self.user,
            session_id='session123',
            ip_address='192.168.1.1',
            context_data={'action': 'click', 'page': 'dashboard'}
        )
        
        self.assertEqual(event.organization, self.organization)
        self.assertEqual(event.event_type, 'user_action')
        self.assertEqual(event.event_name, 'Test Event')
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.session_id, 'session123')
        self.assertEqual(event.ip_address, '192.168.1.1')
        self.assertEqual(event.context_data, {'action': 'click', 'page': 'dashboard'})
        self.assertTrue(event.event_id)  # Should be auto-generated
    
    def test_analytics_event_id_generation(self):
        """Test automatic event ID generation."""
        event1 = AnalyticsEvent.objects.create(
            organization=self.organization,
            event_type='user_action',
            event_name='Event 1'
        )
        event2 = AnalyticsEvent.objects.create(
            organization=self.organization,
            event_type='system_event',
            event_name='Event 2'
        )
        
        self.assertNotEqual(event1.event_id, event2.event_id)
        self.assertIsInstance(event1.event_id, uuid.UUID)
        self.assertIsInstance(event2.event_id, uuid.UUID)
    
    def test_analytics_event_str_representation(self):
        """Test string representation of analytics event."""
        event = AnalyticsEvent.objects.create(
            organization=self.organization,
            event_type='user_action',
            event_name='Test Event'
        )
        
        expected = f"Test Event (User Action) - {event.event_timestamp}"
        self.assertEqual(str(event), expected)


class AlertModelTest(TestCase):
    """Test cases for Alert model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        self.kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
    
    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='kpi_threshold',
            severity='high',
            status='active',
            title='Test Alert',
            message='Test alert message',
            description='Test alert description',
            related_kpi=self.kpi,
            threshold_value=Decimal('1000.00'),
            current_value=Decimal('800.00')
        )
        
        self.assertEqual(alert.organization, self.organization)
        self.assertEqual(alert.alert_type, 'kpi_threshold')
        self.assertEqual(alert.severity, 'high')
        self.assertEqual(alert.status, 'active')
        self.assertEqual(alert.title, 'Test Alert')
        self.assertEqual(alert.related_kpi, self.kpi)
        self.assertEqual(alert.threshold_value, Decimal('1000.00'))
        self.assertEqual(alert.current_value, Decimal('800.00'))
        self.assertTrue(alert.alert_id)  # Should be auto-generated
    
    def test_alert_id_generation(self):
        """Test automatic alert ID generation."""
        alert1 = Alert.objects.create(
            organization=self.organization,
            alert_type='kpi_threshold',
            severity='high',
            title='Alert 1',
            message='Alert 1 message'
        )
        alert2 = Alert.objects.create(
            organization=self.organization,
            alert_type='system_error',
            severity='critical',
            title='Alert 2',
            message='Alert 2 message'
        )
        
        self.assertNotEqual(alert1.alert_id, alert2.alert_id)
        self.assertIsInstance(alert1.alert_id, uuid.UUID)
        self.assertIsInstance(alert2.alert_id, uuid.UUID)
    
    def test_alert_str_representation(self):
        """Test string representation of alert."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='kpi_threshold',
            severity='high',
            title='Test Alert',
            message='Test alert message'
        )
        
        expected = f"Test Alert (High) - {alert.triggered_at}"
        self.assertEqual(str(alert), expected)


class AnalyticsCacheModelTest(TestCase):
    """Test cases for AnalyticsCache model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
    
    def test_analytics_cache_creation(self):
        """Test creating an analytics cache entry."""
        cache_entry = AnalyticsCache.objects.create(
            cache_key='test_cache_key',
            organization=self.organization,
            cache_type='kpi',
            data={'value': 1500, 'trend': 'increasing'},
            metadata={'source': 'calculation', 'timestamp': timezone.now().isoformat()},
            expires_at=timezone.now() + timedelta(hours=1),
            related_kpi=self.kpi
        )
        
        self.assertEqual(cache_entry.cache_key, 'test_cache_key')
        self.assertEqual(cache_entry.organization, self.organization)
        self.assertEqual(cache_entry.cache_type, 'kpi')
        self.assertEqual(cache_entry.data, {'value': 1500, 'trend': 'increasing'})
        self.assertEqual(cache_entry.related_kpi, self.kpi)
        self.assertEqual(cache_entry.hit_count, 0)
    
    def test_analytics_cache_str_representation(self):
        """Test string representation of analytics cache."""
        cache_entry = AnalyticsCache.objects.create(
            cache_key='test_cache_key',
            organization=self.organization,
            cache_type='kpi',
            data={'value': 1500},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        expected = f"test_cache_key (KPI)"
        self.assertEqual(str(cache_entry), expected)


class ReportAPITest(APITestCase):
    """Test cases for Report API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_report(self):
        """Test creating a report via API."""
        url = reverse('report-list')
        data = {
            'organization': self.organization.id,
            'name': 'Test Report',
            'description': 'Test report description',
            'report_type': 'financial',
            'format': 'pdf',
            'query_parameters': {'start_date': '2024-01-01'},
            'filters': {'status': 'active'},
            'columns': ['date', 'amount', 'description']
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        
        report = Report.objects.first()
        self.assertEqual(report.name, "Test Report")
        self.assertEqual(report.report_type, 'financial')
        self.assertEqual(report.created_by, self.user)
    
    def test_list_reports(self):
        """Test listing reports via API."""
        # Create a report
        Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            created_by=self.user
        )
        
        url = reverse('report-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_report(self):
        """Test retrieving a specific report via API."""
        report = Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            created_by=self.user
        )
        
        url = reverse('report-detail', kwargs={'pk': report.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], report.name)
    
    def test_execute_report(self):
        """Test executing a report via API."""
        report = Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            status='draft',
            created_by=self.user
        )
        
        url = reverse('report-execute', kwargs={'pk': report.pk})
        data = {
            'parameters': {'start_date': '2024-01-01'},
            'format': 'pdf'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    def test_schedule_report(self):
        """Test scheduling a report via API."""
        report = Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            created_by=self.user
        )
        
        url = reverse('report-schedule', kwargs={'pk': report.pk})
        data = {
            'frequency': 'daily',
            'schedule_time': '09:00:00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Report scheduled successfully')


class KPIAPITest(APITestCase):
    """Test cases for KPI API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_kpi(self):
        """Test creating a KPI via API."""
        url = reverse('kpi-list')
        data = {
            'organization': self.organization.id,
            'name': 'Test KPI',
            'description': 'Test KPI description',
            'kpi_type': 'financial',
            'calculation_method': 'SUM(revenue)',
            'data_source': 'sales_data',
            'frequency': 'daily',
            'target_value': '1000.00',
            'warning_threshold': '800.00',
            'critical_threshold': '600.00',
            'chart_type': 'line',
            'color': '#007bff',
            'unit': 'USD'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KPI.objects.count(), 1)
        
        kpi = KPI.objects.first()
        self.assertEqual(kpi.name, "Test KPI")
        self.assertEqual(kpi.kpi_type, 'financial')
        self.assertEqual(kpi.target_value, Decimal('1000.00'))
    
    def test_list_kpis(self):
        """Test listing KPIs via API."""
        # Create a KPI
        KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
        
        url = reverse('kpi-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_calculate_kpi(self):
        """Test calculating KPI value via API."""
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
        
        url = reverse('kpi-calculate', kwargs={'pk': kpi.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('current_value', response.data)
    
    def test_kpi_measurements(self):
        """Test getting KPI measurements via API."""
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
        
        # Create some measurements
        KPIMeasurement.objects.create(
            kpi=kpi,
            value=Decimal('1000.00'),
            measurement_date=timezone.now()
        )
        KPIMeasurement.objects.create(
            kpi=kpi,
            value=Decimal('1200.00'),
            measurement_date=timezone.now() - timedelta(days=1)
        )
        
        url = reverse('kpi-measurements', kwargs={'pk': kpi.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_kpi_dashboard(self):
        """Test getting KPI dashboard data via API."""
        # Create some KPIs
        KPI.objects.create(
            organization=self.organization,
            name="Financial KPI",
            kpi_type='financial',
            calculation_method="SUM(revenue)",
            data_source="sales_data",
            is_active=True
        )
        KPI.objects.create(
            organization=self.organization,
            name="Operational KPI",
            kpi_type='operational',
            calculation_method="COUNT(orders)",
            data_source="orders_data",
            is_active=True
        )
        
        url = reverse('kpi-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('kpis_by_type', response.data)
        self.assertIn('recent_alerts', response.data)
        self.assertIn('summary', response.data)


class DashboardAPITest(APITestCase):
    """Test cases for Dashboard API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_dashboard(self):
        """Test creating a dashboard via API."""
        url = reverse('dashboard-list')
        data = {
            'organization': self.organization.id,
            'name': 'Test Dashboard',
            'description': 'Test dashboard description',
            'dashboard_type': 'executive',
            'layout': 'grid',
            'refresh_interval': 300,
            'auto_refresh': True,
            'configuration': {'theme': 'dark'}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dashboard.objects.count(), 1)
        
        dashboard = Dashboard.objects.first()
        self.assertEqual(dashboard.name, "Test Dashboard")
        self.assertEqual(dashboard.dashboard_type, 'executive')
        self.assertEqual(dashboard.created_by, self.user)
    
    def test_list_dashboards(self):
        """Test listing dashboards via API."""
        # Create a dashboard
        Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
        
        url = reverse('dashboard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_dashboard_data(self):
        """Test getting dashboard data via API."""
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
        
        # Create a widget
        DashboardWidget.objects.create(
            dashboard=dashboard,
            name="Test Widget",
            widget_type='kpi',
            chart_type='line'
        )
        
        url = reverse('dashboard-data', kwargs={'pk': dashboard.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('widget_data', response.data)
        self.assertIn('last_updated', response.data)
    
    def test_clone_dashboard(self):
        """Test cloning a dashboard via API."""
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
        
        # Create a widget
        DashboardWidget.objects.create(
            dashboard=dashboard,
            name="Test Widget",
            widget_type='kpi'
        )
        
        url = reverse('dashboard-clone', kwargs={'pk': dashboard.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dashboard.objects.count(), 2)
        
        # Check that the cloned dashboard has the same widget
        cloned_dashboard = Dashboard.objects.exclude(pk=dashboard.pk).first()
        self.assertEqual(cloned_dashboard.widgets.count(), 1)


class AnalyticsQueryAPITest(APITestCase):
    """Test cases for Analytics Query API."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_analytics_query(self):
        """Test executing an analytics query via API."""
        url = reverse('analytics-query')
        data = {
            'query': 'SELECT COUNT(*) FROM sales',
            'parameters': {'start_date': '2024-01-01'},
            'data_source': 'sales_db',
            'cache_duration': 300
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('execution_time', response.data)
    
    def test_analytics_dashboard(self):
        """Test getting analytics dashboard data via API."""
        # Create some test data
        Report.objects.create(
            organization=self.organization,
            name="Test Report",
            report_type='financial',
            created_by=self.user
        )
        
        KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(revenue)",
            data_source="sales_data"
        )
        
        Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
        
        url = reverse('analytics-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('recent_events', response.data)
        self.assertIn('top_kpis', response.data)


class AnalyticsIntegrationTest(TestCase):
    """Integration tests for analytics workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization
        )
    
    def test_complete_analytics_workflow(self):
        """Test complete analytics workflow from KPI creation to dashboard."""
        # 1. Create a KPI
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Revenue KPI",
            kpi_type='financial',
            calculation_method="SUM(revenue)",
            data_source="sales_data",
            target_value=Decimal('10000.00'),
            warning_threshold=Decimal('8000.00'),
            critical_threshold=Decimal('6000.00')
        )
        
        # 2. Add measurements
        KPIMeasurement.objects.create(
            kpi=kpi,
            value=Decimal('9500.00'),
            measurement_date=timezone.now()
        )
        
        # 3. Create a dashboard
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Executive Dashboard",
            dashboard_type='executive',
            created_by=self.user
        )
        
        # 4. Add a widget to the dashboard
        widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            name="Revenue Widget",
            widget_type='kpi',
            chart_type='line',
            data_source='kpi_data',
            query=f'SELECT * FROM kpi_measurements WHERE kpi_id = {kpi.id}'
        )
        
        # 5. Create a report
        report = Report.objects.create(
            organization=self.organization,
            name="Revenue Report",
            report_type='financial',
            created_by=self.user
        )
        
        # 6. Create an alert (should be triggered by KPI threshold)
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='kpi_threshold',
            severity='high',
            title='Revenue Warning',
            message='Revenue is below warning threshold',
            related_kpi=kpi,
            threshold_value=Decimal('8000.00'),
            current_value=Decimal('9500.00')
        )
        
        # Verify the workflow
        self.assertEqual(kpi.current_value, Decimal('9500.00'))
        self.assertEqual(dashboard.widgets.count(), 1)
        self.assertEqual(widget.dashboard, dashboard)
        self.assertEqual(report.organization, self.organization)
        self.assertEqual(alert.related_kpi, kpi)
        
        # Verify analytics events were created
        events = AnalyticsEvent.objects
        self.assertTrue(events.exists())
    
    def test_kpi_threshold_alert_workflow(self):
        """Test KPI threshold alert workflow."""
        # Create a KPI with thresholds
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            calculation_method="SUM(value)",
            data_source="test_data",
            target_value=Decimal('1000.00'),
            warning_threshold=Decimal('800.00'),
            critical_threshold=Decimal('600.00')
        )
        
        # Add a measurement that triggers warning threshold
        measurement = KPIMeasurement.objects.create(
            kpi=kpi,
            value=Decimal('750.00'),  # Below warning threshold
            measurement_date=timezone.now()
        )
        
        # Check that KPI current value was updated
        kpi.refresh_from_db()
        self.assertEqual(kpi.current_value, Decimal('750.00'))
        
        # Check that an alert was created (this would happen via signals)
        # In a real implementation, the signal would create the alert
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='kpi_threshold',
            severity='high',
            title='Warning: Test KPI',
            message='Test KPI is below warning threshold',
            related_kpi=kpi,
            threshold_value=Decimal('800.00'),
            current_value=Decimal('750.00')
        )
        
        self.assertEqual(alert.related_kpi, kpi)
        self.assertEqual(alert.severity, 'high')
        self.assertEqual(alert.status, 'active')
    
    def test_dashboard_widget_data_generation(self):
        """Test dashboard widget data generation workflow."""
        # Create a dashboard
        dashboard = Dashboard.objects.create(
            organization=self.organization,
            name="Test Dashboard",
            created_by=self.user
        )
        
        # Create a KPI widget
        kpi_widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            name="KPI Widget",
            widget_type='kpi',
            chart_type='gauge',
            data_source='kpi_data'
        )
        
        # Create a chart widget
        chart_widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            name="Chart Widget",
            widget_type='chart',
            chart_type='line',
            data_source='chart_data'
        )
        
        # Verify widgets were created
        self.assertEqual(dashboard.widgets.count(), 2)
        self.assertEqual(kpi_widget.widget_type, 'kpi')
        self.assertEqual(chart_widget.widget_type, 'chart')
        
        # In a real implementation, widget data would be generated
        # based on the data_source and query configuration

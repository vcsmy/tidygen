"""
Comprehensive payroll management tests.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.core.models import User
from apps.hr.models import Employee, Department, Position, PayrollPeriod
from .models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile,
    PayrollRun, PayrollItem, PayrollAdjustment, TaxYear, EmployeeTaxInfo,
    PayrollReport, PayrollAnalytics, PayrollIntegration, PayrollWebhook,
    PayrollNotification
)

User = get_user_model()


class PayrollConfigurationModelTest(TestCase):
    """Test PayrollConfiguration model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.config = PayrollConfiguration.objects.create(
            organization=self.organization,
            currency="USD",
            pay_frequency="biweekly",
            tax_year=2024,
            federal_tax_rate=Decimal('0.22'),
            state_tax_rate=Decimal('0.05'),
            social_security_rate=Decimal('0.062'),
            medicare_rate=Decimal('0.0145')
        )
    
    def test_payroll_configuration_creation(self):
        """Test payroll configuration creation."""
        self.assertEqual(self.config.organization, self.organization)
        self.assertEqual(self.config.currency, "USD")
        self.assertEqual(self.config.pay_frequency, "biweekly")
        self.assertEqual(self.config.tax_year, 2024)
        self.assertEqual(self.config.federal_tax_rate, Decimal('0.22'))
        self.assertEqual(self.config.state_tax_rate, Decimal('0.05'))
        self.assertEqual(self.config.social_security_rate, Decimal('0.062'))
        self.assertEqual(self.config.medicare_rate, Decimal('0.0145'))
    
    def test_payroll_configuration_str(self):
        """Test payroll configuration string representation."""
        expected = f"Payroll Configuration - {self.organization.name} (2024)"
        self.assertEqual(str(self.config), expected)
    
    def test_payroll_configuration_validation(self):
        """Test payroll configuration validation."""
        # Test invalid tax rate
        with self.assertRaises(ValidationError):
            config = PayrollConfiguration(
                organization=self.organization,
                currency="USD",
                pay_frequency="biweekly",
                tax_year=2024,
                federal_tax_rate=Decimal('1.5')  # Invalid rate > 1
            )
            config.full_clean()


class PayrollComponentModelTest(TestCase):
    """Test PayrollComponent model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.component = PayrollComponent.objects.create(
            organization=self.organization,
            name="Regular Hours",
            component_type="earning",
            calculation_type="hours",
            amount=Decimal('25.00'),
            is_taxable=True,
            is_mandatory=True,
            sort_order=1
        )
    
    def test_payroll_component_creation(self):
        """Test payroll component creation."""
        self.assertEqual(self.component.organization, self.organization)
        self.assertEqual(self.component.name, "Regular Hours")
        self.assertEqual(self.component.component_type, "earning")
        self.assertEqual(self.component.calculation_type, "hours")
        self.assertEqual(self.component.amount, Decimal('25.00'))
        self.assertTrue(self.component.is_taxable)
        self.assertTrue(self.component.is_mandatory)
        self.assertEqual(self.component.sort_order, 1)
    
    def test_payroll_component_str(self):
        """Test payroll component string representation."""
        expected = f"Regular Hours - {self.organization.name}"
        self.assertEqual(str(self.component), expected)


class EmployeePayrollProfileModelTest(TestCase):
    """Test EmployeePayrollProfile model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=timezone.now().date()
        )
        self.profile = EmployeePayrollProfile.objects.create(
            employee=self.employee,
            pay_type="hourly",
            hourly_rate=Decimal('25.00'),
            federal_exemptions=2,
            state_exemptions=2,
            bank_name="Test Bank",
            bank_routing_number="123456789",
            bank_account_number="987654321"
        )
    
    def test_employee_payroll_profile_creation(self):
        """Test employee payroll profile creation."""
        self.assertEqual(self.profile.employee, self.employee)
        self.assertEqual(self.profile.pay_type, "hourly")
        self.assertEqual(self.profile.hourly_rate, Decimal('25.00'))
        self.assertEqual(self.profile.federal_exemptions, 2)
        self.assertEqual(self.profile.state_exemptions, 2)
        self.assertEqual(self.profile.bank_name, "Test Bank")
        self.assertEqual(self.profile.bank_routing_number, "123456789")
        self.assertEqual(self.profile.bank_account_number, "987654321")
    
    def test_employee_payroll_profile_str(self):
        """Test employee payroll profile string representation."""
        expected = f"Payroll Profile - {self.employee.full_name}"
        self.assertEqual(str(self.profile), expected)


class PayrollRunModelTest(TestCase):
    """Test PayrollRun model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="Test Period",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.run = PayrollRun.objects.create(
            organization=self.organization,
            payroll_period=self.period,
            run_name="Test Run",
            run_type="regular",
            status="draft"
        )
    
    def test_payroll_run_creation(self):
        """Test payroll run creation."""
        self.assertEqual(self.run.organization, self.organization)
        self.assertEqual(self.run.payroll_period, self.period)
        self.assertEqual(self.run.run_name, "Test Run")
        self.assertEqual(self.run.run_type, "regular")
        self.assertEqual(self.run.status, "draft")
    
    def test_payroll_run_str(self):
        """Test payroll run string representation."""
        expected = f"Test Run - {self.organization.name} ({self.period.name})"
        self.assertEqual(str(self.run), expected)


class PayrollItemModelTest(TestCase):
    """Test PayrollItem model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=timezone.now().date()
        )
        self.period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="Test Period",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.component = PayrollComponent.objects.create(
            organization=self.organization,
            name="Regular Hours",
            component_type="earning",
            calculation_type="hours",
            amount=Decimal('25.00'),
            is_taxable=True
        )
        self.run = PayrollRun.objects.create(
            organization=self.organization,
            payroll_period=self.period,
            run_name="Test Run",
            run_type="regular",
            status="draft"
        )
        self.item = PayrollItem.objects.create(
            payroll_run=self.run,
            component=self.component,
            item_type="earning",
            quantity=40,
            rate=Decimal('25.00'),
            amount=Decimal('1000.00'),
            is_taxable=True
        )
    
    def test_payroll_item_creation(self):
        """Test payroll item creation."""
        self.assertEqual(self.item.payroll_run, self.run)
        self.assertEqual(self.item.component, self.component)
        self.assertEqual(self.item.item_type, "earning")
        self.assertEqual(self.item.quantity, 40)
        self.assertEqual(self.item.rate, Decimal('25.00'))
        self.assertEqual(self.item.amount, Decimal('1000.00'))
        self.assertTrue(self.item.is_taxable)
    
    def test_payroll_item_str(self):
        """Test payroll item string representation."""
        expected = f"Regular Hours - {self.organization.name} - $1000.00"
        self.assertEqual(str(self.item), expected)


class PayrollAdjustmentModelTest(TestCase):
    """Test PayrollAdjustment model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=timezone.now().date()
        )
        self.period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="Test Period",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.run = PayrollRun.objects.create(
            organization=self.organization,
            payroll_period=self.period,
            run_name="Test Run",
            run_type="regular",
            status="draft"
        )
        self.adjustment = PayrollAdjustment.objects.create(
            payroll_run=self.run,
            adjustment_type="bonus",
            amount=Decimal('500.00'),
            is_positive=True,
            is_taxable=True,
            reason="Performance bonus"
        )
    
    def test_payroll_adjustment_creation(self):
        """Test payroll adjustment creation."""
        self.assertEqual(self.adjustment.payroll_run, self.run)
        self.assertEqual(self.adjustment.adjustment_type, "bonus")
        self.assertEqual(self.adjustment.amount, Decimal('500.00'))
        self.assertTrue(self.adjustment.is_positive)
        self.assertTrue(self.adjustment.is_taxable)
        self.assertEqual(self.adjustment.reason, "Performance bonus")
    
    def test_payroll_adjustment_str(self):
        """Test payroll adjustment string representation."""
        expected = f"Bonus - {self.organization.name} - $500.00"
        self.assertEqual(str(self.adjustment), expected)


class TaxYearModelTest(TestCase):
    """Test TaxYear model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.tax_year = TaxYear.objects.create(
            organization=self.organization,
            year=2024,
            federal_tax_rate=Decimal('0.22'),
            state_tax_rate=Decimal('0.05'),
            social_security_rate=Decimal('0.062'),
            medicare_rate=Decimal('0.0145'),
            is_active=True
        )
    
    def test_tax_year_creation(self):
        """Test tax year creation."""
        self.assertEqual(self.tax_year.organization, self.organization)
        self.assertEqual(self.tax_year.year, 2024)
        self.assertEqual(self.tax_year.federal_tax_rate, Decimal('0.22'))
        self.assertEqual(self.tax_year.state_tax_rate, Decimal('0.05'))
        self.assertEqual(self.tax_year.social_security_rate, Decimal('0.062'))
        self.assertEqual(self.tax_year.medicare_rate, Decimal('0.0145'))
        self.assertTrue(self.tax_year.is_active)
    
    def test_tax_year_str(self):
        """Test tax year string representation."""
        expected = f"2024 - {self.organization.name}"
        self.assertEqual(str(self.tax_year), expected)


class EmployeeTaxInfoModelTest(TestCase):
    """Test EmployeeTaxInfo model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=timezone.now().date()
        )
        self.tax_info = EmployeeTaxInfo.objects.create(
            employee=self.employee,
            tax_year=2024,
            filing_status="single",
            federal_exemptions=2,
            state_exemptions=2,
            additional_federal_withholding=Decimal('50.00'),
            additional_state_withholding=Decimal('25.00')
        )
    
    def test_employee_tax_info_creation(self):
        """Test employee tax info creation."""
        self.assertEqual(self.tax_info.employee, self.employee)
        self.assertEqual(self.tax_info.tax_year, 2024)
        self.assertEqual(self.tax_info.filing_status, "single")
        self.assertEqual(self.tax_info.federal_exemptions, 2)
        self.assertEqual(self.tax_info.state_exemptions, 2)
        self.assertEqual(self.tax_info.additional_federal_withholding, Decimal('50.00'))
        self.assertEqual(self.tax_info.additional_state_withholding, Decimal('25.00'))
    
    def test_employee_tax_info_str(self):
        """Test employee tax info string representation."""
        expected = f"Tax Info - {self.employee.full_name} (2024)"
        self.assertEqual(str(self.tax_info), expected)


class PayrollReportModelTest(TestCase):
    """Test PayrollReport model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.report = PayrollReport.objects.create(
            organization=self.organization,
            report_name="Test Report",
            report_type="summary",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            status="draft"
        )
    
    def test_payroll_report_creation(self):
        """Test payroll report creation."""
        self.assertEqual(self.report.organization, self.organization)
        self.assertEqual(self.report.report_name, "Test Report")
        self.assertEqual(self.report.report_type, "summary")
        self.assertEqual(self.report.status, "draft")
    
    def test_payroll_report_str(self):
        """Test payroll report string representation."""
        expected = f"Test Report - {self.organization.name}"
        self.assertEqual(str(self.report), expected)


class PayrollAnalyticsModelTest(TestCase):
    """Test PayrollAnalytics model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.analytics = PayrollAnalytics.objects.create(
            organization=self.organization,
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timezone.timedelta(days=30),
            period_type="monthly",
            total_employees=10,
            total_gross_pay=Decimal('50000.00'),
            total_net_pay=Decimal('40000.00'),
            total_taxes=Decimal('8000.00'),
            total_benefits=Decimal('2000.00')
        )
    
    def test_payroll_analytics_creation(self):
        """Test payroll analytics creation."""
        self.assertEqual(self.analytics.organization, self.organization)
        self.assertEqual(self.analytics.period_type, "monthly")
        self.assertEqual(self.analytics.total_employees, 10)
        self.assertEqual(self.analytics.total_gross_pay, Decimal('50000.00'))
        self.assertEqual(self.analytics.total_net_pay, Decimal('40000.00'))
        self.assertEqual(self.analytics.total_taxes, Decimal('8000.00'))
        self.assertEqual(self.analytics.total_benefits, Decimal('2000.00'))
    
    def test_payroll_analytics_str(self):
        """Test payroll analytics string representation."""
        expected = f"Analytics - {self.organization.name} (Monthly)"
        self.assertEqual(str(self.analytics), expected)


class PayrollIntegrationModelTest(TestCase):
    """Test PayrollIntegration model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.integration = PayrollIntegration.objects.create(
            organization=self.organization,
            integration_name="Test Integration",
            integration_type="accounting",
            provider_name="Test Provider",
            provider_url="https://testprovider.com",
            is_active=True,
            sync_status="connected"
        )
    
    def test_payroll_integration_creation(self):
        """Test payroll integration creation."""
        self.assertEqual(self.integration.organization, self.organization)
        self.assertEqual(self.integration.integration_name, "Test Integration")
        self.assertEqual(self.integration.integration_type, "accounting")
        self.assertEqual(self.integration.provider_name, "Test Provider")
        self.assertEqual(self.integration.provider_url, "https://testprovider.com")
        self.assertTrue(self.integration.is_active)
        self.assertEqual(self.integration.sync_status, "connected")
    
    def test_payroll_integration_str(self):
        """Test payroll integration string representation."""
        expected = f"Test Integration - {self.organization.name}"
        self.assertEqual(str(self.integration), expected)


class PayrollWebhookModelTest(TestCase):
    """Test PayrollWebhook model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.integration = PayrollIntegration.objects.create(
            organization=self.organization,
            integration_name="Test Integration",
            integration_type="accounting",
            provider_name="Test Provider",
            is_active=True
        )
        self.webhook = PayrollWebhook.objects.create(
            organization=self.organization,
            integration=self.integration,
            event_type="payroll_processed",
            webhook_url="https://example.com/webhook",
            is_active=True
        )
    
    def test_payroll_webhook_creation(self):
        """Test payroll webhook creation."""
        self.assertEqual(self.webhook.organization, self.organization)
        self.assertEqual(self.webhook.integration, self.integration)
        self.assertEqual(self.webhook.event_type, "payroll_processed")
        self.assertEqual(self.webhook.webhook_url, "https://example.com/webhook")
        self.assertTrue(self.webhook.is_active)
    
    def test_payroll_webhook_str(self):
        """Test payroll webhook string representation."""
        expected = f"payroll_processed - {self.organization.name}"
        self.assertEqual(str(self.webhook), expected)


class PayrollNotificationModelTest(TestCase):
    """Test PayrollNotification model."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.notification = PayrollNotification.objects.create(
            organization=self.organization,
            notification_type="payroll_processed",
            subject="Payroll Processed",
            message="Payroll has been processed successfully",
            delivery_method="email",
            status="pending"
        )
    
    def test_payroll_notification_creation(self):
        """Test payroll notification creation."""
        self.assertEqual(self.notification.organization, self.organization)
        self.assertEqual(self.notification.notification_type, "payroll_processed")
        self.assertEqual(self.notification.subject, "Payroll Processed")
        self.assertEqual(self.notification.message, "Payroll has been processed successfully")
        self.assertEqual(self.notification.delivery_method, "email")
        self.assertEqual(self.notification.status, "pending")
    
    def test_payroll_notification_str(self):
        """Test payroll notification string representation."""
        expected = f"Payroll Processed - {self.organization.name}"
        self.assertEqual(str(self.notification), expected)


class PayrollModelIntegrationTest(TestCase):
    """Integration tests for payroll models."""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            organization=self.organization,
            employee_id="EMP001",
            hire_date=timezone.now().date()
        )
        self.period = PayrollPeriod.objects.create(
            organization=self.organization,
            name="Test Period",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        self.config = PayrollConfiguration.objects.create(
            organization=self.organization,
            currency="USD",
            pay_frequency="biweekly",
            tax_year=2024
        )
        self.component = PayrollComponent.objects.create(
            organization=self.organization,
            name="Regular Hours",
            component_type="earning",
            calculation_type="hours",
            amount=Decimal('25.00'),
            is_taxable=True
        )
        self.profile = EmployeePayrollProfile.objects.create(
            employee=self.employee,
            pay_type="hourly",
            hourly_rate=Decimal('25.00')
        )
    
    def test_payroll_workflow(self):
        """Test complete payroll workflow."""
        # Create payroll run
        run = PayrollRun.objects.create(
            organization=self.organization,
            payroll_period=self.period,
            run_name="Test Run",
            run_type="regular",
            status="draft"
        )
        
        # Create payroll item
        item = PayrollItem.objects.create(
            payroll_run=run,
            component=self.component,
            item_type="earning",
            quantity=40,
            rate=Decimal('25.00'),
            amount=Decimal('1000.00'),
            is_taxable=True
        )
        
        # Create adjustment
        adjustment = PayrollAdjustment.objects.create(
            payroll_run=run,
            adjustment_type="bonus",
            amount=Decimal('500.00'),
            is_positive=True,
            is_taxable=True,
            reason="Performance bonus"
        )
        
        # Verify relationships
        self.assertEqual(item.payroll_run, run)
        self.assertEqual(adjustment.payroll_run, run)
        self.assertEqual(run.organization, self.organization)
        self.assertEqual(run.payroll_period, self.period)
    
    def test_payroll_calculations(self):
        """Test payroll calculations."""
        # Create payroll run
        run = PayrollRun.objects.create(
            organization=self.organization,
            payroll_period=self.period,
            run_name="Test Run",
            run_type="regular",
            status="draft"
        )
        
        # Create earning item
        earning_item = PayrollItem.objects.create(
            payroll_run=run,
            component=self.component,
            item_type="earning",
            quantity=40,
            rate=Decimal('25.00'),
            amount=Decimal('1000.00'),
            is_taxable=True
        )
        
        # Create deduction component
        deduction_component = PayrollComponent.objects.create(
            organization=self.organization,
            name="Federal Tax",
            component_type="deduction",
            calculation_type="percentage",
            percentage=Decimal('0.22'),
            is_taxable=False
        )
        
        # Create deduction item
        deduction_item = PayrollItem.objects.create(
            payroll_run=run,
            component=deduction_component,
            item_type="deduction",
            quantity=1,
            rate=Decimal('220.00'),
            amount=Decimal('220.00'),
            is_taxable=False
        )
        
        # Verify calculations
        self.assertEqual(earning_item.amount, Decimal('1000.00'))
        self.assertEqual(deduction_item.amount, Decimal('220.00'))
        
        # Test total calculations
        total_earnings = sum(item.amount for item in run.payroll_items.filter(item_type='earning'))
        total_deductions = sum(item.amount for item in run.payroll_items.filter(item_type='deduction'))
        net_pay = total_earnings - total_deductions
        
        self.assertEqual(total_earnings, Decimal('1000.00'))
        self.assertEqual(total_deductions, Decimal('220.00'))
        self.assertEqual(net_pay, Decimal('780.00'))
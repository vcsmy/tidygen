"""
Comprehensive payroll management signals for automated operations.
"""
import logging
from decimal import Decimal
from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from apps.core.models import User
from apps.hr.models import Employee, PayrollPeriod
from .models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile,
    PayrollRun, PayrollItem, PayrollAdjustment, TaxYear, EmployeeTaxInfo,
    PayrollReport, PayrollAnalytics, PayrollIntegration, PayrollWebhook,
    PayrollNotification
)

logger = logging.getLogger(__name__)


# ==================== PAYROLL CONFIGURATION SIGNALS ====================

@receiver(post_save, sender=PayrollConfiguration)
def payroll_configuration_created(sender, instance, created, **kwargs):
    """Handle payroll configuration creation."""
    if created:
        logger.info(f"New payroll configuration created")
        
        # Note: PayrollConfiguration doesn't have organization field
        # Skip organization-dependent operations
        
        # Create default payroll components
        # create_default_payroll_components(instance)
        
        # Note: TaxYear creation requires organization context, skipping for now
        # current_year = timezone.now().year
        # TaxYear.objects.get_or_create(
        #     organization=instance.organization,
        #     year=current_year,
        #     defaults={
        #         'federal_tax_rate': instance.federal_tax_rate,
        #         'state_tax_rate': instance.state_tax_rate,
        #         'social_security_rate': instance.social_security_rate,
        #         'medicare_rate': instance.medicare_rate,
        #         'is_active': True
        #     }
        # )


def create_default_payroll_components(config):
    """Create default payroll components for a new configuration."""
    default_components = [
        # Earnings
        {'name': 'Regular Hours', 'component_type': 'earning', 'calculation_type': 'hours', 'is_taxable': True, 'is_mandatory': True},
        {'name': 'Overtime Hours', 'component_type': 'earning', 'calculation_type': 'hours', 'is_taxable': True, 'is_mandatory': True},
        {'name': 'Holiday Pay', 'component_type': 'earning', 'calculation_type': 'hours', 'is_taxable': True, 'is_mandatory': True},
        {'name': 'Vacation Pay', 'component_type': 'earning', 'calculation_type': 'hours', 'is_taxable': True, 'is_mandatory': True},
        {'name': 'Sick Pay', 'component_type': 'earning', 'calculation_type': 'hours', 'is_taxable': True, 'is_mandatory': True},
        {'name': 'Bonus', 'component_type': 'earning', 'calculation_type': 'fixed', 'is_taxable': True, 'is_mandatory': False},
        {'name': 'Commission', 'component_type': 'earning', 'calculation_type': 'percentage', 'is_taxable': True, 'is_mandatory': False},
        
        # Deductions
        {'name': 'Federal Tax', 'component_type': 'deduction', 'calculation_type': 'percentage', 'is_taxable': False, 'is_mandatory': True},
        {'name': 'State Tax', 'component_type': 'deduction', 'calculation_type': 'percentage', 'is_taxable': False, 'is_mandatory': True},
        {'name': 'Social Security', 'component_type': 'deduction', 'calculation_type': 'percentage', 'is_taxable': False, 'is_mandatory': True},
        {'name': 'Medicare', 'component_type': 'deduction', 'calculation_type': 'percentage', 'is_taxable': False, 'is_mandatory': True},
        {'name': 'Health Insurance', 'component_type': 'deduction', 'calculation_type': 'fixed', 'is_taxable': False, 'is_pretax': True, 'is_mandatory': False},
        {'name': 'Dental Insurance', 'component_type': 'deduction', 'calculation_type': 'fixed', 'is_taxable': False, 'is_pretax': True, 'is_mandatory': False},
        {'name': 'Vision Insurance', 'component_type': 'deduction', 'calculation_type': 'fixed', 'is_taxable': False, 'is_pretax': True, 'is_mandatory': False},
        {'name': '401(k) Contribution', 'component_type': 'deduction', 'calculation_type': 'percentage', 'is_taxable': False, 'is_pretax': True, 'is_mandatory': False},
    ]
    
    for i, component_data in enumerate(default_components):
        PayrollComponent.objects.get_or_create(
            organization=config.organization,
            name=component_data['name'],
            defaults={
                'component_type': component_data['component_type'],
                'calculation_type': component_data['calculation_type'],
                'is_taxable': component_data.get('is_taxable', False),
                'is_pretax': component_data.get('is_pretax', False),
                'is_mandatory': component_data.get('is_mandatory', False),
                'sort_order': i + 1,
                'is_active': True
            }
        )


# ==================== EMPLOYEE PAYROLL PROFILE SIGNALS ====================

@receiver(post_save, sender=EmployeePayrollProfile)
def employee_payroll_profile_created(sender, instance, created, **kwargs):
    """Handle employee payroll profile creation."""
    if created:
        logger.info(f"New payroll profile created for {instance.employee.full_name}")
        
        # Create tax info for current year
        current_year = timezone.now().year
        EmployeeTaxInfo.objects.get_or_create(
            employee=instance.employee,
            tax_year=current_year,
            defaults={
                'federal_exemptions': instance.federal_exemptions,
                'state_exemptions': instance.state_exemptions,
                'additional_federal_withholding': instance.additional_federal_withholding,
                'additional_state_withholding': instance.additional_state_withholding
            }
        )


@receiver(pre_save, sender=EmployeePayrollProfile)
def employee_payroll_profile_pre_save(sender, instance, **kwargs):
    """Handle employee payroll profile pre-save operations."""
    # Validate bank account information
    if instance.bank_routing_number and len(instance.bank_routing_number) != 9:
        logger.warning(f"Invalid routing number for {instance.employee.full_name}")
    
    # Validate account number
    if instance.bank_account_number and len(instance.bank_account_number) < 4:
        logger.warning(f"Invalid account number for {instance.employee.full_name}")


# ==================== PAYROLL RUN SIGNALS ====================

@receiver(post_save, sender=PayrollRun)
def payroll_run_created(sender, instance, created, **kwargs):
    """Handle payroll run creation."""
    if created:
        logger.info(f"New payroll run created: {instance.run_name}")
        
        # Generate payroll items for all active employees
        generate_payroll_items(instance)
        
        # Send notification to HR
        if instance.organization.payroll_config.notify_hr:
            send_payroll_notification(
                instance,
                'payroll_run_created',
                f"New payroll run '{instance.run_name}' has been created"
            )


@receiver(pre_save, sender=PayrollRun)
def payroll_run_pre_save(sender, instance, **kwargs):
    """Handle payroll run pre-save operations."""
    # Calculate totals if not already calculated
    if instance.status in ['draft', 'processing']:
        calculate_payroll_totals(instance)


def generate_payroll_items(payroll_run):
    """Generate payroll items for all active employees in the period."""
    active_employees = Employee.objects.filter(
        organization=payroll_run.organization,
        is_active=True,
        payroll_profile__is_active=True
    )
    
    for employee in active_employees:
        # Create payroll record for employee
        from .models import Payroll
        payroll, created = Payroll.objects.get_or_create(
            employee=employee,
            payroll_period=payroll_run.payroll_period,
            defaults={
                'status': 'draft',
                'gross_pay': Decimal('0.00'),
                'net_pay': Decimal('0.00')
            }
        )
        
        # Generate items based on employee's payroll profile
        generate_employee_payroll_items(payroll, payroll_run)


def generate_employee_payroll_items(payroll, payroll_run):
    """Generate payroll items for a specific employee."""
    profile = payroll.employee.payroll_profile
    
    # Regular hours
    if profile.pay_type == 'hourly':
        regular_hours = 40  # Default 40 hours per week
        hourly_rate = profile.hourly_rate
        
        PayrollItem.objects.get_or_create(
            payroll=payroll,
            payroll_run=payroll_run,
            component=PayrollComponent.objects.get(
                organization=payroll.employee.organization,
                name='Regular Hours'
            ),
            defaults={
                'item_type': 'earning',
                'quantity': regular_hours,
                'rate': hourly_rate,
                'amount': regular_hours * hourly_rate,
                'is_taxable': True
            }
        )
    elif profile.pay_type == 'salary':
        # Salary is typically paid in full for the period
        PayrollItem.objects.get_or_create(
            payroll=payroll,
            payroll_run=payroll_run,
            component=PayrollComponent.objects.get(
                organization=payroll.employee.organization,
                name='Regular Hours'
            ),
            defaults={
                'item_type': 'earning',
                'quantity': 1,
                'rate': profile.base_salary,
                'amount': profile.base_salary,
                'is_taxable': True
            }
        )


def calculate_payroll_totals(payroll_run):
    """Calculate totals for a payroll run."""
    items = PayrollItem.objects.filter(payroll_run=payroll_run)
    
    total_gross = sum(item.amount for item in items if item.item_type == 'earning')
    total_deductions = sum(item.amount for item in items if item.item_type == 'deduction')
    total_taxes = sum(item.amount for item in items if item.component.component_type == 'tax')
    total_net = total_gross - total_deductions
    
    payroll_run.total_gross_pay = total_gross
    payroll_run.total_deductions = total_deductions
    payroll_run.total_taxes = total_taxes
    payroll_run.total_net_pay = total_net
    payroll_run.total_employees = items.values('payroll__employee').distinct().count()


# ==================== PAYROLL ITEM SIGNALS ====================

@receiver(post_save, sender=PayrollItem)
def payroll_item_created(sender, instance, created, **kwargs):
    """Handle payroll item creation."""
    if created:
        logger.info(f"New payroll item created for {instance.payroll.employee.full_name}")
        
        # Update payroll totals
        update_payroll_totals(instance.payroll)


@receiver(post_delete, sender=PayrollItem)
def payroll_item_deleted(sender, instance, **kwargs):
    """Handle payroll item deletion."""
    logger.info(f"Payroll item deleted for {instance.payroll.employee.full_name}")
    
    # Update payroll totals
    update_payroll_totals(instance.payroll)


def update_payroll_totals(payroll):
    """Update totals for a payroll record."""
    items = PayrollItem.objects.filter(payroll=payroll)
    
    gross_pay = sum(item.amount for item in items if item.item_type == 'earning')
    deductions = sum(item.amount for item in items if item.item_type == 'deduction')
    net_pay = gross_pay - deductions
    
    payroll.gross_pay = gross_pay
    payroll.deductions = deductions
    payroll.net_pay = net_pay
    payroll.save(update_fields=['gross_pay', 'deductions', 'net_pay'])


# ==================== PAYROLL ADJUSTMENT SIGNALS ====================

@receiver(post_save, sender=PayrollAdjustment)
def payroll_adjustment_created(sender, instance, created, **kwargs):
    """Handle payroll adjustment creation."""
    if created:
        logger.info(f"New payroll adjustment created for {instance.payroll.employee.full_name}")
        
        # Update payroll totals
        update_payroll_totals(instance.payroll)
        
        # Send notification if adjustment requires approval
        if not instance.approved_at:
            send_payroll_notification(
                instance.payroll,
                'adjustment_requires_approval',
                f"Payroll adjustment requires approval for {instance.payroll.employee.full_name}"
            )


@receiver(pre_save, sender=PayrollAdjustment)
def payroll_adjustment_pre_save(sender, instance, **kwargs):
    """Handle payroll adjustment pre-save operations."""
    # Set approval timestamp if approved
    if instance.approved_by and not instance.approved_at:
        instance.approved_at = timezone.now()


# ==================== TAX YEAR SIGNALS ====================

@receiver(post_save, sender=TaxYear)
def tax_year_created(sender, instance, created, **kwargs):
    """Handle tax year creation."""
    if created:
        logger.info(f"New tax year created: {instance.year}")
        
        # Create tax info for all active employees
        create_employee_tax_info_for_year(instance)


def create_employee_tax_info_for_year(tax_year):
    """Create tax info for all active employees for a new tax year."""
    active_employees = Employee.objects.filter(
        organization=tax_year.organization,
        is_active=True
    )
    
    for employee in active_employees:
        EmployeeTaxInfo.objects.get_or_create(
            employee=employee,
            tax_year=tax_year.year,
            defaults={
                'federal_exemptions': 1,  # Default exemptions
                'state_exemptions': 1,
                'filing_status': 'single'
            }
        )


# ==================== EMPLOYEE TAX INFO SIGNALS ====================

@receiver(post_save, sender=EmployeeTaxInfo)
def employee_tax_info_updated(sender, instance, created, **kwargs):
    """Handle employee tax info updates."""
    if not created:
        logger.info(f"Tax info updated for {instance.employee.full_name} for year {instance.tax_year}")
        
        # Recalculate payroll for current period if needed
        recalculate_current_payroll(instance.employee)


def recalculate_current_payroll(employee):
    """Recalculate payroll for current period based on updated tax info."""
    current_period = PayrollPeriod.objects.filter(
        organization=employee.organization,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()
    
    if current_period:
        payroll = Payroll.objects.filter(
            employee=employee,
            payroll_period=current_period
        ).first()
        
        if payroll:
            # Recalculate tax deductions
            recalculate_tax_deductions(payroll)


def recalculate_tax_deductions(payroll):
    """Recalculate tax deductions for a payroll record."""
    tax_info = EmployeeTaxInfo.objects.filter(
        employee=payroll.employee,
        tax_year=timezone.now().year
    ).first()
    
    if tax_info:
        # Update federal tax deduction
        federal_tax_item = PayrollItem.objects.filter(
            payroll=payroll,
            component__name='Federal Tax'
        ).first()
        
        if federal_tax_item:
            # Calculate federal tax based on gross pay and exemptions
            gross_pay = payroll.gross_pay
            federal_tax = calculate_federal_tax(gross_pay, tax_info.federal_exemptions)
            federal_tax_item.amount = federal_tax
            federal_tax_item.save()


def calculate_federal_tax(gross_pay, exemptions):
    """Calculate federal tax based on gross pay and exemptions."""
    # Simplified federal tax calculation
    # In a real system, this would use the official tax tables
    standard_deduction = 12550  # 2021 standard deduction
    exemption_amount = 4300 * exemptions  # 2021 exemption amount
    
    taxable_income = max(0, gross_pay - standard_deduction - exemption_amount)
    
    if taxable_income <= 9950:
        return taxable_income * Decimal('0.10')
    elif taxable_income <= 40525:
        return 995 + (taxable_income - 9950) * Decimal('0.12')
    elif taxable_income <= 86375:
        return 4664 + (taxable_income - 40525) * Decimal('0.22')
    else:
        return 14751 + (taxable_income - 86375) * Decimal('0.24')


# ==================== PAYROLL REPORT SIGNALS ====================

@receiver(post_save, sender=PayrollReport)
def payroll_report_created(sender, instance, created, **kwargs):
    """Handle payroll report creation."""
    if created:
        logger.info(f"New payroll report created: {instance.report_name}")
        
        # Generate report data
        generate_report_data(instance)


def generate_report_data(report):
    """Generate data for a payroll report."""
    # This would contain the actual report generation logic
    # For now, we'll just log the report creation
    logger.info(f"Generating report data for {report.report_name}")


# ==================== PAYROLL ANALYTICS SIGNALS ====================

@receiver(post_save, sender=PayrollAnalytics)
def payroll_analytics_created(sender, instance, created, **kwargs):
    """Handle payroll analytics creation."""
    if created:
        logger.info(f"New payroll analytics created for period {instance.period_start} to {instance.period_end}")
        
        # Calculate analytics metrics
        calculate_analytics_metrics(instance)


def calculate_analytics_metrics(analytics):
    """Calculate analytics metrics for a period."""
    # This would contain the actual analytics calculation logic
    # For now, we'll just log the analytics creation
    logger.info(f"Calculating analytics metrics for period {analytics.period_start} to {analytics.period_end}")


# ==================== PAYROLL INTEGRATION SIGNALS ====================

@receiver(post_save, sender=PayrollIntegration)
def payroll_integration_created(sender, instance, created, **kwargs):
    """Handle payroll integration creation."""
    if created:
        logger.info(f"New payroll integration created: {instance.integration_name}")
        
        # Test integration connection
        test_integration_connection(instance)


def test_integration_connection(integration):
    """Test connection to payroll integration."""
    # This would contain the actual connection testing logic
    # For now, we'll just log the integration creation
    logger.info(f"Testing connection for integration {integration.integration_name}")


# ==================== PAYROLL WEBHOOK SIGNALS ====================

@receiver(post_save, sender=PayrollWebhook)
def payroll_webhook_created(sender, instance, created, **kwargs):
    """Handle payroll webhook creation."""
    if created:
        logger.info(f"New payroll webhook created: {instance.event_type}")
        
        # Test webhook endpoint
        test_webhook_endpoint(instance)


def test_webhook_endpoint(webhook):
    """Test webhook endpoint."""
    # This would contain the actual webhook testing logic
    # For now, we'll just log the webhook creation
    logger.info(f"Testing webhook endpoint for {webhook.event_type}")


# ==================== PAYROLL NOTIFICATION SIGNALS ====================

@receiver(post_save, sender=PayrollNotification)
def payroll_notification_created(sender, instance, created, **kwargs):
    """Handle payroll notification creation."""
    if created:
        logger.info(f"New payroll notification created: {instance.notification_type}")
        
        # Send notification if it's immediate
        if instance.delivery_method == 'immediate':
            send_notification(instance)


def send_notification(notification):
    """Send a payroll notification."""
    try:
        if notification.delivery_method == 'email':
            send_email_notification(notification)
        elif notification.delivery_method == 'sms':
            send_sms_notification(notification)
        elif notification.delivery_method == 'push':
            send_push_notification(notification)
        
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        notification.status = 'failed'
        notification.save()


def send_email_notification(notification):
    """Send email notification."""
    subject = notification.subject
    message = notification.message
    
    # Get recipient emails
    recipient_emails = []
    for recipient in notification.recipients.all():
        if recipient.email:
            recipient_emails.append(recipient.email)
    
    if recipient_emails:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_emails,
            fail_silently=False
        )


def send_sms_notification(notification):
    """Send SMS notification."""
    # This would integrate with an SMS service like Twilio
    logger.info(f"Sending SMS notification: {notification.subject}")


def send_push_notification(notification):
    """Send push notification."""
    # This would integrate with a push notification service
    logger.info(f"Sending push notification: {notification.subject}")


# ==================== UTILITY FUNCTIONS ====================

def send_payroll_notification(payroll_object, notification_type, message):
    """Send a payroll-related notification."""
    try:
        PayrollNotification.objects.create(
            organization=payroll_object.organization,
            notification_type=notification_type,
            subject=f"Payroll Notification: {notification_type.replace('_', ' ').title()}",
            message=message,
            delivery_method='email',
            status='pending',
            scheduled_at=timezone.now()
        )
    except Exception as e:
        logger.error(f"Failed to create payroll notification: {e}")


# ==================== M2M SIGNAL HANDLERS ====================

# Note: M2M signal handlers are commented out due to Django's deferred attribute handling
# These would need to be implemented differently in a production environment

# @receiver(m2m_changed, sender=PayrollReport.departments.through)
# def payroll_report_departments_changed(sender, instance, action, **kwargs):
#     """Handle changes to payroll report departments."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Payroll report departments changed for {instance.report_name}")


# @receiver(m2m_changed, sender=PayrollReport.employees.through)
# def payroll_report_employees_changed(sender, instance, action, **kwargs):
#     """Handle changes to payroll report employees."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Payroll report employees changed for {instance.report_name}")


# @receiver(m2m_changed, sender=PayrollReport.payroll_periods.through)
# def payroll_report_periods_changed(sender, instance, action, **kwargs):
#     """Handle changes to payroll report periods."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Payroll report periods changed for {instance.report_name}")


# @receiver(m2m_changed, sender=PayrollNotification.recipients.through)
# def payroll_notification_recipients_changed(sender, instance, action, **kwargs):
#     """Handle changes to payroll notification recipients."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Payroll notification recipients changed for {instance.notification_type}")
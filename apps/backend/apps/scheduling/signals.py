"""
Comprehensive scheduling management signals for automated operations.
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
from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)

logger = logging.getLogger(__name__)


# ==================== SCHEDULE TEMPLATE SIGNALS ====================

@receiver(post_save, sender=ScheduleTemplate)
def schedule_template_created(sender, instance, created, **kwargs):
    """Handle schedule template creation."""
    if created:
        logger.info(f"New schedule template created: {instance.name}")
        
        # If this is set as default, unset other defaults
        if instance.is_default:
            ScheduleTemplate.objects.filter(
                organization=instance.organization,
                is_default=True
            ).exclude(id=instance.id).update(is_default=False)


@receiver(pre_save, sender=ScheduleTemplate)
def schedule_template_pre_save(sender, instance, **kwargs):
    """Handle schedule template pre-save operations."""
    # Validate time settings
    if instance.end_time and instance.start_time:
        if instance.end_time <= instance.start_time:
            logger.warning(f"Invalid time range for template {instance.name}")
    
    # Calculate duration if not set
    if not instance.duration_minutes and instance.start_time and instance.end_time:
        start_minutes = instance.start_time.hour * 60 + instance.start_time.minute
        end_minutes = instance.end_time.hour * 60 + instance.end_time.minute
        instance.duration_minutes = end_minutes - start_minutes


# ==================== RESOURCE SIGNALS ====================

@receiver(post_save, sender=Resource)
def resource_created(sender, instance, created, **kwargs):
    """Handle resource creation."""
    if created:
        logger.info(f"New resource created: {instance.name}")
        
        # Set default availability schedule if not provided
        if not instance.specifications:
            instance.specifications = {
                'features': [],
                'amenities': [],
                'notes': ''
            }
            instance.save()


@receiver(pre_save, sender=Resource)
def resource_pre_save(sender, instance, **kwargs):
    """Handle resource pre-save operations."""
    # Validate capacity
    if instance.capacity <= 0:
        logger.warning(f"Invalid capacity for resource {instance.name}")
    
    # Check maintenance schedule
    if instance.next_maintenance and instance.next_maintenance <= timezone.now():
        logger.warning(f"Resource {instance.name} has overdue maintenance")


# ==================== TEAM SIGNALS ====================

@receiver(post_save, sender=Team)
def team_created(sender, instance, created, **kwargs):
    """Handle team creation."""
    if created:
        logger.info(f"New team created: {instance.name}")
        
        # Set default availability schedule if not provided
        if not instance.availability_schedule:
            instance.availability_schedule = {
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'},
                'wednesday': {'start': '09:00', 'end': '17:00'},
                'thursday': {'start': '09:00', 'end': '17:00'},
                'friday': {'start': '09:00', 'end': '17:00'},
                'saturday': {'start': '10:00', 'end': '14:00'},
                'sunday': {'start': '10:00', 'end': '14:00'}
            }
            instance.save()


@receiver(post_save, sender=TeamMember)
def team_member_created(sender, instance, created, **kwargs):
    """Handle team member creation."""
    if created:
        logger.info(f"New team member added: {instance.user.get_full_name()} to {instance.team.name}")
        
        # Set default availability schedule if not provided
        if not instance.availability_schedule:
            instance.availability_schedule = instance.team.availability_schedule
            instance.save()


# ==================== APPOINTMENT SIGNALS ====================

@receiver(post_save, sender=Appointment)
def appointment_created(sender, instance, created, **kwargs):
    """Handle appointment creation."""
    if created:
        logger.info(f"New appointment created: {instance.title}")
        
        # Check for conflicts
        check_appointment_conflicts(instance)
        
        # Set reminder if not set
        if not instance.reminder_datetime:
            # Set reminder 24 hours before appointment
            instance.reminder_datetime = instance.start_datetime - timezone.timedelta(hours=24)
            instance.save()
        
        # Send creation notification
        send_appointment_notification(instance, 'appointment_created')


@receiver(pre_save, sender=Appointment)
def appointment_pre_save(sender, instance, **kwargs):
    """Handle appointment pre-save operations."""
    # Calculate duration if not set
    if not instance.duration_minutes and instance.start_datetime and instance.end_datetime:
        duration = instance.end_datetime - instance.start_datetime
        instance.duration_minutes = int(duration.total_seconds() / 60)
    
    # Validate datetime range
    if instance.end_datetime and instance.start_datetime:
        if instance.end_datetime <= instance.start_datetime:
            logger.warning(f"Invalid datetime range for appointment {instance.title}")


@receiver(post_save, sender=Appointment)
def appointment_updated(sender, instance, created, **kwargs):
    """Handle appointment updates."""
    if not created:
        logger.info(f"Appointment updated: {instance.title}")
        
        # Check for conflicts if time changed
        if instance.status in ['scheduled', 'confirmed']:
            check_appointment_conflicts(instance)
        
        # Send update notification
        send_appointment_notification(instance, 'appointment_updated')


def check_appointment_conflicts(appointment):
    """Check for scheduling conflicts."""
    # Check for time conflicts with other appointments
    conflicting_appointments = Appointment.objects.filter(
        organization=appointment.organization,
        start_datetime__lt=appointment.end_datetime,
        end_datetime__gt=appointment.start_datetime,
        status__in=['scheduled', 'confirmed', 'in_progress']
    ).exclude(id=appointment.id)
    
    for conflicting_appointment in conflicting_appointments:
        # Create conflict record
        conflict, created = ScheduleConflict.objects.get_or_create(
            organization=appointment.organization,
            primary_appointment=appointment,
            conflicting_appointment=conflicting_appointment,
            defaults={
                'conflict_type': 'time_conflict',
                'conflict_description': f"Time conflict between {appointment.title} and {conflicting_appointment.title}",
                'conflict_datetime': appointment.start_datetime,
                'impact_level': 'medium'
            }
        )
        
        if created:
            logger.warning(f"Schedule conflict detected: {conflict.conflict_description}")
            
            # Send conflict notification
            send_conflict_notification(conflict)


def send_appointment_notification(appointment, notification_type):
    """Send appointment notification."""
    try:
        # Get recipients
        recipients = []
        if appointment.assigned_team:
            recipients.extend(appointment.assigned_team.members.filter(is_active=True).values_list('user', flat=True))
        recipients.extend(appointment.assigned_users.values_list('id', flat=True))
        
        if recipients:
            ScheduleNotification.objects.create(
                organization=appointment.organization,
                notification_type=notification_type,
                subject=f"Appointment {notification_type.replace('_', ' ').title()}: {appointment.title}",
                message=f"Appointment '{appointment.title}' has been {notification_type.replace('_', ' ')}.",
                delivery_method='email',
                status='pending',
                scheduled_at=timezone.now(),
                related_appointment=appointment
            )
    except Exception as e:
        logger.error(f"Failed to send appointment notification: {e}")


def send_conflict_notification(conflict):
    """Send conflict notification."""
    try:
        # Get organization admins or managers
        recipients = User.objects.filter(
            organization=conflict.organization,
            is_staff=True
        )
        
        if recipients.exists():
            ScheduleNotification.objects.create(
                organization=conflict.organization,
                notification_type='conflict_detected',
                subject=f"Schedule Conflict Detected: {conflict.get_conflict_type_display()}",
                message=f"Schedule conflict detected: {conflict.conflict_description}",
                delivery_method='email',
                status='pending',
                scheduled_at=timezone.now(),
                related_conflict=conflict
            )
    except Exception as e:
        logger.error(f"Failed to send conflict notification: {e}")


# ==================== SCHEDULE CONFLICT SIGNALS ====================

@receiver(post_save, sender=ScheduleConflict)
def schedule_conflict_created(sender, instance, created, **kwargs):
    """Handle schedule conflict creation."""
    if created:
        logger.info(f"New schedule conflict created: {instance.conflict_type}")
        
        # Send immediate notification for high-impact conflicts
        if instance.impact_level in ['high', 'critical']:
            send_conflict_notification(instance)


@receiver(pre_save, sender=ScheduleConflict)
def schedule_conflict_pre_save(sender, instance, **kwargs):
    """Handle schedule conflict pre-save operations."""
    # Set resolution timestamp if being resolved
    if instance.status == 'resolved' and not instance.resolved_at:
        instance.resolved_at = timezone.now()


# ==================== SCHEDULE RULE SIGNALS ====================

@receiver(post_save, sender=ScheduleRule)
def schedule_rule_created(sender, instance, created, **kwargs):
    """Handle schedule rule creation."""
    if created:
        logger.info(f"New schedule rule created: {instance.name}")
        
        # Apply rule to existing appointments if needed
        apply_schedule_rule(instance)


def apply_schedule_rule(rule):
    """Apply schedule rule to existing appointments."""
    # This would implement rule application logic
    # For example, checking if appointments violate the rule
    logger.info(f"Applying schedule rule: {rule.name}")


# ==================== SCHEDULE NOTIFICATION SIGNALS ====================

@receiver(post_save, sender=ScheduleNotification)
def schedule_notification_created(sender, instance, created, **kwargs):
    """Handle schedule notification creation."""
    if created:
        logger.info(f"New schedule notification created: {instance.notification_type}")
        
        # Send notification if it's immediate
        if instance.delivery_method == 'immediate' or not instance.scheduled_at:
            send_notification(instance)


def send_notification(notification):
    """Send a schedule notification."""
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
        notification.error_message = str(e)
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


# ==================== SCHEDULE ANALYTICS SIGNALS ====================

@receiver(post_save, sender=ScheduleAnalytics)
def schedule_analytics_created(sender, instance, created, **kwargs):
    """Handle schedule analytics creation."""
    if created:
        logger.info(f"New schedule analytics created for period {instance.period_start} to {instance.period_end}")
        
        # Calculate additional metrics
        calculate_additional_metrics(instance)


def calculate_additional_metrics(analytics):
    """Calculate additional analytics metrics."""
    # This would contain additional metric calculations
    logger.info(f"Calculating additional metrics for analytics {analytics.id}")


# ==================== SCHEDULE INTEGRATION SIGNALS ====================

@receiver(post_save, sender=ScheduleIntegration)
def schedule_integration_created(sender, instance, created, **kwargs):
    """Handle schedule integration creation."""
    if created:
        logger.info(f"New schedule integration created: {instance.name}")
        
        # Test integration connection
        test_integration_connection(instance)


def test_integration_connection(integration):
    """Test connection to schedule integration."""
    # This would contain the actual connection testing logic
    logger.info(f"Testing connection for integration {integration.name}")


# ==================== UTILITY FUNCTIONS ====================

def send_schedule_notification(schedule_object, notification_type, message):
    """Send a schedule-related notification."""
    try:
        ScheduleNotification.objects.create(
            organization=schedule_object.organization,
            notification_type=notification_type,
            subject=f"Schedule Notification: {notification_type.replace('_', ' ').title()}",
            message=message,
            delivery_method='email',
            status='pending',
            scheduled_at=timezone.now()
        )
    except Exception as e:
        logger.error(f"Failed to create schedule notification: {e}")


# ==================== M2M SIGNAL HANDLERS ====================

# Note: M2M signal handlers are commented out due to Django's deferred attribute handling
# These would need to be implemented differently in a production environment

# @receiver(m2m_changed, sender=Appointment.assigned_users.through)
# def appointment_assigned_users_changed(sender, instance, action, **kwargs):
#     """Handle changes to appointment assigned users."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Appointment assigned users changed for {instance.title}")

# @receiver(m2m_changed, sender=Appointment.required_resources.through)
# def appointment_required_resources_changed(sender, instance, action, **kwargs):
#     """Handle changes to appointment required resources."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Appointment required resources changed for {instance.title}")

# @receiver(m2m_changed, sender=ScheduleNotification.recipients.through)
# def schedule_notification_recipients_changed(sender, instance, action, **kwargs):
#     """Handle changes to schedule notification recipients."""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         logger.info(f"Schedule notification recipients changed for {instance.notification_type}")

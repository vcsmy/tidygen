"""
Analytics & Reporting Signals

This module contains Django signals for the analytics and reporting system,
providing automated logic for reports, KPIs, dashboards, and analytics components.
"""

import logging
from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from datetime import timedelta

from apps.analytics.models import (
    Report, KPI, KPIMeasurement, Dashboard, DashboardWidget,
    DataSource, ReportTemplate, AnalyticsEvent, Alert, AnalyticsCache
)

logger = logging.getLogger(__name__)


# ==================== REPORT SIGNALS ====================

@receiver(pre_save, sender=Report)
def report_pre_save(sender, instance, **kwargs):
    """Handle report pre-save logic."""
    # Generate report ID if not set
    if not instance.report_id:
        import uuid
        instance.report_id = uuid.uuid4()
    
    # Set next run time if scheduling is enabled
    if instance.is_scheduled and instance.schedule_frequency and not instance.next_run:
        instance.next_run = _calculate_next_run_time(instance.schedule_frequency, instance.schedule_time)


@receiver(post_save, sender=Report)
def report_post_save(sender, instance, created, **kwargs):
    """Handle report post-save logic."""
    if created:
        logger.info(f"New report created: {instance.name}")
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.organization,
            event_type='system_event',
            event_name=f'Report Created: {instance.name}',
            user=instance.created_by,
            context_data={
                'report_id': str(instance.report_id),
                'report_type': instance.report_type
            }
        )
    else:
        logger.info(f"Report updated: {instance.name} - Status: {instance.status}")
        
        # Log status change
        if instance.status in ['completed', 'failed']:
            AnalyticsEvent.objects.create(
                organization=instance.organization,
                event_type='report_generated',
                event_name=f'Report {instance.status.title()}: {instance.name}',
                user=instance.created_by,
                context_data={
                    'report_id': str(instance.report_id),
                    'status': instance.status,
                    'execution_time': str(instance.execution_time) if instance.execution_time else None
                }
            )


@receiver(post_delete, sender=Report)
def report_post_delete(sender, instance, **kwargs):
    """Handle report deletion."""
    logger.info(f"Report deleted: {instance.name}")
    
    # Log analytics event
    AnalyticsEvent.objects.create(
        organization=instance.organization,
        event_type='system_event',
        event_name=f'Report Deleted: {instance.name}',
        context_data={
            'report_id': str(instance.report_id),
            'report_type': instance.report_type
        }
    )


# ==================== KPI SIGNALS ====================

@receiver(pre_save, sender=KPI)
def kpi_pre_save(sender, instance, **kwargs):
    """Handle KPI pre-save logic."""
    # Generate KPI ID if not set
    if not instance.kpi_id:
        import uuid
        instance.kpi_id = uuid.uuid4()
    
    # Calculate next calculation time if frequency is set
    if instance.frequency and not instance.next_calculation:
        instance.next_calculation = _calculate_next_calculation_time(instance.frequency)


@receiver(post_save, sender=KPI)
def kpi_post_save(sender, instance, created, **kwargs):
    """Handle KPI post-save logic."""
    if created:
        logger.info(f"New KPI created: {instance.name}")
        
        # Note: KPI model doesn't have organization field, so we skip analytics event creation
        # This could be enhanced in the future if organization context is needed
        
    else:
        logger.info(f"KPI updated: {instance.name}")
        
        # Check for threshold alerts if current value changed
        if instance.current_value is not None:
            _check_kpi_thresholds(instance)


@receiver(post_delete, sender=KPI)
def kpi_post_delete(sender, instance, **kwargs):
    """Handle KPI deletion."""
    logger.info(f"KPI deleted: {instance.name}")
    
    # Log analytics event
    AnalyticsEvent.objects.create(
        organization=instance.organization,
        event_type='system_event',
        event_name=f'KPI Deleted: {instance.name}',
        context_data={
            'kpi_id': str(instance.kpi_id),
            'kpi_type': instance.kpi_type
        }
    )


# ==================== KPI MEASUREMENT SIGNALS ====================

@receiver(post_save, sender=KPIMeasurement)
def kpi_measurement_post_save(sender, instance, created, **kwargs):
    """Handle KPI measurement post-save logic."""
    if created:
        logger.info(f"New KPI measurement: {instance.kpi.name} = {instance.value}")
        
        # Update KPI current value
        instance.kpi.current_value = instance.value
        instance.kpi.last_calculated = timezone.now()
        instance.kpi.save()
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.kpi.organization,
            event_type='kpi_updated',
            event_name=f'KPI Updated: {instance.kpi.name}',
            context_data={
                'kpi_id': str(instance.kpi.kpi_id),
                'value': float(instance.value),
                'measurement_date': instance.measurement_date.isoformat()
            }
        )
        
        # Check for threshold alerts
        _check_kpi_thresholds(instance.kpi)


@receiver(post_delete, sender=KPIMeasurement)
def kpi_measurement_post_delete(sender, instance, **kwargs):
    """Handle KPI measurement deletion."""
    logger.info(f"KPI measurement deleted: {instance.kpi.name} = {instance.value}")


# ==================== DASHBOARD SIGNALS ====================

@receiver(pre_save, sender=Dashboard)
def dashboard_pre_save(sender, instance, **kwargs):
    """Handle dashboard pre-save logic."""
    # Generate dashboard ID if not set
    if not instance.dashboard_id:
        import uuid
        instance.dashboard_id = uuid.uuid4()


@receiver(post_save, sender=Dashboard)
def dashboard_post_save(sender, instance, created, **kwargs):
    """Handle dashboard post-save logic."""
    if created:
        logger.info(f"New dashboard created: {instance.name}")
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.organization,
            event_type='system_event',
            event_name=f'Dashboard Created: {instance.name}',
            user=instance.created_by,
            context_data={
                'dashboard_id': str(instance.dashboard_id),
                'dashboard_type': instance.dashboard_type
            }
        )
    else:
        logger.info(f"Dashboard updated: {instance.name}")


@receiver(post_delete, sender=Dashboard)
def dashboard_post_delete(sender, instance, **kwargs):
    """Handle dashboard deletion."""
    logger.info(f"Dashboard deleted: {instance.name}")
    
    # Clear related cache entries
    cache_keys = [
        f"dashboard_{instance.dashboard_id}",
        f"dashboard_widget_{instance.dashboard_id}_*"
    ]
    for key in cache_keys:
        cache.delete(key)


# ==================== DASHBOARD WIDGET SIGNALS ====================

@receiver(pre_save, sender=DashboardWidget)
def dashboard_widget_pre_save(sender, instance, **kwargs):
    """Handle dashboard widget pre-save logic."""
    # Generate widget ID if not set
    if not instance.widget_id:
        import uuid
        instance.widget_id = uuid.uuid4()


@receiver(post_save, sender=DashboardWidget)
def dashboard_widget_post_save(sender, instance, created, **kwargs):
    """Handle dashboard widget post-save logic."""
    if created:
        logger.info(f"New dashboard widget created: {instance.name}")
    else:
        logger.info(f"Dashboard widget updated: {instance.name}")
        
        # Clear widget cache
        cache_key = f"dashboard_widget_{instance.widget_id}"
        cache.delete(cache_key)


@receiver(post_delete, sender=DashboardWidget)
def dashboard_widget_post_delete(sender, instance, **kwargs):
    """Handle dashboard widget deletion."""
    logger.info(f"Dashboard widget deleted: {instance.name}")
    
    # Clear widget cache
    cache_key = f"dashboard_widget_{instance.widget_id}"
    cache.delete(cache_key)


# ==================== DATA SOURCE SIGNALS ====================

@receiver(pre_save, sender=DataSource)
def data_source_pre_save(sender, instance, **kwargs):
    """Handle data source pre-save logic."""
    # Generate source ID if not set
    if not instance.source_id:
        import uuid
        instance.source_id = uuid.uuid4()


@receiver(post_save, sender=DataSource)
def data_source_post_save(sender, instance, created, **kwargs):
    """Handle data source post-save logic."""
    if created:
        logger.info(f"New data source created: {instance.name}")
    else:
        logger.info(f"Data source updated: {instance.name}")


@receiver(post_delete, sender=DataSource)
def data_source_post_delete(sender, instance, **kwargs):
    """Handle data source deletion."""
    logger.info(f"Data source deleted: {instance.name}")


# ==================== REPORT TEMPLATE SIGNALS ====================

@receiver(pre_save, sender=ReportTemplate)
def report_template_pre_save(sender, instance, **kwargs):
    """Handle report template pre-save logic."""
    # Generate template ID if not set
    if not instance.template_id:
        import uuid
        instance.template_id = uuid.uuid4()


@receiver(post_save, sender=ReportTemplate)
def report_template_post_save(sender, instance, created, **kwargs):
    """Handle report template post-save logic."""
    if created:
        logger.info(f"New report template created: {instance.name}")
    else:
        logger.info(f"Report template updated: {instance.name}")


@receiver(post_delete, sender=ReportTemplate)
def report_template_post_delete(sender, instance, **kwargs):
    """Handle report template deletion."""
    logger.info(f"Report template deleted: {instance.name}")


# ==================== ANALYTICS EVENT SIGNALS ====================

@receiver(pre_save, sender=AnalyticsEvent)
def analytics_event_pre_save(sender, instance, **kwargs):
    """Handle analytics event pre-save logic."""
    # Generate event ID if not set
    if not instance.event_id:
        import uuid
        instance.event_id = uuid.uuid4()


@receiver(post_save, sender=AnalyticsEvent)
def analytics_event_post_save(sender, instance, created, **kwargs):
    """Handle analytics event post-save logic."""
    if created:
        # Update analytics cache if needed
        _update_analytics_cache(instance)


# ==================== ALERT SIGNALS ====================

@receiver(pre_save, sender=Alert)
def alert_pre_save(sender, instance, **kwargs):
    """Handle alert pre-save logic."""
    # Generate alert ID if not set
    if not instance.alert_id:
        import uuid
        instance.alert_id = uuid.uuid4()


@receiver(post_save, sender=Alert)
def alert_post_save(sender, instance, created, **kwargs):
    """Handle alert post-save logic."""
    if created:
        logger.info(f"New alert created: {instance.title}")
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.organization,
            event_type='system_event',
            event_name=f'Alert Created: {instance.title}',
            context_data={
                'alert_id': str(instance.alert_id),
                'alert_type': instance.alert_type,
                'severity': instance.severity
            }
        )
    else:
        logger.info(f"Alert updated: {instance.title} - Status: {instance.status}")


@receiver(post_delete, sender=Alert)
def alert_post_delete(sender, instance, **kwargs):
    """Handle alert deletion."""
    logger.info(f"Alert deleted: {instance.title}")


# ==================== ANALYTICS CACHE SIGNALS ====================

@receiver(post_save, sender=AnalyticsCache)
def analytics_cache_post_save(sender, instance, created, **kwargs):
    """Handle analytics cache post-save logic."""
    if created:
        logger.info(f"New analytics cache entry created: {instance.cache_key}")
    else:
        logger.info(f"Analytics cache entry updated: {instance.cache_key}")


@receiver(post_delete, sender=AnalyticsCache)
def analytics_cache_post_delete(sender, instance, **kwargs):
    """Handle analytics cache deletion."""
    logger.info(f"Analytics cache entry deleted: {instance.cache_key}")


# ==================== HELPER FUNCTIONS ====================

def _calculate_next_run_time(frequency, schedule_time=None):
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
    
    # Adjust time if schedule_time is specified
    if schedule_time:
        next_run = next_run.replace(
            hour=schedule_time.hour,
            minute=schedule_time.minute,
            second=schedule_time.second,
            microsecond=0
        )
    
    return next_run


def _calculate_next_calculation_time(frequency):
    """Calculate next calculation time based on frequency."""
    now = timezone.now()
    
    if frequency == 'real_time':
        return now + timedelta(minutes=1)
    elif frequency == 'hourly':
        return now + timedelta(hours=1)
    elif frequency == 'daily':
        return now + timedelta(days=1)
    elif frequency == 'weekly':
        return now + timedelta(weeks=1)
    elif frequency == 'monthly':
        return now + timedelta(days=30)
    elif frequency == 'quarterly':
        return now + timedelta(days=90)
    elif frequency == 'yearly':
        return now + timedelta(days=365)
    else:
        return now + timedelta(hours=1)


def _check_kpi_thresholds(kpi):
    """Check if KPI triggers any threshold alerts."""
    if kpi.current_value is None:
        return
    
    # Check critical threshold
    if kpi.critical_threshold and kpi.current_value <= kpi.critical_threshold:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            organization=kpi.organization,
            related_kpi=kpi,
            alert_type='kpi_threshold',
            severity='critical',
            status='active'
        ).first()
        
        if not existing_alert:
            Alert.objects.create(
                organization=kpi.organization,
                alert_type='kpi_threshold',
                severity='critical',
                title=f'Critical KPI Alert: {kpi.name}',
                message=f'KPI "{kpi.name}" has reached critical threshold of {kpi.critical_threshold}',
                description=f'Current value: {kpi.current_value}',
                related_kpi=kpi,
                threshold_value=kpi.critical_threshold,
                current_value=kpi.current_value,
                alert_data={
                    'kpi_id': str(kpi.kpi_id),
                    'kpi_name': kpi.name,
                    'threshold_type': 'critical'
                }
            )
    
    # Check warning threshold
    elif kpi.warning_threshold and kpi.current_value <= kpi.warning_threshold:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            organization=kpi.organization,
            related_kpi=kpi,
            alert_type='kpi_threshold',
            severity='high',
            status='active'
        ).first()
        
        if not existing_alert:
            Alert.objects.create(
                organization=kpi.organization,
                alert_type='kpi_threshold',
                severity='high',
                title=f'Warning KPI Alert: {kpi.name}',
                message=f'KPI "{kpi.name}" has reached warning threshold of {kpi.warning_threshold}',
                description=f'Current value: {kpi.current_value}',
                related_kpi=kpi,
                threshold_value=kpi.warning_threshold,
                current_value=kpi.current_value,
                alert_data={
                    'kpi_id': str(kpi.kpi_id),
                    'kpi_name': kpi.name,
                    'threshold_type': 'warning'
                }
            )


def _update_analytics_cache(event):
    """Update analytics cache based on event."""
    # This is a simplified example
    # In a real implementation, this would update relevant cache entries
    # based on the event type and context
    
    cache_key = f"analytics_events_{event.organization.id}_{event.event_type}"
    
    # Get existing cache or create new
    cached_data = cache.get(cache_key, [])
    cached_data.append({
        'event_id': str(event.event_id),
        'event_name': event.event_name,
        'timestamp': event.event_timestamp.isoformat(),
        'user': event.user.get_full_name() if event.user else None
    })
    
    # Keep only last 100 events
    if len(cached_data) > 100:
        cached_data = cached_data[-100:]
    
    # Cache for 1 hour
    cache.set(cache_key, cached_data, 3600)


# ==================== M2M SIGNAL HANDLERS ====================

@receiver(m2m_changed, sender=Report.allowed_users.through)
def report_allowed_users_changed(sender, instance, action, **kwargs):
    """Handle changes to report allowed users."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        logger.info(f"Report allowed users changed for {instance.name}")
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.organization,
            event_type='system_event',
            event_name=f'Report Access Changed: {instance.name}',
            context_data={
                'report_id': str(instance.report_id),
                'action': action
            }
        )


@receiver(m2m_changed, sender=Dashboard.allowed_users.through)
def dashboard_allowed_users_changed(sender, instance, action, **kwargs):
    """Handle changes to dashboard allowed users."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        logger.info(f"Dashboard allowed users changed for {instance.name}")
        
        # Log analytics event
        AnalyticsEvent.objects.create(
            organization=instance.organization,
            event_type='system_event',
            event_name=f'Dashboard Access Changed: {instance.name}',
            context_data={
                'dashboard_id': str(instance.dashboard_id),
                'action': action
            }
        )

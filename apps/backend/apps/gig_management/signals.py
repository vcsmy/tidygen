"""
Signals for gig_management app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import GigJob, GigApplication, JobMilestone

User = get_user_model()


@receiver(pre_save, sender=GigJob)
def generate_job_id(sender, instance, **kwargs):
    """
    Generate job ID if not provided.
    """
    if not instance.job_id:
        import uuid
        instance.job_id = f"GIG{str(uuid.uuid4())[:8].upper()}"


@receiver(post_save, sender=GigApplication)
def handle_application_status_change(sender, instance, created, **kwargs):
    """
    Handle application status changes and notify relevant parties.
    """
    if not created and instance.status == 'accepted':
        # Update the job status when an application is accepted
        job = instance.job
        if job.status == 'published':
            job.status = 'assigned'
            job.assigned_freelancer = instance.freelancer
            job.assigned_at = timezone.now()
            job.save(update_fields=['status', 'assigned_freelancer', 'assigned_at'])


@receiver(post_save, sender=JobMilestone)
def handle_milestone_completion(sender, instance, created, **kwargs):
    """
    Handle milestone completion and update job status if needed.
    """
    if not created and instance.is_completed and instance.milestone_type == 'completion':
        # Mark job as completed when completion milestone is done
        job = instance.job
        if job.status == 'in_progress':
            job.status = 'completed'
            job.actual_end_date = timezone.now()
            job.save(update_fields=['status', 'actual_end_date'])


@receiver(pre_save, sender=GigJob)
def calculate_actual_duration(sender, instance, **kwargs):
    """
    Calculate actual duration when job is completed.
    """
    if instance.status == 'completed' and instance.actual_start_date and instance.actual_end_date:
        if not instance.actual_duration_hours:
            duration = instance.actual_end_date - instance.actual_start_date
            instance.actual_duration_hours = duration.total_seconds() / 3600

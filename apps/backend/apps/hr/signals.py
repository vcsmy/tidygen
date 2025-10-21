"""
Signals for automated HR management operations in TidyGen ERP platform.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from apps.hr.models import (
    Employee, Attendance, LeaveRequest, PayrollPeriod, Payroll, PerformanceReview,
    Training, TrainingEnrollment, Document, Policy, PolicyAcknowledgment
)


@receiver(post_save, sender=Employee)
def update_employee_hire_date(sender, instance, created, **kwargs):
    """Update employee hire date and related fields when employee is created."""
    if created:
        # Set default probation end date (typically 3 months from hire date)
        if not instance.probation_end_date:
            instance.probation_end_date = instance.hire_date + timedelta(days=90)
            # Save without triggering signals again
            Employee.objects.filter(pk=instance.pk).update(probation_end_date=instance.probation_end_date)


@receiver(post_save, sender=Attendance)
def calculate_attendance_hours(sender, instance, created, **kwargs):
    """Calculate total hours and overtime when attendance is recorded."""
    if instance.check_in_time and instance.check_out_time:
        # Calculate total hours worked
        from datetime import datetime, date
        
        # Combine date with time
        check_in_datetime = datetime.combine(instance.date, instance.check_in_time)
        check_out_datetime = datetime.combine(instance.date, instance.check_out_time)
        
        # Calculate total time
        total_time = check_out_datetime - check_in_datetime
        total_hours = total_time.total_seconds() / 3600  # Convert to hours
        
        # Subtract break time if provided
        if instance.break_start_time and instance.break_end_time:
            break_start_datetime = datetime.combine(instance.date, instance.break_start_time)
            break_end_datetime = datetime.combine(instance.date, instance.break_end_time)
            break_time = break_end_datetime - break_start_datetime
            break_hours = break_time.total_seconds() / 3600
            total_hours -= break_hours
        
        # Calculate overtime (assuming 8 hours is standard)
        overtime_hours = max(0, total_hours - 8)
        
        # Update the instance
        instance.total_hours = round(total_hours, 2)
        instance.overtime_hours = round(overtime_hours, 2)
        
        # Save without triggering signals again
        Attendance.objects.filter(pk=instance.pk).update(
            total_hours=instance.total_hours,
            overtime_hours=instance.overtime_hours
        )


@receiver(post_save, sender=LeaveRequest)
def update_leave_request_status(sender, instance, created, **kwargs):
    """Update leave request status and related fields."""
    if created:
        # Calculate total days if not provided
        if not instance.total_days:
            total_days = (instance.end_date - instance.start_date).days + 1
            instance.total_days = total_days
            # Save without triggering signals again
            LeaveRequest.objects.filter(pk=instance.pk).update(total_days=instance.total_days)
    
    # If leave is approved, update employee status if needed
    if instance.status == 'approved' and not created:
        employee = instance.employee
        # Check if the leave period includes today
        today = timezone.now().date()
        if instance.start_date <= today <= instance.end_date:
            if employee.employment_status == 'active':
                employee.employment_status = 'on_leave'
                # Save without triggering signals again
                Employee.objects.filter(pk=employee.pk).update(employment_status='on_leave')


@receiver(post_save, sender=Payroll)
def calculate_payroll_totals(sender, instance, created, **kwargs):
    """Calculate payroll totals when payroll is created or updated."""
    # Calculate gross pay
    gross_pay = instance.basic_salary + instance.overtime_pay + instance.allowances + instance.bonuses + instance.commissions
    
    # Calculate total deductions
    total_deductions = instance.tax_deduction + instance.social_security + instance.health_insurance + instance.other_deductions
    
    # Calculate net pay
    net_pay = gross_pay - total_deductions
    
    # Update the instance
    instance.gross_pay = gross_pay
    instance.total_deductions = total_deductions
    instance.net_pay = net_pay
    
    # Save without triggering signals again
    Payroll.objects.filter(pk=instance.pk).update(
        gross_pay=instance.gross_pay,
        total_deductions=instance.total_deductions,
        net_pay=instance.net_pay
    )


@receiver(post_save, sender=PerformanceReview)
def update_performance_review_status(sender, instance, created, **kwargs):
    """Update performance review status and calculate average rating."""
    if not created:
        # Calculate overall rating if individual ratings are provided
        ratings = [
            instance.quality_rating,
            instance.productivity_rating,
            instance.teamwork_rating,
            instance.communication_rating
        ]
        
        # Filter out None values
        valid_ratings = [rating for rating in ratings if rating is not None]
        
        if valid_ratings and not instance.overall_rating:
            average_rating = sum(valid_ratings) / len(valid_ratings)
            instance.overall_rating = round(average_rating, 1)
            # Save without triggering signals again
            PerformanceReview.objects.filter(pk=instance.pk).update(overall_rating=instance.overall_rating)


@receiver(post_save, sender=TrainingEnrollment)
def update_training_enrollment_status(sender, instance, created, **kwargs):
    """Update training enrollment status and completion details."""
    if not created and instance.status == 'completed':
        # Set completion date if not provided
        if not instance.completion_date:
            instance.completion_date = timezone.now().date()
            # Save without triggering signals again
            TrainingEnrollment.objects.filter(pk=instance.pk).update(completion_date=instance.completion_date)


@receiver(post_save, sender=Document)
def update_document_verification(sender, instance, created, **kwargs):
    """Update document verification status."""
    if not created and instance.is_verified and not instance.verified_at:
        instance.verified_at = timezone.now()
        # Save without triggering signals again
        Document.objects.filter(pk=instance.pk).update(verified_at=instance.verified_at)


@receiver(post_save, sender=PolicyAcknowledgment)
def update_policy_acknowledgment(sender, instance, created, **kwargs):
    """Update policy acknowledgment timestamp."""
    if created:
        instance.acknowledged_at = timezone.now()
        # Save without triggering signals again
        PolicyAcknowledgment.objects.filter(pk=instance.pk).update(acknowledged_at=instance.acknowledged_at)


@receiver(pre_save, sender=Employee)
def validate_employee_data(sender, instance, **kwargs):
    """Validate employee data before saving."""
    # The employee_id field is already unique at the database level,
    # so we don't need additional validation here since the model
    # enforces uniqueness with unique=True
    pass


@receiver(pre_save, sender=LeaveRequest)
def validate_leave_request(sender, instance, **kwargs):
    """Validate leave request data before saving."""
    # Ensure end date is not before start date
    if instance.start_date and instance.end_date and instance.end_date < instance.start_date:
        raise ValueError("End date cannot be before start date.")
    
    # Ensure leave request is not in the past (unless it's an update)
    if instance.start_date and instance.start_date < timezone.now().date():
        # Allow past dates for updates
        if not instance.pk:  # New leave request
            raise ValueError("Cannot create leave request for past dates.")


@receiver(pre_save, sender=Attendance)
def validate_attendance_data(sender, instance, **kwargs):
    """Validate attendance data before saving."""
    # Ensure check-out time is after check-in time
    if instance.check_in_time and instance.check_out_time and instance.check_out_time <= instance.check_in_time:
        raise ValueError("Check-out time must be after check-in time.")
    
    # Ensure break end time is after break start time
    if instance.break_start_time and instance.break_end_time and instance.break_end_time <= instance.break_start_time:
        raise ValueError("Break end time must be after break start time.")


@receiver(pre_save, sender=Payroll)
def validate_payroll_data(sender, instance, **kwargs):
    """Validate payroll data before saving."""
    # Ensure net pay is not negative
    if instance.net_pay and instance.net_pay < 0:
        raise ValueError("Net pay cannot be negative.")
    
    # Ensure gross pay is not negative
    if instance.gross_pay and instance.gross_pay < 0:
        raise ValueError("Gross pay cannot be negative.")


@receiver(pre_save, sender=PerformanceReview)
def validate_performance_review(sender, instance, **kwargs):
    """Validate performance review data before saving."""
    # Ensure ratings are within valid range (1-5)
    ratings = [
        instance.overall_rating,
        instance.quality_rating,
        instance.productivity_rating,
        instance.teamwork_rating,
        instance.communication_rating
    ]
    
    for rating in ratings:
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("All ratings must be between 1 and 5.")


@receiver(pre_save, sender=TrainingEnrollment)
def validate_training_enrollment(sender, instance, **kwargs):
    """Validate training enrollment data before saving."""
    # Ensure score is within valid range (0-100)
    if instance.score is not None and (instance.score < 0 or instance.score > 100):
        raise ValueError("Score must be between 0 and 100.")
    
    # Ensure rating is within valid range (1-5)
    if instance.rating is not None and (instance.rating < 1 or instance.rating > 5):
        raise ValueError("Rating must be between 1 and 5.")


@receiver(post_delete, sender=Employee)
def cleanup_employee_data(sender, instance, **kwargs):
    """Clean up related data when employee is deleted."""
    # This could include archiving data, sending notifications, etc.
    # For now, we'll just log the deletion
    pass


@receiver(post_delete, sender=LeaveRequest)
def cleanup_leave_request(sender, instance, **kwargs):
    """Clean up leave request data when deleted."""
    # If the leave was approved and the employee is on leave, update their status
    if instance.status == 'approved':
        employee = instance.employee
        today = timezone.now().date()
        
        # Check if there are other approved leaves for this employee
        other_leaves = LeaveRequest.objects.filter(
            employee=employee,
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).exclude(pk=instance.pk)
        
        # If no other leaves, set employee status back to active
        if not other_leaves.exists() and employee.employment_status == 'on_leave':
            employee.employment_status = 'active'
            # Save without triggering signals again
            Employee.objects.filter(pk=employee.pk).update(employment_status='active')


@receiver(post_save, sender=Employee)
def update_employee_probation_status(sender, instance, created, **kwargs):
    """Update employee probation status based on probation end date."""
    if not created and instance.probation_end_date:
        today = timezone.now().date()
        
        # If probation has ended and employee is still on probation, update status
        if instance.probation_end_date < today and instance.employment_status == 'active':
            # Employee has completed probation
            # This could trigger notifications, salary adjustments, etc.
            pass


@receiver(post_save, sender=Document)
def check_document_expiry(sender, instance, created, **kwargs):
    """Check if document is expiring soon and create notifications."""
    if created and instance.expiry_date:
        # Check if document expires within 30 days
        if instance.expiry_date <= timezone.now().date() + timedelta(days=30):
            # This could create a notification or send an email
            # For now, we'll just log it
            pass


@receiver(post_save, sender=Training)
def update_training_status(sender, instance, created, **kwargs):
    """Update training status based on dates."""
    if not created:
        today = timezone.now().date()
        
        # Update training status based on dates
        if instance.start_date > today:
            new_status = 'planned'
        elif instance.start_date <= today <= instance.end_date:
            new_status = 'in_progress'
        elif instance.end_date < today:
            new_status = 'completed'
        else:
            new_status = instance.status
        
        if new_status != instance.status:
            instance.status = new_status
            # Save without triggering signals again
            Training.objects.filter(pk=instance.pk).update(status=new_status)


@receiver(post_save, sender=PayrollPeriod)
def update_payroll_period_status(sender, instance, created, **kwargs):
    """Update payroll period status based on dates."""
    if not created:
        today = timezone.now().date()
        
        # Update payroll period status based on dates
        if instance.end_date < today and instance.status == 'draft':
            # Period has ended, should be processed
            pass
        elif instance.pay_date < today and instance.status == 'completed':
            # Pay date has passed, should be paid
            pass


@receiver(post_save, sender=Policy)
def update_policy_status(sender, instance, created, **kwargs):
    """Update policy status based on effective date."""
    if not created:
        today = timezone.now().date()
        
        # Update policy status based on effective date
        if instance.effective_date <= today and instance.status == 'approved':
            instance.status = 'active'
            # Save without triggering signals again
            Policy.objects.filter(pk=instance.pk).update(status='active')
        elif instance.expiry_date and instance.expiry_date < today and instance.status == 'active':
            instance.status = 'archived'
            # Save without triggering signals again
            Policy.objects.filter(pk=instance.pk).update(status='archived')

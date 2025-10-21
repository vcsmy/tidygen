"""
Signals for freelancers app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth import get_user_model
from .models import Freelancer, FreelancerReview

User = get_user_model()


@receiver(post_save, sender=FreelancerReview)
def update_freelancer_rating(sender, instance, created, **kwargs):
    """
    Update freelancer's overall rating when a new review is created.
    """
    freelancer = instance.freelancer
    
    # Calculate average rating from all reviews
    reviews = FreelancerReview.objects.filter(freelancer=freelancer)
    if reviews.exists():
        avg_rating = reviews.aggregate(avg_rating=models.Avg('overall_rating'))['avg_rating']
        freelancer.rating = round(avg_rating, 2)
        freelancer.save(update_fields=['rating'])


@receiver(pre_save, sender=Freelancer)
def generate_freelancer_id(sender, instance, **kwargs):
    """
    Generate freelancer ID if not provided.
    """
    if not instance.freelancer_id:
        import uuid
        instance.freelancer_id = f"FL{str(uuid.uuid4())[:8].upper()}"


@receiver(post_save, sender=User)
def create_freelancer_profile(sender, instance, created, **kwargs):
    """
    Auto-create freelancer profile when user registers if requested.
    This is optional and can be triggered by a form field or user preference.
    """
    # Only create if user has indicated they want to be a freelancer
    # This would typically be set during registration
    if created and hasattr(instance, '_create_freelancer_profile'):
        Freelancer.objects.create(user=instance)

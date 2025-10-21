"""
Views for gig_management app API.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsOwnerOrReadOnly
from .models import (
    GigCategory, GigJob, GigApplication, JobMilestone,
    JobPhoto, JobMessage, JobReview
)
from .serializers import (
    GigCategorySerializer, GigJobListSerializer, GigJobDetailSerializer, 
    GigJobCreateSerializer, GigApplicationSerializer, GigApplicationCreateSerializer,
    JobMilestoneSerializer, JobMilestoneCreateSerializer, JobPhotoSerializer,
    JobPhotoUploadSerializer, JobMessageSerializer, JobMessageCreateSerializer,
    JobReviewSerializer
)
from .filters import GigJobFilter

User = get_user_model()


@extend_schema(tags=['Gig Management'])
class GigCategoryListView(generics.ListAPIView):
    """
    List all active gig categories.
    """
    queryset = GigCategory.objects.filter(is_active=True)
    serializer_class = GigCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=['Gig Management'])
class GigJobListCreateView(generics.ListCreateAPIView):
    """
    List all gig jobs or create a new one.
    """
    queryset = GigJob.objects.select_related('client', 'category', 'assigned_freelancer').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GigJobFilter
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GigJobCreateSerializer
        return GigJobListSerializer
    
    def perform_create(self, serializer):
        """Set the client when creating a gig job."""
        serializer.save(client=self.request.user)


@extend_schema(tags=['Gig Management'])
class GigJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a gig job instance.
    """
    queryset = GigJob.objects.select_related(
        'client', 'category', 'assigned_freelancer', 'assigned_by'
    ).prefetch_related('applications__freelancer', 'milestones', 'photos', 'messages', 'reviews')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return GigJobCreateSerializer
        return GigJobDetailSerializer
    
    def get_permissions(self):
        """Custom permissions for different operations."""
        if self.request.method in ['GET']:
            # Anyone can view published jobs
            return [permissions.IsAuthenticated()]
        else:
            # Only job owner can modify
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]


@extend_schema(tags=['Gig Management'])
class GigApplicationView(generics.ListCreateAPIView):
    """
    List and create gig applications for a specific job.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        
        # Only job owner and assigned freelancer can see applications
        if self.request.user == job.client:
            return GigApplication.objects.filter(job=job).select_related('freelancer')
        elif job.assigned_freelancer and self.request.user == job.assigned_freelancer.user:
            return GigApplication.objects.filter(job=job, freelancer=job.assigned_freelancer)
        else:
            # Others can only see their own application
            try:
                freelancer = self.request.user.freelancer_profile
                return GigApplication.objects.filter(job=job, freelancer=freelancer)
            except:
                return GigApplication.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GigApplicationCreateSerializer
        return GigApplicationSerializer
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        serializer.save(job=job)


@extend_schema(tags=['Gig Management'])
class GigApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific application.
    """
    serializer_class = GigApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        
        # Only job owner and application owner can see applications
        if self.request.user == job.client:
            return GigApplication.objects.filter(job=job).select_related('freelancer')
        else:
            try:
                freelancer = self.request.user.freelancer_profile
                return GigApplication.objects.filter(job=job, freelancer=freelancer)
            except:
                return GigApplication.objects.none()


@extend_schema(tags=['Gig Management'])
class JobMilestoneView(generics.ListCreateAPIView):
    """
    List and create milestones for a job.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        self.check_job_permissions(job)
        return JobMilestone.objects.filter(job=job)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobMilestoneCreateSerializer
        return JobMilestoneSerializer
    
    def check_job_permissions(self, job):
        """Check if user has permission to access this job."""
        if not (self.request.user == job.client or 
                (job.assigned_freelancer and self.request.user == job.assigned_freelancer.user)):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this job.")
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        self.check_job_permissions(job)
        serializer.save(job=job)


@extend_schema(tags=['Gig Management'])
class JobMilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific milestone.
    """
    serializer_class = JobMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        self.check_job_permissions(job)
        return JobMilestone.objects.filter(job=job)
    
    def check_job_permissions(self, job):
        """Check if user has permission to access this job."""
        if not (self.request.user == job.client or 
                (job.assigned_freelancer and self.request.user == job.assigned_freelancer.user)):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this job.")


@extend_schema(tags=['Gig Management'])
class JobPhotoView(generics.ListCreateAPIView):
    """
    List and upload photos for a job.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        self.check_job_permissions(job)
        return JobPhoto.objects.filter(job=job)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobPhotoUploadSerializer
        return JobPhotoSerializer
    
    def check_job_permissions(self, job):
        """Check if user has permission to access this job."""
        if not (self.request.user == job.client or 
                (job.assigned_freelancer and self.request.user == job.assigned_freelancer.user)):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this job.")


@extend_schema(tags=['Gig Management'])
class JobMessageView(generics.ListCreateAPIView):
    """
    List and send messages for a job.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        self.check_job_permissions(job)
        return JobMessage.objects.filter(job=job).order_by('-created')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobMessageCreateSerializer
        return JobMessageSerializer
    
    def check_job_permissions(self, job):
        """Check if user has permission to access this job."""
        if not (self.request.user == job.client or 
                (job.assigned_freelancer and self.request.user == job.assigned_freelancer.user)):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this job.")


@extend_schema(tags=['Gig Management'])
class JobReviewView(generics.ListCreateAPIView):
    """
    List and create reviews for a job.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(GigJob, id=job_id)
        return JobReview.objects.filter(job=job).order_by('-created')
    
    serializer_class = JobReviewSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_freelancer(request, job_id, application_id):
    """
    Assign a freelancer to a job (job owner only).
    """
    job = get_object_or_404(GigJob, id=job_id)
    
    # Check if user owns the job
    if request.user != job.client:
        return Response(
            {'error': 'Only job owners can assign freelancers.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if job is still available for assignment
    if job.status not in ['published']:
        return Response(
            {'error': 'Job is not available for assignment.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    application = get_object_or_404(GigApplication, id=application_id, job=job)
    
    # Update job assignment
    job.assigned_freelancer = application.freelancer
    job.assigned_at = timezone.now()
    job.assigned_by = request.user
    job.status = 'assigned'
    job.save()
    
    # Update application status
    application.status = 'accepted'
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save()
    
    # Reject other applications
    GigApplication.objects.filter(
        job=job, status='submitted'
    ).exclude(id=application_id).update(
        status='rejected',
        reviewed_by=request.user,
        reviewed_at=timezone.now()
    )
    
    serializer = GigJobDetailSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_jobs(request):
    """
    Search gig jobs by various criteria.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    city = request.GET.get('city', '').strip()
    min_rate = request.GET.get('min_rate')
    max_rate = request.GET.get('max_rate')
    job_status = request.GET.get('status', 'published')
    
    queryset = GigJob.objects.filter(status=job_status).select_related(
        'client', 'category', 'assigned_freelancer'
    )
    
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(service_type__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    if city:
        queryset = queryset.filter(city__icontains=city)
    
    if min_rate:
        try:
            queryset = queryset.filter(
                Q(hourly_rate__gte=float(min_rate)) | Q(fixed_price__gte=float(min_rate))
            )
        except ValueError:
            pass
    
    if max_rate:
        try:
            queryset = queryset.filter(
                Q(hourly_rate__lte=float(max_rate)) | Q(fixed_price__lte=float(max_rate))
            )
        except ValueError:
            pass
    
    # Order by creation date and priority
    queryset = queryset.order_by('-priority', '-created')
    
    serializer = GigJobListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def job_statistics(request, job_id):
    """
    Get statistics for a specific job.
    """
    job = get_object_or_404(GigJob, id=job_id)
    
    # Check permissions
    if not (request.user == job.client or 
            (job.assigned_freelancer and request.user == job.assigned_freelancer.user)):
        return Response(
            {'error': 'You don\'t have permission to access this job.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    applications_count = job.applications.count()
    milestones_count = job.milestones.count()
    completed_milestones = job.milestones.filter(is_completed=True).count()
    photos_count = job.photos.count()
    messages_count = job.messages.count()
    
    avg_review_rating = job.reviews.aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
    
    stats = {
        'job_id': job.job_id,
        'title': job.title,
        'status': job.status,
        'applications_count': applications_count,
        'milestones_count': milestones_count,
        'completed_milestones': completed_milestones,
        'milestone_completion_rate': (completed_milestones / milestones_count * 100) if milestones_count > 0 else 0,
        'photos_count': photos_count,
        'messages_count': messages_count,
        'average_rating': float(avg_review_rating),
        'total_reviews': job.reviews.count()
    }
    
    return Response(stats)

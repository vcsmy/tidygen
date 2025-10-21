"""
Views for freelancers app API.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsOwnerOrReadOnly
from .models import (
    Freelancer, FreelancerDocument, FreelancerAvailability,
    FreelancerSkill, FreelancerSkillAssignment, FreelancerReview
)
from .serializers import (
    FreelancerListSerializer, FreelancerDetailSerializer, FreelancerCreateSerializer,
    FreelancerUpdateSerializer, FreelancerDocumentSerializer, FreelancerAvailabilitySerializer,
    FreelancerAvailabilityUpdateSerializer, FreelancerDocumentUploadSerializer,
    FreelancerSkillSerializer, FreelancerSkillAssignmentSerializer, FreelancerReviewSerializer
)
from .filters import FreelancerFilter

User = get_user_model()


@extend_schema(tags=['Freelancers'])
class FreelancerListCreateView(generics.ListCreateAPIView):
    """
    List all freelancers or create a new freelancer.
    """
    queryset = Freelancer.objects.select_related('user').prefetch_related(
        'availability_slots', 'skill_assignments__skill', 'reviews'
    ).all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FreelancerFilter
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FreelancerCreateSerializer
        return FreelancerListSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method == 'GET':
            # Anyone can view freelancer list
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'POST':
            # Only authenticated users can register as freelancers
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Set the user relationship when creating a freelancer."""
        serializer.save(user=self.request.user)


@extend_schema(tags=['Freelancers'])
class FreelancerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a freelancer instance.
    """
    queryset = Freelancer.objects.select_related('user').prefetch_related(
        'documents', 'availability_slots', 'skill_assignments__skill', 'reviews'
    ).all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FreelancerUpdateSerializer
        return FreelancerDetailSerializer
    
    def get_object(self):
        """Get freelancer by ID or by user if requesting own profile."""
        pk = self.kwargs.get('pk')
        if pk == 'me' and self.request.user.is_authenticated:
            try:
                return self.request.user.freelancer_profile
            except Freelancer.DoesNotExist:
                from django.http import Http404
                raise Http404("Freelancer profile not found")
        return super().get_object()


@extend_schema(tags=['Freelancers'])
class FreelancerAvailabilityView(generics.ListCreateAPIView):
    """
    List and manage freelancer availability.
    """
    serializer_class = FreelancerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        return FreelancerAvailability.objects.filter(freelancer=freelancer)
    
    def perform_create(self, serializer):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        serializer.save(freelancer=freelancer)


class FreelancerAvailabilityUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update or delete specific availability slot.
    """
    serializer_class = FreelancerAvailabilityUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        return FreelancerAvailability.objects.filter(freelancer=freelancer)


class FreelancerDocumentView(generics.ListCreateAPIView):
    """
    List and upload freelancer documents.
    """
    serializer_class = FreelancerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        return FreelancerDocument.objects.filter(freelancer=freelancer)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FreelancerDocumentUploadSerializer
        return FreelancerDocumentSerializer
    
    def perform_create(self, serializer):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        serializer.save(freelancer=freelancer)


class FreelancerDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific document.
    """
    serializer_class = FreelancerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        return FreelancerDocument.objects.filter(freelancer=freelancer)


class FreelancerSkillsView(APIView):
    """
    Manage freelancer skills and skill assignments.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, freelancer_id=None):
        """Get available skills or freelancer's assigned skills."""
        if freelancer_id:
            # Get freelancer's assigned skills
            freelancer = get_object_or_404(Freelancer, id=freelancer_id)
            self.check_object_permissions(request, freelancer)
            skill_assignments = FreelancerSkillAssignment.objects.filter(
                freelancer=freelancer
            ).select_related('skill')
            serializer = FreelancerSkillAssignmentSerializer(skill_assignments, many=True)
        else:
            # Get all available skills
            skills = FreelancerSkill.objects.all()
            serializer = FreelancerSkillSerializer(skills, many=True)
        
        return Response(serializer.data)
    
    def post(self, request, freelancer_id):
        """Assign a skill to a freelancer."""
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(request, freelancer)
        
        serializer = FreelancerSkillAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(freelancer=freelancer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FreelancerSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a freelancer skill assignment.
    """
    serializer_class = FreelancerSkillAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        self.check_object_permissions(self.request, freelancer)
        return FreelancerSkillAssignment.objects.filter(freelancer=freelancer)


class FreelancerReviewsView(generics.ListCreateAPIView):
    """
    List and create reviews for a freelancer.
    """
    serializer_class = FreelancerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        return FreelancerReview.objects.filter(freelancer=freelancer)
    
    def perform_create(self, serializer):
        freelancer_id = self.kwargs.get('freelancer_id')
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        serializer.save(freelancer=freelancer, reviewer=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def freelancer_stats(request, freelancer_id):
    """
    Get statistics for a specific freelancer.
    """
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    # Calculate average ratings
    reviews = FreelancerReview.objects.filter(freelancer=freelancer)
    avg_ratings = reviews.aggregate(
        overall=Avg('overall_rating'),
        quality=Avg('quality_rating'),
        punctuality=Avg('punctuality_rating'),
        communication=Avg('communication_rating'),
        professionalism=Avg('professionalism_rating')
    )
    
    stats = {
        'freelancer_id': freelancer.freelancer_id,
        'name': freelancer.full_name,
        'total_jobs_completed': freelancer.total_jobs_completed,
        'rating': float(freelancer.rating),
        'on_time_percentage': float(freelancer.on_time_percentage),
        'completion_rate': float(freelancer.completion_rate),
        'total_reviews': reviews.count(),
        'average_ratings': {
            'overall': float(avg_ratings['overall'] or 0),
            'quality': float(avg_ratings['quality'] or 0),
            'punctuality': float(avg_ratings['punctuality'] or 0),
            'communication': float(avg_ratings['communication'] or 0),
            'professionalism': float(avg_ratings['professionalism'] or 0),
        }
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_freelancers(request):
    """
    Search freelancers by various criteria.
    """
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    cleaning_type = request.GET.get('cleaning_type', '').strip()
    max_rate = request.GET.get('max_rate')
    min_rating = request.GET.get('min_rating')
    
    queryset = Freelancer.objects.filter(
        status='active',
        is_available=True
    ).select_related('user')
    
    if query:
        queryset = queryset.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(special_skills__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )
    
    if city:
        queryset = queryset.filter(city__icontains=city)
    
    if cleaning_type:
        queryset = queryset.filter(cleaning_types__contains=[cleaning_type])
    
    if max_rate:
        try:
            queryset = queryset.filter(hourly_rate__lte=float(max_rate))
        except ValueError:
            pass
    
    if min_rating:
        try:
            queryset = queryset.filter(rating__gte=float(min_rating))
        except ValueError:
            pass
    
    # Order by rating and availability
    queryset = queryset.order_by('-rating', '-is_available')
    
    serializer = FreelancerListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_document(request, freelancer_id, document_id):
    """
    Verify a freelancer document (admin/staff only).
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Only staff members can verify documents.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    document = get_object_or_404(
        FreelancerDocument,
        id=document_id,
        freelancer_id=freelancer_id
    )
    
    is_verified = request.data.get('is_verified', True)
    verification_notes = request.data.get('verification_notes', '')
    
    document.is_verified = is_verified
    document.verified_by = request.user
    document.verification_notes = verification_notes
    document.save()
    
    serializer = FreelancerDocumentSerializer(document)
    return Response(serializer.data)

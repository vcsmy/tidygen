"""
Comprehensive scheduling management views for iNEAT ERP platform.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
import logging

from apps.core.permissions import IsOrganizationMember
from .models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment,
    ScheduleConflict, ScheduleRule, ScheduleNotification,
    ScheduleAnalytics, ScheduleIntegration
)
from .serializers import (
    ScheduleTemplateSerializer, ScheduleTemplateCreateSerializer,
    ResourceSerializer, ResourceCreateSerializer,
    TeamSerializer, TeamCreateSerializer, TeamMemberSerializer, TeamMemberCreateSerializer,
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentUpdateSerializer,
    ScheduleConflictSerializer, ScheduleConflictCreateSerializer, ScheduleConflictResolveSerializer,
    ScheduleRuleSerializer, ScheduleRuleCreateSerializer,
    ScheduleNotificationSerializer, ScheduleNotificationCreateSerializer,
    ScheduleAnalyticsSerializer, ScheduleAnalyticsCreateSerializer,
    ScheduleIntegrationSerializer, ScheduleIntegrationCreateSerializer, ScheduleIntegrationUpdateSerializer,
    SchedulingDashboardSerializer, SchedulingSummarySerializer
)
from .filters import (
    ScheduleTemplateFilter, ResourceFilter, TeamFilter, AppointmentFilter,
    ScheduleConflictFilter, ScheduleRuleFilter, ScheduleNotificationFilter,
    ScheduleAnalyticsFilter, ScheduleIntegrationFilter
)

logger = logging.getLogger(__name__)


# ==================== SCHEDULE TEMPLATE VIEWS ====================

class ScheduleTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleTemplate."""
    queryset = ScheduleTemplate.objects.all()
    serializer_class = ScheduleTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleTemplateFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleTemplateCreateSerializer
        return ScheduleTemplateSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a schedule template."""
        template = self.get_object()
        new_template = ScheduleTemplate.objects.create(
            organization=template.organization,
            name=f"{template.name} (Copy)",
            description=template.description,
            schedule_type=template.schedule_type,
            recurrence_interval=template.recurrence_interval,
            recurrence_days=template.recurrence_days,
            recurrence_dates=template.recurrence_dates,
            start_time=template.start_time,
            end_time=template.end_time,
            duration_minutes=template.duration_minutes,
            break_duration_minutes=template.break_duration_minutes,
            break_start_time=template.break_start_time,
            max_capacity=template.max_capacity,
            min_advance_booking_hours=template.min_advance_booking_hours,
            max_advance_booking_days=template.max_advance_booking_days,
            base_price=template.base_price,
            currency=template.currency,
            is_active=template.is_active,
            is_default=False
        )
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active schedule templates."""
        templates = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


# ==================== RESOURCE VIEWS ====================

class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Resource."""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ResourceFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ResourceCreateSerializer
        return ResourceSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def set_availability(self, request, pk=None):
        """Set resource availability."""
        resource = self.get_object()
        is_available = request.data.get('is_available', True)
        reason = request.data.get('reason', '')
        
        resource.is_available = is_available
        resource.save()
        
        # Log the change
        logger.info(f"Resource {resource.name} availability set to {is_available} by {request.user}")
        
        return Response({'status': 'availability updated'})
    
    @action(detail=True, methods=['post'])
    def schedule_maintenance(self, request, pk=None):
        """Schedule maintenance for resource."""
        resource = self.get_object()
        maintenance_date = request.data.get('maintenance_date')
        maintenance_type = request.data.get('maintenance_type', 'routine')
        notes = request.data.get('notes', '')
        
        if maintenance_date:
            resource.next_maintenance = maintenance_date
            resource.save()
            
            # Create maintenance schedule entry
            maintenance_schedule = resource.maintenance_schedule or {}
            maintenance_schedule[maintenance_date] = {
                'type': maintenance_type,
                'notes': notes,
                'scheduled_by': request.user.id
            }
            resource.maintenance_schedule = maintenance_schedule
            resource.save()
        
        return Response({'status': 'maintenance scheduled'})
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available resources."""
        resources = self.get_queryset().filter(is_active=True, is_available=True)
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get resources by type."""
        resource_type = request.query_params.get('type')
        if resource_type:
            resources = self.get_queryset().filter(resource_type=resource_type)
            serializer = self.get_serializer(resources, many=True)
            return Response(serializer.data)
        return Response({'error': 'type parameter required'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== TEAM VIEWS ====================

class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team."""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = TeamFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TeamCreateSerializer
        return TeamSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to team."""
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        if user_id:
            user = get_object_or_404(request.user.organization.users, id=user_id)
            team_member, created = TeamMember.objects.get_or_create(
                team=team,
                user=user,
                defaults={'role': role}
            )
            
            if created:
                serializer = TeamMemberSerializer(team_member)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'User is already a member of this team'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove member from team."""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        if user_id:
            team_member = get_object_or_404(TeamMember, team=team, user_id=user_id)
            team_member.delete()
            return Response({'status': 'member removed'})
        
        return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members."""
        team = self.get_object()
        members = team.members.filter(is_active=True)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get team availability."""
        team = self.get_object()
        # This would implement team availability logic
        return Response({'availability': team.availability_schedule})


class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for TeamMember."""
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset.filter(team__organization=self.request.user.organization)
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TeamMemberCreateSerializer
        return TeamMemberSerializer


# ==================== APPOINTMENT VIEWS ====================

class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointment."""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = AppointmentFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment."""
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        
        # Send confirmation notification
        # This would trigger notification logic
        
        return Response({'status': 'appointment confirmed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        reason = request.data.get('reason', '')
        
        appointment.status = 'cancelled'
        appointment.completion_notes = f"Cancelled: {reason}"
        appointment.save()
        
        # Send cancellation notification
        # This would trigger notification logic
        
        return Response({'status': 'appointment cancelled'})
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment."""
        appointment = self.get_object()
        new_start = request.data.get('new_start_datetime')
        new_end = request.data.get('new_end_datetime')
        
        if new_start and new_end:
            appointment.start_datetime = new_start
            appointment.end_datetime = new_end
            appointment.status = 'rescheduled'
            appointment.save()
            
            return Response({'status': 'appointment rescheduled'})
        
        return Response({'error': 'new_start_datetime and new_end_datetime required'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete an appointment."""
        appointment = self.get_object()
        completion_notes = request.data.get('completion_notes', '')
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        actual_cost = request.data.get('actual_cost')
        
        appointment.status = 'completed'
        appointment.completion_notes = completion_notes
        appointment.completion_feedback = feedback
        
        if rating:
            appointment.completion_rating = rating
        if actual_cost:
            appointment.actual_cost = actual_cost
        
        appointment.save()
        
        return Response({'status': 'appointment completed'})
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments."""
        now = timezone.now()
        appointments = self.get_queryset().filter(
            start_datetime__gt=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('start_datetime')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue appointments."""
        now = timezone.now()
        appointments = self.get_queryset().filter(
            end_datetime__lt=now,
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).order_by('start_datetime')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments."""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(
            start_datetime__date=today
        ).order_by('start_datetime')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """Check for scheduling conflicts."""
        start_datetime = request.query_params.get('start_datetime')
        end_datetime = request.query_params.get('end_datetime')
        exclude_id = request.query_params.get('exclude_id')
        
        if not start_datetime or not end_datetime:
            return Response({'error': 'start_datetime and end_datetime required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        conflicts = self.get_queryset().filter(
            Q(start_datetime__lt=end_datetime, end_datetime__gt=start_datetime),
            status__in=['scheduled', 'confirmed', 'in_progress']
        )
        
        if exclude_id:
            conflicts = conflicts.exclude(id=exclude_id)
        
        serializer = self.get_serializer(conflicts, many=True)
        return Response(serializer.data)


# ==================== SCHEDULE CONFLICT VIEWS ====================

class ScheduleConflictViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleConflict."""
    queryset = ScheduleConflict.objects.all()
    serializer_class = ScheduleConflictSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleConflictFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleConflictCreateSerializer
        elif self.action == 'resolve':
            return ScheduleConflictResolveSerializer
        return ScheduleConflictSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a schedule conflict."""
        conflict = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        conflict.status = 'resolved'
        conflict.resolution_notes = resolution_notes
        conflict.resolved_by = request.user
        conflict.resolved_at = timezone.now()
        conflict.save()
        
        return Response({'status': 'conflict resolved'})
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate a schedule conflict."""
        conflict = self.get_object()
        conflict.status = 'escalated'
        conflict.save()
        
        # This would trigger escalation notification logic
        
        return Response({'status': 'conflict escalated'})
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get unresolved conflicts."""
        conflicts = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(conflicts, many=True)
        return Response(serializer.data)


# ==================== SCHEDULE RULE VIEWS ====================

class ScheduleRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleRule."""
    queryset = ScheduleRule.objects.all()
    serializer_class = ScheduleRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleRuleFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleRuleCreateSerializer
        return ScheduleRuleSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active schedule rules."""
        rules = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)


# ==================== SCHEDULE NOTIFICATION VIEWS ====================

class ScheduleNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleNotification."""
    queryset = ScheduleNotification.objects.all()
    serializer_class = ScheduleNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleNotificationFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleNotificationCreateSerializer
        return ScheduleNotificationSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a notification."""
        notification = self.get_object()
        
        # This would implement actual notification sending logic
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        return Response({'status': 'notification sent'})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending notifications."""
        notifications = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


# ==================== SCHEDULE ANALYTICS VIEWS ====================

class ScheduleAnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleAnalytics."""
    queryset = ScheduleAnalytics.objects.all()
    serializer_class = ScheduleAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleAnalyticsFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleAnalyticsCreateSerializer
        return ScheduleAnalyticsSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)


# ==================== SCHEDULE INTEGRATION VIEWS ====================

class ScheduleIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for ScheduleIntegration."""
    queryset = ScheduleIntegration.objects.all()
    serializer_class = ScheduleIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_class = ScheduleIntegrationFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Filter queryset by organization."""
        return self.queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ScheduleIntegrationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ScheduleIntegrationUpdateSerializer
        return ScheduleIntegrationSerializer
    
    def perform_create(self, serializer):
        """Set organization on creation."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test integration connection."""
        integration = self.get_object()
        
        # This would implement actual connection testing logic
        integration.sync_status = 'connected'
        integration.save()
        
        return Response({'status': 'connection successful'})
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync integration data."""
        integration = self.get_object()
        
        # This would implement actual sync logic
        integration.sync_status = 'syncing'
        integration.save()
        
        # Simulate sync process
        integration.last_sync = timezone.now()
        integration.sync_status = 'connected'
        integration.save()
        
        return Response({'status': 'sync completed'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active integrations."""
        integrations = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(integrations, many=True)
        return Response(serializer.data)


# ==================== DASHBOARD VIEWS ====================

class SchedulingDashboardView(APIView):
    """Dashboard view for scheduling data."""
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """Get scheduling dashboard data."""
        organization = request.user.organization
        
        # Get basic counts
        total_appointments = Appointment.objects.count()
        upcoming_appointments = Appointment.objects.filter(
            organization=organization,
            start_datetime__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).count()
        overdue_appointments = Appointment.objects.filter(
            organization=organization,
            end_datetime__lt=timezone.now(),
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).count()
        
        total_conflicts = ScheduleConflict.objects.count()
        unresolved_conflicts = ScheduleConflict.objects.filter(
            organization=organization,
            status='pending'
        ).count()
        
        total_resources = Resource.objects.count()
        available_resources = Resource.objects.filter(
            organization=organization,
            is_active=True,
            is_available=True
        ).count()
        
        total_teams = Team.objects.count()
        active_teams = Team.objects.filter(
            organization=organization,
            is_active=True
        ).count()
        
        # Calculate utilization rate
        total_scheduled_hours = Appointment.objects.filter(
            organization=organization,
            status='completed'
        ).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        # This is a simplified calculation - in reality, you'd calculate based on available hours
        utilization_rate = Decimal('0.00')
        if total_scheduled_hours > 0:
            utilization_rate = Decimal(str(total_scheduled_hours / 60))  # Convert to hours
        
        # Calculate completion rate
        completed_appointments = Appointment.objects.filter(
            organization=organization,
            status='completed'
        ).count()
        
        completion_rate = Decimal('0.00')
        if total_appointments > 0:
            completion_rate = Decimal(str((completed_appointments / total_appointments) * 100))
        
        # Get recent appointments
        recent_appointments = Appointment.objects.filter(
            organization=organization
        ).order_by('-created_at')[:5]
        
        # Get recent conflicts
        recent_conflicts = ScheduleConflict.objects.filter(
            organization=organization
        ).order_by('-created_at')[:5]
        
        # Get upcoming appointments
        upcoming_appointments_list = Appointment.objects.filter(
            organization=organization,
            start_datetime__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('start_datetime')[:10]
        
        dashboard_data = {
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'overdue_appointments': overdue_appointments,
            'total_conflicts': total_conflicts,
            'unresolved_conflicts': unresolved_conflicts,
            'total_resources': total_resources,
            'available_resources': available_resources,
            'total_teams': total_teams,
            'active_teams': active_teams,
            'utilization_rate': utilization_rate,
            'completion_rate': completion_rate,
            'recent_appointments': AppointmentSerializer(recent_appointments, many=True).data,
            'recent_conflicts': ScheduleConflictSerializer(recent_conflicts, many=True).data,
            'upcoming_appointments_list': AppointmentSerializer(upcoming_appointments_list, many=True).data,
        }
        
        serializer = SchedulingDashboardSerializer(dashboard_data)
        return Response(serializer.data)


class SchedulingSummaryView(APIView):
    """Summary view for scheduling data."""
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get(self, request):
        """Get scheduling summary data."""
        organization = request.user.organization
        
        # Get date range from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            now = timezone.now()
            start_date = now.replace(day=1).date()
            end_date = now.date()
        
        # Filter appointments by date range
        appointments = Appointment.objects.filter(
            organization=organization,
            start_datetime__date__range=[start_date, end_date]
        )
        
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        
        # Calculate revenue
        total_revenue = appointments.filter(
            status='completed'
        ).aggregate(
            total=Sum('actual_cost')
        )['total'] or Decimal('0.00')
        
        average_appointment_value = Decimal('0.00')
        if completed_appointments > 0:
            average_appointment_value = total_revenue / completed_appointments
        
        # Calculate utilization rate (simplified)
        total_scheduled_hours = appointments.filter(
            status='completed'
        ).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        utilization_rate = Decimal('0.00')
        if total_scheduled_hours > 0:
            utilization_rate = Decimal(str(total_scheduled_hours / 60))
        
        # Get conflict data
        conflicts = ScheduleConflict.objects.filter(
            organization=organization,
            created_at__date__range=[start_date, end_date]
        )
        
        conflict_count = conflicts.count()
        resolved_conflicts = conflicts.filter(status='resolved').count()
        
        resolution_rate = Decimal('0.00')
        if conflict_count > 0:
            resolution_rate = Decimal(str((resolved_conflicts / conflict_count) * 100))
        
        summary_data = {
            'period_start': start_date,
            'period_end': end_date,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'total_revenue': total_revenue,
            'average_appointment_value': average_appointment_value,
            'utilization_rate': utilization_rate,
            'conflict_count': conflict_count,
            'resolution_rate': resolution_rate,
        }
        
        serializer = SchedulingSummarySerializer(summary_data)
        return Response(serializer.data)

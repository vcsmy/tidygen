"""
Views for Field Operations models.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema

from .models import (
    FieldTeam, TeamMember, ServiceRoute, RouteStop, 
    FieldJob, JobEquipment, DispatchLog
)
from .serializers import (
    FieldTeamSerializer, TeamMemberSerializer, ServiceRouteSerializer,
    RouteStopSerializer, FieldJobSerializer, JobEquipmentSerializer,
    DispatchLogSerializer, FieldTeamSummarySerializer, FieldJobSummarySerializer,
    ServiceRouteSummarySerializer
)


@extend_schema(tags=['Field Operations'])
class FieldTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for FieldTeam model."""
    
    queryset = FieldTeam.objects.all()
    serializer_class = FieldTeamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team_type', 'status', 'home_base', 'assigned_vehicle']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'total_jobs_completed', 'average_rating']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FieldTeamSummarySerializer
        return FieldTeamSerializer
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members for a specific team."""
        team = self.get_object()
        members = team.members.filter(is_active=True)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team."""
        team = self.get_object()
        data = request.data.copy()
        data['team'] = team.id
        
        serializer = TeamMemberSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """Get jobs assigned to a specific team."""
        team = self.get_object()
        jobs = team.assigned_jobs.all()
        serializer = FieldJobSummarySerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for field teams."""
        total_teams = FieldTeam.objects.count()
        active_teams = FieldTeam.objects.filter(status='active').count()
        total_members = TeamMember.objects.filter(is_active=True).count()
        
        # Team types distribution
        team_types = FieldTeam.objects.values('team_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Status distribution
        status_distribution = FieldTeam.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_teams': total_teams,
            'active_teams': active_teams,
            'total_members': total_members,
            'team_types': list(team_types),
            'status_distribution': list(status_distribution)
        })


@extend_schema(tags=['Field Operations'])
class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for TeamMember model."""
    
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'role', 'is_team_leader', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name', 'team__name']
    ordering_fields = ['assigned_date', 'individual_rating', 'jobs_completed']
    ordering = ['team', 'role']


@extend_schema(tags=['Field Operations'])
class ServiceRouteViewSet(viewsets.ModelViewSet):
    """ViewSet for ServiceRoute model."""
    
    queryset = ServiceRoute.objects.all()
    serializer_class = ServiceRouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route_type', 'status', 'assigned_team', 'scheduled_date']
    search_fields = ['name', 'description']
    ordering_fields = ['scheduled_date', 'start_time', 'efficiency_rating']
    ordering = ['-scheduled_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceRouteSummarySerializer
        return ServiceRouteSerializer
    
    @action(detail=True, methods=['get'])
    def stops(self, request, pk=None):
        """Get stops for a specific route."""
        route = self.get_object()
        stops = route.stops.all()
        serializer = RouteStopSerializer(stops, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_stop(self, request, pk=None):
        """Add a stop to the route."""
        route = self.get_object()
        data = request.data.copy()
        data['route'] = route.id
        
        serializer = RouteStopSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start_route(self, request, pk=None):
        """Start a route."""
        route = self.get_object()
        if route.status != 'planned':
            return Response(
                {'error': 'Route can only be started if it is planned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route.status = 'active'
        route.save()
        
        # Log the route start
        DispatchLog.objects.create(
            route=route,
            team=route.assigned_team,
            log_type='route_change',
            message=f'Route {route.name} started',
            created_by=request.user
        )
        
        serializer = self.get_serializer(route)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_route(self, request, pk=None):
        """Complete a route."""
        route = self.get_object()
        if route.status != 'active':
            return Response(
                {'error': 'Route can only be completed if it is active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route.status = 'completed'
        route.actual_duration = timezone.now() - route.start_time if route.start_time else None
        route.save()
        
        # Log the route completion
        DispatchLog.objects.create(
            route=route,
            team=route.assigned_team,
            log_type='route_change',
            message=f'Route {route.name} completed',
            created_by=request.user
        )
        
        serializer = self.get_serializer(route)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for service routes."""
        total_routes = ServiceRoute.objects.count()
        active_routes = ServiceRoute.objects.filter(status='active').count()
        completed_routes = ServiceRoute.objects.filter(status='completed').count()
        
        # Route types distribution
        route_types = ServiceRoute.objects.values('route_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Status distribution
        status_distribution = ServiceRoute.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_routes': total_routes,
            'active_routes': active_routes,
            'completed_routes': completed_routes,
            'route_types': list(route_types),
            'status_distribution': list(status_distribution)
        })


@extend_schema(tags=['Field Operations'])
class RouteStopViewSet(viewsets.ModelViewSet):
    """ViewSet for RouteStop model."""
    
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route', 'stop_type', 'status', 'client']
    search_fields = ['address', 'service_notes']
    ordering_fields = ['sequence_number', 'estimated_arrival', 'actual_arrival']
    ordering = ['route', 'sequence_number']
    
    @action(detail=True, methods=['post'])
    def arrive(self, request, pk=None):
        """Mark stop as arrived."""
        stop = self.get_object()
        if stop.status != 'pending':
            return Response(
                {'error': 'Stop can only be marked as arrived if it is pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stop.status = 'in_progress'
        stop.actual_arrival = timezone.now()
        stop.save()
        
        serializer = self.get_serializer(stop)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark stop as completed."""
        stop = self.get_object()
        if stop.status != 'in_progress':
            return Response(
                {'error': 'Stop can only be completed if it is in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stop.status = 'completed'
        stop.actual_departure = timezone.now()
        if stop.actual_arrival:
            stop.actual_duration = stop.actual_departure - stop.actual_arrival
        stop.save()
        
        serializer = self.get_serializer(stop)
        return Response(serializer.data)


@extend_schema(tags=['Field Operations'])
class FieldJobViewSet(viewsets.ModelViewSet):
    """ViewSet for FieldJob model."""
    
    queryset = FieldJob.objects.all()
    serializer_class = FieldJobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'priority', 'status', 'client', 'assigned_team', 'scheduled_date']
    search_fields = ['job_number', 'title', 'description', 'service_address']
    ordering_fields = ['scheduled_date', 'scheduled_start_time', 'priority']
    ordering = ['-scheduled_date', 'scheduled_start_time']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FieldJobSummarySerializer
        return FieldJobSerializer
    
    @action(detail=True, methods=['get'])
    def equipment_used(self, request, pk=None):
        """Get equipment used for a specific job."""
        job = self.get_object()
        equipment = job.equipment_used.all()
        serializer = JobEquipmentSerializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_team(self, request, pk=None):
        """Assign a team to the job."""
        job = self.get_object()
        team_id = request.data.get('team_id')
        
        if not team_id:
            return Response(
                {'error': 'team_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            team = FieldTeam.objects.get(id=team_id)
            job.assigned_team = team
            job.status = 'assigned'
            job.save()
            
            # Log the assignment
            DispatchLog.objects.create(
                job=job,
                team=team,
                log_type='assignment',
                message=f'Job {job.job_number} assigned to team {team.name}',
                created_by=request.user
            )
            
            serializer = self.get_serializer(job)
            return Response(serializer.data)
        except FieldTeam.DoesNotExist:
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def start_job(self, request, pk=None):
        """Start a job."""
        job = self.get_object()
        if job.status != 'assigned':
            return Response(
                {'error': 'Job can only be started if it is assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'in_progress'
        job.save()
        
        # Log the job start
        DispatchLog.objects.create(
            job=job,
            team=job.assigned_team,
            log_type='update',
            message=f'Job {job.job_number} started',
            created_by=request.user
        )
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_job(self, request, pk=None):
        """Complete a job."""
        job = self.get_object()
        if job.status != 'in_progress':
            return Response(
                {'error': 'Job can only be completed if it is in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'completed'
        job.actual_duration = timezone.now() - job.scheduled_start_time if job.scheduled_start_time else None
        job.save()
        
        # Log the job completion
        DispatchLog.objects.create(
            job=job,
            team=job.assigned_team,
            log_type='update',
            message=f'Job {job.job_number} completed',
            created_by=request.user
        )
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for field jobs."""
        total_jobs = FieldJob.objects.count()
        scheduled_jobs = FieldJob.objects.filter(status='scheduled').count()
        in_progress_jobs = FieldJob.objects.filter(status='in_progress').count()
        completed_jobs = FieldJob.objects.filter(status='completed').count()
        
        # Job types distribution
        job_types = FieldJob.objects.values('job_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Priority distribution
        priority_distribution = FieldJob.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average satisfaction rating
        avg_satisfaction = FieldJob.objects.filter(
            client_satisfaction_rating__isnull=False
        ).aggregate(avg_rating=Avg('client_satisfaction_rating'))['avg_rating'] or 0
        
        return Response({
            'total_jobs': total_jobs,
            'scheduled_jobs': scheduled_jobs,
            'in_progress_jobs': in_progress_jobs,
            'completed_jobs': completed_jobs,
            'job_types': list(job_types),
            'priority_distribution': list(priority_distribution),
            'average_satisfaction_rating': round(avg_satisfaction, 2)
        })


@extend_schema(tags=['Field Operations'])
class JobEquipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for JobEquipment model."""
    
    queryset = JobEquipment.objects.all()
    serializer_class = JobEquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'equipment']
    search_fields = ['job__job_number', 'equipment__name']
    ordering_fields = ['created']
    ordering = ['-created']


@extend_schema(tags=['Field Operations'])
class DispatchLogViewSet(viewsets.ModelViewSet):
    """ViewSet for DispatchLog model."""
    
    queryset = DispatchLog.objects.all()
    serializer_class = DispatchLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['log_type', 'team', 'created_by']
    search_fields = ['message', 'job__job_number', 'team__name']
    ordering_fields = ['timestamp', 'created']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary for dispatch logs."""
        total_logs = DispatchLog.objects.count()
        today_logs = DispatchLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        # Log types distribution
        log_types = DispatchLog.objects.values('log_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent activity (last 24 hours)
        recent_activity = DispatchLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-timestamp')[:10]
        
        serializer = DispatchLogSerializer(recent_activity, many=True)
        
        return Response({
            'total_logs': total_logs,
            'today_logs': today_logs,
            'log_types': list(log_types),
            'recent_activity': serializer.data
        })

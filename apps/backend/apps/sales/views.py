"""
Sales and client management views for TidyGen ERP platform.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, F, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.core.permissions import IsOrganizationMember
from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientTag, ClientTagAssignment, ClientInteraction,
    ClientSegment, ClientSegmentAssignment
)
from apps.sales.serializers import (
    ClientSerializer, ClientCreateSerializer, ClientListSerializer,
    IndividualClientSerializer, CorporateClientSerializer, ClientContactSerializer,
    ClientNoteSerializer, ClientDocumentSerializer, ClientTagSerializer,
    ClientTagAssignmentSerializer, ClientInteractionSerializer,
    ClientSegmentSerializer, ClientSegmentAssignmentSerializer,
    ClientDashboardSerializer, ClientAnalyticsSerializer, ClientInteractionAnalyticsSerializer
)
from apps.sales.filters import (
    ClientFilter, IndividualClientFilter, CorporateClientFilter,
    ClientContactFilter, ClientNoteFilter, ClientDocumentFilter,
    ClientInteractionFilter, ClientTagFilter, ClientSegmentFilter,
    ClientAnalyticsFilter, ClientInteractionAnalyticsFilter
)


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Client model."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientFilter
    search_fields = ['email', 'phone', 'city', 'state', 'country', 'industry', 'source']
    ordering_fields = ['created', 'last_contact_date', 'last_activity_date', 'credit_limit']
    ordering = ['-created']
    
    def get_queryset(self):
        return Client.objects.all().select_related('assigned_to', 'created_by').prefetch_related(
            'individual_client', 'corporate_client', 'contacts', 'notes',
            'documents', 'interactions', 'tag_assignments__tag',
            'segment_assignments__segment'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        elif self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """Add a contact to the client."""
        client = self.get_object()
        serializer = ClientContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to the client."""
        client = self.get_object()
        serializer = ClientNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client, related_user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_interaction(self, request, pk=None):
        """Add an interaction to the client."""
        client = self.get_object()
        serializer = ClientInteractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client, initiated_by=request.user)
            # Update last contact date
            client.last_contact_date = timezone.now()
            client.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_tag(self, request, pk=None):
        """Assign a tag to the client."""
        client = self.get_object()
        tag_id = request.data.get('tag_id')
        if not tag_id:
            return Response({'error': 'tag_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tag = ClientTag.objects.get(id=tag_id, organization=client.organization)
            assignment, created = ClientTagAssignment.objects.get_or_create(
                client=client,
                tag=tag,
                defaults={'assigned_by': request.user}
            )
            if created:
                return Response({'status': 'Tag assigned successfully'})
            else:
                return Response({'status': 'Tag already assigned'})
        except ClientTag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_tag(self, request, pk=None):
        """Remove a tag from the client."""
        client = self.get_object()
        tag_id = request.data.get('tag_id')
        if not tag_id:
            return Response({'error': 'tag_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            assignment = ClientTagAssignment.objects.get(client=client, tag_id=tag_id)
            assignment.delete()
            return Response({'status': 'Tag removed successfully'})
        except ClientTagAssignment.DoesNotExist:
            return Response({'error': 'Tag assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def assign_segment(self, request, pk=None):
        """Assign a segment to the client."""
        client = self.get_object()
        segment_id = request.data.get('segment_id')
        if not segment_id:
            return Response({'error': 'segment_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            segment = ClientSegment.objects.get(id=segment_id, organization=client.organization)
            assignment, created = ClientSegmentAssignment.objects.get_or_create(
                client=client,
                segment=segment,
                defaults={'assigned_by': request.user}
            )
            if created:
                return Response({'status': 'Segment assigned successfully'})
            else:
                return Response({'status': 'Segment already assigned'})
        except ClientSegment.DoesNotExist:
            return Response({'error': 'Segment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_segment(self, request, pk=None):
        """Remove a segment from the client."""
        client = self.get_object()
        segment_id = request.data.get('segment_id')
        if not segment_id:
            return Response({'error': 'segment_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            assignment = ClientSegmentAssignment.objects.get(client=client, segment_id=segment_id)
            assignment.delete()
            return Response({'status': 'Segment removed successfully'})
        except ClientSegmentAssignment.DoesNotExist:
            return Response({'error': 'Segment assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change client status."""
        client = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in [choice[0] for choice in Client.STATUS_CHOICES]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = client.status
        client.status = new_status
        client.save()
        
        # Add a note about the status change
        ClientNote.objects.create(
            client=client,
            note_type='general',
            title=f'Status changed from {old_status} to {new_status}',
            content=f'Client status was changed from {old_status} to {new_status}',
            related_user=request.user
        )
        
        return Response({'status': f'Status changed to {new_status}'})
    
    @action(detail=True, methods=['post'])
    def change_priority(self, request, pk=None):
        """Change client priority."""
        client = self.get_object()
        new_priority = request.data.get('priority')
        if not new_priority:
            return Response({'error': 'priority is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_priority not in [choice[0] for choice in Client.PRIORITY_CHOICES]:
            return Response({'error': 'Invalid priority'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_priority = client.priority
        client.priority = new_priority
        client.save()
        
        # Add a note about the priority change
        ClientNote.objects.create(
            client=client,
            note_type='general',
            title=f'Priority changed from {old_priority} to {new_priority}',
            content=f'Client priority was changed from {old_priority} to {new_priority}',
            related_user=request.user
        )
        
        return Response({'status': f'Priority changed to {new_priority}'})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get client analytics."""
        filter_backend = ClientAnalyticsFilter()
        queryset = filter_backend.filter_queryset(request, self.get_queryset(), None)
        
        # Basic counts
        total_clients = queryset.count()
        new_clients_this_month = queryset.filter(
            created__month=timezone.now().month,
            created__year=timezone.now().year
        ).count()
        active_clients = queryset.filter(status='active').count()
        
        # Conversion rate (prospects to active)
        prospects = queryset.filter(status='prospect').count()
        conversion_rate = (active_clients / prospects * 100) if prospects > 0 else 0
        
        # Average client value (placeholder - would need financial data)
        average_client_value = Decimal('0.00')
        
        # Client retention rate (placeholder - would need historical data)
        client_retention_rate = Decimal('85.00')
        
        # Top sources
        top_sources = queryset.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Client distribution
        client_distribution = [
            {'type': 'individual', 'count': queryset.filter(client_type='individual').count()},
            {'type': 'corporate', 'count': queryset.filter(client_type='corporate').count()}
        ]
        
        # Interaction trends (last 12 months)
        interaction_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_interactions = ClientInteraction.objects.filter(
                client__in=queryset,
                created__gte=month_start,
                created__lt=month_end
            ).count()
            
            interaction_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'interactions': month_interactions
            })
        
        interaction_trends.reverse()
        
        # Geographic distribution
        geographic_distribution = queryset.values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        analytics_data = {
            'total_clients': total_clients,
            'new_clients_this_month': new_clients_this_month,
            'active_clients': active_clients,
            'conversion_rate': float(conversion_rate),
            'average_client_value': float(average_client_value),
            'client_retention_rate': float(client_retention_rate),
            'top_sources': list(top_sources),
            'client_distribution': client_distribution,
            'interaction_trends': interaction_trends,
            'geographic_distribution': list(geographic_distribution)
        }
        
        serializer = ClientAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class IndividualClientViewSet(viewsets.ModelViewSet):
    """ViewSet for IndividualClient model."""
    queryset = IndividualClient.objects.all()
    serializer_class = IndividualClientSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = IndividualClientFilter
    search_fields = ['first_name', 'last_name', 'job_title', 'company']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        return IndividualClient.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client')


class CorporateClientViewSet(viewsets.ModelViewSet):
    """ViewSet for CorporateClient model."""
    queryset = CorporateClient.objects.all()
    serializer_class = CorporateClientSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CorporateClientFilter
    search_fields = ['company_name', 'legal_name', 'ceo_name', 'cfo_name', 'cto_name']
    ordering_fields = ['company_name', 'founded_year', 'annual_revenue']
    ordering = ['company_name']
    
    def get_queryset(self):
        return CorporateClient.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client')


class ClientContactViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientContact model."""
    queryset = ClientContact.objects.all()
    serializer_class = ClientContactSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientContactFilter
    search_fields = ['first_name', 'last_name', 'email', 'job_title']
    ordering_fields = ['first_name', 'last_name', 'is_primary']
    ordering = ['-is_primary', 'last_name', 'first_name']
    
    def get_queryset(self):
        return ClientContact.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client')


class ClientNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientNote model."""
    queryset = ClientNote.objects.all()
    serializer_class = ClientNoteSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientNoteFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created', 'related_date']
    ordering = ['-created']
    
    def get_queryset(self):
        return ClientNote.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client', 'related_user')


class ClientDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientDocument model."""
    queryset = ClientDocument.objects.all()
    serializer_class = ClientDocumentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientDocumentFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created', 'title', 'file_size']
    ordering = ['-created']
    
    def get_queryset(self):
        return ClientDocument.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client', 'uploaded_by')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ClientTagViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientTag model."""
    queryset = ClientTag.objects.all()
    serializer_class = ClientTagSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientTagFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']
    
    def get_queryset(self):
        return ClientTag.objects.all()
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class ClientTagAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientTagAssignment model."""
    queryset = ClientTagAssignment.objects.all()
    serializer_class = ClientTagAssignmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created']
    ordering = ['-created']
    
    def get_queryset(self):
        return ClientTagAssignment.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client', 'tag', 'assigned_by')


class ClientInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientInteraction model."""
    queryset = ClientInteraction.objects.all()
    serializer_class = ClientInteractionSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientInteractionFilter
    search_fields = ['subject', 'description', 'outcome']
    ordering_fields = ['created', 'follow_up_date']
    ordering = ['-created']
    
    def get_queryset(self):
        return ClientInteraction.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client', 'initiated_by')
    
    def perform_create(self, serializer):
        serializer.save(initiated_by=self.request.user)
        # Update client's last contact date
        client = serializer.validated_data['client']
        client.last_contact_date = timezone.now()
        client.save()
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get client interaction analytics."""
        filter_backend = ClientInteractionAnalyticsFilter()
        queryset = filter_backend.filter_queryset(request, self.get_queryset(), None)
        
        # Basic counts
        total_interactions = queryset.count()
        
        # Interactions by type
        interactions_by_type = queryset.values('interaction_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Interactions by user
        interactions_by_user = queryset.values(
            'initiated_by__first_name', 'initiated_by__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Average interactions per client
        unique_clients = queryset.values('client').distinct().count()
        average_interactions_per_client = (total_interactions / unique_clients) if unique_clients > 0 else 0
        
        # Interaction trends (last 12 months)
        interaction_trends = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_interactions = queryset.filter(
                created__gte=month_start,
                created__lt=month_end
            ).count()
            
            interaction_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'interactions': month_interactions
            })
        
        interaction_trends.reverse()
        
        # Follow-up information
        follow_up_required = queryset.filter(requires_follow_up=True).count()
        overdue_follow_ups = queryset.filter(
            requires_follow_up=True,
            follow_up_date__lt=timezone.now()
        ).count()
        
        analytics_data = {
            'total_interactions': total_interactions,
            'interactions_by_type': list(interactions_by_type),
            'interactions_by_user': list(interactions_by_user),
            'average_interactions_per_client': float(average_interactions_per_client),
            'interaction_trends': interaction_trends,
            'follow_up_required': follow_up_required,
            'overdue_follow_ups': overdue_follow_ups
        }
        
        serializer = ClientInteractionAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class ClientSegmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientSegment model."""
    queryset = ClientSegment.objects.all()
    serializer_class = ClientSegmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientSegmentFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']
    
    def get_queryset(self):
        return ClientSegment.objects.filter(organization=self.request.user.organization_memberships.first().organization)
    
    def perform_create(self, serializer):
        organization = self.request.user.organization_memberships.first().organization
        serializer.save(organization=organization)


class ClientSegmentAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientSegmentAssignment model."""
    queryset = ClientSegmentAssignment.objects.all()
    serializer_class = ClientSegmentAssignmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['assigned_date']
    ordering = ['-assigned_date']
    
    def get_queryset(self):
        return ClientSegmentAssignment.objects.filter(
            client__organization=self.request.user.organization_memberships.first().organization
        ).select_related('client', 'segment', 'assigned_by')


class ClientDashboardViewSet(viewsets.ViewSet):
    """ViewSet for client dashboard data."""
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get client dashboard overview."""
        organization = request.user.organization_memberships.first().organization
        clients = Client.objects
        
        # Basic counts
        total_clients = clients.count()
        active_clients = clients.filter(status='active').count()
        prospect_clients = clients.filter(status='prospect').count()
        individual_clients = clients.filter(client_type='individual').count()
        corporate_clients = clients.filter(client_type='corporate').count()
        
        # Clients by status
        clients_by_status = clients.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Clients by type
        clients_by_type = [
            {'type': 'individual', 'count': individual_clients},
            {'type': 'corporate', 'count': corporate_clients}
        ]
        
        # Clients by priority
        clients_by_priority = clients.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent clients (last 10)
        recent_clients = clients.order_by('-created')[:10].values(
            'id', 'client_type', 'status', 'priority', 'email', 'city', 'created'
        )
        
        # Top clients by interactions
        top_clients_by_interactions = clients.annotate(
            interaction_count=Count('interactions')
        ).order_by('-interaction_count')[:5].values(
            'id', 'client_type', 'status', 'email', 'city', 'interaction_count'
        )
        
        # Clients by source
        clients_by_source = clients.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Monthly client growth (last 12 months)
        monthly_client_growth = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            month_clients = clients.filter(
                created__gte=month_start,
                created__lt=month_end
            ).count()
            
            monthly_client_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'clients': month_clients
            })
        
        monthly_client_growth.reverse()
        
        dashboard_data = {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'prospect_clients': prospect_clients,
            'individual_clients': individual_clients,
            'corporate_clients': corporate_clients,
            'clients_by_status': list(clients_by_status),
            'clients_by_type': clients_by_type,
            'clients_by_priority': list(clients_by_priority),
            'recent_clients': list(recent_clients),
            'top_clients_by_interactions': list(top_clients_by_interactions),
            'clients_by_source': list(clients_by_source),
            'monthly_client_growth': monthly_client_growth
        }
        
        serializer = ClientDashboardSerializer(dashboard_data)
        return Response(serializer.data)

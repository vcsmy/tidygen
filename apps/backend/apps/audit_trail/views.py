from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from django.utils import timezone

from .models import AuditEvent
from .serializers import (
    AuditEventSerializer,
    AuditEventCreateSerializer,
    AuditEventVerificationSerializer,
    AuditEventBatchSerializer,
    AuditEventStatsSerializer,
)
from .services import AuditService


class AuditEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing audit events.
    """
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'actor', 'entity_type', 'is_verified']
    search_fields = ['event_type', 'entity_type', 'entity_id', 'data_hash']
    ordering_fields = ['created_at', 'event_type', 'actor']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AuditEventCreateSerializer
        return AuditEventSerializer

    def perform_create(self, serializer):
        """
        Create a new audit event with automatic hash generation.
        """
        event_data = serializer.validated_data.get('event_data', {})
        event_type = serializer.validated_data.get('event_type')
        actor = serializer.validated_data.get('actor')
        entity_type = serializer.validated_data.get('entity_type')
        entity_id = serializer.validated_data.get('entity_id')

        # Use the audit service to create the event with hash
        audit_service = AuditService()
        audit_event = audit_service.log_event(
            event_type=event_type,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            event_data=event_data
        )
        
        # Return the created event
        return audit_event

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Verify the integrity of an audit event.
        """
        serializer = AuditEventVerificationSerializer(data=request.data)
        if serializer.is_valid():
            event_id = serializer.validated_data['event_id']
            expected_hash = serializer.validated_data['expected_hash']
            merkle_proof = serializer.validated_data.get('merkle_proof')
            merkle_root = serializer.validated_data.get('merkle_root')

            try:
                audit_event = AuditEvent.objects.get(id=event_id)
                audit_service = AuditService()
                
                # Verify the event
                is_valid = audit_service.verify_event(
                    audit_event=audit_event,
                    expected_hash=expected_hash,
                    merkle_proof=merkle_proof,
                    merkle_root=merkle_root
                )

                if is_valid:
                    audit_event.is_verified = True
                    audit_event.verification_timestamp = timezone.now()
                    audit_event.save()

                return Response({
                    'verified': is_valid,
                    'event_id': event_id,
                    'message': 'Event verified successfully' if is_valid else 'Event verification failed'
                })
            except AuditEvent.DoesNotExist:
                return Response(
                    {'error': 'Audit event not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def batch_operation(self, request):
        """
        Perform batch operations on audit events.
        """
        serializer = AuditEventBatchSerializer(data=request.data)
        if serializer.is_valid():
            event_ids = serializer.validated_data['event_ids']
            operation = serializer.validated_data['operation']

            try:
                audit_events = AuditEvent.objects.filter(id__in=event_ids)
                audit_service = AuditService()
                results = []

                if operation == 'verify':
                    for event in audit_events:
                        is_valid = audit_service.verify_event(event)
                        if is_valid:
                            event.is_verified = True
                            event.verification_timestamp = timezone.now()
                            event.save()
                        results.append({
                            'event_id': event.id,
                            'verified': is_valid
                        })

                elif operation == 'anchor_on_chain':
                    for event in audit_events:
                        tx_hash = audit_service.anchor_event_on_chain(event)
                        if tx_hash:
                            event.on_chain_tx_hash = tx_hash
                            event.save()
                        results.append({
                            'event_id': event.id,
                            'tx_hash': tx_hash
                        })

                elif operation == 'store_ipfs':
                    for event in audit_events:
                        cid = audit_service.store_event_on_ipfs(event)
                        if cid:
                            event.ipfs_cid = cid
                            event.save()
                        results.append({
                            'event_id': event.id,
                            'ipfs_cid': cid
                        })

                elif operation == 'generate_merkle':
                    merkle_data = audit_service.generate_merkle_tree(audit_events)
                    for event in audit_events:
                        if event.id in merkle_data['proofs']:
                            event.merkle_root = merkle_data['root']
                            event.merkle_proof = merkle_data['proofs'][event.id]
                            event.save()
                    results = merkle_data

                return Response({
                    'operation': operation,
                    'results': results
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get audit event statistics.
        """
        queryset = self.get_queryset()
        
        # Basic stats
        total_events = queryset.count()
        verified_events = queryset.filter(is_verified=True).count()
        on_chain_events = queryset.filter(on_chain_tx_hash__isnull=False).count()
        ipfs_events = queryset.filter(ipfs_cid__isnull=False).count()

        # Events by type
        events_by_type = dict(
            queryset.values('event_type').annotate(count=Count('id')).values_list('event_type', 'count')
        )

        # Events by actor
        events_by_actor = dict(
            queryset.filter(actor__isnull=False)
            .values('actor__username')
            .annotate(count=Count('id'))
            .values_list('actor__username', 'count')
        )

        # Recent events
        recent_events = queryset.order_by('-created_at')[:10]
        recent_events_data = AuditEventSerializer(recent_events, many=True).data

        stats_data = {
            'total_events': total_events,
            'verified_events': verified_events,
            'on_chain_events': on_chain_events,
            'ipfs_events': ipfs_events,
            'events_by_type': events_by_type,
            'events_by_actor': events_by_actor,
            'recent_events': recent_events_data,
        }

        serializer = AuditEventStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def integrity_check(self, request):
        """
        Perform integrity check on all audit events.
        """
        audit_service = AuditService()
        results = audit_service.integrity_check()
        
        return Response({
            'total_checked': results['total_checked'],
            'passed': results['passed'],
            'failed': results['failed'],
            'failed_events': results['failed_events'],
            'message': f"Integrity check completed: {results['passed']}/{results['total_checked']} events passed"
        })

    @action(detail=True, methods=['post'])
    def anchor_on_chain(self, request, pk=None):
        """
        Anchor a specific audit event on-chain.
        """
        audit_event = self.get_object()
        audit_service = AuditService()
        
        try:
            tx_hash = audit_service.anchor_event_on_chain(audit_event)
            if tx_hash:
                audit_event.on_chain_tx_hash = tx_hash
                audit_event.save()
                return Response({
                    'success': True,
                    'tx_hash': tx_hash,
                    'message': 'Event anchored on-chain successfully'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to anchor event on-chain'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def store_ipfs(self, request, pk=None):
        """
        Store a specific audit event on IPFS.
        """
        audit_event = self.get_object()
        audit_service = AuditService()
        
        try:
            cid = audit_service.store_event_on_ipfs(audit_event)
            if cid:
                audit_event.ipfs_cid = cid
                audit_event.save()
                return Response({
                    'success': True,
                    'ipfs_cid': cid,
                    'message': 'Event stored on IPFS successfully'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to store event on IPFS'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.audit_trail.models import AuditEvent
from apps.audit_trail.services import AuditService
import json


class Command(BaseCommand):
    """
    Management command to verify audit trail integrity.
    """
    help = 'Verify the integrity of all audit events in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event-id',
            type=int,
            help='Verify a specific audit event by ID'
        )
        parser.add_argument(
            '--event-type',
            type=str,
            help='Verify all events of a specific type'
        )
        parser.add_argument(
            '--export-failed',
            type=str,
            help='Export failed verification results to a JSON file'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each event'
        )

    def handle(self, *args, **options):
        """
        Handle the command execution.
        """
        self.stdout.write(
            self.style.SUCCESS('Starting audit trail integrity verification...')
        )

        # Initialize audit service
        audit_service = AuditService()
        
        # Get events to verify
        if options['event_id']:
            try:
                events = [AuditEvent.objects.get(id=options['event_id'])]
                self.stdout.write(f'Verifying specific event ID: {options["event_id"]}')
            except AuditEvent.DoesNotExist:
                raise CommandError(f'Audit event with ID {options["event_id"]} does not exist')
        elif options['event_type']:
            events = AuditEvent.objects.filter(event_type=options['event_type'])
            self.stdout.write(f'Verifying all events of type: {options["event_type"]}')
        else:
            events = AuditEvent.objects.all()
            self.stdout.write('Verifying all audit events')

        if not events.exists():
            self.stdout.write(
                self.style.WARNING('No audit events found to verify')
            )
            return

        # Perform integrity check
        results = audit_service.integrity_check(events)
        
        # Display results
        self.display_results(results, options['verbose'])
        
        # Export failed results if requested
        if options['export_failed'] and results['failed_events']:
            self.export_failed_results(results['failed_events'], options['export_failed'])

        # Exit with appropriate code
        if results['failed'] > 0:
            raise CommandError(
                f'Integrity check failed: {results["failed"]}/{results["total_checked"]} events failed verification'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Integrity check passed: {results["passed"]}/{results["total_checked"]} events verified successfully'
                )
            )

    def display_results(self, results, verbose=False):
        """
        Display verification results.
        """
        self.stdout.write('\n' + '='*60)
        self.stdout.write('AUDIT TRAIL INTEGRITY VERIFICATION RESULTS')
        self.stdout.write('='*60)
        
        self.stdout.write(f'Total Events Checked: {results["total_checked"]}')
        self.stdout.write(
            self.style.SUCCESS(f'Passed: {results["passed"]}')
        )
        self.stdout.write(
            self.style.ERROR(f'Failed: {results["failed"]}')
        )
        
        if results['failed'] > 0:
            self.stdout.write('\nFAILED EVENTS:')
            self.stdout.write('-' * 40)
            
            for event_data in results['failed_events']:
                event = event_data['event']
                error = event_data['error']
                
                self.stdout.write(
                    f'Event ID: {event.id} | Type: {event.event_type} | '
                    f'Created: {event.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                )
                self.stdout.write(f'Error: {error}')
                
                if verbose:
                    self.stdout.write(f'Data Hash: {event.data_hash}')
                    self.stdout.write(f'Entity: {event.entity_type}:{event.entity_id}')
                    if event.actor:
                        self.stdout.write(f'Actor: {event.actor.username}')
                    self.stdout.write('-' * 40)
        
        # Show summary by event type
        if verbose and results.get('by_type'):
            self.stdout.write('\nSUMMARY BY EVENT TYPE:')
            self.stdout.write('-' * 40)
            for event_type, stats in results['by_type'].items():
                self.stdout.write(
                    f'{event_type}: {stats["passed"]}/{stats["total"]} passed'
                )

    def export_failed_results(self, failed_events, filename):
        """
        Export failed verification results to a JSON file.
        """
        export_data = []
        
        for event_data in failed_events:
            event = event_data['event']
            export_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'actor': event.actor.username if event.actor else None,
                'entity_type': event.entity_type,
                'entity_id': event.entity_id,
                'data_hash': event.data_hash,
                'created_at': event.created_at.isoformat(),
                'error': event_data['error'],
            })
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'Failed verification results exported to: {filename}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to export results: {str(e)}')
            )

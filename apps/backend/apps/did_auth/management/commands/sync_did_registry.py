"""
Management command for DID registry synchronization.
"""

from django.core.management.base import BaseCommand, CommandError
from apps.did_auth.models import DIDDocument
from apps.did_auth.services import DIDRegistrySyncService


class Command(BaseCommand):
    help = 'Synchronize DID documents with on-chain registry'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['sync-all', 'sync-to-registry', 'sync-from-registry', 'check-status', 'network-info'],
            required=True,
            help='Action to perform'
        )
        parser.add_argument(
            '--did',
            type=str,
            help='Specific DID to sync (for sync-to-registry, sync-from-registry, check-status)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Batch size for bulk operations (default: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making actual changes'
        )

    def handle(self, *args, **options):
        action = options['action']
        did_string = options.get('did')
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        registry_sync = DIDRegistrySyncService()
        
        if not registry_sync.is_registry_available():
            self.stdout.write(
                self.style.ERROR('Registry is not available. Check Web3 configuration.')
            )
            return
        
        if action == 'network-info':
            self._show_network_info(registry_sync)
        elif action == 'sync-all':
            self._sync_all_dids(registry_sync, batch_size, dry_run)
        elif action == 'sync-to-registry':
            self._sync_to_registry(registry_sync, did_string, dry_run)
        elif action == 'sync-from-registry':
            self._sync_from_registry(registry_sync, did_string, dry_run)
        elif action == 'check-status':
            self._check_status(registry_sync, did_string)

    def _show_network_info(self, registry_sync):
        """Show network information."""
        self.stdout.write(self.style.SUCCESS('Getting network information...'))
        
        info = registry_sync.get_network_info()
        
        if info.get('connected'):
            self.stdout.write(f"Network: Connected")
            self.stdout.write(f"Chain ID: {info.get('chain_id')}")
            self.stdout.write(f"Latest Block: {info.get('latest_block')}")
            self.stdout.write(f"Gas Price: {info.get('gas_price')} wei")
            self.stdout.write(f"Registry Available: {info.get('registry_available')}")
        else:
            self.stdout.write(
                self.style.ERROR(f"Network: Not connected - {info.get('error', 'Unknown error')}")
            )

    def _sync_all_dids(self, registry_sync, batch_size, dry_run):
        """Sync all local DIDs to registry."""
        self.stdout.write(self.style.SUCCESS('Syncing all DIDs to registry...'))
        
        did_documents = DIDDocument.objects.filter(status='active')
        total = did_documents.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No active DIDs found to sync'))
            return
        
        self.stdout.write(f"Found {total} active DIDs to sync")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes will be made'))
            for did_doc in did_documents[:batch_size]:
                self.stdout.write(f"Would sync: {did_doc.did}")
            return
        
        successful = 0
        failed = 0
        
        for i in range(0, total, batch_size):
            batch = did_documents[i:i + batch_size]
            self.stdout.write(f"Processing batch {i//batch_size + 1} ({len(batch)} DIDs)...")
            
            for did_doc in batch:
                result = registry_sync.sync_did_to_registry(did_doc)
                
                if result['success']:
                    successful += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Synced {did_doc.did} - TX: {result['tx_hash']}")
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Failed to sync {did_doc.did}: {result['error']}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sync completed: {successful} successful, {failed} failed")
        )

    def _sync_to_registry(self, registry_sync, did_string, dry_run):
        """Sync a specific DID to registry."""
        if not did_string:
            raise CommandError('DID string is required for sync-to-registry action')
        
        try:
            did_doc = DIDDocument.objects.get(did=did_string)
        except DIDDocument.DoesNotExist:
            raise CommandError(f'DID {did_string} not found')
        
        self.stdout.write(f"Syncing DID {did_string} to registry...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes will be made'))
            self.stdout.write(f"Would sync: {did_doc.did}")
            return
        
        result = registry_sync.sync_did_to_registry(did_doc)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully synced {did_string}")
            )
            self.stdout.write(f"Transaction Hash: {result['tx_hash']}")
            self.stdout.write(f"Block Number: {result.get('block_number')}")
            self.stdout.write(f"Gas Used: {result.get('gas_used')}")
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to sync {did_string}: {result['error']}")
            )

    def _sync_from_registry(self, registry_sync, did_string, dry_run):
        """Sync a specific DID from registry."""
        if not did_string:
            raise CommandError('DID string is required for sync-from-registry action')
        
        self.stdout.write(f"Syncing DID {did_string} from registry...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes will be made'))
            self.stdout.write(f"Would resolve: {did_string}")
            return
        
        result = registry_sync.sync_did_from_registry(did_string)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully resolved {did_string}")
            )
            self.stdout.write(f"Document: {result['document']}")
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to resolve {did_string}: {result['error']}")
            )

    def _check_status(self, registry_sync, did_string):
        """Check registry status of a DID."""
        if not did_string:
            raise CommandError('DID string is required for check-status action')
        
        self.stdout.write(f"Checking registry status for {did_string}...")
        
        result = registry_sync.get_registry_status(did_string)
        
        if result['success']:
            self.stdout.write(f"Status: {result['status']}")
            if result.get('document'):
                self.stdout.write(f"Document: {result['document']}")
        else:
            self.stdout.write(
                self.style.ERROR(f"Error checking status: {result['error']}")
            )

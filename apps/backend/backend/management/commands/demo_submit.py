"""
Django management command to submit service verification records to the ink! smart contract.

This command demonstrates how to interact with the service verification contract
deployed on a local Substrate node.
"""

import hashlib
import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

try:
    import substrateinterface
    from substrateinterface import SubstrateInterface, KeyPair
except ImportError:
    substrateinterface = None


class Command(BaseCommand):
    help = 'Submit a service verification record to the ink! smart contract'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contract',
            type=str,
            required=True,
            help='Contract address (e.g., 5F...)'
        )
        parser.add_argument(
            '--service-id',
            type=int,
            required=True,
            help='Service ID (integer)'
        )
        parser.add_argument(
            '--payload',
            type=str,
            required=True,
            help='Payload string to hash and store'
        )
        parser.add_argument(
            '--substrate-ws',
            type=str,
            help='Substrate WebSocket URL (overrides env var)'
        )
        parser.add_argument(
            '--sender-seed',
            type=str,
            help='Sender account seed (overrides env var)'
        )

    def handle(self, *args, **options):
        # Check if substrate-interface is available
        if substrateinterface is None:
            raise CommandError(
                'substrate-interface is required. Install it with: pip install substrate-interface'
            )

        # Get configuration from environment variables or command line arguments
        substrate_ws = (
            options.get('substrate_ws') or 
            os.getenv('SUBSTRATE_WS', 'ws://127.0.0.1:9944')
        )
        sender_seed = (
            options.get('sender_seed') or 
            os.getenv('SUBSTRATE_SENDER_SEED', '//Alice')
        )
        
        contract_address = options['contract']
        service_id = options['service_id']
        payload = options['payload']

        try:
            # Submit the service verification
            tx_hash = self.submit_service_verification(
                substrate_url=substrate_ws,
                sender_seed=sender_seed,
                contract_address=contract_address,
                service_id=service_id,
                payload=payload
            )

            self.stdout.write(
                self.style.SUCCESS('Transaction submitted successfully!')
            )
            self.stdout.write(f'Extrinsic hash: {tx_hash}')
            self.stdout.write(f'Service ID: {service_id}')
            self.stdout.write(f'Payload: {payload}')
            self.stdout.write(f'Data hash: {self.compute_data_hash(payload).hex()}')

        except FileNotFoundError as e:
            raise CommandError(
                f'Contract metadata not found: {e}\n'
                'Make sure the contract is compiled and metadata.json exists in contracts/substrate-poc/target/ink/'
            )
        except Exception as e:
            raise CommandError(f'Error submitting transaction: {e}')

    def load_contract_metadata(self, contract_path: str) -> dict:
        """Load contract metadata from the compiled contract bundle."""
        metadata_path = Path(contract_path) / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Contract metadata not found at {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)

    def compute_data_hash(self, payload: str) -> bytes:
        """Compute SHA256 hash of the payload."""
        return hashlib.sha256(payload.encode('utf-8')).digest()

    def submit_service_verification(
        self,
        substrate_url: str,
        sender_seed: str,
        contract_address: str,
        service_id: int,
        payload: str
    ) -> str:
        """Submit a service verification record to the contract."""
        
        # Connect to Substrate node
        substrate = SubstrateInterface(url=substrate_url)
        
        # Load contract metadata
        # Look for contract metadata in the project root
        project_root = Path(settings.BASE_DIR).parent.parent
        contract_path = project_root / "contracts" / "substrate-poc" / "target" / "ink"
        metadata = self.load_contract_metadata(contract_path)
        
        # Create keypair from seed
        keypair = KeyPair.create_from_uri(sender_seed)
        
        # Compute data hash
        data_hash = self.compute_data_hash(payload)
        
        # Create contract call
        contract = substrate.create_contract_instance(
            contract_address=contract_address,
            metadata_file=metadata,
            keypair=keypair
        )
        
        # Call the store method
        call = contract.compose_call(
            call_function="store",
            call_args={
                "service_id": service_id,
                "data_hash": data_hash
            }
        )
        
        # Submit the transaction
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        response = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        
        if response.is_success:
            return response.extrinsic_hash
        else:
            raise Exception(f"Transaction failed: {response.error_message}")

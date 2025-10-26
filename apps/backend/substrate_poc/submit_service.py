#!/usr/bin/env python3
"""
Service Verification Submission Script

A demo script to submit service verification records to the ink! smart contract
deployed on a local Substrate node.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

import substrateinterface
from substrateinterface import SubstrateInterface, KeyPair


def load_contract_metadata(contract_path: str) -> dict:
    """Load contract metadata from the compiled contract bundle."""
    metadata_path = Path(contract_path) / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Contract metadata not found at {metadata_path}")
    
    with open(metadata_path, 'r') as f:
        return json.load(f)


def compute_data_hash(payload: str) -> bytes:
    """Compute SHA256 hash of the payload."""
    return hashlib.sha256(payload.encode('utf-8')).digest()


def submit_service_verification(
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
    contract_path = Path(__file__).parent.parent.parent.parent / "contracts" / "substrate-poc" / "target" / "ink"
    metadata = load_contract_metadata(contract_path)
    
    # Create keypair from seed
    keypair = KeyPair.create_from_uri(sender_seed)
    
    # Compute data hash
    data_hash = compute_data_hash(payload)
    
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


def main():
    """Main function to handle command line arguments and submit service verification."""
    parser = argparse.ArgumentParser(
        description="Submit a service verification record to the ink! contract"
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Contract address (e.g., 5F...)"
    )
    parser.add_argument(
        "--service-id",
        type=int,
        required=True,
        help="Service ID (integer)"
    )
    parser.add_argument(
        "--payload",
        required=True,
        help="Payload string to hash and store"
    )
    parser.add_argument(
        "--substrate-ws",
        default=os.getenv("SUBSTRATE_WS", "ws://127.0.0.1:9944"),
        help="Substrate WebSocket URL (default: ws://127.0.0.1:9944)"
    )
    parser.add_argument(
        "--sender-seed",
        default=os.getenv("SUBSTRATE_SENDER_SEED", "//Alice"),
        help="Sender account seed (default: //Alice)"
    )
    
    args = parser.parse_args()
    
    # Check if contract address is provided
    if not args.contract:
        print("Error: Contract address is required. Use --contract <address>")
        print("Example: python submit_service.py --contract 5F... --service-id 1 --payload 'demo'")
        sys.exit(1)
    
    try:
        # Submit the service verification
        tx_hash = submit_service_verification(
            substrate_url=args.substrate_ws,
            sender_seed=args.sender_seed,
            contract_address=args.contract,
            service_id=args.service_id,
            payload=args.payload
        )
        
        print(f"Transaction submitted successfully!")
        print(f"Extrinsic hash: {tx_hash}")
        print(f"Service ID: {args.service_id}")
        print(f"Payload: {args.payload}")
        print(f"Data hash: {compute_data_hash(args.payload).hex()}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the contract is compiled and metadata.json exists in contracts/substrate-poc/target/ink/")
        sys.exit(1)
    except Exception as e:
        print(f"Error submitting transaction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

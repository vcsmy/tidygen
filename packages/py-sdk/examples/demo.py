#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from tidygen_sdk import connect, submit_service

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python demo.py <contract_address> <service_id> <payload>")
        sys.exit(2)
    contract_address = sys.argv[1]
    service_id = int(sys.argv[2])
    payload = sys.argv[3]
    substrate = connect()
    metadata_path = Path("contracts/substrate-poc/target/ink/metadata.json")
    if not metadata_path.exists():
        print("Contract metadata not found. Build contract first.")
        sys.exit(1)
    tx = submit_service(substrate, contract_address, str(metadata_path), seed="//Alice", service_id=service_id, payload=payload)
    print("Submitted, extrinsic:", tx)
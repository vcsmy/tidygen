"""
TidyGen Python SDK - minimal helpers to interact with the service verification contract.
"""

from substrateinterface import SubstrateInterface, KeyPair
import json
from pathlib import Path
from hashlib import sha256
from typing import Optional

def connect(ws_url: str = "ws://127.0.0.1:9944"):
    return SubstrateInterface(url=ws_url)

def compute_hash(payload: str) -> bytes:
    return sha256(payload.encode("utf-8")).digest()

def submit_service(substrate: SubstrateInterface, contract_address: str, metadata_path: str, seed: str, service_id: int, payload: str) -> str:
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    keypair = KeyPair.create_from_uri(seed)
    # Create contract instance and submit similar to deploy script
    contract = substrate.create_contract_instance(contract_address=contract_address, metadata_file=metadata, keypair=keypair)
    data_hash = compute_hash(payload)
    call = contract.compose_call(call_function="store", call_args={"service_id": service_id, "data_hash": data_hash})
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
    resp = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    if resp.is_success:
        return resp.extrinsic_hash
    raise RuntimeError("Contract call failed")
#!/usr/bin/env python3
"""
Permanent deployment helper for the ink! contract.

Usage:
  python deploy_contract.py --wasm path/to/contract.wasm --metadata path/to/metadata.json [--ws ws://127.0.0.1:9944] [--seed //Alice]

Outputs the deployed contract address to stdout and writes to /tmp/tidygen_contract_address.txt
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from substrateinterface import SubstrateInterface, KeyPair
    from scalecodec.type_registry import load_type_registry_file
except Exception as e:
    print("ERROR: py-substrate-interface is required. Install: pip install substrate-interface")
    raise

def deploy_contract(wasm_path: Path, metadata_path: Path, substrate_ws: str, sender_seed: str) -> str:
    if not wasm_path.exists():
        raise FileNotFoundError(f"WASM file not found: {wasm_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    substrate = SubstrateInterface(url=substrate_ws)

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    keypair = KeyPair.create_from_uri(sender_seed)

    # Upload code
    print("[deploy] Uploading contract code...")
    # For Contracts pallet, we call upload_code (some runtimes may differ)
    code_bytes = wasm_path.read_bytes()
    # Compose and submit raw upload extrinsic via Contracts.upload_code or create code storage based on runtime
    call = substrate.compose_call(
        call_module="Contracts",
        call_function="upload_code",
        call_params={
            "code": code_bytes,
            "storage_deposit_limit": None
        }
    )
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
    print("[deploy] Submitting upload_code extrinsic...")
    resp = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    if not resp.is_success:
        raise RuntimeError(f"Code upload failed: {getattr(resp, 'error_message', resp)}")
    # Extract code hash if present
    code_hash = getattr(resp, "contract_code_hash", None)
    print(f"[deploy] upload_code response OK; code_hash={code_hash}")

    # Instantiate contract
    print("[deploy] Instantiating contract...")
    instantiate_call = substrate.compose_call(
        call_module="Contracts",
        call_function="instantiate",
        call_params={
            "value": 0,
            "gas_limit": 1000000000000,
            "storage_deposit_limit": None,
            "code_hash": code_hash,
            "data": b"",  # no constructor args
            "salt": b"tidygen_poc"
        }
    )
    extrinsic = substrate.create_signed_extrinsic(call=instantiate_call, keypair=keypair)
    resp = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    if not resp.is_success:
        raise RuntimeError(f"Contract instantiation failed: {getattr(resp, 'error_message', resp)}")

    # The event handling will vary by runtime. Try to extract Instantiated event.
    contract_address = None
    try:
        events = resp.triggered_events
    except Exception:
        events = []
    for ev in events:
        try:
            module = ev.value.get("module_id") if isinstance(ev.value, dict) else None
            event_id = ev.value.get("event_id") if isinstance(ev.value, dict) else None
            params = ev.value.get("params") if isinstance(ev.value, dict) else None
            if module == "Contracts" and event_id in ("Instantiated", "ContractInstantiated"):
                # params often contain deployer and contract account
                if params and len(params) >= 2:
                    contract_address = params[1].get("value") if isinstance(params[1], dict) else None
        except Exception:
            continue

    # Fallback: check the file /tmp/tidygen_contract_address.txt
    if not contract_address:
        temp_path = Path("/tmp/tidygen_contract_address.txt")
        if temp_path.exists():
            contract_address = temp_path.read_text().strip()

    if not contract_address:
        raise RuntimeError("Unable to determine deployed contract address from events or /tmp file")

    print(f"[deploy] Contract deployed at: {contract_address}")
    # Write to tmp file for other scripts
    Path("/tmp/tidygen_contract_address.txt").write_text(contract_address)
    return contract_address

def main():
    parser = argparse.ArgumentParser(description="Deploy ink! contract and print address")
    parser.add_argument("--wasm", required=True, help="Path to compiled contract .wasm")
    parser.add_argument("--metadata", required=True, help="Path to contract metadata.json")
    parser.add_argument("--ws", default="ws://127.0.0.1:9944", help="Substrate websocket endpoint")
    parser.add_argument("--seed", default="//Alice", help="Sender seed (dev account)")

    args = parser.parse_args()
    try:
        addr = deploy_contract(Path(args.wasm), Path(args.metadata), args.ws, args.seed)
        print(addr)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
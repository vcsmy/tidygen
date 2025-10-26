#!/bin/bash
set -e

# TidyGen Substrate Quickstart Script
# This script runs a local Substrate node, builds the ink! contract, deploys it, and runs the demo

echo "🚀 TidyGen Substrate Quickstart"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SUBSTRATE_NODE_IMAGE="paritytech/ink-playground:latest"
CONTRACT_DIR="contracts/substrate-poc"
BACKEND_DIR="apps/backend"
SCRIPTS_DIR="scripts"
CONTRACT_ADDRESS_FILE="/tmp/tidygen_contract_address.txt"
HEADLESS_MODE=false

# Function to print colored output
print_status() {
    if [ "$HEADLESS_MODE" = "true" ]; then
        echo "[INFO] $1"
    else
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

print_success() {
    if [ "$HEADLESS_MODE" = "true" ]; then
        echo "[SUCCESS] $1"
    else
        echo -e "${GREEN}[SUCCESS]${NC} $1"
    fi
}

print_warning() {
    if [ "$HEADLESS_MODE" = "true" ]; then
        echo "[WARNING] $1"
    else
        echo -e "${YELLOW}[WARNING]${NC} $1"
    fi
}

print_error() {
    if [ "$HEADLESS_MODE" = "true" ]; then
        echo "[ERROR] $1"
    else
        echo -e "${RED}[ERROR]${NC} $1"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to start Substrate node
start_substrate_node() {
    print_status "Starting Substrate node..."
    
    # Stop any existing containers
    docker-compose -f "$SCRIPTS_DIR/docker-compose.quickstart.yml" down >/dev/null 2>&1 || true
    
    # Start the Substrate node
    docker-compose -f "$SCRIPTS_DIR/docker-compose.quickstart.yml" up -d
    
    # Wait for the node to be ready
    wait_for_service "http://127.0.0.1:9944" "Substrate node"
}

# Function to build the ink! contract
build_contract() {
    print_status "Building ink! contract..."
    
    if [ ! -d "$CONTRACT_DIR" ]; then
        print_error "Contract directory $CONTRACT_DIR not found!"
        exit 1
    fi
    
    cd "$CONTRACT_DIR"
    
    # Check if cargo-contract is available
    if command_exists cargo-contract; then
        print_status "Using local cargo-contract..."
        cargo +nightly contract build
    else
        print_status "Using Docker to build contract..."
        # Use Docker to build the contract
        docker run --rm \
            -v "$(pwd)":/code \
            -w /code \
            paritytech/ink-ci-linux:latest \
            cargo +nightly contract build
    fi
    
    if [ ! -f "target/ink/service_verification_poc.contract" ]; then
        print_error "Contract build failed! Expected target/ink/service_verification_poc.contract not found."
        exit 1
    fi
    
    print_success "Contract built successfully!"
    cd - >/dev/null
}

# Function to deploy the contract
deploy_contract() {
    print_status "Deploying contract..."
    
    # Create deployment script
    cat > /tmp/deploy_contract.py << 'EOF'
#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

try:
    import substrateinterface
    from substrateinterface import SubstrateInterface, KeyPair
except ImportError:
    print("ERROR: substrate-interface is required. Install it with: pip install substrate-interface")
    sys.exit(1)

def deploy_contract():
    # Connect to Substrate node
    substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
    
    # Load contract metadata
    contract_path = Path("contracts/substrate-poc/target/ink")
    metadata_path = contract_path / "metadata.json"
    
    if not metadata_path.exists():
        print(f"ERROR: Contract metadata not found at {metadata_path}")
        sys.exit(1)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Create keypair from //Alice
    keypair = KeyPair.create_from_uri("//Alice")
    
    # Upload contract code
    print("Uploading contract code...")
    code_upload = substrate.compose_call(
        call_module="Contracts",
        call_function="upload_code",
        call_params={
            "code": str(contract_path / "service_verification_poc.wasm"),
            "storage_deposit_limit": None,
        }
    )
    
    extrinsic = substrate.create_signed_extrinsic(call=code_upload, keypair=keypair)
    response = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    
    if not response.is_success:
        print(f"ERROR: Code upload failed: {response.error_message}")
        sys.exit(1)
    
    code_hash = response.contract_code_hash
    print(f"Code uploaded successfully. Code hash: {code_hash}")
    
    # Instantiate contract
    print("Instantiating contract...")
    instantiate_call = substrate.compose_call(
        call_module="Contracts",
        call_function="instantiate",
        call_params={
            "value": 0,
            "gas_limit": 1000000000000,
            "storage_deposit_limit": None,
            "code_hash": code_hash,
            "data": b"",  # Constructor data (empty for our contract)
            "salt": b"tidygen_poc",
        }
    )
    
    extrinsic = substrate.create_signed_extrinsic(call=instantiate_call, keypair=keypair)
    response = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    
    if not response.is_success:
        print(f"ERROR: Contract instantiation failed: {response.error_message}")
        sys.exit(1)
    
    # Extract contract address from events
    contract_address = None
    for event in response.triggered_events:
        if event.value['module_id'] == 'Contracts' and event.value['event_id'] == 'Instantiated':
            contract_address = event.value['params'][1]['value']
            break
    
    if not contract_address:
        print("ERROR: Could not extract contract address from events")
        sys.exit(1)
    
    print(f"Contract deployed successfully!")
    print(f"Contract address: {contract_address}")
    
    # Save contract address to file
    with open("/tmp/tidygen_contract_address.txt", "w") as f:
        f.write(contract_address)
    
    return contract_address

if __name__ == "__main__":
    deploy_contract()
EOF
    
    # Run deployment script
    python3 /tmp/deploy_contract.py
    
    # Read contract address
    if [ -f "$CONTRACT_ADDRESS_FILE" ]; then
        CONTRACT_ADDRESS=$(cat "$CONTRACT_ADDRESS_FILE")
        print_success "Contract deployed at: $CONTRACT_ADDRESS"
    else
        print_error "Failed to get contract address!"
        exit 1
    fi
}

# Function to run the demo
run_demo() {
    print_status "Running demo submission..."
    
    if [ -z "$CONTRACT_ADDRESS" ]; then
        print_error "Contract address not found!"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -q -r requirements.txt
    pip install -q substrate-interface
    
    # Set environment variables
    export SUBSTRATE_WS="ws://127.0.0.1:9944"
    export SUBSTRATE_SENDER_SEED="//Alice"
    
    # Run the demo command
    print_status "Submitting service verification record..."
    python manage.py demo_submit \
        --contract "$CONTRACT_ADDRESS" \
        --service-id 1 \
        --payload "demo"
    
    print_success "Demo completed successfully!"
    cd - >/dev/null
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f "$SCRIPTS_DIR/docker-compose.quickstart.yml" down >/dev/null 2>&1 || true
    rm -f "$CONTRACT_ADDRESS_FILE" /tmp/deploy_contract.py
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --headless)
                HEADLESS_MODE=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --headless    Run in headless mode (no colors, minimal output)"
                echo "  -h, --help    Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Set up cleanup on exit
    trap cleanup EXIT
    
    print_status "Starting TidyGen Substrate Quickstart..."
    
    # Check prerequisites
    check_docker
    
    # Start Substrate node
    start_substrate_node
    
    # Build contract
    build_contract
    
    # Deploy contract
    deploy_contract
    
    # Run demo
    run_demo
    
    print_success "🎉 Quickstart completed successfully!"
    print_status "Contract address: $CONTRACT_ADDRESS"
    print_status "You can now interact with the contract using the Django management command:"
    print_status "cd $BACKEND_DIR && python manage.py demo_submit --contract $CONTRACT_ADDRESS --service-id <id> --payload '<data>'"
}

# Run main function
main "$@"

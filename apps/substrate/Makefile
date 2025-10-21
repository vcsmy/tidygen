.PHONY: build run test clean check fmt clippy benchmarks help

# Default target
help:
	@echo "TidyGen Substrate Node - Build Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make build        - Build the node in release mode"
	@echo "  make run          - Run the development node"
	@echo "  make test         - Run all tests"
	@echo "  make check        - Check code without building"
	@echo "  make fmt          - Format code with rustfmt"
	@echo "  make clippy       - Run clippy linter"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make benchmarks   - Run runtime benchmarks"
	@echo ""

# Build the node in release mode
build:
	@echo "Building TidyGen Substrate node..."
	cargo build --release
	@echo "Build complete! Binary: ./target/release/tidygen-node"

# Build in debug mode (faster compilation)
build-dev:
	@echo "Building TidyGen Substrate node (debug)..."
	cargo build
	@echo "Build complete! Binary: ./target/debug/tidygen-node"

# Run the development node
run:
	@echo "Starting TidyGen Substrate development node..."
	@echo "WebSocket endpoint: ws://127.0.0.1:9944"
	@echo "HTTP RPC endpoint: http://127.0.0.1:9933"
	@echo ""
	./target/release/tidygen-node --dev --tmp

# Run with custom port
run-custom:
	@echo "Starting TidyGen Substrate node on custom ports..."
	./target/release/tidygen-node --dev \
		--ws-port 9944 \
		--rpc-port 9933 \
		--tmp

# Run all tests
test:
	@echo "Running all tests..."
	cargo test --all
	@echo "All tests passed!"

# Run tests with output
test-verbose:
	@echo "Running tests with verbose output..."
	cargo test --all -- --nocapture

# Run tests for specific pallet
test-ledger:
	cargo test -p pallet-tidygen-ledger

test-did:
	cargo test -p pallet-tidygen-did

test-dao:
	cargo test -p pallet-tidygen-dao

# Check code without building
check:
	@echo "Checking code..."
	cargo check --all

# Format code
fmt:
	@echo "Formatting code..."
	cargo fmt --all

# Run clippy linter
clippy:
	@echo "Running clippy..."
	cargo clippy --all --all-targets -- -D warnings

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cargo clean
	@echo "Clean complete!"

# Build runtime for benchmarking
build-benchmarks:
	@echo "Building with benchmark features..."
	cargo build --release --features runtime-benchmarks

# Run runtime benchmarks
benchmarks: build-benchmarks
	@echo "Running benchmarks for TidyGen Ledger pallet..."
	./target/release/tidygen-node benchmark pallet \
		--pallet=pallet_tidygen_ledger \
		--extrinsic='*' \
		--steps=50 \
		--repeat=20 \
		--output=./pallets/tidygen-ledger/src/weights.rs

# Purge chain data
purge:
	@echo "Purging development chain data..."
	./target/release/tidygen-node purge-chain --dev -y

# Build and run
all: build run

# Install Rust and dependencies
setup:
	@echo "Setting up Substrate development environment..."
	@echo "Installing Rust..."
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
	@echo "Configuring Rust..."
	rustup default stable
	rustup update
	rustup update nightly
	rustup target add wasm32-unknown-unknown --toolchain nightly
	rustup component add rust-src
	@echo "Setup complete!"

# Update dependencies
update:
	@echo "Updating dependencies..."
	cargo update

# Generate documentation
docs:
	@echo "Generating documentation..."
	cargo doc --no-deps --open

# Watch for changes and rebuild
watch:
	@echo "Watching for changes..."
	cargo watch -x build

# Run node with detailed logging
run-debug:
	@echo "Starting node with debug logging..."
	RUST_LOG=debug ./target/release/tidygen-node --dev --tmp

# Try runtime for testing runtime upgrades
try-runtime:
	cargo build --release --features try-runtime
	./target/release/tidygen-node try-runtime


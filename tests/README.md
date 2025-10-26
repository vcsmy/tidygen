# TidyGen Community Tests

This directory contains all test files for the TidyGen Community project.

## Directory Structure

```
tests/
├── integration/          # Integration tests
│   ├── test_substrate_poc_quickstart.py
│   └── __init__.py
├── unit/                 # Unit tests
├── conftest.py          # Pytest configuration and fixtures
└── README.md            # This file
```

## Running Tests

### All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_substrate_poc_quickstart.py
```

### Integration Tests
```bash
# Run integration tests only
pytest -m integration

# Run integration tests with verbose output
pytest -m integration -v

# Run specific integration test
pytest tests/integration/test_substrate_poc_quickstart.py -v
```

### Unit Tests
```bash
# Run unit tests only
pytest -m unit

# Run unit tests with verbose output
pytest -m unit -v
```

### Slow Tests
```bash
# Run all tests including slow ones
pytest

# Skip slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

### Docker-Dependent Tests
```bash
# Run tests that require Docker
pytest -m docker

# Skip Docker-dependent tests
pytest -m "not docker"
```

## Test Categories

### Integration Tests (`integration/`)

Integration tests verify that different components work together correctly.

#### Substrate POC Quickstart Test
- **File**: `test_substrate_poc_quickstart.py`
- **Purpose**: Validates the complete quickstart flow
- **Requirements**: Docker, Substrate node
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.docker`

**What it tests:**
1. Quickstart script exists and is executable
2. Docker Compose file is valid
3. Contract directory and files exist
4. Django management command exists
5. Quickstart produces a valid transaction hash
6. Retry logic works for robustness

**Running the test:**
```bash
# Run the specific test
pytest tests/integration/test_substrate_poc_quickstart.py -v

# Run with retries and detailed output
pytest tests/integration/test_substrate_poc_quickstart.py -v -s

# Run only if Docker is available
pytest tests/integration/test_substrate_poc_quickstart.py -v --tb=short
```

### Unit Tests (`unit/`)

Unit tests verify individual components in isolation.

## Test Configuration

### Pytest Configuration
- **File**: `pytest.ini` (root directory)
- **Markers**: Defined for different test categories
- **Timeouts**: 600 seconds for slow tests
- **Output**: Verbose by default

### Fixtures
- **File**: `conftest.py`
- **Fixtures**: `project_root`, `docker_available`, `docker_compose_available`
- **Auto-markers**: Automatically adds markers based on test names

## Prerequisites

### For All Tests
- Python 3.7+
- pytest
- Required Python packages (see requirements.txt)

### For Integration Tests
- Docker installed and running
- Docker Compose available
- Internet connection (for pulling Docker images)

### For Substrate Tests
- Docker (required for Substrate node)
- Sufficient disk space for Docker images
- Available ports: 9944, 9933, 30333

## Test Markers

| Marker | Description | Usage |
|--------|-------------|-------|
| `slow` | Tests that take a long time to run | `pytest -m "not slow"` |
| `integration` | Integration tests | `pytest -m integration` |
| `unit` | Unit tests | `pytest -m unit` |
| `docker` | Tests requiring Docker | `pytest -m docker` |
| `substrate` | Tests requiring Substrate | `pytest -m substrate` |
| `web3` | Tests requiring Web3 | `pytest -m web3` |

## Troubleshooting

### Common Issues

1. **Docker not available**
   ```
   pytest.skip("Docker is not available or not running")
   ```
   - Solution: Install Docker and ensure it's running

2. **Test timeouts**
   ```
   pytest.TimeoutExpired: Quickstart script timed out
   ```
   - Solution: Increase timeout or check system resources

3. **Permission errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - Solution: Ensure test files are executable and have proper permissions

4. **Missing dependencies**
   ```
   ModuleNotFoundError: No module named 'substrateinterface'
   ```
   - Solution: Install required packages: `pip install -r requirements.txt`

### Debug Mode

Run tests with debug output:
```bash
# Verbose output with print statements
pytest tests/integration/test_substrate_poc_quickstart.py -v -s

# Show local variables on failure
pytest tests/integration/test_substrate_poc_quickstart.py -v --tb=long

# Run with debug logging
pytest tests/integration/test_substrate_poc_quickstart.py -v --log-cli-level=DEBUG
```

### CI/CD Integration

For CI/CD pipelines, use:
```bash
# Skip slow tests in CI
pytest -m "not slow" --tb=short

# Run only fast tests
pytest -m "not slow and not docker"

# Generate coverage report
pytest --cov=. --cov-report=html
```

## Contributing

When adding new tests:

1. **Choose the right directory**: `integration/` for integration tests, `unit/` for unit tests
2. **Add appropriate markers**: Use `@pytest.mark.slow`, `@pytest.mark.docker`, etc.
3. **Write descriptive test names**: Use `test_` prefix and descriptive names
4. **Add docstrings**: Document what each test does
5. **Handle cleanup**: Use fixtures for setup/teardown
6. **Make tests robust**: Add retry logic and proper error handling

## Examples

### Running Specific Tests
```bash
# Run only the quickstart test
pytest tests/integration/test_substrate_poc_quickstart.py::TestSubstratePOCQuickstart::test_quickstart_produces_transaction_hash -v

# Run all quickstart tests
pytest tests/integration/test_substrate_poc_quickstart.py -v

# Run with specific markers
pytest -m "slow and integration" -v
```

### Test Output
```
tests/integration/test_substrate_poc_quickstart.py::TestSubstratePOCQuickstart::test_quickstart_produces_transaction_hash PASSED [100%]

✅ Quickstart test passed!
📝 Transaction hash: 0x1234567890abcdef...
📊 Output length: 1234 characters
```
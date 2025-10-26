# TidyGen Backend

Django backend application for the TidyGen Community ERP system.

## Quick Start

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Management Commands

### Substrate Demo Commands

#### `demo_submit` - Submit Service Verification Records

Submit service verification records to the ink! smart contract deployed on a local Substrate node.

**Prerequisites:**
- Local Substrate node running (e.g., `substrate-contracts-node --dev`)
- Deployed service verification contract
- `substrate-interface` package installed: `pip install substrate-interface`

**Usage:**
```bash
python manage.py demo_submit --contract <CONTRACT_ADDRESS> --service-id <SERVICE_ID> --payload "<PAYLOAD>"
```

**Examples:**
```bash
# Basic usage
python manage.py demo_submit --contract 5F... --service-id 1 --payload "demo"

# With custom Substrate endpoint
python manage.py demo_submit --contract 5F... --service-id 2 --payload "test data" --substrate-ws ws://localhost:9944

# With custom sender account
python manage.py demo_submit --contract 5F... --service-id 3 --payload "verification" --sender-seed "//Bob"
```

**Environment Variables:**
- `SUBSTRATE_WS` - Substrate WebSocket URL (default: `ws://127.0.0.1:9944`)
- `SUBSTRATE_SENDER_SEED` - Sender account seed (default: `//Alice`)

**What it does:**
1. Connects to the local Substrate node
2. Loads contract metadata from `contracts/substrate-poc/target/ink/metadata.json`
3. Computes SHA256 hash of the provided payload
4. Calls the contract's `store` method with service_id and data_hash
5. Prints the transaction hash and details

**Output:**
```
Transaction submitted successfully!
Extrinsic hash: 0x1234567890abcdef...
Service ID: 1
Payload: demo
Data hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

### Other Management Commands

- `seed_demo` - Seed demo data for testing
- `seed_comprehensive_demo` - Seed comprehensive demo data
- `seed_business_data` - Seed business-specific data
- `setup_single_organization` - Setup single organization structure

## Project Structure

```
apps/backend/
├── apps/                    # Django applications
│   ├── core/               # Core functionality
│   ├── accounts/           # User management
│   ├── web3/              # Web3 integration
│   └── ...                # Other modules
├── backend/               # Django project settings
│   └── management/        # Management commands
│       └── commands/      # Custom commands
├── services/              # External service integrations
├── substrate_poc/         # Substrate POC scripts
├── smart_contracts/       # Smart contract artifacts
└── requirements.txt       # Python dependencies
```

## Development

### Adding New Management Commands

1. Create command file in `backend/management/commands/`
2. Inherit from `django.core.management.base.BaseCommand`
3. Implement `add_arguments()` and `handle()` methods
4. Add documentation to this README

### Environment Configuration

Key environment variables in `.env`:

```bash
# Django
DJANGO_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Web3
WEB3_ENABLED=True
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY

# Substrate
SUBSTRATE_WS=ws://127.0.0.1:9944
SUBSTRATE_SENDER_SEED=//Alice
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.core

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

See `Dockerfile` and `docker-compose.yml` for containerized deployment.

## API Documentation

API documentation is available at `/api/docs/` when `API_DOCS_ENABLED=True` in settings.

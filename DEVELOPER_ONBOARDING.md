# Developer Onboarding Guide

Welcome to the TidyGen ERP project! This guide will help you get up and running with the development environment.

## Prerequisites

Before you begin, ensure you have the following tools installed:

### Required Software
- **Node.js**: 18+ (LTS recommended)
  - Download from [nodejs.org](https://nodejs.org/)
  - Verify: `node --version`
- **Python**: 3.12+
  - Download from [python.org](https://python.org/)
  - Verify: `python --version`
- **Docker**: Latest version
  - Download from [docker.com](https://docker.com/)
  - Verify: `docker --version`
- **Docker Compose**: v2.0+
  - Verify: `docker-compose --version`
- **Git**: Latest version
  - Download from [git-scm.com](https://git-scm.com/)
  - Verify: `git --version`

### Package Managers
- **pnpm**: 8+ (recommended for frontend)
  - Install: `npm install -g pnpm`
  - Verify: `pnpm --version`
- **pip**: Python package manager
  - Usually included with Python
  - Verify: `pip --version`

### Optional Tools
- **VS Code**: Recommended IDE
  - Download from [code.visualstudio.com](https://code.visualstudio.com/)
- **MetaMask**: For Web3 testing
  - Install from [metamask.io](https://metamask.io/)
- **Postman**: For API testing
  - Download from [postman.com](https://postman.com/)

## Setup Steps

### 1. Clone the Repository
```bash
git clone https://github.com/tidygen-community/tidygen-community.git
cd tidygen-community
```

### 2. Environment Configuration
```bash
# Copy environment files
cp .env.example .env
cp apps/backend/env.example apps/backend/.env
cp apps/frontend/env.example apps/frontend/.env

# Edit configuration files as needed
# Backend: apps/backend/.env
# Frontend: apps/frontend/.env
```

### 3. Start with Docker (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin

### 5. Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`
- ⚠️ **Important**: Change the default password after first login!

## Development Setup

### Backend Development
```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Development
```bash
cd apps/frontend

# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Or with npm
npm install
npm run dev
```

### Smart Contracts Development
```bash
cd contracts

# Install dependencies (when contracts are added)
npm install

# Compile contracts
npm run compile

# Run tests
npm run test

# Deploy to testnet
npm run deploy:testnet
```

## Testing

### Backend Tests
```bash
cd apps/backend

# Run all tests
python manage.py test

# Run specific test
python manage.py test apps.accounts.tests.test_models

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests
```bash
cd apps/frontend

# Run tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test:watch
```

### Smart Contract Tests
```bash
cd contracts

# Run contract tests
npm run test

# Run gas optimization tests
npm run test:gas

# Run security tests
npm run test:security
```

## Linting and Code Quality

### Backend Linting
```bash
cd apps/backend

# Run flake8 linting
flake8 .

# Run black formatting
black .

# Run isort import sorting
isort .

# Run all linting tools
pre-commit run --all-files
```

### Frontend Linting
```bash
cd apps/frontend

# Run ESLint
pnpm lint

# Fix ESLint issues
pnpm lint:fix

# Run Prettier formatting
pnpm format

# Run TypeScript type checking
pnpm type-check
```

### Smart Contract Linting
```bash
cd contracts

# Run Solidity linting
npm run lint

# Fix linting issues
npm run lint:fix

# Run security analysis
npm run security
```

## Demo and Testing

### Running the Demo
Once smart contracts are added, you can run the demo:

```bash
# Start the application
docker-compose up --build

# Access the demo
# Frontend: http://localhost:3000
# Backend: http://localhost:8000

# Follow the demo instructions
# See: contracts/demo.md
```

### Demo Workflow
1. **Connect Wallet**: Use MetaMask to connect to the application
2. **Create Service**: Create a new cleaning service
3. **Deploy Contract**: Smart contract is automatically deployed
4. **Service Verification**: Provider marks service as completed
5. **Payment Release**: Payment is automatically released
6. **Verification**: Check transaction on blockchain

### Testing Web3 Features
```bash
# Start local blockchain (Ganache)
npx ganache-cli

# Deploy contracts to local network
npm run deploy:local

# Run integration tests
npm run test:integration
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Clean up Docker containers
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

#### Database Issues
```bash
# Reset database
python manage.py flush
python manage.py migrate

# Create new superuser
python manage.py createsuperuser
```

#### Frontend Issues
```bash
# Clear node modules
rm -rf node_modules
pnpm install

# Clear cache
pnpm cache clean
```

#### Smart Contract Issues
```bash
# Reset contracts
rm -rf artifacts/
npm run compile

# Reset network
npm run reset:network
```

### Port Conflicts
If you encounter port conflicts:

```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :8545  # Blockchain

# Kill processes if needed
kill -9 <PID>
```

### Environment Issues
```bash
# Check environment variables
echo $DATABASE_URL
echo $SECRET_KEY

# Verify Python version
python --version
which python

# Verify Node version
node --version
which node
```

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request
# Go to GitHub and create PR
```

### Code Standards
- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript/TypeScript**: Follow ESLint rules, use Prettier
- **Solidity**: Follow Solidity style guide
- **Commits**: Use conventional commit messages

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Getting Help

### Documentation
- **Main Documentation**: [./docs/](./docs/)
- **API Documentation**: [./docs/API_REFERENCE.md](./docs/API_REFERENCE.md)
- **Web3 Implementation**: [./docs/WEB3_TECHNICAL_IMPLEMENTATION.md](./docs/WEB3_TECHNICAL_IMPLEMENTATION.md)
- **Smart Contracts**: [./contracts/](./contracts/)

### Community Support
- **GitHub Issues**: [Report bugs and issues](https://github.com/tidygen-community/tidygen-community/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/tidygen-community/tidygen-community/discussions)
- **Discord**: [Join our community](https://discord.gg/tidygen)
- **Email**: [hello@tidygen.com](mailto:hello@tidygen.com)

### Development Resources
- **Backend API**: http://localhost:8000/api/docs
- **Frontend Storybook**: http://localhost:6006 (when available)
- **Database Admin**: http://localhost:8000/admin
- **Redis Commander**: http://localhost:8081 (when available)

## Next Steps

1. **Explore the Codebase**: Familiarize yourself with the project structure
2. **Read Documentation**: Go through the comprehensive documentation
3. **Run Tests**: Ensure all tests pass
4. **Make Your First Contribution**: Pick an issue and submit a PR
5. **Join the Community**: Connect with other developers

## Project Structure

```
tidygen-community/
├── apps/
│   ├── backend/          # Django REST API
│   └── frontend/         # React SPA
├── contracts/            # Smart contracts
├── docs/                 # Documentation
├── .github/              # GitHub workflows
├── docker-compose.yml    # Docker configuration
└── README.md            # Project overview
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed contribution guidelines.

---

**Welcome to the TidyGen ERP community!** 🚀

We're excited to have you on board. If you have any questions or need help, don't hesitate to reach out to the community.

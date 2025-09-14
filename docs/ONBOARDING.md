# TidyGen ERP - Developer Onboarding Guide

Welcome to the TidyGen ERP development team! This guide will help you get up and running quickly with our Web3-enabled ERP platform.

## 📋 **Table of Contents**

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Quality](#code-quality)
- [Web3 Development](#web3-development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## 🔧 **Prerequisites**

Before you begin, ensure you have the following installed on your development machine:

### **Required Software**

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **Node.js** | 18.x or higher | Frontend development | [Download](https://nodejs.org/) |
| **Python** | 3.11.x | Backend development | [Download](https://python.org/) |
| **Docker** | 20.x or higher | Containerization | [Download](https://docker.com/) |
| **Docker Compose** | 2.x or higher | Multi-container orchestration | [Download](https://docker.com/) |
| **Git** | 2.x or higher | Version control | [Download](https://git-scm.com/) |
| **pnpm** | 8.x or higher | Package manager | `npm install -g pnpm` |

### **Recommended Tools**

| Tool | Purpose | Installation |
|------|---------|--------------|
| **VS Code** | Code editor | [Download](https://code.visualstudio.com/) |
| **MetaMask** | Web3 wallet for testing | [Download](https://metamask.io/) |
| **Postman** | API testing | [Download](https://postman.com/) |
| **DBeaver** | Database management | [Download](https://dbeaver.io/) |

### **VS Code Extensions**

Install these recommended extensions for the best development experience:

```bash
# Essential extensions
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension ms-vscode.vscode-eslint
code --install-extension ms-vscode.vscode-json

# Web3 development
code --install-extension JuanBlanco.solidity
code --install-extension ms-vscode.vscode-docker
```

## 🚀 **Quick Start**

### **1. Clone the Repository**

```bash
# Clone the repository
git clone https://github.com/your-org/tidygen-erp.git
cd tidygen-erp

# Verify you're in the correct directory
ls -la
# You should see: apps/, docs/, infra/, scripts/, etc.
```

### **2. Environment Setup**

```bash
# Copy environment files
cp apps/backend/env.example apps/backend/.env
cp apps/frontend/env.example apps/frontend/.env.local

# Edit the environment files with your configuration
# Backend: Update database URLs, secrets, etc.
# Frontend: Update API URLs, Web3 configuration, etc.
```

### **3. Start Development Environment**

```bash
# Option 1: Use the setup script (recommended)
./scripts/setup/setup-dev.sh

# Option 2: Manual setup
# Install dependencies
pnpm install

# Start Docker services
docker-compose -f infra/docker/development/docker-compose.yml up -d

# Run database migrations
docker-compose -f infra/docker/development/docker-compose.yml exec backend python manage.py migrate

# Create superuser (optional)
docker-compose -f infra/docker/development/docker-compose.yml exec backend python manage.py createsuperuser
```

### **4. Verify Installation**

```bash
# Check if services are running
docker-compose -f infra/docker/development/docker-compose.yml ps

# Test backend API
curl http://localhost:8000/api/health/

# Test frontend
curl http://localhost:3000
```

**🎉 Congratulations! You should now have:**
- Backend API running at: http://localhost:8000
- Frontend app running at: http://localhost:3000
- API documentation at: http://localhost:8000/api/docs/
- Admin panel at: http://localhost:8000/admin/

## 🏗️ **Development Setup**

### **Backend Development**

```bash
# Navigate to backend directory
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run development server
python manage.py runserver

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .
```

### **Frontend Development**

```bash
# Navigate to frontend directory
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Run linting
npm run lint

# Build for production
npm run build
```

### **Web3 Development**

```bash
# Install MetaMask browser extension
# Configure test networks (Goerli, Mumbai)

# Set up test environment variables
# In apps/frontend/.env.local:
VITE_WALLETCONNECT_PROJECT_ID=your_project_id
VITE_ETHEREUM_RPC_URL=https://goerli.infura.io/v3/your_key
VITE_POLYGON_RPC_URL=https://mumbai.infura.io/v3/your_key
```

## 📁 **Project Structure**

```
TidyGen/
├── apps/                          # Main applications
│   ├── backend/                   # Django REST API
│   │   ├── apps/                  # Django apps
│   │   │   ├── core/             # Core functionality
│   │   │   ├── accounts/         # User management
│   │   │   ├── organizations/    # Multi-tenancy
│   │   │   ├── web3/             # Web3 integration
│   │   │   └── ...               # Other ERP modules
│   │   ├── tidygen_erp/            # Django project settings
│   │   ├── tests/                # Backend tests
│   │   └── requirements*.txt     # Dependencies
│   └── frontend/                 # React + TypeScript
│       ├── src/                  # Source code
│       │   ├── components/       # React components
│       │   ├── hooks/            # Custom hooks
│       │   ├── pages/            # Page components
│       │   ├── store/            # State management
│       │   ├── services/         # API services
│       │   └── types/            # TypeScript types
│       ├── public/               # Static assets
│       └── package.json          # Dependencies
├── docs/                         # Documentation
├── infra/                        # Infrastructure
│   ├── docker/                   # Docker configurations
│   ├── k8s/                      # Kubernetes configs
│   └── terraform/                # Infrastructure as Code
├── scripts/                      # Automation scripts
├── tests/                        # End-to-end tests
└── tools/                        # Development tools
```

## 🔄 **Development Workflow**

### **Branching Strategy**

We use **Git Flow** with the following branches:

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features (e.g., `feature/user-authentication`)
- **`bugfix/*`**: Bug fixes (e.g., `bugfix/login-error`)
- **`hotfix/*`**: Critical production fixes (e.g., `hotfix/security-patch`)

### **Creating a New Feature**

```bash
# 1. Start from develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes
# ... code changes ...

# 4. Commit your changes
git add .
git commit -m "feat: add user authentication system"

# 5. Push to remote
git push origin feature/your-feature-name

# 6. Create Pull Request
# Go to GitHub and create PR from feature branch to develop
```

### **Commit Message Convention**

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(auth): add JWT authentication"
git commit -m "fix(web3): resolve wallet connection issue"
git commit -m "docs: update API documentation"
git commit -m "test(backend): add user model tests"
```

### **Pull Request Process**

1. **Create PR**: From feature branch to `develop`
2. **Fill Template**: Use the PR template provided
3. **Run Tests**: Ensure all tests pass
4. **Code Review**: Get at least one approval
5. **Merge**: Squash and merge to `develop`

**PR Template Checklist:**
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No breaking changes (or documented)
- [ ] Security considerations addressed

## 🧪 **Testing Guidelines**

### **Backend Testing (pytest)**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/unit/test_models.py::TestUserModel::test_user_creation
```

**Test Structure:**
```python
# tests/unit/test_models.py
import pytest
from django.test import TestCase
from apps.accounts.models import User

class TestUserModel(TestCase):
    def test_user_creation(self):
        """Test user creation with valid data."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
```

### **Frontend Testing (Vitest)**

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm run test src/components/auth/LoginForm.test.tsx
```

**Test Structure:**
```typescript
// src/components/auth/LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import LoginForm from './LoginForm'

describe('LoginForm', () => {
  it('renders login form correctly', () => {
    render(<LoginForm />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    const mockSubmit = vi.fn()
    render(<LoginForm onSubmit={mockSubmit} />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    
    expect(mockSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    })
  })
})
```

### **Web3 Testing**

```typescript
// src/hooks/useWeb3.test.ts
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useWeb3 } from './useWeb3'

// Mock Web3 provider
const mockProvider = {
  request: vi.fn(),
  on: vi.fn(),
  removeListener: vi.fn(),
}

describe('useWeb3', () => {
  it('connects wallet successfully', async () => {
    mockProvider.request.mockResolvedValue(['0x123...'])
    
    const { result } = renderHook(() => useWeb3())
    
    await act(async () => {
      await result.current.connectWallet()
    })
    
    expect(result.current.isConnected).toBe(true)
    expect(result.current.wallet?.address).toBe('0x123...')
  })
})
```

## 📏 **Code Quality**

### **Backend Code Quality**

**Black (Code Formatting):**
```bash
# Format code
black .

# Check formatting
black --check .
```

**Flake8 (Linting):**
```bash
# Run linting
flake8 .

# Configuration in pyproject.toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [".git", "__pycache__", "venv"]
```

**MyPy (Type Checking):**
```bash
# Run type checking
mypy .

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

### **Frontend Code Quality**

**ESLint (Linting):**
```bash
# Run linting
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

**Prettier (Formatting):**
```bash
# Format code
npm run format

# Check formatting
npm run format:check
```

**TypeScript:**
```bash
# Type checking
npx tsc --noEmit
```

### **Pre-commit Hooks**

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## ⛓️ **Web3 Development**

### **Setting Up Web3 Environment**

1. **Install MetaMask**: Browser extension for wallet testing
2. **Get Test Tokens**: Use faucets for test networks
3. **Configure Networks**: Add test networks to MetaMask

### **Test Networks**

| Network | Chain ID | RPC URL | Faucet |
|---------|----------|---------|---------|
| Goerli | 5 | https://goerli.infura.io/v3/YOUR_KEY | [Goerli Faucet](https://goerlifaucet.com/) |
| Mumbai | 80001 | https://mumbai.infura.io/v3/YOUR_KEY | [Mumbai Faucet](https://faucet.polygon.technology/) |

### **Web3 Development Tips**

```typescript
// Always check if Web3 is available
if (typeof window.ethereum !== 'undefined') {
  // Web3 is available
  const provider = new ethers.BrowserProvider(window.ethereum)
} else {
  // Web3 not available
  console.error('Please install MetaMask')
}

// Handle network switching
const switchNetwork = async (chainId: number) => {
  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: `0x${chainId.toString(16)}` }],
    })
  } catch (error) {
    // Handle error
    console.error('Failed to switch network:', error)
  }
}

// Sign messages for authentication
const signMessage = async (message: string, address: string) => {
  try {
    const signature = await window.ethereum.request({
      method: 'personal_sign',
      params: [message, address],
    })
    return signature
  } catch (error) {
    console.error('Failed to sign message:', error)
    throw error
  }
}
```

## 🚀 **Deployment**

### **Local Deployment**

```bash
# Build and start all services
docker-compose -f infra/docker/development/docker-compose.yml up --build

# Run in background
docker-compose -f infra/docker/development/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker/development/docker-compose.yml logs -f

# Stop services
docker-compose -f infra/docker/development/docker-compose.yml down
```

### **Staging Deployment**

```bash
# Deploy to staging
./scripts/deployment/deploy-staging.sh

# Or use GitHub Actions
# Push to develop branch triggers staging deployment
```

### **Production Deployment**

```bash
# Create release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically deploy to production
```

## 🔧 **Troubleshooting**

### **Common Issues**

**Docker Issues:**
```bash
# Clean up Docker
docker system prune -a

# Rebuild images
docker-compose -f infra/docker/development/docker-compose.yml build --no-cache

# Check container logs
docker-compose -f infra/docker/development/docker-compose.yml logs backend
```

**Database Issues:**
```bash
# Reset database
docker-compose -f infra/docker/development/docker-compose.yml down -v
docker-compose -f infra/docker/development/docker-compose.yml up -d

# Run migrations
docker-compose -f infra/docker/development/docker-compose.yml exec backend python manage.py migrate
```

**Frontend Issues:**
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Clear build cache
npm run clean
npm run build
```

**Web3 Issues:**
```bash
# Clear browser cache
# Reset MetaMask account
# Check network configuration
# Verify RPC URLs in environment variables
```

### **Getting Help**

1. **Check Documentation**: Start with this guide and other docs
2. **Search Issues**: Look for similar issues in GitHub
3. **Ask in Slack**: Use the #development channel
4. **Create Issue**: If you can't find a solution

## 📚 **Resources**

### **Documentation Links**

- 📖 [Main README](../README.md) - Project overview and quick start
- 🗺️ [Roadmap](ROADMAP.md) - Development roadmap and milestones
- 🏗️ [Architecture](ARCHITECTURE.md) - System architecture and design
- 🔒 [Security](SECURITY.md) - Security practices and policies
- 🤝 [Contributing](../CONTRIBUTING.md) - Contribution guidelines
- 📋 [Code of Conduct](../CODE_OF_CONDUCT.md) - Community guidelines

### **External Resources**

**Django & Python:**
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Best Practices](https://realpython.com/python-pep8/)

**React & TypeScript:**
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)

**Web3 & Blockchain:**
- [ethers.js Documentation](https://docs.ethers.org/)
- [MetaMask Developer Guide](https://docs.metamask.io/guide/)
- [WalletConnect Documentation](https://docs.walletconnect.com/)

**DevOps & Docker:**
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Compose](https://docs.docker.com/compose/)

### **Development Tools**

**API Testing:**
- [Postman Collection](../docs/api/postman-collection.json)
- [API Documentation](http://localhost:8000/api/docs/)

**Database:**
- [Database Schema](../docs/database/schema.md)
- [Migration Guide](../docs/database/migrations.md)

**Web3:**
- [Web3 Integration Guide](../docs/web3/integration.md)
- [Smart Contract Examples](../docs/web3/contracts.md)

---

## 🎉 **Welcome to the Team!**

You're now ready to start contributing to TidyGen ERP! Remember:

- ✅ **Ask Questions**: Don't hesitate to ask for help
- ✅ **Follow Guidelines**: Stick to our coding standards
- ✅ **Write Tests**: Always write tests for new features
- ✅ **Document Changes**: Update documentation when needed
- ✅ **Be Collaborative**: Work together and share knowledge

**Happy Coding! 🚀**

---

*Last updated: $(date)*
*For questions or suggestions, please create an issue or reach out in Slack.*

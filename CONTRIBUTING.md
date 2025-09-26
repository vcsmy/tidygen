# Contributing to TidyGen ERP

Thank you for your interest in contributing to TidyGen ERP! This document provides guidelines and instructions for contributing to our Web3-enabled ERP platform.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Code Review Process](#code-review-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Docker** and **Docker Compose** for containerized development
- **Python 3.12+** for backend development
- **Node.js 18+** for frontend development
- **PostgreSQL 15+** for database operations
- **Redis 7+** for caching
- Basic knowledge of **Django**, **React**, and **Web3** technologies

### Fork and Clone Repository

1. **Fork the repository** on GitHub:
   - Go to [TidyGen ERP Repository](https://github.com/vcsmy/tidygen)
   - Click the "Fork" button in the top-right corner
   - This creates a copy of the repository in your GitHub account

2. **Clone your fork** locally:
   ```bash
   # Replace 'your-username' with your GitHub username
   git clone https://github.com/vcsmy/tidygen.git
   cd tidygen-community
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/vcsmy/tidygen.git
   ```

4. **Verify your setup**:
   ```bash
   git remote -v
   # Should show:
   # origin    https://github.com/vcsmy/tidygen.git (fetch)
   # origin    https://github.com/vcsmy/tidygen.git (push)
   # upstream  https://github.com/vcsmy/tidygen.git (fetch)
   # upstream  https://github.com/vcsmy/tidygen.git (push)
   ```

---

## 🛠️ Development Setup

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

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Development

```bash
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run specific service
docker-compose up backend frontend
```

---

## 📝 Coding Standards

### Python (Backend) Standards

#### PEP 8 Compliance
- **Line Length**: Maximum 88 characters (using Black formatter)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Use absolute imports, group by standard library, third-party, local
- **Naming Conventions**:
  - Variables and functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

#### Code Formatting Tools
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

#### Example Python Code Style
```python
# Good example
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel

User = get_user_model()


class ServiceRecord(BaseModel):
    """Service record model for tracking cleaning services."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_services')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_services')
    service_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['provider', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"Service {self.id} - {self.service_type}"
    
    def complete_service(self) -> None:
        """Mark service as completed."""
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])
```

### TypeScript/JavaScript (Frontend) Standards

#### ESLint Configuration
- **Line Length**: Maximum 100 characters
- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings, double quotes for JSX
- **Semicolons**: Always use semicolons
- **Naming Conventions**:
  - Variables and functions: `camelCase`
  - Components: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Interfaces: `PascalCase` with `I` prefix (optional)

#### Code Formatting Tools
```bash
# Install dependencies
npm install

# Format code with Prettier
npm run format

# Lint with ESLint
npm run lint

# Type check with TypeScript
npm run type-check
```

#### Example TypeScript Code Style
```typescript
// Good example
import React, { useState, useEffect } from 'react';
import { useWeb3 } from '@/contexts/Web3Context';
import { ApiService } from '@/lib/api';

interface ServiceData {
  id: number;
  client: string;
  provider: string;
  serviceType: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  amount: string;
}

interface ServiceCardProps {
  service: ServiceData;
  onStatusChange: (id: number, status: string) => void;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({ 
  service, 
  onStatusChange 
}) => {
  const { account, isConnected } = useWeb3();
  const [loading, setLoading] = useState(false);

  const handleStatusChange = async (newStatus: string): Promise<void> => {
    if (!isConnected) {
      alert('Please connect your wallet first');
      return;
    }

    setLoading(true);
    try {
      await ApiService.patch(`/services/${service.id}/`, { status: newStatus });
      onStatusChange(service.id, newStatus);
    } catch (error) {
      console.error('Failed to update service status:', error);
      alert('Failed to update service status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="service-card">
      <h3>{service.serviceType}</h3>
      <p>Status: {service.status}</p>
      <p>Amount: {service.amount} ETH</p>
      <button 
        onClick={() => handleStatusChange('completed')}
        disabled={loading || service.status === 'completed'}
      >
        {loading ? 'Updating...' : 'Mark Complete'}
      </button>
    </div>
  );
};
```

### Solidity (Smart Contracts) Standards

#### Style Guide
- **Line Length**: Maximum 120 characters
- **Indentation**: 4 spaces
- **Naming Conventions**:
  - Contracts: `PascalCase`
  - Functions: `camelCase`
  - Variables: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Events: `PascalCase`

#### Example Solidity Code Style
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ServiceVerification
 * @dev Smart contract for verifying cleaning service completion
 */
contract ServiceVerification is ReentrancyGuard, Ownable {
    struct ServiceRecord {
        uint256 serviceId;
        address client;
        address provider;
        string serviceType;
        uint256 amount;
        bool completed;
        bool verified;
        uint256 createdAt;
    }
    
    mapping(uint256 => ServiceRecord) public services;
    mapping(address => uint256[]) public clientServices;
    mapping(address => uint256[]) public providerServices;
    
    uint256 public serviceCounter;
    
    event ServiceScheduled(
        uint256 indexed serviceId,
        address indexed client,
        address indexed provider,
        string serviceType,
        uint256 amount
    );
    
    event ServiceCompleted(uint256 indexed serviceId, address indexed provider);
    event ServiceVerified(uint256 indexed serviceId, bool verified);
    
    /**
     * @dev Schedule a new service
     * @param client Address of the client
     * @param provider Address of the service provider
     * @param serviceType Type of service being provided
     * @param amount Amount to be paid for the service
     */
    function scheduleService(
        address client,
        address provider,
        string memory serviceType,
        uint256 amount
    ) external returns (uint256) {
        require(client != address(0), "Invalid client address");
        require(provider != address(0), "Invalid provider address");
        require(amount > 0, "Amount must be greater than 0");
        
        uint256 serviceId = serviceCounter++;
        
        services[serviceId] = ServiceRecord({
            serviceId: serviceId,
            client: client,
            provider: provider,
            serviceType: serviceType,
            amount: amount,
            completed: false,
            verified: false,
            createdAt: block.timestamp
        });
        
        clientServices[client].push(serviceId);
        providerServices[provider].push(serviceId);
        
        emit ServiceScheduled(serviceId, client, provider, serviceType, amount);
        
        return serviceId;
    }
    
    /**
     * @dev Complete a service (only provider can call)
     * @param serviceId ID of the service to complete
     */
    function completeService(uint256 serviceId) external {
        ServiceRecord storage service = services[serviceId];
        require(service.provider == msg.sender, "Only provider can complete service");
        require(!service.completed, "Service already completed");
        
        service.completed = true;
        
        emit ServiceCompleted(serviceId, msg.sender);
    }
    
    /**
     * @dev Verify service completion (only client can call)
     * @param serviceId ID of the service to verify
     * @param verified Whether the service was completed satisfactorily
     */
    function verifyService(uint256 serviceId, bool verified) external {
        ServiceRecord storage service = services[serviceId];
        require(service.client == msg.sender, "Only client can verify service");
        require(service.completed, "Service not completed yet");
        require(!service.verified, "Service already verified");
        
        service.verified = verified;
        
        emit ServiceVerified(serviceId, verified);
    }
}
```

---

## 📝 Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies

### Scopes (Optional)
- **api**: API-related changes
- **web3**: Web3/blockchain-related changes
- **frontend**: Frontend-related changes
- **backend**: Backend-related changes
- **contracts**: Smart contract changes
- **docs**: Documentation changes
- **tests**: Test-related changes

### Examples

#### Good Commit Messages
```bash
feat(web3): add MetaMask wallet integration

- Implement wallet connection functionality
- Add wallet state management
- Create wallet connection UI components

Closes #123

fix(api): resolve service creation validation error

The service creation endpoint was failing validation for
required fields. This fix ensures all required fields
are properly validated before creating a service.

Fixes #456

docs: update installation guide with Docker setup

Add comprehensive Docker installation instructions
and troubleshooting section.

refactor(backend): optimize database queries in service views

- Add database indexes for frequently queried fields
- Implement query optimization for service listings
- Reduce N+1 query problems

test(contracts): add comprehensive test coverage for ServiceVerification

- Test service scheduling functionality
- Test service completion workflow
- Test service verification process
- Add edge case testing

chore: update dependencies to latest versions

- Update Django to 4.2.7
- Update React to 18.2.0
- Update Web3.js to 4.3.0
```

#### Bad Commit Messages
```bash
# Too vague
fix stuff

# No type
add new feature

# Too long without body
feat: add comprehensive user management system with authentication, authorization, profile management, and settings

# No description
feat(api):

# Wrong type
fix: add new endpoint
```

---

## 🔄 Pull Request Process

### Branching Strategy

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Branch naming conventions**:
   - `feature/description` - New features
   - `fix/description` - Bug fixes
   - `docs/description` - Documentation updates
   - `refactor/description` - Code refactoring
   - `test/description` - Test additions/updates
   - `chore/description` - Maintenance tasks

### Development Workflow

1. **Make your changes** following coding standards
2. **Write tests** for new functionality
3. **Update documentation** if needed
4. **Run tests** to ensure everything passes
5. **Commit your changes** with conventional commit messages

### Pre-PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows project coding standards
- [ ] All tests pass locally
- [ ] New features have corresponding tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with main
- [ ] No merge conflicts

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill out the PR template
   - Assign appropriate reviewers
   - Link related issues

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows project standards
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)

   ## Related Issues
   Closes #123
   ```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewer tests the changes locally
4. **Approval**: PR approved by maintainer
5. **Merge**: PR merged into main branch

### After PR is Merged

1. **Delete feature branch**:
   ```bash
   git checkout main
   git pull upstream main
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**:
   ```bash
   git push origin main
   ```

---

## 🐛 Issue Guidelines

### Reporting Bugs

When reporting bugs, include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the bug
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - OS and version
   - Python version
   - Node.js version
   - Browser (for frontend issues)
5. **Screenshots** or error messages
6. **Logs** if applicable

### Feature Requests

When requesting features:

1. **Clear title** describing the feature
2. **Problem description** - what problem does this solve?
3. **Proposed solution** - how should it work?
4. **Use cases** - who would use this feature?
5. **Additional context** - any other relevant information

### Issue Templates

Use the provided issue templates:
- Bug Report
- Feature Request
- Documentation Issue
- Security Vulnerability

---

## 👥 Code Review Process

### For Contributors

1. **Self-review** your code before submitting
2. **Respond to feedback** promptly and constructively
3. **Make requested changes** and push updates
4. **Ask questions** if feedback is unclear

### For Reviewers

1. **Be constructive** and respectful in feedback
2. **Test changes** locally when possible
3. **Check for**:
   - Code quality and standards
   - Test coverage
   - Documentation updates
   - Security implications
   - Performance impact
4. **Approve** when satisfied with changes

### Review Checklist

- [ ] Code follows project standards
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] No breaking changes (or properly documented)

---

## 🧪 Testing Guidelines

### Backend Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test apps.accounts.tests.test_models

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Smart Contract Testing

```bash
cd apps/backend/smart_contracts

# Run tests
npm test

# Run tests with gas reporting
npm run test:gas

# Run tests with coverage
npm run test:coverage
```

### Test Requirements

- **Unit tests** for all new functionality
- **Integration tests** for API endpoints
- **End-to-end tests** for critical user flows
- **Smart contract tests** for all contract functions
- **Minimum 80% code coverage**

---

## 📚 Documentation

### Documentation Standards

- **Clear and concise** writing
- **Code examples** for complex concepts
- **Up-to-date** with code changes
- **Searchable** and well-organized

### Types of Documentation

1. **API Documentation**: Auto-generated from code comments
2. **User Guides**: Step-by-step instructions
3. **Developer Guides**: Technical implementation details
4. **Architecture Docs**: System design and structure
5. **Deployment Guides**: Setup and configuration

### Writing Documentation

```markdown
# Clear Title

Brief description of what this document covers.

## Prerequisites

List any requirements or setup needed.

## Step-by-Step Instructions

1. First step
2. Second step
3. Third step

## Code Examples

```python
# Example code with comments
def example_function():
    """Example function with docstring."""
    return "Hello, World!"
```

## Troubleshooting

Common issues and solutions.

## Related Documentation

Links to related docs.
```

---

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** and constructive
- **Be patient** with newcomers
- **Be collaborative** and helpful
- **Be professional** in all interactions

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Discord**: For real-time chat (link in README)
- **Email**: For security issues or private matters

### Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributor graph**
- **Community highlights**

---

## 🎯 Getting Started as a Contributor

### First Contribution

1. **Start small**: Look for issues labeled "good first issue"
2. **Read documentation**: Understand the project structure
3. **Ask questions**: Don't hesitate to ask for help
4. **Follow guidelines**: Use this contributing guide

### Ways to Contribute

- **Code contributions**: Bug fixes, features, improvements
- **Documentation**: Writing, editing, translating
- **Testing**: Finding bugs, writing tests
- **Design**: UI/UX improvements, graphics
- **Community**: Helping others, moderating discussions

### Mentorship

- **New contributor program**: Pair with experienced contributors
- **Office hours**: Regular sessions for questions
- **Documentation**: Comprehensive guides and tutorials

---

## 📞 Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [hello@tidygen.io](mailto:hello@tidygen.io)
- **Discord**: [Join our community](https://discord.gg/tidygen)

---

Thank you for contributing to TidyGen ERP! Together, we're building the future of Web3-enabled business management. 🚀

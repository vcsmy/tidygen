# Contributing to TidyGen ERP

Thank you for your interest in contributing to **TidyGen ERP**! This document provides comprehensive guidelines and information for contributors to help you get started and make meaningful contributions to our Web3-enabled ERP platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

## 🤝 Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@tidygen.com](mailto:conduct@tidygen.com).

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (latest version)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)
- **Git** (for version control)
- **Basic knowledge** of React, Django, and Web3 concepts

### Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/tidygen.git
   cd tidygen
   ```
3. **Start development environment**:
   ```bash
   make docker-up
   ```
4. **Run tests** to ensure everything works:
   ```bash
   make test
   ```

## 🛠️ Development Setup

### Environment Setup

1. **Copy environment files**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

2. **Start all services**:
   ```bash
   make docker-up
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/

### Local Development (Without Docker)

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📝 Coding Standards

### 🐍 **Python (Backend)**

- **Style Guide**: Follow [PEP 8](https://pep8.org/)
- **Code Formatting**: Use [Black](https://black.readthedocs.io/)
- **Linting**: Use [flake8](https://flake8.pycqa.org/)
- **Type Checking**: Use [mypy](https://mypy.readthedocs.io/)
- **Import Sorting**: Use [isort](https://pycqa.github.io/isort/)

```python
# Example of good Python code
from typing import List, Optional
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    """Product model for inventory management."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name
    
    def get_display_price(self) -> str:
        """Return formatted price string."""
        return f"${self.price:.2f}"
```

### ⚛️ **TypeScript/JavaScript (Frontend)**

- **Linting**: Use [ESLint](https://eslint.org/) with our configuration
- **Formatting**: Use [Prettier](https://prettier.io/)
- **Type Safety**: Use TypeScript strict mode
- **Import Style**: Use absolute imports

```typescript
// Example of good TypeScript code
import React, { useState, useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { Product } from '@/types/product'

interface ProductListProps {
  products: Product[]
  onProductSelect: (product: Product) => void
}

export const ProductList: React.FC<ProductListProps> = ({
  products,
  onProductSelect,
}) => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const { user } = useAuthStore()

  useEffect(() => {
    if (selectedProduct) {
      onProductSelect(selectedProduct)
    }
  }, [selectedProduct, onProductSelect])

  return (
    <div className="product-list">
      {products.map((product) => (
        <div
          key={product.id}
          className="product-item"
          onClick={() => setSelectedProduct(product)}
        >
          {product.name}
        </div>
      ))}
    </div>
  )
}
```

### ⛓️ **Web3 Integration**

- **Wallet Integration**: Use ethers.js for frontend, web3.py for backend
- **Error Handling**: Always handle wallet connection failures
- **Security**: Never store private keys in the application
- **Testing**: Mock blockchain interactions in tests

```typescript
// Example Web3 integration
import { ethers } from 'ethers'

export const connectWallet = async (): Promise<string> => {
  try {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed')
    }
    
    const provider = new ethers.BrowserProvider(window.ethereum)
    const signer = await provider.getSigner()
    const address = await signer.getAddress()
    
    return address
  } catch (error) {
    console.error('Wallet connection failed:', error)
    throw error
  }
}
```

## 🧪 Testing Guidelines

### **Backend Testing (pytest)**

```bash
# Run all tests
cd backend && pytest

# Run with coverage
cd backend && pytest --cov=. --cov-report=html

# Run specific test categories
cd backend && pytest tests/unit/        # Unit tests
cd backend && pytest tests/integration/ # Integration tests
cd backend && pytest tests/web3/        # Web3 tests
```

### **Frontend Testing (Vitest)**

```bash
# Run all tests
cd frontend && npm test

# Run with coverage
cd frontend && npm run test:coverage

# Run with UI
cd frontend && npm run test:ui
```

### **Test Requirements**

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and component interactions
- **Web3 Tests**: Test blockchain interactions (use mocks)
- **E2E Tests**: Test complete user workflows
- **Coverage**: Maintain 90%+ coverage for backend, 85%+ for frontend

## 📚 Documentation

### **Code Documentation**

- **Docstrings**: Use Google-style docstrings for Python
- **JSDoc**: Use JSDoc for TypeScript functions
- **Comments**: Explain complex business logic
- **README**: Keep setup instructions current

### **API Documentation**

- **OpenAPI**: Update API specifications when adding endpoints
- **Examples**: Provide request/response examples
- **Authentication**: Document authentication requirements

### **Architecture Documentation**

- **System Design**: Update architecture docs for structural changes
- **Database Schema**: Document model changes
- **Web3 Integration**: Document blockchain interactions

## 🔄 Pull Request Process

### **Before Submitting**

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following coding standards

3. **Add tests** for new functionality

4. **Update documentation** as needed

5. **Run the full test suite**:
   ```bash
   make test
   make lint
   make format
   ```

6. **Commit your changes** using conventional commits:
   ```bash
   git commit -m "feat(inventory): add product search functionality"
   ```

### **Pull Request Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Web3 Integration (if applicable)
- [ ] Wallet connection tested
- [ ] Smart contract interaction tested
- [ ] Transaction handling tested

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## 🐛 Issue Guidelines

### **Bug Reports**

Use the bug report template and include:

- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, browser, Node.js version)
- **Screenshots** (if applicable)
- **Error logs** (if applicable)

### **Feature Requests**

Use the feature request template and include:

- **Use case description**
- **Proposed solution**
- **Alternative solutions considered**
- **Additional context**

### **Web3 Issues**

For Web3-related issues, also include:

- **Wallet type and version**
- **Network** (mainnet, testnet, local)
- **Transaction hash** (if applicable)
- **Smart contract address** (if applicable)

## 🚀 Release Process

### **Version Bumping**

- **Major**: Breaking changes
- **Minor**: New features
- **Patch**: Bug fixes

### **Release Checklist**

1. **Update version numbers** in package.json and setup.py
2. **Update CHANGELOG.md** with new features and fixes
3. **Create git tag**: `git tag v1.0.0`
4. **Update documentation** for new features
5. **Deploy to staging** for final testing
6. **Deploy to production**

## 🆘 Getting Help

### **Community Support**

- **GitHub Discussions**: [Community discussions](https://github.com/vcsmy/tidygen/discussions)
- **Discord**: [Join our Discord server](https://discord.gg/tidygen)
- **Stack Overflow**: Tag questions with `tidygen-erp`

### **Direct Support**

- **Technical Issues**: [GitHub Issues](https://github.com/vcsmy/tidygen/issues)
- **Security Issues**: [security@tidygen.com](mailto:security@tidygen.com)
- **General Questions**: [support@tidygen.com](mailto:support@tidygen.com)

### **Documentation**

- **Architecture Guide**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Documentation**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Roadmap**: [docs/ROADMAP.md](docs/ROADMAP.md)

## 🏆 Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Feature contributors highlighted
- **Documentation**: Code contributors credited
- **Community**: Special recognition for significant contributions

## 📋 Contribution Areas

### **High Priority**

- **Bug fixes** and security improvements
- **Web3 integration** enhancements
- **Performance optimizations**
- **Test coverage** improvements

### **Medium Priority**

- **New ERP modules** (HR, Advanced Analytics)
- **UI/UX improvements**
- **Documentation** enhancements
- **Developer tools** and utilities

### **Low Priority**

- **Experimental features**
- **Nice-to-have** functionality
- **Code refactoring**
- **Style improvements**

---

Thank you for contributing to **TidyGen ERP**! Your contributions help us build the future of Web3-enabled business management. 🚀

**Questions?** Feel free to reach out to our community or open a discussion on GitHub!
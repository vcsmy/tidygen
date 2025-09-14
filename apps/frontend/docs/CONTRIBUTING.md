# Contributing to TidyGen

Thank you for your interest in contributing to TidyGen! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Report issues and bugs
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit code improvements
- **Documentation**: Improve documentation
- **Testing**: Add or improve tests
- **Web3 Integration**: Enhance blockchain features
- **UI/UX**: Improve user interface and experience

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+ and pip
- Docker and Docker Compose
- Git
- Basic knowledge of React, TypeScript, and Django

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/tidygen.git
   cd tidygen
   ```

2. **Install Dependencies**
   ```bash
   # Frontend
   cd apps/frontend
   npm install
   
   # Backend
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1: Frontend
   cd apps/frontend
   npm run dev
   
   # Terminal 2: Backend
   cd apps/backend
   python manage.py runserver
   ```

## 📋 Development Guidelines

### Code Style

#### Frontend (React/TypeScript)
- Use TypeScript for all new code
- Follow React best practices and hooks
- Use functional components over class components
- Implement proper error boundaries
- Use ESLint and Prettier for code formatting

```typescript
// Good example
interface UserProps {
  id: string;
  name: string;
  email: string;
}

const UserComponent: React.FC<UserProps> = ({ id, name, email }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    // Component logic
  }, [id]);
  
  return (
    <div className="user-component">
      <h2>{name}</h2>
      <p>{email}</p>
    </div>
  );
};
```

#### Backend (Django/Python)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Implement proper error handling
- Write comprehensive docstrings
- Use Django best practices

```python
# Good example
from typing import List, Optional
from django.db import models
from django.contrib.auth.models import User

class Partner(models.Model):
    """Partner model for managing reseller accounts."""
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=255)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    
    def get_commission_rate(self) -> float:
        """Calculate commission rate based on tier."""
        return TIER_RATES.get(self.tier, 0.15)
    
    def __str__(self) -> str:
        return f"{self.company} ({self.name})"
```

### Git Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add partner commission tracking"
   ```

4. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(partner): add commission calculation logic
fix(auth): resolve JWT token refresh issue
docs(api): update authentication endpoints
test(web3): add DID authentication tests
```

## 🧪 Testing

### Frontend Testing
```bash
cd apps/frontend
npm run test              # Run tests
npm run test:coverage     # Run with coverage
npm run test:watch        # Watch mode
```

### Backend Testing
```bash
cd apps/backend
python manage.py test                    # Run all tests
python manage.py test apps.partners     # Run specific app tests
python manage.py test --coverage        # Run with coverage
```

### Integration Testing
```bash
npm run test:integration
```

### Test Requirements
- Maintain >80% code coverage
- Write unit tests for new functions
- Write integration tests for API endpoints
- Test Web3 functionality with mock providers

## 📚 Documentation

### Code Documentation
- Use JSDoc for TypeScript functions
- Use Python docstrings for Django functions
- Document complex algorithms and business logic
- Include examples in documentation

### API Documentation
- Update Swagger/OpenAPI specifications
- Document new endpoints
- Include request/response examples
- Document authentication requirements

### User Documentation
- Update README.md for new features
- Add screenshots for UI changes
- Document configuration options
- Provide troubleshooting guides

## 🔧 Web3 Development

### Blockchain Integration
- Use Polkadot.js for Substrate interaction
- Implement proper error handling for blockchain calls
- Add retry logic for network issues
- Mock blockchain calls in tests

### IPFS Integration
- Handle file upload/download errors gracefully
- Implement progress tracking for large files
- Add content validation
- Test with local IPFS node

### Example Web3 Component
```typescript
import { useEffect, useState } from 'react';
import { ApiPromise, WsProvider } from '@polkadot/api';

const Web3Component: React.FC = () => {
  const [api, setApi] = useState<ApiPromise | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const connectToSubstrate = async () => {
      try {
        const provider = new WsProvider('ws://localhost:9944');
        const apiInstance = await ApiPromise.create({ provider });
        setApi(apiInstance);
        setIsConnected(true);
      } catch (error) {
        console.error('Failed to connect to Substrate:', error);
        setIsConnected(false);
      }
    };

    connectToSubstrate();
  }, []);

  return (
    <div>
      <p>Substrate Connection: {isConnected ? 'Connected' : 'Disconnected'}</p>
    </div>
  );
};
```

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues
2. Test with latest version
3. Gather relevant information

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS, Windows, Linux]
- Browser: [e.g., Chrome, Firefox, Safari]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

## 🔍 Code Review Process

### For Contributors
1. Ensure all tests pass
2. Update documentation
3. Follow coding standards
4. Respond to review feedback
5. Keep PRs focused and small

### For Reviewers
1. Check code quality and style
2. Verify tests are adequate
3. Test functionality manually
4. Provide constructive feedback
5. Approve when ready

## 🏷️ Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] Docker images built
- [ ] Deployed to staging
- [ ] Deployed to production

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the golden rule

### Communication
- Use GitHub issues for bug reports and feature requests
- Use GitHub discussions for questions and ideas
- Join our Discord for real-time chat
- Follow us on Twitter for updates

## 📞 Getting Help

### Resources
- [Documentation](https://docs.tidygen.io)
- [GitHub Issues](https://github.com/your-org/tidygen/issues)
- [Discord Community](https://discord.gg/your-discord)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/tidygen)

### Contact
- **Email**: contributors@tidygen.io
- **Discord**: Join our community server
- **Twitter**: [@tidygen_io](https://twitter.com/tidygen_io)

## 🎉 Recognition

### Contributors
We recognize contributors in several ways:
- GitHub contributor list
- Release notes acknowledgments
- Contributor badges
- Special recognition for significant contributions

### Types of Recognition
- **Bug Hunter**: Finding and reporting bugs
- **Feature Creator**: Implementing new features
- **Documentation Hero**: Improving documentation
- **Web3 Pioneer**: Advancing blockchain integration
- **Community Champion**: Helping other contributors

## 📄 License

By contributing to TidyGen, you agree that your contributions will be licensed under the same license as the project.

- **Community Edition**: MIT License
- **Commercial Edition**: Commercial License

## 🙏 Thank You

Thank you for contributing to TidyGen! Your contributions help make this project better for everyone in the Web3 and enterprise communities.

---

**Happy Contributing! 🚀**

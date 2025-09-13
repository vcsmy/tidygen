# Contributing to iNeat ERP Community Edition

Thank you for your interest in contributing to iNeat ERP Community Edition! We welcome contributions from the community and appreciate your help in making this project better.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** provided
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

We love feature suggestions! Please:

1. **Check the roadmap** to see if it's already planned
2. **Use the feature request template**
3. **Provide clear use cases** and benefits
4. **Consider the community impact**

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/ineat-erp-community.git
   cd ineat-erp-community
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Setup

1. **Backend Development**:
   ```bash
   cd apps/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   python manage.py migrate
   python manage.py setup_single_organization --create-admin
   python manage.py runserver
   ```

2. **Frontend Development**:
   ```bash
   cd apps/frontend
   npm install
   npm run dev
   ```

3. **Docker Development**:
   ```bash
   docker-compose up -d
   ```

#### Code Style Guidelines

- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript/TypeScript**: Use Prettier, follow ESLint rules
- **Django**: Follow Django best practices
- **React**: Use functional components with hooks
- **Commits**: Use semantic commit messages

#### Testing

- **Write tests** for new features
- **Ensure all tests pass** before submitting
- **Add integration tests** for API endpoints
- **Test with different user roles**

#### Documentation

- **Update README** if needed
- **Add docstrings** to new functions/classes
- **Update API documentation** for new endpoints
- **Include examples** in your changes

### Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run tests locally**:
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests
   npm test
   
   # Docker tests
   docker-compose exec backend python manage.py test
   ```

3. **Create a pull request** with:
   - Clear title and description
   - Reference related issues
   - Screenshots for UI changes
   - Testing instructions

4. **Respond to feedback** promptly and make requested changes

## 🏗️ Project Structure

```
ineat-erp-community/
├── apps/
│   ├── backend/          # Django backend
│   │   ├── apps/         # Django apps
│   │   ├── backend/      # Django settings
│   │   └── manage.py
│   └── frontend/         # React frontend
├── infra/               # Infrastructure files
├── docs/               # Documentation
├── docker-compose.yml  # Development setup
└── README.md
```

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.hr

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## 📝 Commit Message Format

Use semantic commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(hr): add employee leave management
fix(sales): resolve invoice calculation bug
docs: update deployment guide
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**:
   - OS and version
   - Python version
   - Node.js version
   - Docker version (if using)

2. **Steps to reproduce**:
   - Clear, numbered steps
   - Expected behavior
   - Actual behavior

3. **Additional context**:
   - Screenshots
   - Error messages
   - Log files

## 💡 Feature Requests

When suggesting features:

1. **Use case**: Why is this feature needed?
2. **User story**: How would users interact with it?
3. **Implementation**: Any ideas on how to implement?
4. **Alternatives**: Other solutions considered?

## 🏷️ Labels

We use labels to categorize issues and PRs:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Community Forum**: For broader community discussions

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Community highlights

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to iNeat ERP Community Edition! 🚀

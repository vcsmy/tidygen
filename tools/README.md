# Tools Directory

This directory contains development tools, configurations, and utilities for code quality, consistency, and productivity in the TidyGen ERP platform.

## 📁 Structure

```
tools/
├── linting/        # Linting configurations
├── formatting/     # Code formatting tools
├── generators/     # Code generators
└── validation/     # Validation tools
```

## 🔧 Tool Categories

### Linting (`linting/`)
- **ESLint**: JavaScript/TypeScript linting
- **Pylint**: Python code linting
- **Markdownlint**: Markdown file linting

### Formatting (`formatting/`)
- **Prettier**: Code formatting for frontend
- **Black**: Python code formatting
- **isort**: Python import sorting

### Generators (`generators/`)
- **Django Generators**: Django app and model generators
- **React Generators**: Component and page generators
- **API Generators**: API endpoint generators

### Validation (`validation/`)
- **Schema Validation**: Data schema validation
- **Security Validation**: Security rule validation
- **Performance Validation**: Performance rule validation

## 🚀 Quick Start

### Linting
```bash
# Lint all code
npm run lint

# Lint frontend code
npm run lint:frontend

# Lint backend code
npm run lint:backend
```

### Formatting
```bash
# Format all code
npm run format

# Format frontend code
npm run format:frontend

# Format backend code
npm run format:backend
```

### Code Generation
```bash
# Generate Django app
./tools/generators/django/app_generator.py myapp

# Generate React component
./tools/generators/react/component_generator.js MyComponent

# Generate API endpoint
./tools/generators/api/endpoint_generator.py myendpoint
```

## 📋 Tool Configurations

### ESLint Configuration
```javascript
// tools/linting/eslint/.eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  rules: {
    'react/prop-types': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

### Prettier Configuration
```json
// tools/formatting/prettier/.prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

### Black Configuration
```toml
# tools/formatting/black/pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

## 🎯 Code Generators

### Django App Generator
```python
# tools/generators/django/app_generator.py
import os
import sys
from django.core.management import execute_from_command_line

def generate_app(app_name):
    """Generate a new Django app with standard structure."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tidygen_erp.settings')
    
    # Create app
    execute_from_command_line(['manage.py', 'startapp', app_name])
    
    # Create additional files
    create_app_files(app_name)

def create_app_files(app_name):
    """Create additional files for the app."""
    # Create serializers.py
    # Create permissions.py
    # Create managers.py
    # Create utils.py
    pass
```

### React Component Generator
```javascript
// tools/generators/react/component_generator.js
const fs = require('fs');
const path = require('path');

function generateComponent(componentName) {
  const componentDir = path.join('apps/frontend/src/components', componentName);
  
  // Create component directory
  fs.mkdirSync(componentDir, { recursive: true });
  
  // Generate component files
  generateComponentFile(componentName, componentDir);
  generateTestFile(componentName, componentDir);
  generateIndexFile(componentName, componentDir);
}

function generateComponentFile(name, dir) {
  const content = `import React from 'react';
import { ${name}Props } from './types';

export const ${name}: React.FC<${name}Props> = ({ ...props }) => {
  return (
    <div className="${name.toLowerCase()}">
      {/* Component content */}
    </div>
  );
};
`;
  
  fs.writeFileSync(path.join(dir, `${name}.tsx`), content);
}
```

## 🔍 Validation Tools

### Schema Validation
```python
# tools/validation/schema/validator.py
import jsonschema
from typing import Dict, Any

def validate_api_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate API data against JSON schema."""
    try:
        jsonschema.validate(data, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
```

### Security Validation
```python
# tools/validation/security/security_checker.py
import re
from typing import List, Dict

def check_sql_injection(code: str) -> List[str]:
    """Check for potential SQL injection vulnerabilities."""
    vulnerabilities = []
    
    # Check for raw SQL queries
    if re.search(r'execute\s*\(\s*["\'].*%s', code):
        vulnerabilities.append("Potential SQL injection in raw query")
    
    return vulnerabilities
```

## 🔄 Pre-commit Hooks

### Husky Configuration
```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "pre-push": "npm run test"
    }
  },
  "lint-staged": {
    "apps/frontend/**/*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "apps/backend/**/*.py": [
      "black",
      "isort"
    ]
  }
}
```

### Lint-staged Configuration
```javascript
// tools/linting/lint-staged.config.js
module.exports = {
  'apps/frontend/**/*.{js,jsx,ts,tsx}': [
    'eslint --fix',
    'prettier --write',
    'git add'
  ],
  'apps/backend/**/*.py': [
    'black',
    'isort',
    'git add'
  ],
  '*.md': [
    'markdownlint --fix',
    'git add'
  ]
};
```

## 📊 Code Quality Metrics

### Coverage Reports
- **Backend Coverage**: Python code coverage with pytest-cov
- **Frontend Coverage**: JavaScript/TypeScript coverage with Jest
- **Integration Coverage**: API and database integration coverage

### Quality Gates
- **Minimum Coverage**: 90% backend, 85% frontend
- **Linting Errors**: Zero linting errors allowed
- **Security Issues**: Zero critical security issues
- **Performance**: Response time < 200ms

## 🛠️ Development Workflow

### Code Review Process
1. **Pre-commit**: Automatic linting and formatting
2. **Pre-push**: Run tests and quality checks
3. **Pull Request**: Automated CI/CD pipeline
4. **Code Review**: Manual review with quality metrics

### Quality Assurance
- **Automated Testing**: Unit, integration, and E2E tests
- **Code Analysis**: Static code analysis and security scanning
- **Performance Testing**: Load and stress testing
- **Documentation**: Automated documentation generation

## 📚 Tool Documentation

### Configuration Files
- **ESLint**: `tools/linting/eslint/.eslintrc.js`
- **Prettier**: `tools/formatting/prettier/.prettierrc`
- **Black**: `tools/formatting/black/pyproject.toml`
- **Pylint**: `tools/linting/pylint/.pylintrc`

### Usage Guides
- **Linting Guide**: How to configure and use linting tools
- **Formatting Guide**: Code formatting standards and tools
- **Generator Guide**: How to use code generators
- **Validation Guide**: Data and security validation

## 🆘 Troubleshooting

### Common Issues
1. **Linting Errors**: Check configuration files and fix violations
2. **Formatting Issues**: Run formatters and check configuration
3. **Generator Failures**: Verify input parameters and dependencies
4. **Validation Errors**: Check data format and schema definitions

### Debug Mode
```bash
# Debug linting issues
npm run lint -- --debug

# Debug formatting issues
npm run format -- --debug

# Debug generator issues
./tools/generators/django/app_generator.py --debug myapp
```

### Support
- **Tool Issues**: Check tool documentation and configuration
- **Configuration Issues**: Verify configuration files
- **Performance Issues**: Review tool performance and optimization
- **Integration Issues**: Check tool integration with CI/CD

# Testing Guide

## 🧪 **Testing Overview**

The TidyGen ERP system implements comprehensive testing across all layers, from unit tests to end-to-end testing. This guide covers testing strategies, tools, and best practices.

## 🏗️ **Testing Architecture**

### **Testing Pyramid**
```
    /\
   /  \     E2E Tests (Cypress)
  /____\    
 /      \   Integration Tests (Vitest + RTL)
/________\  
/          \ Unit Tests (Pytest, Vitest)
/____________\
```

### **Testing Layers**
1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - API endpoints and component interactions
3. **End-to-End Tests** - Complete user workflows
4. **Performance Tests** - Load and stress testing

## 🔧 **Backend Testing**

### **Testing Stack**
- **Pytest** - Python testing framework
- **Django TestCase** - Django-specific test utilities
- **Factory Boy** - Test data generation
- **Coverage** - Code coverage reporting
- **Mock** - Mocking external dependencies

### **Test Structure**
```
apps/backend/
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── fixtures/            # Test fixtures
│   ├── unit/                # Unit tests
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_serializers.py
│   ├── integration/         # Integration tests
│   │   ├── test_api.py
│   │   └── test_workflows.py
│   └── performance/         # Performance tests
│       └── test_load.py
```

### **Running Backend Tests**
```bash
cd apps/backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=apps --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_models.py::test_user_creation
```

### **Test Examples**

#### **Model Tests**
```python
# tests/unit/test_models.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.models import Organization

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_superuser_creation(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            organization=self.organization
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
```

#### **API Tests**
```python
# tests/integration/test_api.py
import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITest(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
        self.client.force_authenticate(user=self.user)
    
    def test_user_list(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_user_creation(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
```

#### **View Tests**
```python
# tests/unit/test_views.py
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            organization=self.organization
        )
    
    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_view_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')
```

### **Test Fixtures**
```python
# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organization

User = get_user_model()

@pytest.fixture
def organization():
    return Organization.objects.create(
        name='Test Organization',
        slug='test-org'
    )

@pytest.fixture
def user(organization):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        organization=organization
    )

@pytest.fixture
def admin_user(organization):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        organization=organization
    )
```

## 🎨 **Frontend Testing**

### **Testing Stack**
- **Vitest** - Fast unit test runner
- **React Testing Library** - Component testing utilities
- **MSW (Mock Service Worker)** - API mocking
- **Cypress** - End-to-end testing
- **@testing-library/jest-dom** - Custom matchers

### **Test Structure**
```
apps/frontend/
├── src/
│   └── test/
│       ├── setup.ts              # Test setup
│       ├── integration-setup.ts  # Integration test setup
│       ├── utils/
│       │   └── test-utils.tsx    # Custom render utilities
│       └── mocks/
│           ├── handlers.ts       # MSW request handlers
│           └── server.ts         # MSW server setup
├── cypress/
│   ├── e2e/                      # E2E test files
│   ├── support/                  # Cypress support files
│   └── fixtures/                 # Test fixtures
├── vitest.config.ts              # Vitest configuration
├── vitest.integration.config.ts  # Integration test config
└── cypress.config.ts             # Cypress configuration
```

### **Running Frontend Tests**
```bash
cd apps/frontend

# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage

# Watch mode
npm run test:watch
```

### **Test Examples**

#### **Component Tests**
```tsx
// src/components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../ui/button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies variant styles', () => {
    render(<Button variant="destructive">Delete</Button>)
    const button = screen.getByText('Delete')
    expect(button).toHaveClass('bg-destructive')
  })
})
```

#### **Hook Tests**
```tsx
// src/hooks/__tests__/useAuth.test.tsx
import { renderHook, act } from '@testing-library/react'
import { useAuth } from '../useAuth'
import { AuthProvider } from '@/contexts/AuthContext'

describe('useAuth', () => {
  it('should login successfully', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login('admin', 'admin123')
    })

    expect(result.current.user).toBeTruthy()
    expect(result.current.isAuthenticated).toBe(true)
  })
})
```

#### **Integration Tests**
```tsx
// src/test/integration/auth.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Login } from '@/pages/Login'
import { server } from '../mocks/server'

// Start MSW server
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('Authentication Integration', () => {
  it('should login and redirect to dashboard', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    })

    render(
      <QueryClientProvider client={queryClient}>
        <Login />
      </QueryClientProvider>
    )

    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'admin' }
    })
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'admin123' }
    })
    fireEvent.click(screen.getByText('Login'))

    await waitFor(() => {
      expect(screen.getByText('Welcome, Admin!')).toBeInTheDocument()
    })
  })
})
```

### **MSW Setup**
```typescript
// src/test/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  rest.post('/api/auth/login/', (req, res, ctx) => {
    return res(
      ctx.json({
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          first_name: 'Admin',
          last_name: 'User'
        }
      })
    )
  }),

  rest.get('/api/users/', (req, res, ctx) => {
    return res(
      ctx.json({
        results: [
          {
            id: 1,
            username: 'admin',
            email: 'admin@example.com',
            first_name: 'Admin',
            last_name: 'User'
          }
        ]
      })
    )
  })
]
```

## 🎭 **End-to-End Testing**

### **Cypress Setup**
```typescript
// cypress/e2e/auth.cy.ts
describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('should login successfully', () => {
    cy.get('[data-testid="username"]').type('admin')
    cy.get('[data-testid="password"]').type('admin123')
    cy.get('[data-testid="login-button"]').click()
    
    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="user-menu"]').should('contain', 'Admin User')
  })

  it('should show error for invalid credentials', () => {
    cy.get('[data-testid="username"]').type('invalid')
    cy.get('[data-testid="password"]').type('wrong')
    cy.get('[data-testid="login-button"]').click()
    
    cy.get('[data-testid="error-message"]').should('be.visible')
    cy.url().should('include', '/login')
  })
})
```

### **Complete Workflow Tests**
```typescript
// cypress/e2e/complete-workflow.cy.ts
describe('Complete User Workflow', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123')
  })

  it('should create and manage a user', () => {
    // Navigate to user management
    cy.visit('/admin/users')
    
    // Create new user
    cy.get('[data-testid="add-user-button"]').click()
    cy.get('[data-testid="username"]').type('newuser')
    cy.get('[data-testid="email"]').type('newuser@example.com')
    cy.get('[data-testid="first-name"]').type('New')
    cy.get('[data-testid="last-name"]').type('User')
    cy.get('[data-testid="save-button"]').click()
    
    // Verify user was created
    cy.get('[data-testid="user-table"]').should('contain', 'newuser')
    
    // Edit user
    cy.get('[data-testid="edit-user-button"]').first().click()
    cy.get('[data-testid="first-name"]').clear().type('Updated')
    cy.get('[data-testid="save-button"]').click()
    
    // Verify user was updated
    cy.get('[data-testid="user-table"]').should('contain', 'Updated')
  })
})
```

## 📊 **Test Coverage**

### **Backend Coverage**
```bash
cd apps/backend
pytest --cov=apps --cov-report=html --cov-report=term
```

### **Frontend Coverage**
```bash
cd apps/frontend
npm run test:coverage
```

### **Coverage Targets**
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **Critical Paths**: 100% coverage

## 🚀 **Performance Testing**

### **Load Testing**
```python
# tests/performance/test_load.py
import pytest
import requests
from concurrent.futures import ThreadPoolExecutor

def test_api_load():
    def make_request():
        response = requests.get('http://localhost:8000/api/users/')
        return response.status_code == 200
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [future.result() for future in futures]
    
    assert all(results)
```

### **Frontend Performance**
```typescript
// cypress/e2e/performance.cy.ts
describe('Performance Tests', () => {
  it('should load dashboard within 2 seconds', () => {
    const start = performance.now()
    cy.visit('/dashboard')
    cy.get('[data-testid="dashboard-content"]').should('be.visible')
    cy.then(() => {
      const end = performance.now()
      expect(end - start).to.be.lessThan(2000)
    })
  })
})
```

## 🔧 **CI/CD Integration**

### **GitHub Actions**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd apps/backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd apps/backend
          pytest --cov=apps --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd apps/frontend
          npm ci
      - name: Run tests
        run: |
          cd apps/frontend
          npm run test:coverage
      - name: Run E2E tests
        run: |
          cd apps/frontend
          npm run test:e2e:ci
```

## 📝 **Testing Best Practices**

### **Test Organization**
- Group related tests in describe blocks
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated

### **Test Data**
- Use factories for test data generation
- Clean up test data after each test
- Use realistic test data
- Avoid hardcoded values

### **Assertions**
- Use specific assertions
- Test both positive and negative cases
- Verify error conditions
- Check side effects

### **Mocking**
- Mock external dependencies
- Use MSW for API mocking
- Mock time-dependent functions
- Avoid over-mocking

## 🐛 **Debugging Tests**

### **Backend Debugging**
```bash
# Run tests with debug output
pytest -v -s

# Run specific test with pdb
pytest --pdb tests/test_models.py::test_user_creation

# Run with coverage and debug
pytest --cov=apps --cov-report=html -v
```

### **Frontend Debugging**
```bash
# Run tests in watch mode
npm run test:watch

# Run with debug output
npm run test -- --reporter=verbose

# Run specific test file
npm run test Button.test.tsx
```

### **Cypress Debugging**
```bash
# Run Cypress in headed mode
npx cypress open

# Run specific test
npx cypress run --spec "cypress/e2e/auth.cy.ts"
```

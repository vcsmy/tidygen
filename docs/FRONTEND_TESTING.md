# Frontend Testing Guide

## 🎯 **Testing Overview**

This document provides a comprehensive guide to the frontend testing setup for the TidyGen ERP system. The testing infrastructure includes unit tests, integration tests, and end-to-end tests with full coverage reporting.

## 🧪 **Testing Stack**

### **Testing Frameworks**
- **Vitest**: Fast unit testing framework
- **React Testing Library**: Component testing utilities
- **MSW (Mock Service Worker)**: API mocking
- **Cypress**: End-to-end testing
- **@testing-library/user-event**: User interaction simulation

### **Coverage Tools**
- **@vitest/coverage-v8**: Code coverage reporting
- **HTML Coverage Reports**: Detailed coverage analysis

## 📁 **Testing Structure**

```
src/
├── test/
│   ├── setup.ts                    # Test setup configuration
│   ├── integration-setup.ts        # Integration test setup
│   ├── mocks/
│   │   ├── server.ts              # MSW server setup
│   │   └── handlers.ts            # API mock handlers
│   ├── utils/
│   │   └── test-utils.tsx         # Testing utilities
│   └── integration/
│       ├── auth.integration.test.tsx
│       └── dashboard.integration.test.tsx
├── components/
│   └── ui/
│       └── __tests__/
│           ├── button.test.tsx
│           ├── input.test.tsx
│           └── card.test.tsx
├── contexts/
│   └── __tests__/
│       └── AuthContext.test.tsx
└── cypress/
    ├── e2e/
    │   ├── auth.cy.ts
    │   ├── dashboard.cy.ts
    │   └── complete-workflow.cy.ts
    └── support/
        ├── e2e.ts
        └── commands.ts
```

## 🚀 **Running Tests**

### **Install Dependencies**
```bash
npm install
```

### **Unit Tests**
```bash
# Run all unit tests
npm run test:unit

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### **Integration Tests**
```bash
# Run integration tests
npm run test:integration
```

### **End-to-End Tests**
```bash
# Run E2E tests headlessly
npm run test:e2e

# Open Cypress UI
npm run test:e2e:open
```

### **All Tests**
```bash
# Run all test suites
npm run test:all
```

## 📊 **Test Coverage**

### **Coverage Targets**
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 85%+ coverage
- **E2E Tests**: 80%+ of critical user flows

### **Coverage Reports**
- **Terminal**: Real-time coverage in terminal
- **HTML**: Detailed HTML report in `coverage/` directory
- **JSON**: Machine-readable coverage data

## 🧩 **Component Testing**

### **Testing UI Components**
```typescript
import { render, screen, fireEvent } from '../test/utils/test-utils'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### **Testing Custom Hooks**
```typescript
import { renderHook, act } from '@testing-library/react'
import { useAuth } from '../useAuth'

describe('useAuth Hook', () => {
  it('should login user successfully', async () => {
    const { result } = renderHook(() => useAuth())
    
    await act(async () => {
      await result.current.login('test@example.com', 'password')
    })
    
    expect(result.current.user).toBeTruthy()
    expect(result.current.isAuthenticated).toBe(true)
  })
})
```

## 🔗 **Integration Testing**

### **API Integration Tests**
```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { server } from '../mocks/server'
import { http, HttpResponse } from 'msw'

describe('Authentication Integration', () => {
  it('should login user and redirect to dashboard', async () => {
    server.use(
      http.post('/api/v1/auth/login/', () => {
        return HttpResponse.json({
          access: 'mock-access-token',
          user: { id: 1, email: 'test@example.com' }
        })
      })
    )

    render(<LoginForm />)
    
    // Test user interaction
    await user.type(screen.getByTestId('email-input'), 'test@example.com')
    await user.click(screen.getByTestId('login-button'))
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
  })
})
```

## 🎭 **End-to-End Testing**

### **Cypress E2E Tests**
```typescript
describe('Authentication Flow', () => {
  it('should complete full login flow', () => {
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type('admin@example.com')
    cy.get('[data-testid="password-input"]').type('password')
    cy.get('[data-testid="login-button"]').click()
    
    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="user-menu"]').should('be.visible')
  })
})
```

### **Custom Commands**
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(email)
  cy.get('[data-testid="password-input"]').type(password)
  cy.get('[data-testid="login-button"]').click()
  cy.url().should('include', '/dashboard')
})
```

## 🎯 **Testing Best Practices**

### **Component Testing**
1. **Test Behavior, Not Implementation**: Focus on what users see and do
2. **Use Data Test IDs**: Consistent selectors across components
3. **Test Error States**: Ensure error handling works correctly
4. **Test Accessibility**: Include a11y tests in component tests

### **Integration Testing**
1. **Mock External APIs**: Use MSW for consistent API mocking
2. **Test Real User Flows**: Complete user journeys
3. **Test Error Scenarios**: Network failures, API errors
4. **Test Loading States**: Ensure proper loading indicators

### **E2E Testing**
1. **Test Critical Paths**: Most important business workflows
2. **Use Page Object Model**: Reusable page components
3. **Test Cross-browser**: Chrome, Firefox, Safari
4. **Test Mobile**: Responsive design testing

## 🔧 **Mock Data**

### **API Mocking with MSW**
```typescript
// src/test/mocks/handlers.ts
export const handlers = [
  http.post('/api/v1/auth/login/', () => {
    return HttpResponse.json({
      access: 'mock-access-token',
      user: { id: 1, email: 'test@example.com' }
    })
  }),
  
  http.get('/api/v1/dashboard/', () => {
    return HttpResponse.json({
      metrics: { total_revenue: 2400000 }
    })
  })
]
```

### **Test Data Factories**
```typescript
// src/test/utils/test-utils.tsx
export const createMockProduct = (overrides = {}) => ({
  id: 1,
  name: 'Test Product',
  price: 99.99,
  stock: 100,
  ...overrides
})
```

## 📈 **Performance Testing**

### **Component Performance**
```typescript
import { performance } from 'perf_hooks'

describe('Component Performance', () => {
  it('should render within acceptable time', () => {
    const start = performance.now()
    render(<LargeComponent />)
    const end = performance.now()
    
    expect(end - start).toBeLessThan(100) // 100ms
  })
})
```

### **API Performance**
```typescript
describe('API Performance', () => {
  it('should load dashboard data within 2 seconds', async () => {
    const start = performance.now()
    await apiClient.get('/api/v1/dashboard/')
    const end = performance.now()
    
    expect(end - start).toBeLessThan(2000) // 2 seconds
  })
})
```

## 🐛 **Debugging Tests**

### **Debug Unit Tests**
```bash
# Run specific test file
npm run test button.test.tsx

# Run tests in debug mode
npm run test -- --reporter=verbose

# Run tests with UI for debugging
npm run test:ui
```

### **Debug E2E Tests**
```bash
# Open Cypress in headed mode
npm run test:e2e:open

# Run specific test file
npx cypress run --spec "cypress/e2e/auth.cy.ts"
```

## 📊 **CI/CD Integration**

### **GitHub Actions**
```yaml
# .github/workflows/test.yml
name: Frontend Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Run E2E tests
        run: npm run test:e2e
```

## 🎯 **Test Coverage Reports**

### **Coverage Thresholds**
```typescript
// vitest.config.ts
coverage: {
  thresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

### **Coverage Reports**
- **Terminal**: Real-time coverage during test runs
- **HTML**: Detailed report in `coverage/index.html`
- **JSON**: Machine-readable data for CI/CD

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
npm install
```

### **2. Run Tests**
```bash
# Start with unit tests
npm run test:unit

# Then integration tests
npm run test:integration

# Finally E2E tests
npm run test:e2e:open
```

### **3. Check Coverage**
```bash
npm run test:coverage
open coverage/index.html
```

## 📝 **Writing New Tests**

### **Component Test Template**
```typescript
import { render, screen, fireEvent } from '../test/utils/test-utils'
import { YourComponent } from './YourComponent'

describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent />)
    expect(screen.getByTestId('your-component')).toBeInTheDocument()
  })

  it('should handle user interactions', () => {
    const handleClick = vi.fn()
    render(<YourComponent onClick={handleClick} />)
    
    fireEvent.click(screen.getByTestId('your-component'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### **Integration Test Template**
```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { YourPage } from './YourPage'

describe('YourPage Integration', () => {
  it('should load data successfully', async () => {
    render(<YourPage />)
    
    await waitFor(() => {
      expect(screen.getByTestId('data-loaded')).toBeInTheDocument()
    })
  })
})
```

### **E2E Test Template**
```typescript
describe('Your Feature', () => {
  it('should complete user workflow', () => {
    cy.visit('/your-page')
    cy.get('[data-testid="your-element"]').click()
    cy.get('[data-testid="result"]').should('be.visible')
  })
})
```

## 🎯 **Success Criteria**

### **Testing Complete When:**
- [ ] 90%+ unit test coverage
- [ ] 85%+ integration test coverage
- [ ] 80%+ E2E test coverage
- [ ] All critical user flows tested
- [ ] Error scenarios covered
- [ ] Performance benchmarks met
- [ ] CI/CD pipeline integrated
- [ ] Coverage reports generated

---

**The frontend testing infrastructure is now fully implemented and ready for comprehensive testing of the TidyGen ERP system!** 🚀

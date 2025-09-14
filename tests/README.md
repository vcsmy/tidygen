# Tests Directory

This directory contains end-to-end tests, integration tests, and performance testing suites for the TidyGen ERP platform.

## 📁 Structure

```
tests/
├── e2e/           # End-to-end tests
├── integration/   # Integration tests
├── performance/   # Performance testing
└── fixtures/      # Test data and fixtures
```

## 🧪 Test Categories

### End-to-End Tests (`e2e/`)
- **Cypress**: Browser-based E2E testing
- **Playwright**: Cross-browser E2E testing
- **Scenarios**: User journey and business flow tests

### Integration Tests (`integration/`)
- **API Tests**: Backend API integration testing
- **Database Tests**: Database integration testing
- **Web3 Tests**: Blockchain integration testing
- **Third-party Tests**: External service integration

### Performance Tests (`performance/`)
- **Load Testing**: Normal load conditions
- **Stress Testing**: High load conditions
- **K6 Tests**: Performance testing with K6
- **Reports**: Performance test results

## 🚀 Quick Start

### Running Tests
```bash
# Run all tests
npm run test

# Run E2E tests
npm run test:e2e

# Run integration tests
npm run test:integration

# Run performance tests
npm run test:performance
```

### Individual Test Suites
```bash
# Cypress E2E tests
cd tests/e2e/cypress
npm run cypress:open
npm run cypress:run

# Playwright E2E tests
cd tests/e2e/playwright
npm run playwright:test

# K6 performance tests
cd tests/performance/k6
k6 run load-test.js
```

## 📋 Test Configuration

### Cypress Configuration
```javascript
// tests/e2e/cypress/cypress.config.js
module.exports = {
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
  },
}
```

### Playwright Configuration
```javascript
// tests/e2e/playwright/playwright.config.js
module.exports = {
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
}
```

### K6 Configuration
```javascript
// tests/performance/k6/load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};
```

## 🎯 Test Scenarios

### User Journey Tests
- **User Registration**: Complete user onboarding flow
- **Login Process**: Authentication and authorization
- **ERP Module Navigation**: Accessing different ERP modules
- **Web3 Integration**: Wallet connection and transactions
- **Data Management**: CRUD operations across modules

### Business Flow Tests
- **Sales Process**: Quote → Order → Invoice → Payment
- **Inventory Management**: Stock → Purchase → Receipt
- **Financial Process**: Transaction → Journal → Report
- **HR Process**: Employee → Payroll → Benefits

### Integration Tests
- **API Integration**: Backend API endpoints
- **Database Integration**: Data persistence and retrieval
- **Web3 Integration**: Blockchain interactions
- **Third-party Integration**: External service connections

## 📊 Test Data Management

### Fixtures (`fixtures/`)
- **Users**: Test user accounts and profiles
- **Organizations**: Test organization data
- **Transactions**: Sample transaction data
- **Products**: Test product catalog
- **Customers**: Test customer data

### Test Data Setup
```bash
# Load test fixtures
./scripts/setup/load-fixtures.sh

# Reset test database
./scripts/setup/reset-test-db.sh

# Generate test data
./scripts/development/generate-test-data.sh
```

## 🔧 Test Automation

### CI/CD Integration
- **GitHub Actions**: Automated test execution
- **Test Reports**: JUnit and coverage reports
- **Quality Gates**: Test failure prevention
- **Parallel Execution**: Faster test execution

### Test Reporting
- **Coverage Reports**: Code coverage analysis
- **Test Results**: Detailed test execution reports
- **Performance Metrics**: Performance test results
- **Screenshots**: Visual test failure documentation

## 🛡️ Test Security

### Security Testing
- **Authentication Tests**: Login and session management
- **Authorization Tests**: Role-based access control
- **Input Validation**: Malicious input handling
- **Web3 Security**: Wallet and transaction security

### Data Privacy
- **Test Data**: Anonymized test data only
- **Environment Isolation**: Separate test environments
- **Data Cleanup**: Automatic test data cleanup
- **Access Control**: Restricted test environment access

## 📈 Performance Testing

### Load Testing Scenarios
- **Normal Load**: Typical user traffic
- **Peak Load**: High traffic periods
- **Stress Testing**: System breaking points
- **Endurance Testing**: Long-running stability

### Performance Metrics
- **Response Time**: API and page load times
- **Throughput**: Requests per second
- **Error Rate**: Failed request percentage
- **Resource Usage**: CPU, memory, and disk usage

## 🔄 Test Maintenance

### Test Updates
- **Regular Updates**: Keep tests current with application changes
- **Test Refactoring**: Improve test maintainability
- **Coverage Analysis**: Ensure adequate test coverage
- **Performance Optimization**: Optimize slow tests

### Test Documentation
- **Test Cases**: Documented test scenarios
- **Test Data**: Test data documentation
- **Test Environment**: Environment setup documentation
- **Troubleshooting**: Common test issues and solutions

## 🆘 Troubleshooting

### Common Issues
1. **Test Timeouts**: Increase timeout values or optimize tests
2. **Flaky Tests**: Add proper waits and retries
3. **Environment Issues**: Check test environment setup
4. **Data Issues**: Verify test data and fixtures

### Debug Mode
```bash
# Run tests in debug mode
DEBUG=1 npm run test:e2e

# Verbose test output
npm run test -- --verbose

# Test specific scenarios
npm run test -- --grep "user registration"
```

### Support
- **Test Failures**: Check test logs and screenshots
- **Environment Issues**: Verify test environment setup
- **Performance Issues**: Review performance test results
- **Data Issues**: Check test fixtures and data setup

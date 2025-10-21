# Testing Guide - TidyGen Community Edition Freelancer Modules

This guide covers comprehensive testing for the freelancer ecosystem modules added to the TidyGen Community Edition.

## 📋 Test Coverage Overview

### Backend Django Apps Tested
- **`apps.freelancers`** - Individual contractor management
- **`apps.gig_management`** - Job posting and assignment system
- **`apps.contractor_payments`** - Payment processing and escrow
- **`apps.freelancer_web3`** - Advanced Web3 features and NFT badges

### Test Types Implemented
1. **Unit Tests** - Individual model and view testing
2. **API Integration Tests** - Complete workflow testing
3. **Performance Tests** - Scalability and performance validation
4. **E2E Tests** - Frontend component testing

## 🚀 Running Tests

### Backend Tests

#### Quick Test Run
```bash
# Run all freelancer module tests
python apps/backend/run_tests.py

# Or run individual apps
python apps/backend/manage.py test apps.freelancers --verbosity=2
python apps/backend/manage.py test apps.gig_management --verbosity=2
python apps/backend/manage.py test apps.contractor_payments --verbosity=2
python apps/backend/manage.py test apps.freelancer_web3 --verbosity=2
```

#### With Coverage
```bash
cd apps/backend
pytest --cov=apps.freelancers --cov=apps.gig_management --cov=apps.contractor_payments --cov=apps.freelancer_web3 --cov-report=html
```

#### Integration Tests
```bash
python apps/backend/manage.py test tests.test_freelancer_integration --verbosity=2
```

### Frontend Tests

#### Unit Tests
```bash
cd apps/frontend
npm run test        # Interactive mode
npm run test:run    # Single run
npm run test:coverage  # With coverage
```

#### E2E Tests
```bash
cd apps/frontend
npm run test:e2e        # Headless mode
npm run test:e2e:ui     # Interactive UI mode
npm run test:e2e:headed # Headed browser mode
```

## 🧪 Test Categories

### 1. Unit Tests

#### Freelancers App (`apps/freelancers/tests.py`)
- **Model Tests**: `FreelancerModelTests`
  - Freelancer ID generation
  - Full name property
  - Full address property
  - Job eligibility logic

- **API Tests**: `FreelancerAPITests`
  - List, detail, create, update operations
  - Authentication and permissions
  - Search functionality
  - Statistics endpoint

- **Related Model Tests**:
  - `FreelancerDocumentTests` - Document management
  - `FreelancerAvailabilityTests` - Availability scheduling
  - `FreelancerSkillTests` - Skill management
  - `FreelancerReviewTests` - Review system

#### Gig Management App (`apps/gig_management/tests.py`)
- **Model Tests**: `GigCategoryModelTests`, `GigJobModelTests`
  - Job ID generation
  - Address formatting
  - Cost calculations

- **API Tests**: `GigJobAPITests`
  - Job CRUD operations
  - Search and filtering
  - Access control

- **Workflow Tests**:
  - `GigApplicationTests` - Application process
  - `JobMilestoneTests` - Milestone tracking
  - `JobReviewTests` - Review system

#### Contractor Payments App (`apps/contractor_payments/tests.py`)
- **Model Tests**: `PaymentMethodModelTests`, `ContractorPaymentModelTests`
  - Payment ID generation
  - Net amount calculations
  - Payment processing logic

- **API Tests**: `ContractorPaymentAPITests`
  - Payment CRUD operations
  - Statistics and reporting
  - Payment methods

- **Advanced Features**:
  - `EscrowAccountModelTests` - Escrow management
  - `PaymentScheduleTests` - Scheduled payments
  - `DisputeResolutionTests` - Dispute handling

#### Freelancer Web3 App (`apps/freelancer_web3/tests.py`)
- **Model Tests**: Various NFT and Web3 model tests
  - NFT badge creation and management
  - Smart contract deployment
  - Wallet connections
  - Web3 transactions

- **API Tests**: `FreelancerWeb3APITests`
  - NFT badge listing
  - Wallet connection
  - Web3 statistics

### 2. Integration Tests (`tests/test_freelancer_integration.py`)

#### Complete Workflow Tests
- **`test_complete_freelancer_job_lifecycle`**: Full flow from freelancer registration → job posting → application → assignment → completion → payment → review
- **`test_web3_features_integration`**: Web3 wallet connection and NFT badge workflows
- **`test_search_and_filtering_integration`**: Cross-module search and filtering

#### Performance Tests
- **Large Dataset Testing**: Freelancer list performance with 100+ records
- **Search Performance**: Multi-module search efficiency

### 3. Frontend Tests

#### Unit Tests (`tests/unit/components/`)
- **`freelancer-profile.test.tsx`**: Profile component testing
  - Display and navigation
  - Tab switching
  - Data loading states
  - Error handling

- **`freelancer-list.test.tsx`**: List component testing
  - Search and filtering
  - Card display
  - Loading states

- **`job-board.test.tsx`**: Job board component testing
  - Job display
  - Filtering options
  - Application flow

#### E2E Tests (`tests/e2e/`)
- **`freelancer.spec.ts`**: Complete user workflows
  - Freelancer browsing and filtering
  - Job board interaction
  - Profile management
  - Responsive design

- **`auth.spec.ts`**: Authentication flows
  - Login/logout
  - Protected routes
  - Web3 wallet login

## 🔧 Test Configuration

### Backend Configuration
- **Pytest Configuration** (`pytest.ini`):
  - Django test settings
  - Coverage reporting
  - Test markers for categorization

- **Fixtures** (`tests/conftest.py`):
  - User fixtures (regular, admin, freelancer, client)
  - Model fixtures (freelancer profiles, job categories, payment methods)
  - Mock Web3 providers and wallet addresses

### Frontend Configuration
- **Playwright** (`playwright.config.ts`):
  - Multi-browser testing (Chrome, Firefox, Safari)
  - Mobile viewport testing
  - Test server setup

- **Vitest** (in `vite.config.ts`):
  - Component testing setup
  - jsdom environment
  - Test utilities

## 📊 Test Metrics and Coverage

### Coverage Targets
- **Model Tests**: 95%+ coverage for all models
- **API Tests**: 90%+ coverage for all endpoints
- **Frontend Components**: 85%+ coverage for user interactions

### Performance Benchmarks
- **API Response Time**: < 200ms for list endpoints
- **Search Performance**: < 500ms for complex queries
- **Frontend Load Time**: < 2s for component rendering

## 🐛 Debugging Tests

### Common Issues and Solutions

#### Backend Tests
```bash
# Database issues
python apps/backend/manage.py migrate --run-syncdb

# Import errors
export DJANGO_SETTINGS_MODULE=backend.settings.test

# Coverage issues
pytest --cov-report=term-missing
```

#### Frontend Tests
```bash
# Clear test cache
rm -rf apps/frontend/node_modules/.cache

# Debug E2E tests
npm run test:e2e:headed -- --debug

# Update Playwright browsers
npx playwright install
```

## 📈 Continuous Integration

### GitHub Actions Integration
The test suite is designed to run in CI/CD pipelines:

```yaml
# Example CI configuration
- name: Run Backend Tests
  run: |
    cd apps/backend
    python run_tests.py

- name: Run Frontend Tests
  run: |
    cd apps/frontend
    npm run test:run
    npm run test:e2e
```

### Test Data Management
- Use factories instead of direct model creation in tests
- Clean up test data between test runs
- Use database transactions for faster test execution

## 🎯 Test Best Practices

1. **Isolation**: Each test should be independent
2. **Realistic Data**: Use realistic test data that mirrors production
3. **Error Cases**: Test both success and failure scenarios
4. **Performance**: Include performance tests for critical paths
5. **Documentation**: Keep test descriptions clear and descriptive

## 🔄 Test Maintenance

### Regular Tasks
- Update test data when models change
- Review and update E2E tests for UI changes
- Monitor test execution time and optimize slow tests
- Ensure test coverage remains above targets

### Test Review Checklist
- [ ] All new features have corresponding tests
- [ ] Error scenarios are covered
- [ ] Performance tests validate scalability
- [ ] E2E tests cover critical user journeys
- [ ] Test documentation is up to date

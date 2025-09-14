# Development Guide

## 🛠️ **Development Setup**

### **Prerequisites**
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### **Quick Start**

1. **Clone and start the system**
   ```bash
   git clone <repository-url>
   cd tidygen
   make dev
   ```

2. **Seed with demo data**
   ```bash
   make seed-demo
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000/api
   - Admin: http://localhost:8000/admin

### **Local Development**

#### **Backend Development**
```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### **Frontend Development**
```bash
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🏗️ **Project Structure**

### **Backend Structure**
```
apps/backend/
├── apps/                    # Django applications
│   ├── core/               # Core functionality
│   ├── accounts/           # User management
│   ├── organizations/      # Multi-tenancy
│   ├── finance/            # Financial management
│   ├── inventory/          # Inventory management
│   ├── hr/                 # Human resources
│   ├── projects/           # Project management
│   ├── sales/              # Sales management
│   ├── purchasing/         # Purchasing management
│   └── web3/               # Web3 integration
├── tidygen_erp/              # Django project settings
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── Dockerfile              # Docker configuration
```

### **Frontend Structure**
```
apps/frontend/
├── src/
│   ├── components/         # Reusable components
│   │   ├── ui/            # Base UI components
│   │   ├── auth/          # Authentication
│   │   ├── finance/       # Finance components
│   │   ├── inventory/     # Inventory components
│   │   ├── hr/            # HR components
│   │   ├── projects/      # Project components
│   │   ├── sales/         # Sales components
│   │   ├── purchasing/    # Purchasing components
│   │   └── web3/          # Web3 components
│   ├── pages/             # Page components
│   ├── contexts/          # React contexts
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utilities and configurations
│   ├── types/             # TypeScript definitions
│   └── test/              # Test utilities
├── public/                # Static assets
├── package.json           # Dependencies and scripts
└── Dockerfile             # Docker configuration
```

## 🔧 **Development Commands**

### **Docker Commands**
```bash
# Start development environment
make dev

# Build and start
make dev-build

# Stop environment
make dev-stop

# View logs
make dev-logs

# Clean up
make clean
```

### **Database Commands**
```bash
# Run migrations
make db-migrate

# Reset database (WARNING: destroys data)
make db-reset

# Open database shell
make db-shell

# Seed with demo data
make seed-demo
```

### **Testing Commands**
```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend
```

### **Backend Commands**
```bash
# Django shell
make shell

# Create migrations
make makemigrations

# Collect static files
make collectstatic

# Run development server
make runserver
```

## 🧪 **Testing**

### **Backend Testing**
```bash
cd apps/backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=apps --cov-report=html
```

### **Frontend Testing**
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
```

## 🔍 **Code Quality**

### **Backend Code Quality**
```bash
cd apps/backend

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### **Frontend Code Quality**
```bash
cd apps/frontend

# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

## 🌐 **Environment Configuration**

### **Backend Environment**
```bash
# Copy environment template
cp apps/backend/env.example apps/backend/.env

# Configure variables
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/tidygen_erp
REDIS_URL=redis://localhost:6379/1
```

### **Frontend Environment**
```bash
# Copy environment template
cp apps/frontend/env.example apps/frontend/.env.local

# Configure variables
VITE_API_URL=http://localhost:8000/api
VITE_WEB3_PROVIDER_URL=http://localhost:8545
```

## 📦 **Dependencies**

### **Backend Dependencies**
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL adapter (psycopg2)
- Redis (django-redis)
- Celery (task queue)
- JWT authentication (djangorestframework-simplejwt)
- Web3 integration (web3.py)

### **Frontend Dependencies**
- React 18+
- TypeScript 5+
- Vite (build tool)
- Tailwind CSS (styling)
- shadcn/ui (components)
- Zustand (state management)
- React Query (server state)
- ethers.js (Web3 integration)

## 🚀 **Deployment**

### **Development Deployment**
```bash
# Start with Docker
make dev

# Or manually
cd apps/backend && python manage.py runserver
cd apps/frontend && npm run dev
```

### **Production Deployment**
```bash
# Build and start production
make prod

# Or use production compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 **Debugging**

### **Backend Debugging**
```bash
# Django shell
python manage.py shell

# Debug toolbar (development)
pip install django-debug-toolbar

# Logging
tail -f logs/django.log
```

### **Frontend Debugging**
```bash
# React DevTools
# Install browser extension

# Console debugging
console.log('Debug info:', data)

# Network debugging
# Use browser DevTools Network tab
```

## 📝 **Best Practices**

### **Code Style**
- Follow PEP 8 for Python
- Use ESLint/Prettier for JavaScript/TypeScript
- Write comprehensive tests
- Document complex functions
- Use meaningful variable names

### **Git Workflow**
- Create feature branches
- Write descriptive commit messages
- Use pull requests for code review
- Keep commits atomic and focused

### **API Design**
- Follow RESTful conventions
- Use proper HTTP status codes
- Implement proper error handling
- Document APIs with OpenAPI/Swagger

## 🔗 **Useful Resources**

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

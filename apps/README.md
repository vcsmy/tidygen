# Apps Directory

This directory contains all application code for the TidyGen ERP platform, organized by technology stack and responsibility.

## 📁 Structure

```
apps/
├── backend/     # Django REST Framework backend
└── frontend/    # React TypeScript frontend
```

## 🚀 Quick Start

### Development
```bash
# Start all applications
npm run dev

# Start individual applications
npm run dev:backend
npm run dev:frontend
```

### Building
```bash
# Build all applications
npm run build

# Build individual applications
npm run build:backend
npm run build:frontend
```

### Testing
```bash
# Run all tests
npm run test

# Run individual tests
npm run test:backend
npm run test:frontend
```

## 📋 Applications

### Backend (`backend/`)
- **Technology**: Django REST Framework, Python 3.11+
- **Purpose**: API server, business logic, database management
- **Key Features**: Multi-tenant architecture, Web3 integration, ERP modules

### Frontend (`frontend/`)
- **Technology**: React 18, TypeScript, Vite
- **Purpose**: User interface, client-side logic, Web3 wallet integration
- **Key Features**: Modern UI, responsive design, real-time updates

## 🔧 Development Guidelines

1. **Code Organization**: Follow the established folder structure
2. **Dependencies**: Use workspace-level dependency management
3. **Testing**: Maintain high test coverage (>90% backend, >85% frontend)
4. **Documentation**: Keep README files updated for each application
5. **Standards**: Follow coding standards defined in the root directory

## 📚 Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Architecture Overview](../../docs/architecture/overview.md)
- [API Documentation](../../docs/api/backend/)

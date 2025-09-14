# Frontend Development Guide

## 🎯 **Overview**

The TidyGen ERP frontend is built with React 18, TypeScript, and modern web technologies. It provides a comprehensive user interface for all ERP modules with real-time data integration and Web3 capabilities.

## 🏗️ **Architecture**

### **Technology Stack**
- **React 18** - UI library with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Pre-built accessible components
- **Zustand** - Lightweight state management
- **React Query** - Server state management and caching
- **React Router v6** - Client-side routing
- **ethers.js** - Web3 blockchain integration
- **Axios** - HTTP client for API communication

### **Project Structure**
```
apps/frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # Base UI components (shadcn/ui)
│   │   ├── auth/            # Authentication components
│   │   ├── finance/         # Finance module components
│   │   ├── inventory/       # Inventory module components
│   │   ├── hr/              # HR module components
│   │   ├── projects/        # Project module components
│   │   ├── sales/           # Sales module components
│   │   ├── purchasing/      # Purchasing module components
│   │   ├── web3/            # Web3 integration components
│   │   ├── admin/           # Admin components
│   │   ├── layout/          # Layout components
│   │   └── shared/          # Shared components
│   ├── pages/               # Page components
│   │   ├── admin/           # Admin pages
│   │   ├── finance/         # Finance pages
│   │   ├── inventory/       # Inventory pages
│   │   ├── hr/              # HR pages
│   │   ├── projects/        # Project pages
│   │   ├── sales/           # Sales pages
│   │   ├── purchasing/      # Purchasing pages
│   │   ├── web3/            # Web3 pages
│   │   └── reports/         # Reports pages
│   ├── contexts/            # React contexts
│   │   ├── AuthContext.tsx  # Authentication context
│   │   └── Web3Context.tsx  # Web3 context
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities and configurations
│   │   ├── api.ts           # API service layer
│   │   ├── config.ts        # Environment configuration
│   │   ├── error-handler.ts # Error handling utilities
│   │   └── utils.ts         # General utilities
│   ├── types/               # TypeScript type definitions
│   ├── test/                # Test utilities and mocks
│   └── assets/              # Static assets
├── public/                  # Public static files
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── Dockerfile               # Docker configuration
```

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+
- npm or yarn
- Docker (optional)

### **Installation**
```bash
cd apps/frontend
npm install
```

### **Development Server**
```bash
npm run dev
```
Access the application at http://localhost:3000

### **Build for Production**
```bash
npm run build
```

### **Preview Production Build**
```bash
npm run preview
```

## 🎨 **UI Components**

### **shadcn/ui Components**
The project uses shadcn/ui for consistent, accessible components:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
```

### **Custom Components**
Create reusable components following the established patterns:

```tsx
// components/shared/DataTable.tsx
interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T>[]
  loading?: boolean
  onAdd?: () => void
  addButtonText?: string
  searchPlaceholder?: string
  searchValue?: string
  onSearchChange?: (value: string) => void
}

export function DataTable<T>({ data, columns, ...props }: DataTableProps<T>) {
  // Implementation
}
```

## 🔐 **Authentication**

### **AuthContext**
The authentication context manages user state and API integration:

```tsx
import { useAuth } from "@/contexts/AuthContext"

function MyComponent() {
  const { user, login, logout, isLoading } = useAuth()
  
  if (isLoading) return <div>Loading...</div>
  
  return (
    <div>
      {user ? (
        <div>Welcome, {user.first_name}!</div>
      ) : (
        <div>Please log in</div>
      )}
    </div>
  )
}
```

### **Protected Routes**
Use the ProtectedRoute component for authentication:

```tsx
import { ProtectedRoute } from "@/components/ProtectedRoute"

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
    </Routes>
  )
}
```

### **Role-Based Access**
Use RoleBasedRoute for role-based access control:

```tsx
import { RoleBasedRoute } from "@/components/RoleBasedRoute"

function AdminPage() {
  return (
    <RoleBasedRoute allowedRoles={['admin']}>
      <AdminContent />
    </RoleBasedRoute>
  )
}
```

## 🌐 **API Integration**

### **API Service Layer**
The API service provides a centralized way to interact with the backend:

```tsx
import { ApiService } from "@/lib/api"

// GET request
const users = await ApiService.get('/users/')

// POST request
const newUser = await ApiService.post('/users/', {
  username: 'newuser',
  email: 'user@example.com'
})

// PUT request
const updatedUser = await ApiService.put(`/users/${id}/`, userData)

// DELETE request
await ApiService.delete(`/users/${id}/`)
```

### **Error Handling**
The error handler provides consistent error management:

```tsx
import { ErrorHandler } from "@/lib/error-handler"

try {
  const data = await ApiService.get('/users/')
} catch (error) {
  const apiError = ErrorHandler.handle(error)
  toast.error(apiError.message)
}
```

## 🎨 **Styling**

### **Tailwind CSS**
Use Tailwind utility classes for styling:

```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 className="text-xl font-semibold text-gray-900">Title</h2>
  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
    Action
  </Button>
</div>
```

### **Custom CSS**
Add custom styles in the global CSS file:

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .custom-card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}
```

## 🧪 **Testing**

### **Unit Testing with Vitest**
```tsx
// components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '../ui/button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByText('Click me')).toBeInTheDocument()
})
```

### **Integration Testing**
```tsx
// test/integration/auth.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Login } from '@/pages/Login'

test('user can login successfully', async () => {
  render(<Login />)
  
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
```

### **E2E Testing with Cypress**
```typescript
// cypress/e2e/auth.cy.ts
describe('Authentication', () => {
  it('should login successfully', () => {
    cy.visit('/login')
    cy.get('[data-testid="username"]').type('admin')
    cy.get('[data-testid="password"]').type('admin123')
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/dashboard')
  })
})
```

## ⛓️ **Web3 Integration**

### **Web3Context**
The Web3 context manages blockchain interactions:

```tsx
import { useWeb3 } from "@/contexts/Web3Context"

function WalletComponent() {
  const { 
    account, 
    connectWallet, 
    disconnectWallet, 
    switchNetwork,
    balance 
  } = useWeb3()
  
  return (
    <div>
      {account ? (
        <div>
          <p>Connected: {account}</p>
          <p>Balance: {balance} ETH</p>
          <Button onClick={disconnectWallet}>Disconnect</Button>
        </div>
      ) : (
        <Button onClick={connectWallet}>Connect Wallet</Button>
      )}
    </div>
  )
}
```

### **Smart Contract Integration**
```tsx
import { ethers } from 'ethers'

async function interactWithContract() {
  const provider = new ethers.providers.Web3Provider(window.ethereum)
  const signer = provider.getSigner()
  const contract = new ethers.Contract(contractAddress, abi, signer)
  
  const result = await contract.someMethod()
  return result
}
```

## 📱 **Responsive Design**

### **Mobile-First Approach**
Design components with mobile-first principles:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card>Content 1</Card>
  <Card>Content 2</Card>
  <Card>Content 3</Card>
</div>
```

### **Breakpoints**
Use Tailwind's responsive breakpoints:

- `sm:` - 640px and up
- `md:` - 768px and up
- `lg:` - 1024px and up
- `xl:` - 1280px and up
- `2xl:` - 1536px and up

## 🚀 **Performance Optimization**

### **Code Splitting**
Use React.lazy for code splitting:

```tsx
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('@/pages/Dashboard'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Dashboard />
    </Suspense>
  )
}
```

### **Memoization**
Use React.memo and useMemo for performance:

```tsx
import { memo, useMemo } from 'react'

const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return data.map(item => processItem(item))
  }, [data])
  
  return <div>{processedData}</div>
})
```

## 🔧 **Development Tools**

### **ESLint Configuration**
```json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

### **Prettier Configuration**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

## 📦 **Build and Deployment**

### **Environment Variables**
```bash
# .env.local
VITE_API_URL=http://localhost:8000/api
VITE_WEB3_PROVIDER_URL=http://localhost:8545
VITE_APP_NAME=TidyGen ERP
```

### **Docker Build**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🐛 **Debugging**

### **React DevTools**
Install the React Developer Tools browser extension for debugging.

### **Console Debugging**
```tsx
import { useEffect } from 'react'

function MyComponent({ data }) {
  useEffect(() => {
    console.log('Data updated:', data)
  }, [data])
  
  return <div>Component content</div>
}
```

### **Network Debugging**
Use browser DevTools Network tab to monitor API requests and responses.

## 📚 **Best Practices**

### **Component Design**
- Keep components small and focused
- Use TypeScript for type safety
- Follow the single responsibility principle
- Use proper prop validation

### **State Management**
- Use local state for component-specific data
- Use context for shared state
- Use React Query for server state
- Avoid prop drilling

### **Performance**
- Use React.memo for expensive components
- Implement proper loading states
- Optimize bundle size with code splitting
- Use proper dependency arrays in hooks

### **Accessibility**
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers

import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock environment variables for tests
Object.defineProperty(window, 'ENV', {
  value: {
    VITE_API_BASE_URL: 'http://localhost:8000/api/v1',
    VITE_WEB3_PROVIDER_URL: 'http://localhost:8545',
  },
});

// Mock fetch for API calls
global.fetch = vi.fn();

// Mock Web3 provider
global.ethereum = {
  isMetaMask: true,
  request: vi.fn(),
  on: vi.fn(),
  removeListener: vi.fn(),
};

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

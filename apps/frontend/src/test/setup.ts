/**
 * Vitest setup file
 * Runs before all tests
 */

import '@testing-library/jest-dom';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';

// Establish API mocking before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

// Reset any request handlers that are declared as a part of tests
afterEach(() => {
  server.resetHandlers();
  cleanup();
});

// Clean up after all tests are done
afterAll(() => server.close());

// Mock environment variables
process.env.VITE_API_BASE_URL = 'http://localhost:8002/api/v1';
process.env.VITE_WS_ENDPOINT = 'ws://localhost:9944';
process.env.VITE_APP_NAME = 'TidyGen ERP Test';


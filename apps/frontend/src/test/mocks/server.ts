/**
 * MSW Server for API mocking
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const handlers = [
  // Mock Django API endpoints
  http.post('http://localhost:8002/api/v1/auth/login', () => {
    return HttpResponse.json({
      access: 'mock-jwt-token',
      refresh: 'mock-refresh-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
      },
    });
  }),

  http.get('http://localhost:8002/api/v1/finance/invoices', () => {
    return HttpResponse.json({
      count: 1,
      results: [
        {
          id: 1,
          invoice_number: 'INV-2025-001',
          amount: 1000,
          blockchain_anchored: true,
          blockchain_tx_hash: '0x1234567890abcdef',
        },
      ],
    });
  }),

  http.post('http://localhost:8002/api/v1/blockchain/invoices', () => {
    return HttpResponse.json({
      success: true,
      tx_hash: '0x1234567890abcdef1234567890abcdef',
      blockchain_invoice_id: 0,
    });
  }),

  http.get('http://localhost:8002/api/v1/blockchain/did/:account', () => {
    return HttpResponse.json({
      controller: '5GrwvaEF...',
      public_key: '0x04a1b2c3...',
      status: 'active',
      did_identifier: 'did:substrate:tidygen:a1b2c3d4',
    });
  }),

  http.post('http://localhost:8002/api/v1/dao/proposals', () => {
    return HttpResponse.json({
      id: 1,
      proposal_id: 0,
      blockchain_tx_hash: '0xabcdef1234567890',
      status: 'active',
    });
  }),
];

export const server = setupServer(...handlers);


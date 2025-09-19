/**
 * Wallet Service
 * 
 * High-level service for wallet management and authentication
 * coordinating between different wallet types and API calls.
 */

import { 
  WalletInfo, 
  WalletConnectionRequest, 
  WalletAuthenticationRequest,
  WalletAuthenticationResponse,
  WalletAuthenticationVerify,
  WalletAuthenticationResult,
  TransactionSignatureRequest,
  TransactionSignatureResponse,
  WalletStatus,
  SupportedWallet,
  NetworkInfo,
  WalletError
} from '../../types/wallet';

class WalletService {
  private apiBaseUrl: string;
  private accessToken: string | null = null;

  constructor(apiBaseUrl: string = '/api/v1') {
    this.apiBaseUrl = apiBaseUrl;
    this.loadAccessToken();
  }

  /**
   * Load access token from localStorage
   */
  private loadAccessToken(): void {
    this.accessToken = localStorage.getItem('access_token');
  }

  /**
   * Set access token for API authentication
   */
  setAccessToken(token: string): void {
    this.accessToken = token;
    localStorage.setItem('access_token', token);
  }

  /**
   * Clear access token
   */
  clearAccessToken(): void {
    this.accessToken = null;
    localStorage.removeItem('access_token');
  }

  /**
   * Get authorization headers
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    return headers;
  }

  /**
   * Make API request with error handling
   */
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.apiBaseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new WalletError(
        response.status.toString(),
        errorData.error || errorData.message || 'Request failed',
        errorData
      );
    }

    return response.json();
  }

  /**
   * Get supported wallet types
   */
  async getSupportedWallets(): Promise<SupportedWallet[]> {
    return this.makeRequest<SupportedWallet[]>('/wallet/supported/');
  }

  /**
   * Connect a wallet to the system
   */
  async connectWallet(connectionRequest: WalletConnectionRequest): Promise<WalletInfo> {
    return this.makeRequest<WalletInfo>('/wallet/connect/', {
      method: 'POST',
      body: JSON.stringify(connectionRequest),
    });
  }

  /**
   * Request wallet authentication signature
   */
  async requestAuthentication(
    authRequest: WalletAuthenticationRequest
  ): Promise<WalletAuthenticationResponse> {
    return this.makeRequest<WalletAuthenticationResponse>('/wallet/auth/', {
      method: 'POST',
      body: JSON.stringify(authRequest),
    });
  }

  /**
   * Verify wallet authentication signature
   */
  async verifyAuthentication(
    verifyRequest: WalletAuthenticationVerify
  ): Promise<WalletAuthenticationResult> {
    return this.makeRequest<WalletAuthenticationResult>('/wallet/auth/', {
      method: 'PUT',
      body: JSON.stringify(verifyRequest),
    });
  }

  /**
   * Get user's wallets
   */
  async getUserWallets(): Promise<WalletInfo[]> {
    return this.makeRequest<WalletInfo[]>('/wallet/wallets/');
  }

  /**
   * Set primary wallet
   */
  async setPrimaryWallet(walletId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>(
      `/wallet/wallets/${walletId}/set_primary/`,
      {
        method: 'POST',
      }
    );
  }

  /**
   * Disconnect wallet
   */
  async disconnectWallet(walletId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>(
      `/wallet/wallets/${walletId}/disconnect/`,
      {
        method: 'POST',
      }
    );
  }

  /**
   * Get wallet status
   */
  async getWalletStatus(walletId: string): Promise<WalletStatus> {
    return this.makeRequest<WalletStatus>(`/wallet/wallets/${walletId}/status/`);
  }

  /**
   * Get wallet account information
   */
  async getWalletAccountInfo(walletId: string): Promise<any> {
    return this.makeRequest<any>(`/wallet/account/${walletId}/`);
  }

  /**
   * Request transaction signature
   */
  async requestTransactionSignature(
    signatureRequest: TransactionSignatureRequest
  ): Promise<TransactionSignatureResponse> {
    return this.makeRequest<TransactionSignatureResponse>('/wallet/sign/', {
      method: 'POST',
      body: JSON.stringify(signatureRequest),
    });
  }

  /**
   * Verify transaction signature
   */
  async verifyTransactionSignature(
    signatureId: string,
    signature: string
  ): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/wallet/sign/', {
      method: 'PUT',
      body: JSON.stringify({ signatureId, signature }),
    });
  }

  /**
   * Get network information for wallet type
   */
  async getNetworkInfo(walletType: string): Promise<{
    networkInfo: NetworkInfo;
    supportedNetworks: NetworkInfo[];
  }> {
    return this.makeRequest<{
      networkInfo: NetworkInfo;
      supportedNetworks: NetworkInfo[];
    }>(`/wallet/network/${walletType}/`);
  }

  /**
   * Get wallet signatures
   */
  async getWalletSignatures(): Promise<any[]> {
    return this.makeRequest<any[]>('/wallet/signatures/');
  }

  /**
   * Get wallet permissions
   */
  async getWalletPermissions(): Promise<any[]> {
    return this.makeRequest<any[]>('/wallet/permissions/');
  }

  /**
   * Get wallet sessions
   */
  async getWalletSessions(): Promise<any[]> {
    return this.makeRequest<any[]>('/wallet/sessions/');
  }

  /**
   * Extend wallet session
   */
  async extendWalletSession(sessionId: string, hours: number = 24): Promise<{ message: string }> {
    return this.makeRequest<{ message: string }>(
      `/wallet/sessions/${sessionId}/extend/`,
      {
        method: 'POST',
        body: JSON.stringify({ hours }),
      }
    );
  }

  /**
   * Deactivate wallet session
   */
  async deactivateWalletSession(sessionId: string): Promise<{ message: string }> {
    return this.makeRequest<{ message: string }>(
      `/wallet/sessions/${sessionId}/deactivate/`,
      {
        method: 'POST',
      }
    );
  }

  /**
   * Create wallet permission
   */
  async createWalletPermission(permission: {
    wallet: string;
    permissionType: string;
    resourceType: string;
    resourceId?: string;
    granted: boolean;
    reason?: string;
    expiresAt?: string;
  }): Promise<any> {
    return this.makeRequest<any>('/wallet/permissions/', {
      method: 'POST',
      body: JSON.stringify(permission),
    });
  }

  /**
   * Update wallet permission
   */
  async updateWalletPermission(
    permissionId: string,
    updates: Partial<{
      granted: boolean;
      reason: string;
      expiresAt: string;
    }>
  ): Promise<any> {
    return this.makeRequest<any>(`/wallet/permissions/${permissionId}/`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete wallet permission
   */
  async deleteWalletPermission(permissionId: string): Promise<void> {
    return this.makeRequest<void>(`/wallet/permissions/${permissionId}/`, {
      method: 'DELETE',
    });
  }
}

// Custom error class for wallet operations
class WalletError extends Error {
  public code: string;
  public details?: any;

  constructor(code: string, message: string, details?: any) {
    super(message);
    this.name = 'WalletError';
    this.code = code;
    this.details = details;
  }
}

// Create singleton instance
export const walletService = new WalletService();
export { WalletError };
export default WalletService;

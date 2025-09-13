/**
 * Authentication context and provider
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi, apiClient } from '@/lib/api';
import type { ApiError, User } from '@/lib/types';

// User interface is imported from @/lib/types

export interface AuthTokens {
  access: string;
  refresh: string;
}

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!tokens;

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (accessToken && refreshToken) {
          setTokens({ access: accessToken, refresh: refreshToken });
          apiClient.setToken(accessToken);
          
          // Try to get user profile
          try {
            const response = await authApi.getProfile();
            setUser(response.data);
          } catch (error) {
            // If profile fetch fails, try to refresh token
            if (error instanceof ApiError && error.status === 401) {
              await refreshTokenFromStorage();
            } else {
              throw error;
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // Clear invalid tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        apiClient.setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const refreshTokenFromStorage = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authApi.refreshToken(refreshToken);
      const newTokens = {
        access: response.data.access,
        refresh: response.data.refresh || refreshToken,
      };
      
      setTokens(newTokens);
      localStorage.setItem('access_token', newTokens.access);
      localStorage.setItem('refresh_token', newTokens.refresh);
      apiClient.setToken(newTokens.access);
      
      // Get user profile with new token
      const profileResponse = await authApi.getProfile();
      setUser(profileResponse.data);
    } catch (error) {
      // Refresh failed, clear all tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      apiClient.setToken(null);
      setTokens(null);
      setUser(null);
      throw error;
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await authApi.login({ email, password });
      
      const newTokens = {
        access: response.data.access,
        refresh: response.data.refresh,
      };
      
      setTokens(newTokens);
      localStorage.setItem('access_token', newTokens.access);
      localStorage.setItem('refresh_token', newTokens.refresh);
      apiClient.setToken(newTokens.access);
      
      // Get user profile
      const profileResponse = await authApi.getProfile();
      setUser(profileResponse.data);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => {
    try {
      setIsLoading(true);
      await authApi.register(userData);
      // After successful registration, automatically log in
      await login(userData.email, userData.password);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (tokens) {
        await authApi.logout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear all auth state regardless of API call success
      setUser(null);
      setTokens(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      apiClient.setToken(null);
    }
  };

  const refreshToken = async () => {
    if (!tokens?.refresh) {
      throw new Error('No refresh token available');
    }
    await refreshTokenFromStorage();
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await authApi.updateProfile(data);
      setUser(response.data);
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    tokens,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

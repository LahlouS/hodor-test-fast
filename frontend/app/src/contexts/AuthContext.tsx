'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import {
  loginUser as apiLogin,
  registerUser as apiRegister,
  refreshToken as apiRefreshToken,
  logoutUser as apiLogout,
} from '../services/authService';

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<string>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuthStatus = () => {
    const stored = localStorage.getItem('access_token');
    if (stored) {
      setToken(stored);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string) => {
    const data = await apiLogin(username, password);
    localStorage.setItem('access_token', data.access_token);
    setToken(data.access_token);
    setIsAuthenticated(true);
  };

  const register = async (username: string, email: string, password: string) => {
    await apiRegister(username, email, password);
    // caller must invoke login() manually after
  };

  const logout = async () => {
    try {
      await apiLogout();
    } finally {
      localStorage.removeItem('access_token');
      setToken(null);
      setIsAuthenticated(false);
    }
  };

  const refresh = async (): Promise<string> => {
    try {
      const data = await apiRefreshToken();
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
      setIsAuthenticated(true);
      return data.access_token;
    } catch (err) {
      await logout();
      throw err;
    }
  };

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, isLoading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

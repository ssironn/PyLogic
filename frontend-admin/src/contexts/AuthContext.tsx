'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import authService, { AdminData, AdminSigninRequest } from '@/services/auth';

interface AuthResult {
  success: boolean;
  message?: string;
}

interface AuthContextData {
  admin: AdminData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (data: AdminSigninRequest) => Promise<AuthResult>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [admin, setAdmin] = useState<AdminData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedAdmin = authService.getAdmin();
    if (storedAdmin && authService.isAuthenticated()) {
      setAdmin(storedAdmin);
    }
    setIsLoading(false);
  }, []);

  const signin = useCallback(async (data: AdminSigninRequest): Promise<AuthResult> => {
    try {
      const response = await authService.signin(data);

      if (response.status === 'success' && response.data) {
        setAdmin(response.data.admin);
        return { success: true };
      }

      return {
        success: false,
        message: response.message || 'Erro ao fazer login',
      };
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      const message =
        err.response?.data?.message ||
        err.message ||
        'Erro ao conectar com o servidor';
      return { success: false, message };
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setAdmin(null);
    router.push('/login');
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        admin,
        isAuthenticated: !!admin,
        isLoading,
        signin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;

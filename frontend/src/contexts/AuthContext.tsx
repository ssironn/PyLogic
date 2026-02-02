'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import authService, { StudentData, SigninRequest, SignupRequest } from '@/services/auth';

interface AuthResult {
  success: boolean;
  message?: string;
  fieldErrors?: Record<string, string>;
}

interface AuthContextData {
  user: StudentData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (data: SigninRequest) => Promise<AuthResult>;
  signup: (data: SignupRequest) => Promise<AuthResult>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<StudentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = authService.getUser();
    if (storedUser && authService.isAuthenticated()) {
      setUser(storedUser);
    }
    setIsLoading(false);
  }, []);

  const signin = useCallback(async (data: SigninRequest): Promise<AuthResult> => {
    try {
      const response = await authService.signin(data);

      if (response.status === 'success' && response.data) {
        setUser(response.data.student);
        return { success: true };
      }

      return {
        success: false,
        message: response.message || 'Erro ao fazer login',
      };
    } catch (error: any) {
      const message =
        error.response?.data?.message ||
        error.message ||
        'Erro ao conectar com o servidor';
      return { success: false, message };
    }
  }, []);

  const signup = useCallback(async (data: SignupRequest): Promise<AuthResult> => {
    try {
      const response = await authService.signup(data);

      if (response.status === 'success' && response.data) {
        setUser(response.data.student);
        return { success: true };
      }

      const fieldErrors: Record<string, string> = {};
      if (response.errors) {
        response.errors.forEach((err) => {
          if (err.field) {
            fieldErrors[err.field] = err.message;
          }
        });
      }

      return {
        success: false,
        message: response.message || 'Erro ao fazer cadastro',
        fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
      };
    } catch (error: any) {
      const message =
        error.response?.data?.message ||
        error.message ||
        'Erro ao conectar com o servidor';
      return { success: false, message };
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    router.push('/login');
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        signin,
        signup,
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

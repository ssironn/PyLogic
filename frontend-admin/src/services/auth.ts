import api from './api';

export interface AdminSigninRequest {
  email: string;
  password: string;
}

export interface AdminData {
  id: string;
  name: string;
  email: string;
}

export interface TokensData {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AdminSigninResponseData {
  admin: AdminData;
  tokens: TokensData;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
  errors?: Array<{
    code: string;
    message: string;
    field?: string;
  }>;
}

const TOKEN_KEY = 'pylogic_admin_access_token';
const REFRESH_TOKEN_KEY = 'pylogic_admin_refresh_token';
const USER_KEY = 'pylogic_admin_user';

export const authService = {
  async signin(data: AdminSigninRequest): Promise<ApiResponse<AdminSigninResponseData>> {
    const response = await api.post<ApiResponse<AdminSigninResponseData>>(
      '/api/admin/auth/signin',
      data
    );

    if (response.data.status === 'success' && response.data.data) {
      const { tokens, admin } = response.data.data;
      this.setTokens(tokens);
      this.setAdmin(admin);
    }

    return response.data;
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  setTokens(tokens: TokensData): void {
    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  },

  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setAdmin(admin: AdminData): void {
    localStorage.setItem(USER_KEY, JSON.stringify(admin));
  },

  getAdmin(): AdminData | null {
    if (typeof window === 'undefined') return null;
    const adminStr = localStorage.getItem(USER_KEY);
    if (!adminStr) return null;
    try {
      return JSON.parse(adminStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  },
};

export default authService;

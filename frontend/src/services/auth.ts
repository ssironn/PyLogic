import api from './api';

export interface SigninRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
  registration_number?: string;
  access_code: string;
}

export interface StudentData {
  id: string;
  name: string;
  email: string;
  registration_number: string;
}

export interface TokensData {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SigninResponseData {
  student: StudentData;
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

const TOKEN_KEY = 'pylogic_access_token';
const REFRESH_TOKEN_KEY = 'pylogic_refresh_token';
const USER_KEY = 'pylogic_user';

export const authService = {
  async signin(data: SigninRequest): Promise<ApiResponse<SigninResponseData>> {
    const response = await api.post<ApiResponse<SigninResponseData>>(
      '/api/auth/signin',
      data
    );

    if (response.data.status === 'success' && response.data.data) {
      const { tokens, student } = response.data.data;
      this.setTokens(tokens);
      this.setUser(student);
    }

    return response.data;
  },

  async signup(data: SignupRequest): Promise<ApiResponse<SigninResponseData>> {
    const response = await api.post<ApiResponse<SigninResponseData>>(
      '/api/auth/signup',
      data
    );

    if (response.data.status === 'success' && response.data.data) {
      const { tokens, student } = response.data.data;
      this.setTokens(tokens);
      this.setUser(student);
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

  setUser(user: StudentData): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  getUser(): StudentData | null {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  },
};

// Add auth interceptor to api
api.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for handling 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default authService;

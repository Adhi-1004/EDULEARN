/**
 * Authentication service for handling user authentication
 */
import api from '../utils/api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  role?: string;
}

export interface GoogleAuthData {
  token: string;
  user: {
    id: string;
    name: string;
    email: string;
    picture: string;
  };
}

export interface FaceAuthData {
  faceDescriptor: number[];
  user: {
    name: string;
    email: string;
  };
}

export interface AuthResponse {
  success: boolean;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  token: string;
  message?: string;
}

class AuthService {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await api.post('/auth/register', userData);
    return response.data;
  }

  /**
   * Login with Google OAuth
   */
  async googleLogin(authData: GoogleAuthData): Promise<AuthResponse> {
    const response = await api.post('/auth/google-login', authData);
    return response.data;
  }

  /**
   * Login with face recognition
   */
  async faceLogin(faceData: FaceAuthData): Promise<AuthResponse> {
    const response = await api.post('/auth/face-login', faceData);
    return response.data;
  }

  /**
   * Register with face recognition
   */
  async faceRegister(faceData: FaceAuthData): Promise<AuthResponse> {
    const response = await api.post('/auth/face-register', faceData);
    return response.data;
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<AuthResponse> {
    const response = await api.get('/auth/me');
    return response.data;
  }

  /**
   * Logout user
   */
  async logout(): Promise<{ success: boolean }> {
    const response = await api.post('/auth/logout');
    return response.data;
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<{ token: string }> {
    const response = await api.post('/auth/refresh');
    return response.data;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  /**
   * Get stored access token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Store access token
   */
  setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  /**
   * Remove access token
   */
  removeToken(): void {
    localStorage.removeItem('access_token');
  }

  /**
   * Get stored user data
   */
  getUser(): any | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Store user data
   */
  setUser(user: any): void {
    localStorage.setItem('user', JSON.stringify(user));
  }

  /**
   * Remove user data
   */
  removeUser(): void {
    localStorage.removeItem('user');
  }
}

export default new AuthService();

/**
 * Authentication service for handling user authentication
 */
import api from "../utils/api"

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
  role?: string
}

export interface AuthResponse {
  success: boolean
  user: {
    id: string
    name: string
    email: string
    role: string
  }
  access_token: string // align with backend key
  message?: string
}

class AuthService {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post("/auth/login", credentials)
    return response.data
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await api.post("/auth/register", userData)
    return response.data
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<any> {
    const response = await api.get("/auth/status") // align with backend endpoint
    return response.data
  }

  /**
   * Logout user
   */
  async logout(): Promise<{ success: boolean }> {
    const response = await api.post("/auth/logout")
    return response.data
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem("access_token")
    return !!token
  }

  /**
   * Get stored access token
   */
  getToken(): string | null {
    return localStorage.getItem("access_token")
  }

  /**
   * Store access token
   */
  setToken(token: string): void {
    localStorage.setItem("access_token", token)
  }

  /**
   * Remove access token
   */
  removeToken(): void {
    localStorage.removeItem("access_token")
  }

  /**
   * Get stored user data
   */
  getUser(): any | null {
    const userStr = localStorage.getItem("user")
    return userStr ? JSON.parse(userStr) : null
  }

  /**
   * Store user data
   */
  setUser(user: any): void {
    localStorage.setItem("user", JSON.stringify(user))
  }

  /**
   * Remove user data
   */
  removeUser(): void {
    localStorage.removeItem("user")
  }
}

export default new AuthService()

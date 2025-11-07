import apiClient from '../api-client'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  ApiResponse,
} from '@/types/auth'

export const authApi = {
  // Register new user
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<ApiResponse<User>>('/api/auth/register', data)
    return response.data.data
  },

  // Login user
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<ApiResponse<AuthResponse>>('/api/auth/login', data)
    const authData = response.data.data

    // Store tokens in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', authData.access_token)
      localStorage.setItem('refresh_token', authData.refresh_token)
    }

    return authData
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>('/api/auth/me')
    const user = response.data.data

    // Store user in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user))
    }

    return user
  },

  // Update user profile
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.put<ApiResponse<User>>('/api/auth/me', data)
    const user = response.data.data

    // Update user in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user))
    }

    return user
  },

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post<ApiResponse<null>>('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  // Logout
  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false
    return !!localStorage.getItem('access_token')
  },

  // Get stored user
  getStoredUser(): User | null {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },
}

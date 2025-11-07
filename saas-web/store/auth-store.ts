import { create } from 'zustand'
import { authApi } from '@/lib/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  clearError: () => void
  initialize: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Initialize auth state from localStorage
  initialize: () => {
    const isAuth = authApi.isAuthenticated()
    const user = authApi.getStoredUser()

    set({
      isAuthenticated: isAuth,
      user: user,
    })

    // Fetch fresh user data if authenticated
    if (isAuth) {
      authApi.getCurrentUser().then((freshUser) => {
        set({ user: freshUser })
      }).catch(() => {
        // Token might be invalid, logout
        authApi.logout()
        set({ user: null, isAuthenticated: false })
      })
    }
  },

  login: async (data: LoginRequest) => {
    set({ isLoading: true, error: null })

    try {
      await authApi.login(data)
      const user = await authApi.getCurrentUser()

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Login failed'
      set({
        error: errorMessage,
        isLoading: false,
        isAuthenticated: false,
      })
      throw error
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null })

    try {
      await authApi.register(data)

      // Auto-login after registration
      await authApi.login({
        email: data.email,
        password: data.password,
      })

      const user = await authApi.getCurrentUser()

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Registration failed'
      set({
        error: errorMessage,
        isLoading: false,
        isAuthenticated: false,
      })
      throw error
    }
  },

  logout: () => {
    authApi.logout()
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    })
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true, error: null })

    try {
      const user = await authApi.getCurrentUser()
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Failed to fetch user'
      set({
        error: errorMessage,
        isLoading: false,
        user: null,
        isAuthenticated: false,
      })
      authApi.logout()
    }
  },

  updateProfile: async (data: Partial<User>) => {
    set({ isLoading: true, error: null })

    try {
      const user = await authApi.updateProfile(data)
      set({
        user,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Update failed'
      set({
        error: errorMessage,
        isLoading: false,
      })
      throw error
    }
  },

  clearError: () => set({ error: null }),
}))

import { defineStore } from 'pinia'
import { authAPI } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    isAuthenticated: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isSuperuser: (state) => state.user?.is_superuser || false,
  },

  actions: {
    async login(credentials) {
      try {
        const response = await authAPI.login(credentials)
        const { access_token } = response.data
        
        this.token = access_token
        localStorage.setItem('access_token', access_token)
        
        await this.fetchUser()
        
        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Login failed' 
        }
      }
    },

    async fetchUser() {
      try {
        const response = await authAPI.getMe()
        this.user = response.data
        this.isAuthenticated = true
        console.log('User data:', this.user)
      } catch (error) {
        console.error('Fetch user error:', error)
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('access_token')
    },
  },
})

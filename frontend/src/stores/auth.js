/**
 * Pinia store for authentication state management.
 * 
 * Handles user login, logout, token management, and
 * authentication state across the application.
 */

import { defineStore } from 'pinia'
import { authAPI } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    isAuthenticated: false,
  }),

  getters: {
    /**
     * Check if user is currently logged in.
     * @returns {boolean} Login status
     */
    isLoggedIn: (state) => !!state.token,

    /**
     * Check if user has superuser privileges.
     * @returns {boolean} Superuser status
     */
    isSuperuser: (state) => state.user?.is_superuser || false,
  },

  actions: {
    /**
     * Authenticate user with credentials.
     * @param {Object} credentials - Login credentials
     * @returns {Object} Success status and error message if applicable
     */
    async login(credentials) {
      try {
        const response = await authAPI.login(credentials)
        const { access_token } = response.data
        
        // Store token and fetch user data
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

    /**
     * Fetch current user data from API.
     * @throws {Error} If token is invalid or user fetch fails
     */
    async fetchUser() {
      if (!this.token) {
        console.log('No token, cannot fetch user')
        return
      }
      
      try {
        const response = await authAPI.getMe()
        this.user = response.data
        this.isAuthenticated = true
        console.log('User fetched:', this.user)
      } catch (error) {
        console.error('Fetch user error:', error)
        if (error.response?.status === 401) {
          // Token is invalid, clear authentication
          this.logout()
        }
        throw error
      }
    },

    /**
     * Clear authentication state and logout user.
     */
    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('access_token')
    },
  },
})

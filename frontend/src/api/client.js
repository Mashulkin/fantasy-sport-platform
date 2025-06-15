/**
 * HTTP client configuration and API service definitions.
 * 
 * Configures Axios with authentication interceptors and defines
 * API service methods for different application modules.
 */

import axios from 'axios'

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: '/api/v1',  // Use relative path for proxy routing
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add authentication token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle authentication errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

// Authentication API service
export const authAPI = {
  /**
   * User login with OAuth2 compatible format.
   * @param {Object} credentials - User credentials
   * @param {string} credentials.username - Username or email
   * @param {string} credentials.password - User password
   * @returns {Promise} API response with access token
   */
  login: (credentials) => {
    // OAuth2 requires application/x-www-form-urlencoded format
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    
    return apiClient.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  /**
   * User registration.
   * @param {Object} userData - New user data
   * @returns {Promise} API response with created user
   */
  register: (userData) => apiClient.post('/auth/register', userData),

  /**
   * Get current user profile.
   * @returns {Promise} API response with user data
   */
  getMe: () => apiClient.get('/auth/me'),
}

// Players API service
export const playersAPI = {
  /**
   * Get paginated list of players with optional filters.
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with players list
   */
  getAll: (params) => apiClient.get('/players', { params }),

  /**
   * Get single player by ID.
   * @param {number} id - Player ID
   * @returns {Promise} API response with player data
   */
  getById: (id) => apiClient.get(`/players/${id}`),

  /**
   * Get player statistics.
   * @param {number} id - Player ID
   * @param {Object} params - Query parameters
   * @returns {Promise} API response with player stats
   */
  getStats: (id, params) => apiClient.get(`/players/${id}/stats`, { params }),
}

// Teams API service
export const teamsAPI = {
  /**
   * Get all teams.
   * @returns {Promise} API response with teams list
   */
  getAll: () => apiClient.get('/teams'),

  /**
   * Get single team by ID.
   * @param {number} id - Team ID
   * @returns {Promise} API response with team data
   */
  getById: (id) => apiClient.get(`/teams/${id}`),
}

// Tournaments API service
export const tournamentsAPI = {
  /**
   * Get all tournaments.
   * @returns {Promise} API response with tournaments list
   */
  getAll: () => apiClient.get('/tournaments'),

  /**
   * Get single tournament by ID.
   * @param {number} id - Tournament ID
   * @returns {Promise} API response with tournament data
   */
  getById: (id) => apiClient.get(`/tournaments/${id}`),

  /**
   * Create new tournament.
   * @param {Object} data - Tournament data
   * @returns {Promise} API response with created tournament
   */
  create: (data) => apiClient.post('/tournaments', data),
}

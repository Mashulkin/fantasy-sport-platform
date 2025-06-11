import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',  // Используем относительный путь
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
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

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

// Auth API
export const authAPI = {
  login: (credentials) => {
    // OAuth2 требует application/x-www-form-urlencoded
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    
    return apiClient.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },
  register: (userData) => apiClient.post('/auth/register', userData),
  getMe: () => apiClient.get('/auth/me'),
}

// Players API
export const playersAPI = {
  getAll: (params) => apiClient.get('/players', { params }),
  getById: (id) => apiClient.get(`/players/${id}`),
  getStats: (id, params) => apiClient.get(`/players/${id}/stats`, { params }),
}

// Teams API  
export const teamsAPI = {
  getAll: () => apiClient.get('/teams'),
  getById: (id) => apiClient.get(`/teams/${id}`),
}

// Tournaments API
export const tournamentsAPI = {
  getAll: () => apiClient.get('/tournaments'),
  getById: (id) => apiClient.get(`/tournaments/${id}`),
  create: (data) => apiClient.post('/tournaments', data),
}

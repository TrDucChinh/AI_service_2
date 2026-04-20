import axios from 'axios'
import { store } from '../store'
import { logout, updateToken } from '../store/authSlice'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const state = store.getState()
  const token = state.auth.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const storedAuth = JSON.parse(localStorage.getItem('auth') || '{}')
        const refreshToken = storedAuth.refreshToken
        if (refreshToken) {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken })
          store.dispatch(updateToken(data.access))
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        }
      } catch {
        store.dispatch(logout())
      }
    }
    return Promise.reject(error)
  }
)

export default api

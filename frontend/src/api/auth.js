import api from './axios'

export const authApi = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  refresh: (refreshToken) => api.post('/auth/refresh/', { refresh: refreshToken }),
  verify: (token) => api.post('/auth/verify/', { token }),
}

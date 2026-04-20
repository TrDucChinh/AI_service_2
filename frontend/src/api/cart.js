import api from './axios'

export const cartApi = {
  get: () => api.get('/cart/'),
  addItem: (data) => api.post('/cart/items/', data),
  updateItem: (id, data) => api.put(`/cart/items/${id}/`, data),
  removeItem: (id) => api.delete(`/cart/items/${id}/`),
  clear: () => api.delete('/cart/clear/'),
}

import api from './axios'

export const ordersApi = {
  list: (params) => api.get('/orders/', { params }),
  get: (id) => api.get(`/orders/${id}/`),
  create: (data) => api.post('/orders/', data),
  cancel: (id) => api.post(`/orders/${id}/cancel/`),
  initiatePayment: (data) => api.post('/payments/initiate/', data),
  confirmPayment: (id) => api.post(`/payments/${id}/confirm/`),
}

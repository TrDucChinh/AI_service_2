import api from './axios'

export const productsApi = {
  list: (service, params) => api.get(`/products/${service}/`, { params }),
  get: (service, id) => api.get(`/products/${service}/${id}/`),
  create: (service, data) => api.post(`/products/${service}/`, data),
  update: (service, id, data) => api.put(`/products/${service}/${id}/`, data),
  delete: (service, id) => api.delete(`/products/${service}/${id}/`),
  brands: (service) => api.get(`/products/${service}/brands/`),
  categories: (service) => api.get(`/products/${service}/categories/`),
  reviews: (service, productId) => api.get(`/products/${service}/reviews/?product=${productId}`),
  addReview: (service, data) => api.post(`/products/${service}/reviews/`, data),
  search: (query, params) => api.get('/search/', { params: { q: query, ...params } }),
}

export const PRODUCT_SERVICES = [
  'laptop', 'mobile', 'tablet', 'audio', 'accessory',
  'smartwatch', 'camera', 'monitor', 'keyboard', 'mouse',
  'printer', 'networking', 'storage', 'component', 'gaminggear'
]

export const SERVICE_LABELS = {
  laptop: 'Laptops', mobile: 'Mobile Phones', tablet: 'Tablets',
  audio: 'Audio', accessory: 'Accessories', smartwatch: 'Smartwatches',
  camera: 'Cameras', monitor: 'Monitors', keyboard: 'Keyboards',
  mouse: 'Mice', printer: 'Printers', networking: 'Networking',
  storage: 'Storage', component: 'PC Components', gaminggear: 'Gaming Gear',
}

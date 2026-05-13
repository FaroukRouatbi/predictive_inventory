import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Automatically attach JWT token to every request
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Products
export const getProducts = () =>
  apiClient.get('/products/').then(r => r.data)

// Inventory
export const getAllInventory = () =>
  apiClient.get('/inventory/').then(r => r.data)

export const getInventoryByProduct = (productId: string) =>
  apiClient.get(`/inventory/${productId}`).then(r => r.data)

// Forecast
export const getForecast = (productId: string) =>
  apiClient.post(`/forecast/${productId}`, {
    horizon_days: 30,
    history_days: 90
  }).then(r => r.data)

// Alerts
export const getUnresolvedAlerts = () =>
  apiClient.get('/alerts/').then(r => r.data)

export const getAllAlerts = () =>
  apiClient.get('/alerts/all').then(r => r.data)

export const resolveAlert = (alertId: string) =>
  apiClient.put(`/alerts/${alertId}/resolve`, {}).then(r => r.data)

export const unresolveAlert = (alertId: string) =>
  apiClient.put(`/alerts/${alertId}/unresolve`, {}).then(r => r.data)

export const recordSale = (data: {
  product_id: string
  inventory_id: string
  quantity_sold: number
  price_at_sale: number
}) => apiClient.post('/sales/', data).then(r => r.data)

// Auth
export const loginUser = (email: string, password: string) =>
  apiClient.post('/auth/login',
    new URLSearchParams({ username: email, password }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  ).then(r => r.data)

export const getGoogleLoginUrl = () =>
  apiClient.get('/auth/google/login').then(r => r.data)
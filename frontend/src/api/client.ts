import axios from "axios";

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1',
    headers:{
        'Content-Type' : 'application/json',
    },
})

export const getProducts = () =>
    apiClient.get('/products/').then(r => r.data)

export const getAllInventory = () =>
    apiClient.get('/inventory/').then(r => r.data)

export const getInventoryByProduct = (productId: string) =>
    apiClient.get(`/inventory/${productId}`).then(r => r.data)

export const getForecast = (productId: string) =>
    apiClient.post(`/forecast/${productId}`,{
        horizon_days: 30,
        history_days: 90
    }).then(r => r.data)

export const getUnresolvedAlerts = () =>
    apiClient.get('/alerts/').then(r => r.data)

export const resolveAlert = (alertId: string) =>
    apiClient.put(`/alerts/${alertId}/resolve`, {}).then(r => r.data)

// Get all alerts including resolved
export const getAllAlerts = () =>
  apiClient.get('/alerts/all').then(r => r.data)

// Unresolve an alert
export const unresolveAlert = (alertId: string) =>
  apiClient.put(`/alerts/${alertId}/unresolve`, {}).then(r => r.data)

// Record a sale
export const recordSale = (data: {
  product_id: string
  inventory_id: string
  quantity_sold: number
  price_at_sale: number
}) => apiClient.post('/sales/', data).then(r => r.data)
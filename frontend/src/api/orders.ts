import api from './client'

export const ordersAPI = {
  // Orders
  getOrders: (params: any) => api.get('/orders/', { params }),
  getOrderDetail: (id: number) => api.get(`/orders/${id}/`),
  createOrder: (data: any) => api.post('/orders/', data),

  // Order actions
  cancelOrder: (id: number) => api.patch(`/orders/${id}/cancel/`),
  trackOrder: (id: number) => api.get(`/orders/${id}/track/`),
}

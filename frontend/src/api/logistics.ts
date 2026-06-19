import api from './client'

export const logisticsAPI = {
  // Shipping methods
  getShippingMethods: () => api.get('/logistics/shipping-methods/'),

  // Shipments
  getShipments: (params: any) => api.get('/logistics/shipments/', { params }),
  getShipmentDetail: (id: number) => api.get(`/logistics/shipments/${id}/`),

  // Returns
  createReturn: (data: any) => api.post('/logistics/returns/create_return/', data),
  getReturns: (params: any) => api.get('/logistics/returns/', { params }),
  approveReturn: (id: number) => api.patch(`/logistics/returns/${id}/approve/`),
  rejectReturn: (id: number) => api.patch(`/logistics/returns/${id}/reject/`),
}

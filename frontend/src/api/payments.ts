import api from './client'

export const paymentsAPI = {
  // Payment history
  getPayments: () => api.get('/payments/'),
  getPaymentDetail: (id: number) => api.get(`/payments/${id}/`),

  // M-Pesa
  initiateMPesaPayment: (data: any) =>
    api.post('/payments/mpesa_payment/', data),

  // Stripe
  initiateStripePayment: (data: any) =>
    api.post('/payments/stripe_payment/', data),
  confirmStripePayment: (paymentIntentId: string) =>
    api.post('/payments/stripe_confirm/', { payment_intent_id: paymentIntentId }),
  checkPaymentStatus: (id: number) =>
    api.post(`/payments/${id}/check_status/`),

  // Refund
  refundPayment: (id: number, data: any) =>
    api.post(`/payments/${id}/refund/`, data),
}

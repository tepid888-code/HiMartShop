import { defineStore } from 'pinia'
import { ref } from 'vue'
import { paymentsAPI } from '@/api/payments'

interface Payment {
  id: number
  order_id: number
  amount: number
  payment_method: string
  status: string
  transaction_id?: string
  created_at: string
}

export const usePaymentsStore = defineStore('payments', () => {
  const payments = ref<Payment[]>([])
  const currentPayment = ref<Payment | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchPayments = async () => {
    try {
      loading.value = true
      const response = await paymentsAPI.getPayments()
      payments.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch payments'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPaymentDetail = async (id: number) => {
    try {
      loading.value = true
      const response = await paymentsAPI.getPaymentDetail(id)
      currentPayment.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const initiateMPesaPayment = async (orderId: number, phone: string, amount: number) => {
    try {
      loading.value = true
      const response = await paymentsAPI.initiateMPesaPayment({
        order_id: orderId,
        phone_number: phone,
        amount: amount,
      })
      currentPayment.value = response.data
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to initiate M-Pesa payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const initiateStripePayment = async (orderId: number, amount: number) => {
    try {
      loading.value = true
      const response = await paymentsAPI.initiateStripePayment({
        order_id: orderId,
        stripe_token: '',
        amount: amount,
      })
      currentPayment.value = response.data
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to initiate Stripe payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const confirmStripePayment = async (paymentIntentId: string) => {
    try {
      loading.value = true
      const response = await paymentsAPI.confirmStripePayment(paymentIntentId)
      if (currentPayment.value) {
        currentPayment.value.status = 'success'
      }
      await fetchPayments()
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to confirm Stripe payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkPaymentStatus = async (id: number) => {
    try {
      const response = await paymentsAPI.checkPaymentStatus(id)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to check payment status'
      throw err
    }
  }

  const pollPaymentStatus = async (id: number, interval: number = 2000, maxAttempts: number = 30) => {
    return new Promise((resolve, reject) => {
      let attempts = 0

      const poll = async () => {
        try {
          const status = await checkPaymentStatus(id)
          if (status.status === 'success') {
            resolve(status)
          } else if (attempts < maxAttempts) {
            attempts++
            setTimeout(poll, interval)
          } else {
            reject(new Error('Payment verification timeout'))
          }
        } catch (error) {
          reject(error)
        }
      }

      poll()
    })
  }

  const refundPayment = async (id: number, reason: string, description: string, amount?: number) => {
    try {
      loading.value = true
      const response = await paymentsAPI.refundPayment(id, {
        reason,
        description,
        amount,
      })
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to request refund'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    payments,
    currentPayment,
    loading,
    error,
    fetchPayments,
    fetchPaymentDetail,
    initiateMPesaPayment,
    initiateStripePayment,
    confirmStripePayment,
    checkPaymentStatus,
    pollPaymentStatus,
    refundPayment,
  }
})

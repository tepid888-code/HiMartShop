import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ordersAPI } from '@/api/orders'

interface OrderItem {
  id: number
  product: any
  quantity: number
  price: number
  subtotal: number
}

interface Order {
  id: number
  order_number: string
  status: string
  payment_status: string
  total_amount: number
  created_at: string
  items?: OrderItem[]
}

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<Order[]>([])
  const currentOrder = ref<Order | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchOrders = async (filters?: any) => {
    try {
      loading.value = true
      const params = {
        ordering: '-created_at',
        ...filters,
      }
      const response = await ordersAPI.getOrders(params)
      orders.value = response.data.results || response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch orders'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchOrderDetail = async (id: number) => {
    try {
      loading.value = true
      const response = await ordersAPI.getOrderDetail(id)
      currentOrder.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch order'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createOrder = async (orderData: any) => {
    try {
      loading.value = true
      const response = await ordersAPI.createOrder(orderData)
      currentOrder.value = response.data
      await fetchOrders()
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create order'
      throw err
    } finally {
      loading.value = false
    }
  }

  const cancelOrder = async (id: number) => {
    try {
      const response = await ordersAPI.cancelOrder(id)
      currentOrder.value = response.data
      await fetchOrders()
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to cancel order'
      throw err
    }
  }

  const trackOrder = async (id: number) => {
    try {
      const response = await ordersAPI.trackOrder(id)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to track order'
      throw err
    }
  }

  const getOrdersByStatus = (status: string) => {
    return orders.value.filter(order => order.status === status)
  }

  return {
    orders,
    currentOrder,
    loading,
    error,
    fetchOrders,
    fetchOrderDetail,
    createOrder,
    cancelOrder,
    trackOrder,
    getOrdersByStatus,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { logisticsAPI } from '@/api/logistics'

interface TrackingEvent {
  id: number
  status: string
  location: string
  description: string
  timestamp: string
}

interface Shipment {
  id: number
  order: any
  tracking_number: string
  carrier: string
  status: string
  tracking_events: TrackingEvent[]
  estimated_delivery: string
  created_at: string
}

interface ReturnRequest {
  id: number
  order: any
  reason: string
  status: string
  created_at: string
}

export const useLogisticsStore = defineStore('logistics', () => {
  const shipments = ref<Shipment[]>([])
  const currentShipment = ref<Shipment | null>(null)
  const shippingMethods = ref<any[]>([])
  const returns = ref<ReturnRequest[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchShippingMethods = async () => {
    try {
      const response = await logisticsAPI.getShippingMethods()
      shippingMethods.value = response.data
    } catch (err: any) {
      console.error('Failed to fetch shipping methods:', err)
    }
  }

  const fetchShipments = async (filters?: any) => {
    try {
      loading.value = true
      const response = await logisticsAPI.getShipments(filters)
      shipments.value = response.data.results || response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取物流信息失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchShipmentDetail = async (id: number) => {
    try {
      loading.value = true
      const response = await logisticsAPI.getShipmentDetail(id)
      currentShipment.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取物流详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createReturn = async (orderId: number, reason: string) => {
    try {
      loading.value = true
      const response = await logisticsAPI.createReturn({
        order_id: orderId,
        reason,
      })
      await fetchReturns()
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '申请退货失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchReturns = async () => {
    try {
      const response = await logisticsAPI.getReturns({})
      returns.value = response.data.results || response.data
    } catch (err: any) {
      console.error('Failed to fetch returns:', err)
    }
  }

  const approveReturn = async (id: number) => {
    try {
      await logisticsAPI.approveReturn(id)
      await fetchReturns()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '批准退货失败'
      throw err
    }
  }

  const rejectReturn = async (id: number) => {
    try {
      await logisticsAPI.rejectReturn(id)
      await fetchReturns()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '拒绝退货失败'
      throw err
    }
  }

  return {
    shipments,
    currentShipment,
    shippingMethods,
    returns,
    loading,
    error,
    fetchShippingMethods,
    fetchShipments,
    fetchShipmentDetail,
    createReturn,
    fetchReturns,
    approveReturn,
    rejectReturn,
  }
})

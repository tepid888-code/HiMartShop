import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sellersAPI } from '@/api/sellers'

interface SellerProfile {
  id: number
  user: any
  store: any
  verification_status: string
  total_revenue: number
  total_orders: number
  average_rating: number
  response_time: number
}

interface SellerStats {
  date: string
  orders_count: number
  revenue: number
  views_count: number
}

interface Dashboard {
  profile: SellerProfile
  stats: SellerStats[]
  recent_orders: any[]
  pending_messages: number
}

export const useSellersStore = defineStore('sellers', () => {
  const profile = ref<SellerProfile | null>(null)
  const dashboard = ref<Dashboard | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchProfile = async () => {
    try {
      loading.value = true
      const response = await sellersAPI.getMyProfile()
      profile.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取卖家资料失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDashboard = async () => {
    try {
      loading.value = true
      const response = await sellersAPI.getDashboard()
      dashboard.value = response.data
      profile.value = response.data.profile
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取仪表板失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const requestWithdrawal = async (amount: number, note: string = '') => {
    try {
      loading.value = true
      const response = await sellersAPI.requestWithdrawal({
        amount,
        note,
      })
      await fetchDashboard()
      error.value = null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '申请提现失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const replyToMessage = async (messageId: number, content: string) => {
    try {
      const response = await sellersAPI.replyToMessage(messageId, {
        content,
      })
      await fetchDashboard()
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '回复消息失败'
      throw err
    }
  }

  return {
    profile,
    dashboard,
    loading,
    error,
    fetchProfile,
    fetchDashboard,
    requestWithdrawal,
    replyToMessage,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { promotionsAPI } from '@/api/promotions'

interface Coupon {
  id: number
  code: string
  description: string
  discount_type: string
  discount_value: string
  discount_value_formatted: string
  min_purchase: number
  max_discount: number | null
  is_valid: boolean
}

export const usePromotionsStore = defineStore('promotions', () => {
  const coupons = ref<Coupon[]>([])
  const appliedCoupon = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCoupons = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await promotionsAPI.getCoupons()
      coupons.value = response.data.results || response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch coupons'
    } finally {
      loading.value = false
    }
  }

  const validateCoupon = async (code: string, amount: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await promotionsAPI.validateCoupon(code, amount)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Invalid coupon'
      throw err
    } finally {
      loading.value = false
    }
  }

  const applyCoupon = async (code: string, amount: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await promotionsAPI.applyCoupon(code, amount)
      appliedCoupon.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to apply coupon'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearAppliedCoupon = () => {
    appliedCoupon.value = null
    error.value = null
  }

  return {
    coupons,
    appliedCoupon,
    loading,
    error,
    fetchCoupons,
    validateCoupon,
    applyCoupon,
    clearAppliedCoupon,
  }
})

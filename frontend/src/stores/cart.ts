import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartAPI } from '@/api/cart'

interface CartItem {
  id: number
  product: any
  product_id: number
  quantity: number
  subtotal: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCart = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await cartAPI.getCart()
      items.value = response.data.items || []
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch cart'
    } finally {
      loading.value = false
    }
  }

  const addItem = async (productId: number, quantity: number = 1) => {
    loading.value = true
    error.value = null
    try {
      const response = await cartAPI.addToCart(productId, quantity)
      // 重新加载购物车
      await fetchCart()
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to add item'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeItem = async (itemId: number) => {
    loading.value = true
    error.value = null
    try {
      await cartAPI.removeCartItem(itemId)
      items.value = items.value.filter(item => item.id !== itemId)
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to remove item'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateQuantity = async (itemId: number, quantity: number) => {
    loading.value = true
    error.value = null
    try {
      await cartAPI.updateCartItem(itemId, quantity)
      const item = items.value.find(i => i.id === itemId)
      if (item) {
        item.quantity = quantity
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update quantity'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearCart = async () => {
    loading.value = true
    error.value = null
    try {
      await cartAPI.clearCart()
      items.value = []
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to clear cart'
      throw err
    } finally {
      loading.value = false
    }
  }

  const total = computed(() => {
    return items.value.reduce((sum, item) => sum + parseFloat(item.subtotal || '0'), 0)
  })

  const itemCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  return {
    items,
    loading,
    error,
    total,
    itemCount,
    fetchCart,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
  }
})


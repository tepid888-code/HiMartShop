import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface CartItem {
  id: number
  product_id: number
  product_name: string
  price: number
  quantity: number
  image?: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  const loadCart = () => {
    const stored = localStorage.getItem('cart')
    if (stored) {
      items.value = JSON.parse(stored)
    }
  }

  const saveCart = () => {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }

  const addItem = (product: any) => {
    const existing = items.value.find(item => item.product_id === product.id)
    if (existing) {
      existing.quantity += 1
    } else {
      items.value.push({
        id: Date.now(),
        product_id: product.id,
        product_name: product.name,
        price: product.price,
        quantity: 1,
        image: product.image,
      })
    }
    saveCart()
  }

  const removeItem = (itemId: number) => {
    items.value = items.value.filter(item => item.id !== itemId)
    saveCart()
  }

  const updateQuantity = (itemId: number, quantity: number) => {
    const item = items.value.find(i => i.id === itemId)
    if (item) {
      item.quantity = Math.max(1, quantity)
      saveCart()
    }
  }

  const clearCart = () => {
    items.value = []
    saveCart()
  }

  const total = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  const itemCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  loadCart()

  return {
    items,
    total,
    itemCount,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
  }
})

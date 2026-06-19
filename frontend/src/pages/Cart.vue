<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-6xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">购物车</h1>

      <!-- Loading -->
      <div v-if="cartStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Empty Cart -->
      <div v-else-if="cartStore.items.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
        </svg>
        <p class="text-gray-600 text-lg mb-4">购物车为空</p>
        <RouterLink to="/products" class="inline-block px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition">
          去购物
        </RouterLink>
      </div>

      <!-- Cart Content -->
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Items List -->
        <div class="md:col-span-2 space-y-4">
          <div v-for="item in cartStore.items" :key="item.id" class="bg-white rounded-lg shadow p-6 flex gap-6">
            <!-- Product Image -->
            <div class="w-24 h-24 bg-gray-200 rounded-lg flex-shrink-0">
              <img
                v-if="item.product?.image"
                :src="item.product.image"
                :alt="item.product_name"
                class="w-full h-full object-cover rounded-lg"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </div>
            </div>

            <!-- Product Info -->
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ item.product_name }}</h3>
              <p class="text-gray-600 text-sm mb-4">SKU: {{ item.sku || 'N/A' }}</p>

              <!-- Price -->
              <div class="mb-4">
                <span class="text-xl font-bold text-indigo-600">¥{{ item.price }}</span>
                <span v-if="item.original_price > item.price" class="ml-2 line-through text-gray-500">¥{{ item.original_price }}</span>
              </div>

              <!-- Quantity Control -->
              <div class="flex items-center gap-3">
                <button
                  @click="updateQuantity(item.id, item.quantity - 1)"
                  :disabled="item.quantity <= 1"
                  class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  −
                </button>
                <span class="px-4 py-1">{{ item.quantity }}</span>
                <button
                  @click="updateQuantity(item.id, item.quantity + 1)"
                  :disabled="item.quantity >= item.stock"
                  class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  +
                </button>
                <span v-if="item.quantity >= item.stock" class="text-xs text-orange-600 ml-2">库存不足</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="text-right">
              <p class="text-lg font-bold text-gray-900 mb-4">¥{{ (item.price * item.quantity).toFixed(2) }}</p>
              <button
                @click="removeItem(item.id)"
                class="text-red-600 hover:text-red-700 font-semibold text-sm"
              >
                移除
              </button>
            </div>
          </div>

          <!-- Clear Cart Button -->
          <button
            @click="clearCart"
            class="w-full px-4 py-2 text-gray-600 hover:text-gray-700 border border-gray-300 rounded-lg transition"
          >
            清空购物车
          </button>
        </div>

        <!-- Order Summary -->
        <div class="md:col-span-1">
          <div class="bg-white rounded-lg shadow p-6 sticky top-8">
            <h2 class="text-xl font-semibold text-gray-900 mb-6">订单总结</h2>

            <!-- Price Breakdown -->
            <div class="space-y-3 mb-6 pb-6 border-b">
              <div class="flex justify-between text-gray-700">
                <span>小计</span>
                <span>¥{{ cartStore.total.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-gray-700">
                <span>商品数量</span>
                <span>{{ cartStore.itemCount }}</span>
              </div>
            </div>

            <!-- Coupon Code -->
            <div class="mb-6">
              <label class="block text-sm font-semibold text-gray-900 mb-2">优惠券</label>
              <div class="flex gap-2">
                <input
                  v-model="couponCode"
                  type="text"
                  placeholder="输入优惠券代码"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <button
                  @click="applyCoupon"
                  :disabled="!couponCode || couponApplying"
                  class="px-3 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 rounded-lg font-semibold text-sm"
                >
                  应用
                </button>
              </div>
              <p v-if="appliedCoupon" class="text-sm text-green-600 mt-2">✓ 优惠券已应用</p>
            </div>

            <!-- Total -->
            <div class="flex justify-between items-center mb-6 pb-6 border-b">
              <span class="text-lg font-semibold text-gray-900">合计</span>
              <span class="text-2xl font-bold text-indigo-600">¥{{ cartStore.total.toFixed(2) }}</span>
            </div>

            <!-- Checkout Button -->
            <RouterLink
              to="/checkout"
              class="block text-center w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition mb-2"
            >
              去结账
            </RouterLink>

            <!-- Continue Shopping -->
            <RouterLink
              to="/products"
              class="block text-center text-indigo-600 hover:text-indigo-700 font-semibold py-2"
            >
              继续购物
            </RouterLink>

            <!-- Error Message -->
            <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-red-700 text-sm">{{ error }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { usePromotionsStore } from '@/stores/promotions'

const cartStore = useCartStore()
const promotionsStore = usePromotionsStore()

const couponCode = ref('')
const appliedCoupon = ref(false)
const couponApplying = ref(false)
const error = ref('')

const updateQuantity = async (itemId: number, newQuantity: number) => {
  error.value = ''
  if (newQuantity < 1) return

  try {
    await cartStore.updateItem(itemId, newQuantity)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '更新购物车失败'
  }
}

const removeItem = async (itemId: number) => {
  error.value = ''
  try {
    await cartStore.removeItem(itemId)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '移除商品失败'
  }
}

const clearCart = async () => {
  if (!confirm('确定要清空购物车吗？')) return

  error.value = ''
  try {
    await cartStore.clearCart()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '清空购物车失败'
  }
}

const applyCoupon = async () => {
  error.value = ''
  if (!couponCode.value.trim()) {
    error.value = '请输入优惠券代码'
    return
  }

  couponApplying.value = true
  try {
    await promotionsStore.validateCoupon(couponCode.value)
    appliedCoupon.value = true
    couponCode.value = ''
  } catch (err: any) {
    error.value = err.response?.data?.detail || '优惠券无效'
  } finally {
    couponApplying.value = false
  }
}
</script>

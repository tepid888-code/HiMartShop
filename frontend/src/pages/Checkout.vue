<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">结账</h1>

      <div v-if="cartStore.items.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
        <p class="text-gray-600 text-lg mb-4">购物车为空</p>
        <RouterLink to="/products" class="text-indigo-600 hover:text-indigo-700 font-semibold">
          继续购物
        </RouterLink>
      </div>

      <div v-else class="grid grid-cols-3 gap-8">
        <!-- Cart Summary -->
        <div class="col-span-2 space-y-6">
          <!-- Order Items -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">订单商品</h2>
            <div class="space-y-4">
              <div v-for="item in cartStore.items" :key="item.id" class="flex justify-between items-center border-b pb-4">
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900">{{ item.product_name }}</h3>
                  <p class="text-gray-600 text-sm">数量: {{ item.quantity }}</p>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-gray-900">¥{{ (item.price * item.quantity).toFixed(2) }}</p>
                  <p class="text-gray-600 text-sm">¥{{ item.price }}/个</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Shipping Address -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">收货地址</h2>
            <div v-if="userAddresses.length > 0" class="space-y-3 mb-4">
              <label v-for="addr in userAddresses" :key="addr.id" class="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                :class="{ 'border-indigo-600 bg-indigo-50': shippingAddressId === addr.id }">
                <input
                  type="radio"
                  :value="addr.id"
                  v-model.number="shippingAddressId"
                  class="mt-1"
                />
                <div class="ml-3">
                  <p class="font-semibold text-gray-900">{{ addr.address_type }}</p>
                  <p class="text-gray-600 text-sm">{{ addr.street_address }}, {{ addr.city }}</p>
                  <p class="text-gray-600 text-sm">{{ addr.postal_code }} {{ addr.country }}</p>
                </div>
              </label>
            </div>

            <!-- Manual Address Entry -->
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">详细地址</label>
                <textarea
                  v-model="shippingAddressText"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
                  rows="3"
                  placeholder="街道地址、城市、邮编、国家"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Billing Address -->
          <div class="bg-white rounded-lg shadow p-6">
            <label class="flex items-center mb-4">
              <input v-model="sameAsBilling" type="checkbox" class="text-indigo-600" />
              <span class="ml-2 text-gray-700">账单地址同收货地址</span>
            </label>

            <div v-if="!sameAsBilling" class="space-y-3">
              <textarea
                v-model="billingAddressText"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
                rows="3"
                placeholder="账单地址"
              ></textarea>
            </div>
          </div>

          <!-- Order Notes -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">订单备注 (可选)</h2>
            <textarea
              v-model="notes"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              rows="3"
              placeholder="输入订单备注..."
            ></textarea>
          </div>

          <!-- Terms -->
          <div class="bg-white rounded-lg shadow p-6">
            <label class="flex items-start">
              <input v-model="agreeTerms" type="checkbox" class="mt-1 text-indigo-600" />
              <span class="ml-2 text-gray-700">
                我同意
                <a href="#" class="text-indigo-600 hover:text-indigo-700">服务条款</a>
                和
                <a href="#" class="text-indigo-600 hover:text-indigo-700">隐私政策</a>
              </span>
            </label>
          </div>
        </div>

        <!-- Order Summary Sidebar -->
        <div class="col-span-1">
          <div class="bg-white rounded-lg shadow p-6 sticky top-8">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">订单总结</h2>

            <!-- Price Breakdown -->
            <div class="space-y-2 mb-4 pb-4 border-b">
              <div class="flex justify-between text-gray-700">
                <span>小计</span>
                <span>¥{{ subtotal.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-gray-700">
                <span>税费 (8%)</span>
                <span>¥{{ tax.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-gray-700">
                <span>运费</span>
                <span>¥{{ shippingCost.toFixed(2) }}</span>
              </div>
            </div>

            <!-- Total -->
            <div class="flex justify-between items-center mb-6">
              <span class="text-lg font-semibold text-gray-900">合计</span>
              <span class="text-2xl font-bold text-indigo-600">¥{{ total.toFixed(2) }}</span>
            </div>

            <!-- Create Order Button -->
            <button
              @click="createOrder"
              :disabled="!agreeTerms || loading"
              class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition mb-2"
            >
              {{ loading ? '创建订单中...' : '创建订单' }}
            </button>

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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useOrdersStore } from '@/stores/orders'
import { useAuthStore } from '@/stores/auth'
import { usersAPI } from '@/api/users'

const router = useRouter()
const cartStore = useCartStore()
const ordersStore = useOrdersStore()
const authStore = useAuthStore()

const userAddresses = ref<any[]>([])
const shippingAddressId = ref<number | null>(null)
const billingAddressId = ref<number | null>(null)
const shippingAddressText = ref('')
const billingAddressText = ref('')
const sameAsBilling = ref(true)
const notes = ref('')
const agreeTerms = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

const subtotal = computed(() => cartStore.total)
const tax = computed(() => subtotal.value * 0.08)
const shippingCost = computed(() => (subtotal.value > 0 ? 50 : 0))
const total = computed(() => subtotal.value + tax.value + shippingCost.value)

onMounted(async () => {
  try {
    const response = await usersAPI.getAddresses()
    userAddresses.value = response.data
    if (userAddresses.value.length > 0) {
      shippingAddressId.value = userAddresses.value[0].id
    }
  } catch (err) {
    console.error('Failed to fetch addresses:', err)
  }
})

const createOrder = async () => {
  error.value = null

  if (!shippingAddressId.value && !shippingAddressText.value) {
    error.value = '请选择或输入收货地址'
    return
  }

  const billingAddr = sameAsBilling.value ? shippingAddressText.value : billingAddressText.value

  if (!sameAsBilling.value && !billingAddr) {
    error.value = '请输入账单地址'
    return
  }

  loading.value = true

  try {
    const items = cartStore.items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
    }))

    const orderData: any = {
      items,
      notes: notes.value,
    }

    if (shippingAddressId.value) {
      orderData.shipping_address_id = shippingAddressId.value
    } else {
      orderData.shipping_address = shippingAddressText.value
    }

    if (sameAsBilling.value && shippingAddressId.value) {
      orderData.billing_address_id = shippingAddressId.value
    } else {
      orderData.billing_address = sameAsBilling.value
        ? shippingAddressText.value
        : billingAddressText.value
    }

    const order = await ordersStore.createOrder(orderData)
    cartStore.clearCart()
    router.push(`/orders/${order.id}`)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to create order'
  } finally {
    loading.value = false
  }
}
</script>


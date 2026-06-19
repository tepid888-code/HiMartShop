<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-2xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">支付</h1>

      <!-- Order Summary -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">订单信息</h2>
        <div class="flex justify-between mb-2">
          <span class="text-gray-700">订单号</span>
          <span class="font-semibold">{{ order?.order_number }}</span>
        </div>
        <div class="flex justify-between mb-2">
          <span class="text-gray-700">金额</span>
          <span class="font-semibold">¥{{ order?.total_amount }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-700">状态</span>
          <span class="font-semibold">{{ order?.status === 'pending' ? '待支付' : '已支付' }}</span>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">选择支付方式</h2>

        <div class="space-y-3 mb-6">
          <!-- M-Pesa -->
          <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer"
            :class="selectedMethod === 'mpesa' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'">
            <input
              type="radio"
              value="mpesa"
              v-model="selectedMethod"
              class="text-indigo-600"
            />
            <div class="ml-3">
              <p class="font-semibold text-gray-900">M-Pesa (肯尼亚本地支付)</p>
              <p class="text-gray-600 text-sm">通过 M-Pesa 钱包支付</p>
            </div>
          </label>

          <!-- Stripe -->
          <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer"
            :class="selectedMethod === 'stripe' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'">
            <input
              type="radio"
              value="stripe"
              v-model="selectedMethod"
              class="text-indigo-600"
            />
            <div class="ml-3">
              <p class="font-semibold text-gray-900">Stripe (信用卡/借记卡)</p>
              <p class="text-gray-600 text-sm">支持 Visa, Mastercard 等</p>
            </div>
          </label>
        </div>

        <!-- M-Pesa Payment Form -->
        <div v-if="selectedMethod === 'mpesa'" class="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">电话号码</label>
            <input
              v-model="mpesaPhone"
              type="tel"
              placeholder="254712345678"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
            />
            <p class="text-gray-600 text-xs mt-1">格式: 254开头的肯尼亚电话号码</p>
          </div>
        </div>

        <!-- Stripe Payment Form -->
        <div v-if="selectedMethod === 'stripe'" class="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
            <p>测试卡号: 4242 4242 4242 4242</p>
            <p>有效期: 12/25 | CVC: 123</p>
          </div>
          <!-- Stripe Elements will be rendered here -->
          <div id="card-element" class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white"></div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-4">
          <button
            @click="processPayment"
            :disabled="loading || !selectedMethod"
            class="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition"
          >
            {{ loading ? '处理中...' : '继续支付' }}
          </button>

          <RouterLink
            to="/orders"
            class="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold rounded-lg transition text-center"
          >
            返回
          </RouterLink>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700 text-sm">{{ error }}</p>
        </div>
      </div>

      <!-- Payment Status -->
      <div v-if="paymentStatus" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">支付状态</h2>
        <div :class="['p-4 rounded-lg', paymentStatus === 'success' ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200']">
          <p :class="['font-semibold', paymentStatus === 'success' ? 'text-green-800' : 'text-yellow-800']">
            {{ paymentStatus === 'success' ? '支付成功!' : '支付处理中...' }}
          </p>
          <p v-if="paymentStatus !== 'success'" class="text-yellow-700 text-sm mt-2">
            请在手机上完成 M-Pesa 确认 (如使用 M-Pesa)
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { usePaymentsStore } from '@/stores/payments'

const route = useRoute()
const router = useRouter()
const ordersStore = useOrdersStore()
const paymentsStore = usePaymentsStore()

const orderId = parseInt(route.params.id as string)
const order = ref(ordersStore.currentOrder)
const selectedMethod = ref('mpesa')
const mpesaPhone = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const paymentStatus = ref<string | null>(null)

onMounted(async () => {
  if (!order.value) {
    await ordersStore.fetchOrderDetail(orderId)
    order.value = ordersStore.currentOrder
  }
})

const processPayment = async () => {
  error.value = null

  if (selectedMethod.value === 'mpesa') {
    if (!mpesaPhone.value) {
      error.value = '请输入电话号码'
      return
    }

    loading.value = true
    try {
      const result = await paymentsStore.initiateMPesaPayment(
        orderId,
        mpesaPhone.value,
        order.value?.total_amount || 0
      )

      paymentStatus.value = 'processing'

      // Poll for payment status
      try {
        await paymentsStore.pollPaymentStatus(result.payment_id, 5000, 60)
        paymentStatus.value = 'success'
        setTimeout(() => {
          router.push(`/orders/${orderId}`)
        }, 2000)
      } catch (err) {
        error.value = '支付验证超时，请稍后检查订单状态'
      }
    } finally {
      loading.value = false
    }
  } else if (selectedMethod.value === 'stripe') {
    loading.value = true
    try {
      const result = await paymentsStore.initiateStripePayment(
        orderId,
        order.value?.total_amount || 0
      )

      // Create Stripe Payment Element
      // This would typically use @stripe/stripe-js and Stripe Elements
      // For now, we'll show a placeholder
      error.value = '需要集成 Stripe Elements 组件'
    } finally {
      loading.value = false
    }
  }
}
</script>

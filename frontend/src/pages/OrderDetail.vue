<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Breadcrumb -->
      <nav class="flex mb-8 text-sm">
        <RouterLink to="/" class="text-indigo-600 hover:text-indigo-700">首页</RouterLink>
        <span class="mx-2 text-gray-500">/</span>
        <RouterLink to="/orders" class="text-indigo-600 hover:text-indigo-700">订单</RouterLink>
        <span class="mx-2 text-gray-500">/</span>
        <span class="text-gray-900" v-if="order">{{ order.order_number }}</span>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Order Detail -->
      <div v-else-if="order" class="space-y-6">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">订单 {{ order.order_number }}</h1>
              <p class="text-gray-600">创建于 {{ formatDate(order.created_at) }}</p>
            </div>
            <div class="text-right">
              <div :class="['inline-block px-4 py-2 rounded text-sm font-semibold mb-2', getStatusColor(order.status)]">
                {{ getStatusLabel(order.status) }}
              </div>
              <br>
              <div :class="['inline-block px-4 py-2 rounded text-sm font-semibold', getPaymentStatusColor(order.payment_status)]">
                {{ getPaymentStatusLabel(order.payment_status) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">订单商品</h2>
          <div class="space-y-4">
            <div v-for="item in order.items" :key="item.id" class="flex items-center justify-between border-b pb-4">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900">{{ item.product?.name }}</h3>
                <p class="text-gray-600 text-sm">SKU: {{ item.product?.sku }}</p>
              </div>
              <div class="text-right">
                <p class="text-gray-700">数量: {{ item.quantity }}</p>
                <p class="font-semibold text-gray-900">¥{{ item.price }}/个</p>
                <p class="text-gray-600">小计: ¥{{ item.subtotal }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Pricing -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">费用信息</h2>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-700">小计</span>
              <span class="font-semibold">¥{{ order.subtotal }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-700">税费</span>
              <span class="font-semibold">¥{{ order.tax }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-700">运费</span>
              <span class="font-semibold">¥{{ order.shipping_cost }}</span>
            </div>
            <div v-if="order.discount > 0" class="flex justify-between text-red-600">
              <span>折扣</span>
              <span>-¥{{ order.discount }}</span>
            </div>
            <div class="flex justify-between text-lg font-bold border-t pt-2">
              <span>合计</span>
              <span class="text-indigo-600">¥{{ order.total_amount }}</span>
            </div>
          </div>
        </div>

        <!-- Shipping Address -->
        <div class="grid grid-cols-2 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">收货地址</h2>
            <p class="text-gray-700 whitespace-pre-wrap">{{ order.shipping_address }}</p>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">账单地址</h2>
            <p class="text-gray-700 whitespace-pre-wrap">{{ order.billing_address }}</p>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">订单状态历史</h2>
          <div class="space-y-4">
            <div v-for="(status, index) in order.status_history" :key="status.id" class="flex">
              <div class="flex flex-col items-center mr-4">
                <div :class="['w-4 h-4 rounded-full border-2', index === 0 ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300']"></div>
                <div v-if="index < order.status_history.length - 1" class="w-1 h-8 bg-gray-300 my-1"></div>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ getStatusLabel(status.status) }}</p>
                <p class="text-gray-600 text-sm">{{ formatDate(status.created_at) }}</p>
                <p v-if="status.message" class="text-gray-600 text-sm mt-1">{{ status.message }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div v-if="order.status === 'pending'" class="flex gap-4">
          <RouterLink
            :to="`/payment/${order.id}`"
            class="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition text-center"
          >
            立即支付
          </RouterLink>
          <button
            @click="cancelOrder"
            class="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition"
          >
            取消订单
          </button>
        </div>

        <!-- Back Button -->
        <RouterLink
          to="/orders"
          class="block text-center text-indigo-600 hover:text-indigo-700 font-semibold py-3"
        >
          返回订单列表
        </RouterLink>
      </div>

      <!-- Error -->
      <div v-else class="bg-white rounded-lg shadow p-8 text-center">
        <p class="text-gray-600 text-lg">订单未找到</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'

const route = useRoute()
const ordersStore = useOrdersStore()

const orderId = parseInt(route.params.id as string)
const order = ref(ordersStore.currentOrder)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await ordersStore.fetchOrderDetail(orderId)
    order.value = ordersStore.currentOrder
  } catch (error) {
    console.error('Failed to fetch order:', error)
  } finally {
    loading.value = false
  }
})

const getStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待确认',
    confirmed: '已确认',
    processing: '处理中',
    shipped: '已发货',
    delivered: '已送达',
    cancelled: '已取消',
    refunded: '已退款',
  }
  return labels[status] || status
}

const getStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    processing: 'bg-blue-100 text-blue-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    refunded: 'bg-orange-100 text-orange-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getPaymentStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    unpaid: '未支付',
    paid: '已支付',
    failed: '支付失败',
    refunded: '已退款',
  }
  return labels[status] || status
}

const getPaymentStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    unpaid: 'bg-red-100 text-red-800',
    paid: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    refunded: 'bg-orange-100 text-orange-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const cancelOrder = async () => {
  if (!confirm('确定要取消此订单吗？')) return
  try {
    await ordersStore.cancelOrder(orderId)
    order.value = ordersStore.currentOrder
  } catch (error) {
    alert('取消订单失败')
  }
}
</script>

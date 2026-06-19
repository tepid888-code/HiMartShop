<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-6xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">我的订单</h1>

      <!-- Status Tabs -->
      <div class="flex gap-2 mb-6 border-b">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          @click="selectedStatus = tab.value"
          :class="[
            'px-4 py-2 font-semibold transition border-b-2',
            selectedStatus === tab.value
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="ordersStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Orders List -->
      <div v-else-if="filteredOrders.length > 0" class="space-y-4">
        <div v-for="order in filteredOrders" :key="order.id" class="bg-white rounded-lg shadow hover:shadow-lg transition">
          <div class="p-6">
            <!-- Order Header -->
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">订单号: {{ order.order_number }}</h3>
                <p class="text-sm text-gray-600">创建于 {{ formatDate(order.created_at) }}</p>
              </div>
              <div class="text-right">
                <div :class="['inline-block px-3 py-1 rounded text-sm font-semibold', getStatusColor(order.status)]">
                  {{ getStatusLabel(order.status) }}
                </div>
              </div>
            </div>

            <!-- Order Items -->
            <div class="mb-4 pb-4 border-b">
              <div v-for="item in order.items" :key="item.id" class="flex justify-between py-2">
                <span class="text-gray-700">{{ item.product?.name }} x {{ item.quantity }}</span>
                <span class="font-semibold text-gray-900">¥{{ item.subtotal }}</span>
              </div>
            </div>

            <!-- Order Footer -->
            <div class="flex justify-between items-center">
              <div>
                <span class="text-gray-600">合计: </span>
                <span class="text-xl font-bold text-indigo-600">¥{{ order.total_amount }}</span>
              </div>
              <div class="flex gap-2">
                <RouterLink
                  :to="`/orders/${order.id}`"
                  class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition"
                >
                  查看详情
                </RouterLink>
                <button
                  v-if="order.status === 'pending'"
                  @click="cancelOrder(order.id)"
                  class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition"
                >
                  取消订单
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-white rounded-lg shadow p-8 text-center">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
        </svg>
        <p class="text-gray-600 text-lg mb-4">暂无订单</p>
        <RouterLink to="/products" class="text-indigo-600 hover:text-indigo-700 font-semibold">
          去购物
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'

const ordersStore = useOrdersStore()

const statusTabs = [
  { value: 'all', label: '全部订单' },
  { value: 'pending', label: '待确认' },
  { value: 'confirmed', label: '已确认' },
  { value: 'processing', label: '处理中' },
  { value: 'shipped', label: '已发货' },
  { value: 'delivered', label: '已送达' },
  { value: 'cancelled', label: '已取消' },
]

const selectedStatus = ref('all')

const filteredOrders = computed(() => {
  if (selectedStatus.value === 'all') {
    return ordersStore.orders
  }
  return ordersStore.getOrdersByStatus(selectedStatus.value)
})

onMounted(async () => {
  await ordersStore.fetchOrders()
})

const getStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待确认',
    confirmed: '已确认',
    processing: '处理中',
    shipped: '已发货',
    delivered: '已送达',
    cancelled: '已取消',
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

const cancelOrder = async (id: number) => {
  if (!confirm('确定要取消此订单吗？')) return

  try {
    await ordersStore.cancelOrder(id)
    await ordersStore.fetchOrders()
  } catch (error) {
    alert('取消订单失败')
  }
}
</script>


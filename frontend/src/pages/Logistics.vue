<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">物流追踪</h1>

      <!-- Loading -->
      <div v-if="logisticsStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Shipments List -->
      <div v-else class="space-y-6">
        <div v-if="logisticsStore.shipments.length > 0">
          <div v-for="shipment in logisticsStore.shipments" :key="shipment.id" class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
            <!-- Header -->
            <div class="p-6 border-b">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">订单号: {{ shipment.order?.order_number }}</h3>
                  <p class="text-sm text-gray-600 mt-1">运单号: {{ shipment.tracking_number }}</p>
                </div>
                <div class="text-right">
                  <span :class="['inline-block px-4 py-2 rounded-lg font-semibold text-white', getStatusColor(shipment.status)]">
                    {{ getStatusLabel(shipment.status) }}
                  </span>
                </div>
              </div>

              <!-- Carrier Info -->
              <div class="flex items-center justify-between text-sm text-gray-600">
                <span>快递公司: {{ shipment.carrier }}</span>
                <span>预计送达: {{ formatDate(shipment.estimated_delivery) }}</span>
              </div>
            </div>

            <!-- Timeline -->
            <div class="p-6">
              <div v-if="shipment.tracking_events && shipment.tracking_events.length > 0" class="relative">
                <!-- Timeline -->
                <div class="space-y-6">
                  <div v-for="(event, index) in shipment.tracking_events" :key="event.id" class="flex gap-4">
                    <!-- Timeline dot -->
                    <div class="flex flex-col items-center">
                      <div :class="['w-4 h-4 rounded-full mt-1.5', index === 0 ? 'bg-green-500' : 'bg-gray-300']"></div>
                      <div v-if="index < shipment.tracking_events.length - 1" class="w-0.5 h-8 bg-gray-300 my-1"></div>
                    </div>

                    <!-- Event Content -->
                    <div class="pb-4">
                      <p class="font-semibold text-gray-900">{{ event.status }}</p>
                      <p class="text-sm text-gray-600 mt-1">{{ event.description }}</p>
                      <p v-if="event.location" class="text-xs text-gray-500 mt-1">📍 {{ event.location }}</p>
                      <p class="text-xs text-gray-500 mt-2">{{ formatDatetime(event.timestamp) }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-6 text-gray-600">
                暂无追踪信息
              </div>
            </div>

            <!-- Return Option -->
            <div v-if="shipment.status === 'delivered'" class="p-6 bg-gray-50 border-t">
              <button
                @click="requestReturn(shipment.order.id)"
                class="text-indigo-600 hover:text-indigo-700 font-semibold text-sm"
              >
                申请退货 →
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="bg-white rounded-lg shadow p-12 text-center">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-gray-600 text-lg mb-4">暂无物流信息</p>
          <RouterLink to="/orders" class="text-indigo-600 hover:text-indigo-700 font-semibold">
            查看订单
          </RouterLink>
        </div>
      </div>

      <!-- Return Requests -->
      <div v-if="logisticsStore.returns.length > 0" class="mt-12">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">退货申请</h2>
        <div class="space-y-4">
          <div v-for="ret in logisticsStore.returns" :key="ret.id" class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-semibold text-gray-900">订单号: {{ ret.order?.order_number }}</p>
                <p class="text-sm text-gray-600 mt-1">理由: {{ ret.reason }}</p>
              </div>
              <span :class="['px-3 py-1 rounded text-sm font-semibold', getReturnStatusColor(ret.status)]">
                {{ getReturnStatusLabel(ret.status) }}
              </span>
            </div>
            <p class="text-xs text-gray-500">申请时间: {{ formatDate(ret.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useLogisticsStore } from '@/stores/logistics'

const logisticsStore = useLogisticsStore()
const router = useRouter()

onMounted(async () => {
  await logisticsStore.fetchShipments()
  await logisticsStore.fetchReturns()
})

const getStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待发货',
    shipped: '已发货',
    in_transit: '运送中',
    delivered: '已送达',
    returned: '已退回',
  }
  return labels[status] || status
}

const getStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    pending: 'bg-yellow-500',
    shipped: 'bg-blue-500',
    in_transit: 'bg-purple-500',
    delivered: 'bg-green-500',
    returned: 'bg-gray-500',
  }
  return colors[status] || 'bg-gray-500'
}

const getReturnStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成',
  }
  return labels[status] || status
}

const getReturnStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const formatDatetime = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const requestReturn = (orderId: number) => {
  router.push(`/orders/${orderId}?tab=return`)
}
</script>

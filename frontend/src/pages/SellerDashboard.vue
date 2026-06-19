<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-6xl mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">卖家仪表板</h1>

      <!-- Loading -->
      <div v-if="sellersStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else-if="sellersStore.dashboard" class="space-y-8">
        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Total Revenue -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-semibold">总收入</p>
                <p class="text-2xl font-bold text-gray-900 mt-2">¥{{ sellersStore.profile?.total_revenue || 0 }}</p>
              </div>
              <div class="bg-indigo-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Total Orders -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-semibold">总订单</p>
                <p class="text-2xl font-bold text-gray-900 mt-2">{{ sellersStore.profile?.total_orders || 0 }}</p>
              </div>
              <div class="bg-green-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Average Rating -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-semibold">平均评分</p>
                <p class="text-2xl font-bold text-gray-900 mt-2">{{ (sellersStore.profile?.average_rating || 0).toFixed(1) }}⭐</p>
              </div>
              <div class="bg-yellow-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Response Time -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-semibold">平均回复时间</p>
                <p class="text-2xl font-bold text-gray-900 mt-2">{{ sellersStore.profile?.response_time || 0 }}h</p>
              </div>
              <div class="bg-blue-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Verification Status -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">卖家资质</h2>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 mb-2">认证状态</p>
              <div :class="['inline-block px-4 py-2 rounded-lg font-semibold text-white', getVerificationColor()]">
                {{ getVerificationLabel(sellersStore.profile?.verification_status) }}
              </div>
            </div>
            <div class="text-right space-y-2">
              <p class="text-gray-600 text-sm">店铺: {{ sellersStore.profile?.store?.name }}</p>
              <p class="text-gray-600 text-sm">账户: {{ sellersStore.profile?.user?.username }}</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <RouterLink
            to="/seller/withdrawals"
            class="bg-white hover:shadow-lg transition rounded-lg shadow p-6 text-center cursor-pointer"
          >
            <svg class="w-8 h-8 text-indigo-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">提现管理</h3>
            <p class="text-sm text-gray-600 mt-2">管理账户提现申请</p>
          </RouterLink>

          <RouterLink
            to="/seller/messages"
            class="bg-white hover:shadow-lg transition rounded-lg shadow p-6 text-center cursor-pointer"
          >
            <svg class="w-8 h-8 text-green-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">消息管理</h3>
            <p class="text-sm text-gray-600 mt-2">处理客户消息</p>
          </RouterLink>

          <RouterLink
            to="/account"
            class="bg-white hover:shadow-lg transition rounded-lg shadow p-6 text-center cursor-pointer"
          >
            <svg class="w-8 h-8 text-purple-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">账户设置</h3>
            <p class="text-sm text-gray-600 mt-2">修改个人资料</p>
          </RouterLink>
        </div>

        <!-- Recent Orders -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">最近订单</h2>
          <div v-if="sellersStore.dashboard.recent_orders.length > 0" class="space-y-3">
            <div v-for="order in sellersStore.dashboard.recent_orders.slice(0, 5)" :key="order.id" class="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <p class="font-semibold text-gray-900">{{ order.order_number }}</p>
                <p class="text-sm text-gray-600">¥{{ order.total_amount }}</p>
              </div>
              <span class="text-sm font-semibold text-indigo-600">{{ order.status }}</span>
            </div>
          </div>
          <div v-else class="text-center py-6">
            <p class="text-gray-600">暂无订单</p>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="bg-white rounded-lg shadow p-8 text-center">
        <p class="text-red-600 text-lg">{{ sellersStore.error || '加载失败' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSellersStore } from '@/stores/sellers'

const sellersStore = useSellersStore()

onMounted(async () => {
  await sellersStore.fetchDashboard()
})

const getVerificationLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待审核',
    verified: '已认证',
    rejected: '未通过',
  }
  return labels[status] || status
}

const getVerificationColor = () => {
  const status = sellersStore.profile?.verification_status
  const colors: { [key: string]: string } = {
    pending: 'bg-yellow-500',
    verified: 'bg-green-500',
    rejected: 'bg-red-500',
  }
  return colors[status || ''] || 'bg-gray-500'
}
</script>

<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center gap-4 mb-8">
        <RouterLink to="/seller/dashboard" class="text-indigo-600 hover:text-indigo-700">
          ← 返回仪表板
        </RouterLink>
        <h1 class="text-3xl font-bold text-gray-900">提现管理</h1>
      </div>

      <!-- Loading -->
      <div v-if="sellersStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else class="space-y-6">
        <!-- Account Balance -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">账户余额</h2>
          <div class="text-center">
            <p class="text-gray-600 text-sm">可提现余额</p>
            <p class="text-5xl font-bold text-indigo-600 mt-4">¥{{ sellersStore.profile?.total_revenue || 0 }}</p>
            <p class="text-gray-600 text-sm mt-2">账户认证状态: {{ getVerificationLabel(sellersStore.profile?.verification_status) }}</p>
          </div>
        </div>

        <!-- Withdrawal Request Form -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-6">新建提现申请</h2>

          <!-- Error Alert -->
          <div v-if="error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-700">{{ error }}</p>
          </div>

          <!-- Success Alert -->
          <div v-if="success" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-700">提现申请已提交！</p>
          </div>

          <form @submit.prevent="submitWithdrawal" class="space-y-4">
            <!-- Amount -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">提现金额 (¥)</label>
              <input
                v-model.number="withdrawalForm.amount"
                type="number"
                min="100"
                :max="sellersStore.profile?.total_revenue || 0"
                step="1"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                placeholder="请输入提现金额"
              />
              <p class="text-xs text-gray-600 mt-1">最低提现金额: 100元</p>
            </div>

            <!-- Note -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">备注 (可选)</label>
              <textarea
                v-model="withdrawalForm.note"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                placeholder="输入提现备注..."
              ></textarea>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="submitting"
              class="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition"
            >
              {{ submitting ? '提交中...' : '提交提现申请' }}
            </button>
          </form>
        </div>

        <!-- Withdrawal History -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">提现历史</h2>

          <div v-if="withdrawals.length > 0" class="space-y-3">
            <div v-for="withdrawal in withdrawals" :key="withdrawal.id" class="p-4 bg-gray-50 rounded-lg border">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <p class="font-semibold text-gray-900">¥{{ withdrawal.amount }}</p>
                  <p class="text-xs text-gray-600">{{ formatDate(withdrawal.created_at) }}</p>
                </div>
                <span :class="['px-3 py-1 rounded text-sm font-semibold', getStatusColor(withdrawal.status)]">
                  {{ getStatusLabel(withdrawal.status) }}
                </span>
              </div>
              <p v-if="withdrawal.note" class="text-sm text-gray-600">备注: {{ withdrawal.note }}</p>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <p class="text-gray-600">暂无提现历史</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSellersStore } from '@/stores/sellers'

const sellersStore = useSellersStore()

const withdrawalForm = ref({
  amount: 0,
  note: '',
})

const submitting = ref(false)
const error = ref('')
const success = ref(false)
const withdrawals = ref<any[]>([])

onMounted(async () => {
  await sellersStore.fetchDashboard()
  // Mock withdrawal history - in real app, would fetch from API
  withdrawals.value = [
    {
      id: 1,
      amount: 1000,
      status: 'completed',
      created_at: '2026-06-15T10:00:00Z',
      note: '月度结算',
    },
    {
      id: 2,
      amount: 500,
      status: 'pending',
      created_at: '2026-06-18T14:30:00Z',
      note: '',
    },
  ]
})

const submitWithdrawal = async () => {
  error.value = ''
  success.value = false

  if (!withdrawalForm.value.amount || withdrawalForm.value.amount < 100) {
    error.value = '提现金额必须不少于 100 元'
    return
  }

  if (withdrawalForm.value.amount > (sellersStore.profile?.total_revenue || 0)) {
    error.value = '提现金额不能超过账户余额'
    return
  }

  try {
    submitting.value = true
    await sellersStore.requestWithdrawal(
      withdrawalForm.value.amount,
      withdrawalForm.value.note
    )
    success.value = true
    withdrawalForm.value = { amount: 0, note: '' }
    await sellersStore.fetchDashboard()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '提现申请失败'
  } finally {
    submitting.value = false
  }
}

const getStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待处理',
    completed: '已完成',
    rejected: '已拒绝',
  }
  return labels[status] || status
}

const getStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getVerificationLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待审核',
    verified: '已认证',
    rejected: '未通过',
  }
  return labels[status] || status
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
</script>

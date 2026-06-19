<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center gap-4 mb-8">
        <RouterLink to="/seller/dashboard" class="text-indigo-600 hover:text-indigo-700">
          ← 返回仪表板
        </RouterLink>
        <h1 class="text-3xl font-bold text-gray-900">消息管理</h1>
      </div>

      <!-- Loading -->
      <div v-if="sellersStore.loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else class="space-y-6">
        <!-- Message Count -->
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-gray-600 text-sm">待处理消息</p>
          <p class="text-3xl font-bold text-indigo-600">{{ unreadCount }}</p>
        </div>

        <!-- Messages List / Detail -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Messages List -->
          <div class="md:col-span-1 bg-white rounded-lg shadow overflow-hidden">
            <div class="p-4 border-b">
              <h2 class="font-semibold text-gray-900">消息</h2>
            </div>

            <div class="divide-y max-h-96 overflow-y-auto">
              <button
                v-for="message in messages"
                :key="message.id"
                @click="selectMessage(message)"
                :class="[
                  'w-full text-left p-4 hover:bg-gray-50 transition border-l-4',
                  selectedMessage?.id === message.id ? 'bg-indigo-50 border-indigo-600' : 'border-transparent'
                ]"
              >
                <p class="font-semibold text-gray-900 text-sm truncate">{{ message.customer_name }}</p>
                <p class="text-xs text-gray-600 truncate mt-1">{{ message.content }}</p>
                <p class="text-xs text-gray-500 mt-2">{{ formatDate(message.created_at) }}</p>
              </button>

              <div v-if="messages.length === 0" class="p-4 text-center">
                <p class="text-gray-600 text-sm">暂无消息</p>
              </div>
            </div>
          </div>

          <!-- Message Detail -->
          <div class="md:col-span-2 bg-white rounded-lg shadow p-6">
            <div v-if="selectedMessage" class="space-y-4">
              <!-- Message Header -->
              <div class="pb-4 border-b">
                <h3 class="text-lg font-semibold text-gray-900">{{ selectedMessage.customer_name }}</h3>
                <p class="text-sm text-gray-600">{{ formatDate(selectedMessage.created_at) }}</p>
              </div>

              <!-- Original Message -->
              <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm text-gray-600 mb-2">客户消息:</p>
                <p class="text-gray-900">{{ selectedMessage.content }}</p>
              </div>

              <!-- Conversation History -->
              <div v-if="selectedMessage.replies && selectedMessage.replies.length > 0" class="space-y-3">
                <div v-for="reply in selectedMessage.replies" :key="reply.id" :class="['p-3 rounded-lg', reply.is_seller ? 'bg-indigo-50 text-right' : 'bg-gray-50']">
                  <p v-if="reply.is_seller" class="text-xs text-indigo-600 font-semibold mb-1">我的回复</p>
                  <p v-else class="text-xs text-gray-600 font-semibold mb-1">{{ selectedMessage.customer_name }}</p>
                  <p class="text-sm text-gray-900">{{ reply.content }}</p>
                  <p class="text-xs text-gray-500 mt-2">{{ formatDate(reply.created_at) }}</p>
                </div>
              </div>

              <!-- Reply Form -->
              <div v-if="!selectedMessage.is_resolved" class="pt-4 border-t">
                <p class="text-sm font-semibold text-gray-900 mb-2">回复消息</p>
                <div class="space-y-2">
                  <textarea
                    v-model="replyForm.content"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                    placeholder="输入回复内容..."
                  ></textarea>
                  <button
                    @click="submitReply"
                    :disabled="replySubmitting || !replyForm.content"
                    class="w-full px-3 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition"
                  >
                    {{ replySubmitting ? '发送中...' : '发送回复' }}
                  </button>
                </div>
              </div>

              <div v-else class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-green-700 text-sm">此消息已标记为已解决</p>
              </div>
            </div>

            <div v-else class="text-center py-12">
              <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
              <p class="text-gray-600">选择一条消息查看详情</p>
            </div>
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

const selectedMessage = ref<any>(null)
const messages = ref<any[]>([])
const replyForm = ref({ content: '' })
const replySubmitting = ref(false)

const unreadCount = computed(() => {
  return messages.value.filter(m => !m.is_read).length
})

onMounted(async () => {
  await sellersStore.fetchDashboard()
  // Mock messages - in real app, would fetch from API
  messages.value = [
    {
      id: 1,
      customer_name: '张三',
      content: '请问这个产品有保修期吗?',
      created_at: '2026-06-19T10:00:00Z',
      is_read: true,
      is_resolved: false,
      replies: [
        {
          id: 1,
          content: '有的，我们提供一年的保修期',
          created_at: '2026-06-19T10:15:00Z',
          is_seller: true,
        },
        {
          id: 2,
          content: '谢谢！那我就下单了',
          created_at: '2026-06-19T10:20:00Z',
          is_seller: false,
        },
      ],
    },
    {
      id: 2,
      customer_name: '李四',
      content: '我想退货，能否协助?',
      created_at: '2026-06-19T14:30:00Z',
      is_read: false,
      is_resolved: false,
      replies: [],
    },
    {
      id: 3,
      customer_name: '王五',
      content: '产品已收到，非常满意!',
      created_at: '2026-06-18T16:45:00Z',
      is_read: true,
      is_resolved: true,
      replies: [
        {
          id: 3,
          content: '感谢您的信任和支持！欢迎再次购买',
          created_at: '2026-06-18T17:00:00Z',
          is_seller: true,
        },
      ],
    },
  ]
  if (messages.value.length > 0) {
    selectMessage(messages.value[0])
  }
})

const selectMessage = (message: any) => {
  selectedMessage.value = message
  replyForm.value = { content: '' }
}

const submitReply = async () => {
  if (!selectedMessage.value || !replyForm.value.content.trim()) return

  try {
    replySubmitting.value = true
    await sellersStore.replyToMessage(
      selectedMessage.value.id,
      replyForm.value.content
    )
    replyForm.value.content = ''
    // In real app, would refresh message detail
  } catch (err) {
    console.error('Failed to send reply:', err)
  } finally {
    replySubmitting.value = false
  }
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

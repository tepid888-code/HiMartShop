<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-3xl font-bold text-gray-900">消息中心</h1>
        <button
          v-if="notificationsStore.unreadCount > 0"
          @click="markAllAsRead"
          class="px-4 py-2 text-sm text-indigo-600 hover:text-indigo-700 font-semibold border border-indigo-600 rounded-lg"
        >
          全部标记已读
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex gap-4 mb-8 border-b">
        <button
          @click="selectedTab = 'all'"
          :class="['px-4 py-2 font-semibold border-b-2 transition', selectedTab === 'all' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          全部 ({{ notificationsStore.notifications.length }})
        </button>
        <button
          @click="selectedTab = 'unread'"
          :class="['px-4 py-2 font-semibold border-b-2 transition', selectedTab === 'unread' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          未读 ({{ notificationsStore.unreadCount }})
        </button>
        <button
          @click="selectedTab = 'settings'"
          :class="['px-4 py-2 font-semibold border-b-2 transition', selectedTab === 'settings' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          设置
        </button>
      </div>

      <!-- Loading -->
      <div v-if="notificationsStore.loading && selectedTab !== 'settings'" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Notifications List -->
      <div v-else-if="selectedTab !== 'settings'" class="space-y-3">
        <div v-if="displayedNotifications.length > 0">
          <div
            v-for="notification in displayedNotifications"
            :key="notification.id"
            @click="markAsRead(notification.id)"
            :class="[
              'bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition',
              !notification.is_read ? 'border-l-4 border-indigo-600' : ''
            ]"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900">{{ notification.title }}</h3>
                <p class="text-gray-600 mt-2">{{ notification.message }}</p>
              </div>
              <div class="text-right ml-4">
                <span :class="['inline-block px-3 py-1 rounded-full text-xs font-semibold', getPriorityColor(notification.priority)]">
                  {{ getPriorityLabel(notification.priority) }}
                </span>
              </div>
            </div>
            <div class="flex items-center justify-between mt-3 text-sm">
              <span class="text-gray-500">{{ getTypeLabel(notification.type) }}</span>
              <span class="text-gray-500">{{ formatDate(notification.created_at) }}</span>
            </div>
            <div v-if="!notification.is_read" class="mt-3">
              <span class="inline-block px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded">未读</span>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-lg shadow p-8 text-center">
          <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <p class="text-gray-600 text-lg">{{ selectedTab === 'unread' ? '暂无未读消息' : '暂无消息' }}</p>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-else class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">通知偏好</h2>

        <div v-if="notificationsStore.preferences.length > 0" class="space-y-4">
          <div v-for="pref in notificationsStore.preferences" :key="pref.channel" class="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p class="font-semibold text-gray-900">{{ getChannelLabel(pref.channel) }}</p>
              <p class="text-sm text-gray-600 mt-1">{{ getChannelDescription(pref.channel) }}</p>
            </div>
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="pref.enabled"
                @change="updatePreference(pref.channel, !pref.enabled)"
                class="w-5 h-5 text-indigo-600 rounded"
              />
              <span class="text-sm text-gray-600">{{ pref.enabled ? '已启用' : '已禁用' }}</span>
            </label>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-600">
          正在加载偏好设置...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'

const notificationsStore = useNotificationsStore()
const selectedTab = ref('all')

const displayedNotifications = computed(() => {
  if (selectedTab.value === 'unread') {
    return notificationsStore.unreadNotifications
  }
  return notificationsStore.notifications
})

onMounted(async () => {
  await notificationsStore.fetchNotifications()
  await notificationsStore.fetchUnreadCount()
  await notificationsStore.fetchPreferences()
})

const markAsRead = async (id: number) => {
  try {
    await notificationsStore.markAsRead(id)
  } catch (err) {
    console.error('Failed to mark as read:', err)
  }
}

const markAllAsRead = async () => {
  try {
    await notificationsStore.markAllAsRead()
  } catch (err) {
    console.error('Failed to mark all as read:', err)
  }
}

const updatePreference = async (channel: string, enabled: boolean) => {
  try {
    await notificationsStore.updatePreferences({
      [channel]: enabled,
    })
  } catch (err) {
    console.error('Failed to update preference:', err)
  }
}

const getPriorityLabel = (priority: string) => {
  const labels: { [key: string]: string } = {
    high: '重要',
    medium: '普通',
    low: '信息',
  }
  return labels[priority] || priority
}

const getPriorityColor = (priority: string) => {
  const colors: { [key: string]: string } = {
    high: 'bg-red-100 text-red-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-blue-100 text-blue-700',
  }
  return colors[priority] || 'bg-gray-100 text-gray-700'
}

const getTypeLabel = (type: string) => {
  const labels: { [key: string]: string } = {
    order: '订单提醒',
    payment: '支付提醒',
    shipment: '物流提醒',
    system: '系统消息',
  }
  return labels[type] || type
}

const getChannelLabel = (channel: string) => {
  const labels: { [key: string]: string } = {
    email: '邮件通知',
    sms: '短信通知',
    push: '推送通知',
  }
  return labels[channel] || channel
}

const getChannelDescription = (channel: string) => {
  const descriptions: { [key: string]: string } = {
    email: '通过邮件接收消息',
    sms: '通过短信接收消息',
    push: '通过应用推送接收消息',
  }
  return descriptions[channel] || ''
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

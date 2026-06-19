import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsAPI } from '@/api/notifications'

interface Notification {
  id: number
  type: string
  title: string
  message: string
  priority: string
  is_read: boolean
  created_at: string
  data?: any
}

interface NotificationPreference {
  channel: string
  enabled: boolean
}

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const preferences = ref<NotificationPreference[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.is_read)
  })

  const fetchNotifications = async (page: number = 1) => {
    try {
      loading.value = true
      const response = await notificationsAPI.getNotifications({ page, page_size: 20 })
      notifications.value = response.data.results || response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取通知失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await notificationsAPI.getUnreadCount()
      unreadCount.value = response.data.unread_count || 0
    } catch (err: any) {
      console.error('Failed to fetch unread count:', err)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      await notificationsAPI.markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '标记失败'
      throw err
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead()
      notifications.value.forEach(n => {
        n.is_read = true
      })
      unreadCount.value = 0
    } catch (err: any) {
      error.value = err.response?.data?.detail || '标记失败'
      throw err
    }
  }

  const fetchPreferences = async () => {
    try {
      const response = await notificationsAPI.getPreferences()
      preferences.value = response.data
    } catch (err: any) {
      console.error('Failed to fetch preferences:', err)
    }
  }

  const updatePreferences = async (prefs: any) => {
    try {
      await notificationsAPI.updatePreferences(prefs)
      await fetchPreferences()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新失败'
      throw err
    }
  }

  return {
    notifications,
    unreadNotifications,
    unreadCount,
    preferences,
    loading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    fetchPreferences,
    updatePreferences,
  }
})

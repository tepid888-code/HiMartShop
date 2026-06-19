import api from './client'

export const notificationsAPI = {
  // Notifications
  getNotifications: (params: any) => api.get('/notifications/notifications/', { params }),
  getUnreadCount: () => api.get('/notifications/notifications/unread_count/'),

  // Mark as read
  markAsRead: (id: number) => api.post(`/notifications/notifications/${id}/mark_as_read/`),
  markAllAsRead: () => api.post('/notifications/notifications/mark_all_as_read/'),

  // Preferences
  getPreferences: () => api.get('/notifications/preferences/'),
  updatePreferences: (data: any) => api.patch('/notifications/preferences/', data),
}

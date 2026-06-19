from django.contrib import admin
from apps.notifications.models import Notification, NotificationTemplate, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'notification_type')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'in_app_notifications', 'email_notifications', 'sms_notifications')
    list_filter = ('in_app_notifications', 'email_notifications', 'sms_notifications')
    search_fields = ('user__username',)

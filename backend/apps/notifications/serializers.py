from rest_framework import serializers
from apps.notifications.models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'notification_type_display', 'title', 'message',
                  'priority', 'priority_display', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['in_app_notifications', 'email_notifications', 'sms_notifications',
                  'order_notifications', 'payment_notifications', 'shipping_notifications',
                  'promotion_notifications', 'wishlist_notifications', 'promotion_frequency']

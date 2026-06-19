from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.notifications.models import Notification, NotificationPreference

class NotificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # 创建测试通知
        Notification.objects.create(
            user=self.user,
            notification_type='order_confirmed',
            title='Order Confirmed',
            message='Your order has been confirmed'
        )

        Notification.objects.create(
            user=self.user,
            notification_type='payment_received',
            title='Payment Received',
            message='Payment has been received',
            is_read=True
        )

    def test_get_notifications(self):
        """测试获取通知列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_unread_count(self):
        """测试获取未读通知数量"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_as_read(self):
        """测试标记为已读"""
        self.client.force_authenticate(user=self.user)
        notification = Notification.objects.filter(is_read=False).first()
        response = self.client.post(f'/api/notifications/notifications/{notification.id}/mark_as_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_read'])

    def test_notification_preference(self):
        """测试通知偏好"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('in_app_notifications', response.data)

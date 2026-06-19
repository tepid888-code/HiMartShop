from django.db import models
from apps.users.models import User

class Notification(models.Model):
    """通知"""
    NOTIFICATION_TYPE_CHOICES = [
        ('order_confirmed', 'Order Confirmed'),
        ('payment_received', 'Payment Received'),
        ('shipped', 'Order Shipped'),
        ('delivery_attempt', 'Delivery Attempted'),
        ('delivered', 'Order Delivered'),
        ('refund_approved', 'Refund Approved'),
        ('refund_processed', 'Refund Processed'),
        ('promotion', 'Promotion Alert'),
        ('wishlist_alert', 'Wishlist Alert'),
        ('restock', 'Product Restock'),
        ('system', 'System Message'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # 关联对象
    related_order_id = models.IntegerField(null=True, blank=True)
    related_product_id = models.IntegerField(null=True, blank=True)

    # 状态
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # 发送状态
    is_sent = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    is_sent_sms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class NotificationTemplate(models.Model):
    """通知模板"""
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=50, unique=True, choices=Notification.NOTIFICATION_TYPE_CHOICES)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class NotificationPreference(models.Model):
    """用户通知偏好"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')

    # 通知渠道
    in_app_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    # 通知类型偏好
    order_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    shipping_notifications = models.BooleanField(default=True)
    promotion_notifications = models.BooleanField(default=True)
    wishlist_notifications = models.BooleanField(default=True)

    # 通知频率
    FREQUENCY_CHOICES = [
        ('instant', 'Instant'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    promotion_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preference for {self.user.username}"

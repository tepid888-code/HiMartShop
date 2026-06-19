from django.db import models

class SiteConfiguration(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Site Configurations'

    def __str__(self):
        return self.key

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('product', 'Product'),
        ('system', 'System'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

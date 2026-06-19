from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.stores.models import Store

class SellerProfile(models.Model):
    """卖家个人资料"""
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='seller_profile')

    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)

    # 商家统计
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_products = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    followers = models.IntegerField(default=0)

    # 认证信息
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Seller: {self.user.username}"

class SellerStats(models.Model):
    """卖家统计（每日更新）"""
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()

    # 销售数据
    orders = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 用户交互
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    favorites = models.IntegerField(default=0)

    class Meta:
        unique_together = ('seller', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.seller.user.username} - {self.date}"

class SellerWithdrawal(models.Model):
    """卖家提现"""
    WITHDRAWAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=WITHDRAWAL_STATUS_CHOICES, default='pending')

    bank_account = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)

    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Withdrawal: {self.seller.user.username} - {self.amount}"

class SellerMessage(models.Model):
    """商家消息"""
    MESSAGE_TYPE_CHOICES = [
        ('inquiry', 'Product Inquiry'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('other', 'Other'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='messages')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    reply = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.customer.username if self.customer else 'Unknown'}"

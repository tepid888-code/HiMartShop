from django.db import models
from apps.users.models import User

class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='store_banners/', null=True, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_products = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class StoreAdmin(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='admins')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[
            ('owner', 'Owner'),
            ('manager', 'Manager'),
            ('staff', 'Staff'),
        ],
        default='staff'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.store.name}"

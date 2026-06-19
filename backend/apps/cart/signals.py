from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from apps.cart.models import Cart

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """在用户创建时自动创建购物车"""
    if created:
        Cart.objects.get_or_create(user=instance)

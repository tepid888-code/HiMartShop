from django.contrib import admin
from .models import User, UserProfile, Address, Wishlist

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_seller', 'is_verified', 'created_at')
    list_filter = ('is_seller', 'is_verified', 'created_at')
    search_fields = ('username', 'email', 'phone')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_purchases', 'total_spent')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'country')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

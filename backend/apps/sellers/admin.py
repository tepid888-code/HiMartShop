from django.contrib import admin
from apps.sellers.models import SellerProfile, SellerStats, SellerWithdrawal, SellerMessage

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_status', 'is_active', 'average_rating', 'total_sales')
    list_filter = ('verification_status', 'is_active')
    search_fields = ('user__username', 'store__name')

@admin.register(SellerStats)
class SellerStatsAdmin(admin.ModelAdmin):
    list_display = ('seller', 'date', 'orders', 'revenue')
    list_filter = ('date',)
    search_fields = ('seller__user__username',)

@admin.register(SellerWithdrawal)
class SellerWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('seller', 'amount', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('seller__user__username',)

@admin.register(SellerMessage)
class SellerMessageAdmin(admin.ModelAdmin):
    list_display = ('seller', 'customer', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read')
    search_fields = ('seller__user__username', 'customer__username')

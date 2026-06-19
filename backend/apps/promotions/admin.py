from django.contrib import admin
from apps.promotions.models import Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'max_uses',
                   'current_uses', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('current_uses', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'min_purchase', 'max_discount')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'current_uses', 'max_uses_per_user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user_id', 'used_at')
    list_filter = ('used_at', 'coupon')
    search_fields = ('coupon__code', 'user_id')
    readonly_fields = ('used_at',)

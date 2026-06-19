from django.contrib import admin
from .models import Payment, PaymentTransaction, RefundRequest, PaymentMethod

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'is_default', 'is_active')
    list_filter = ('method', 'is_active')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__order_number')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')

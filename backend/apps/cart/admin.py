from django.contrib import admin
from apps.cart.models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'get_item_count', 'get_total')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items'

    def get_total(self, obj):
        return f"KES {obj.get_total()}"
    get_total.short_description = 'Total'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'get_subtotal', 'added_at')
    list_filter = ('added_at', 'updated_at')
    search_fields = ('product__name', 'cart__user__username')
    readonly_fields = ('added_at', 'updated_at')

    def get_subtotal(self, obj):
        return f"KES {obj.get_subtotal()}"
    get_subtotal.short_description = 'Subtotal'

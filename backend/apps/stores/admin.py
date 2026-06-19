from django.contrib import admin
from .models import Store, StoreAdmin as StoreAdminModel

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(StoreAdminModel)
class StoreAdminAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'role', 'added_at')
    list_filter = ('role',)

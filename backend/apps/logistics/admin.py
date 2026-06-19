from django.contrib import admin
from apps.logistics.models import (
    ShippingCarrier, ShippingMethod, Shipment, TrackingEvent, ReturnRequest
)

@admin.register(ShippingCarrier)
class ShippingCarrierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'carrier_type', 'is_active')
    list_filter = ('is_active', 'carrier_type')
    search_fields = ('name', 'code')

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'speed', 'base_cost', 'carrier', 'is_active')
    list_filter = ('speed', 'is_active')
    search_fields = ('name',)

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order', 'carrier', 'status', 'shipped_at', 'delivered_at')
    list_filter = ('status', 'created_at', 'carrier')
    search_fields = ('tracking_number', 'order__order_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'event_type', 'location', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('shipment__tracking_number', 'location')

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'reason', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('shipment__tracking_number', 'reason')

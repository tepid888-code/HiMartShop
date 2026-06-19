from rest_framework import serializers
from apps.logistics.models import (
    ShippingCarrier, ShippingMethod, Shipment, TrackingEvent, ReturnRequest
)

class ShippingCarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCarrier
        fields = ['id', 'name', 'code', 'carrier_type', 'is_active']

class ShippingMethodSerializer(serializers.ModelSerializer):
    carrier_name = serializers.CharField(source='carrier.name', read_only=True)

    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'speed', 'base_cost', 'carrier', 'carrier_name', 'is_active']

class TrackingEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = TrackingEvent
        fields = ['id', 'event_type', 'event_type_display', 'location', 'description', 'timestamp']

class ShipmentSerializer(serializers.ModelSerializer):
    tracking_events = TrackingEventSerializer(many=True, read_only=True)
    carrier_name = serializers.CharField(source='carrier.name', read_only=True)
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shipment
        fields = ['id', 'order', 'carrier', 'carrier_name', 'shipping_method', 'shipping_method_name',
                  'tracking_number', 'status', 'status_display', 'shipping_cost',
                  'shipped_at', 'delivered_at', 'expected_delivery',
                  'tracking_events', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'tracking_events']

class ReturnRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = ['id', 'shipment', 'reason', 'reason_display', 'description', 'status', 'status_display',
                  'return_tracking_number', 'created_at', 'approved_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'approved_at', 'completed_at']

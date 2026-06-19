from rest_framework import serializers
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'subtotal', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'status', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'status', 'status_display',
                  'payment_status', 'payment_status_display', 'total_amount',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'order_number', 'user', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'store', 'status', 'status_display',
                  'payment_status', 'payment_status_display', 'items', 'status_history',
                  'subtotal', 'tax', 'shipping_cost', 'discount', 'total_amount',
                  'shipping_address', 'billing_address', 'notes',
                  'created_at', 'updated_at', 'shipped_at', 'delivered_at']
        read_only_fields = ['id', 'order_number', 'user', 'store', 'items', 'status_history',
                           'subtotal', 'tax', 'discount', 'total_amount', 'created_at',
                           'updated_at', 'shipped_at', 'delivered_at']


class OrderCreateSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of {product_id, quantity}'
    )
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    billing_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError('Order must contain at least one item.')
        return value

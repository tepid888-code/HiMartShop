from django.db import models
from django.core.validators import MinValueValidator
from apps.orders.models import Order

class ShippingCarrier(models.Model):
    """物流公司"""
    CARRIER_CHOICES = [
        ('safaricom', 'Safaricom Logistics'),
        ('jne', 'JNE Express'),
        ('ups', 'UPS'),
        ('dhl', 'DHL'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    carrier_type = models.CharField(max_length=50, choices=CARRIER_CHOICES, default='other')
    is_active = models.BooleanField(default=True)
    tracking_url_template = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ShippingMethod(models.Model):
    """配送方式"""
    SHIPPING_SPEED_CHOICES = [
        ('standard', 'Standard (5-7 days)'),
        ('express', 'Express (2-3 days)'),
        ('overnight', 'Overnight'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    speed = models.CharField(max_length=20, choices=SHIPPING_SPEED_CHOICES)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['base_cost']

    def __str__(self):
        return f"{self.name} - KES {self.base_cost}"

class Shipment(models.Model):
    """发货单"""
    SHIPMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True, blank=True)

    tracking_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='pending')

    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment {self.tracking_number} - {self.order.order_number}"

class TrackingEvent(models.Model):
    """物流追踪事件"""
    EVENT_TYPE_CHOICES = [
        ('created', 'Created'),
        ('picked', 'Picked Up'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('attempted', 'Delivery Attempted'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
        ('customs', 'Customs Clearance'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.get_event_type_display()}"

class ReturnRequest(models.Model):
    """退货请求"""
    RETURN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('inspected', 'Inspected'),
        ('refunded', 'Refunded'),
    ]

    RETURN_REASON_CHOICES = [
        ('quality', 'Quality Issue'),
        ('damaged', 'Damaged'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('defective', 'Defective'),
        ('other', 'Other'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='returns')
    reason = models.CharField(max_length=50, choices=RETURN_REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='pending')

    return_tracking_number = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Return for {self.shipment.order.order_number}"

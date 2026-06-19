from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.orders.models import Order, OrderStatus
from apps.payment.models import Payment
from apps.logistics.models import Shipment, TrackingEvent
from apps.notifications.models import Notification

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    """订单创建时发送通知"""
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='order_confirmed',
            title='订单确认',
            message=f'您的订单 #{instance.order_number} 已确认，总金额: KES {instance.total_amount}',
            related_order_id=instance.id,
            priority='high'
        )

@receiver(post_save, sender=Payment)
def create_payment_notification(sender, instance, created, update_fields, **kwargs):
    """支付成功时发送通知"""
    if not created and update_fields and 'status' in update_fields:
        if instance.status == 'success':
            Notification.objects.create(
                user=instance.user,
                notification_type='payment_received',
                title='支付成功',
                message=f'订单 #{instance.order.order_number} 的支付已成功，金额: KES {instance.amount}',
                related_order_id=instance.order_id,
                priority='high'
            )

@receiver(post_save, sender=Shipment)
def create_shipment_notification(sender, instance, update_fields, **kwargs):
    """发货单状态变化时发送通知"""
    if update_fields and 'status' in update_fields:
        if instance.status == 'shipped':
            Notification.objects.create(
                user=instance.order.user,
                notification_type='shipped',
                title='订单已发货',
                message=f'您的订单 #{instance.order.order_number} 已发货，追踪号: {instance.tracking_number}',
                related_order_id=instance.order_id,
                priority='high'
            )
        elif instance.status == 'delivered':
            Notification.objects.create(
                user=instance.order.user,
                notification_type='delivered',
                title='订单已送达',
                message=f'您的订单 #{instance.order.order_number} 已成功送达',
                related_order_id=instance.order_id,
                priority='high'
            )

@receiver(post_save, sender=TrackingEvent)
def create_tracking_notification(sender, instance, created, **kwargs):
    """追踪事件时发送通知"""
    if created and instance.event_type in ['out_for_delivery', 'attempted', 'delivered']:
        shipment = instance.shipment
        message_map = {
            'out_for_delivery': '您的订单正在送达途中',
            'attempted': '送货员已尝试送达您的订单',
            'delivered': '您的订单已成功送达'
        }
        Notification.objects.create(
            user=shipment.order.user,
            notification_type='shipping_notifications',
            title='物流更新',
            message=f"{message_map.get(instance.event_type, instance.description)} - {instance.location}",
            related_order_id=shipment.order_id,
            priority='medium'
        )

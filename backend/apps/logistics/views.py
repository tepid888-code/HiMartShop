from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import uuid

from apps.logistics.models import (
    ShippingCarrier, ShippingMethod, Shipment, TrackingEvent, ReturnRequest
)
from apps.logistics.serializers import (
    ShippingCarrierSerializer, ShippingMethodSerializer, ShipmentSerializer,
    TrackingEventSerializer, ReturnRequestSerializer
)
from apps.orders.models import Order

class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """配送方式视图"""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None

class ShipmentViewSet(viewsets.ModelViewSet):
    """发货单视图"""
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(order__user=self.request.user)\
            .select_related('carrier', 'shipping_method', 'order')\
            .prefetch_related('tracking_events')\
            .order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """创建发货单"""
        order_id = request.data.get('order_id')
        shipping_method_id = request.data.get('shipping_method_id')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
        except ShippingMethod.DoesNotExist:
            return Response(
                {'error': 'Shipping method not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.shipment:
            return Response(
                {'error': 'Order already has a shipment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建发货单
        tracking_number = f"TRACK-{uuid.uuid4().hex[:12].upper()}"
        shipment = Shipment.objects.create(
            order=order,
            shipping_method=shipping_method,
            carrier=shipping_method.carrier,
            tracking_number=tracking_number,
            shipping_cost=shipping_method.base_cost,
            status='pending'
        )

        # 创建初始追踪事件
        TrackingEvent.objects.create(
            shipment=shipment,
            event_type='created',
            description='Shipment created',
            timestamp=timezone.now()
        )

        serializer = self.get_serializer(shipment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_shipped(self, request, pk=None):
        """标记为已发货"""
        shipment = self.get_object()

        shipment.status = 'shipped'
        shipment.shipped_at = timezone.now()
        shipment.save()

        TrackingEvent.objects.create(
            shipment=shipment,
            event_type='shipped',
            description='Package has been shipped',
            timestamp=timezone.now()
        )

        shipment.order.status = 'shipped'
        shipment.order.save()

        return Response(
            ShipmentSerializer(shipment).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """标记为已送达"""
        shipment = self.get_object()

        shipment.status = 'delivered'
        shipment.delivered_at = timezone.now()
        shipment.save()

        TrackingEvent.objects.create(
            shipment=shipment,
            event_type='delivered',
            description='Package delivered successfully',
            timestamp=timezone.now()
        )

        shipment.order.status = 'delivered'
        shipment.order.save()

        return Response(
            ShipmentSerializer(shipment).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def update_tracking(self, request, pk=None):
        """更新追踪信息"""
        shipment = self.get_object()

        event_type = request.data.get('event_type')
        location = request.data.get('location', '')
        description = request.data.get('description', '')

        if not event_type:
            return Response(
                {'error': 'Event type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建追踪事件
        tracking_event = TrackingEvent.objects.create(
            shipment=shipment,
            event_type=event_type,
            location=location,
            description=description,
            timestamp=timezone.now()
        )

        # 根据事件类型更新发货单状态
        if event_type == 'delivered':
            shipment.status = 'delivered'
            shipment.delivered_at = timezone.now()
            shipment.order.status = 'delivered'
            shipment.order.save()
        elif event_type == 'shipped':
            shipment.status = 'shipped'
            shipment.shipped_at = timezone.now()
            shipment.order.status = 'shipped'
            shipment.order.save()
        elif event_type == 'in_transit':
            shipment.status = 'in_transit'
        elif event_type == 'out_for_delivery':
            shipment.status = 'out_for_delivery'

        shipment.save()

        return Response(
            TrackingEventSerializer(tracking_event).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """获取追踪信息"""
        shipment = self.get_object()
        serializer = self.get_serializer(shipment)
        return Response(serializer.data)

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """退货请求视图"""
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReturnRequest.objects.filter(shipment__order__user=self.request.user)\
            .select_related('shipment')\
            .order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_return(self, request):
        """创建退货请求"""
        shipment_id = request.data.get('shipment_id')
        reason = request.data.get('reason')
        description = request.data.get('description', '')

        try:
            shipment = Shipment.objects.get(id=shipment_id, order__user=request.user)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not reason:
            return Response(
                {'error': 'Return reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否已有退货请求
        existing_return = ReturnRequest.objects.filter(shipment=shipment).first()
        if existing_return:
            return Response(
                {'error': 'Return request already exists for this shipment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return_request = ReturnRequest.objects.create(
            shipment=shipment,
            reason=reason,
            description=description,
            status='pending'
        )

        return Response(
            ReturnRequestSerializer(return_request).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """批准退货请求（管理员操作）"""
        return_request = self.get_object()

        if return_request.status != 'pending':
            return Response(
                {'error': 'Only pending return requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return_request.status = 'approved'
        return_request.approved_at = timezone.now()
        return_request.save()

        return Response(
            ReturnRequestSerializer(return_request).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝退货请求（管理员操作）"""
        return_request = self.get_object()

        if return_request.status != 'pending':
            return Response(
                {'error': 'Only pending return requests can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return_request.status = 'rejected'
        return_request.save()

        return Response(
            ReturnRequestSerializer(return_request).data,
            status=status.HTTP_200_OK
        )

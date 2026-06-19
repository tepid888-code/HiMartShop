from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
import uuid

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.orders.serializers import (
    OrderSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderStatusSerializer
)
from apps.products.models import Product
from apps.users.models import Address
from apps.cart.models import Cart


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)\
            .select_related('store', 'user')\
            .prefetch_related('items__product')\
            .order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data.get('items', [])
        shipping_address = serializer.validated_data.get('shipping_address', '')
        billing_address = serializer.validated_data.get('billing_address', '')
        notes = serializer.validated_data.get('notes', '')

        # Get addresses from IDs if provided
        shipping_address_id = serializer.validated_data.get('shipping_address_id')
        billing_address_id = serializer.validated_data.get('billing_address_id')

        if shipping_address_id:
            try:
                addr = Address.objects.get(id=shipping_address_id, user=request.user)
                shipping_address = str(addr)
            except Address.DoesNotExist:
                return Response(
                    {'error': 'Shipping address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if billing_address_id:
            try:
                addr = Address.objects.get(id=billing_address_id, user=request.user)
                billing_address = str(addr)
            except Address.DoesNotExist:
                return Response(
                    {'error': 'Billing address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not shipping_address or not billing_address:
            return Response(
                {'error': 'Shipping and billing addresses are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate totals and validate products
        subtotal = 0
        order_items = []

        for item in items_data:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Product {product_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if product.stock < quantity:
                return Response(
                    {'error': f'Insufficient stock for {product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price,
                'subtotal': item_subtotal
            })

        # Create order
        order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        tax = subtotal * 0.08  # 8% tax
        shipping_cost = 50 if subtotal > 0 else 0  # Free shipping over certain amount
        total_amount = subtotal + tax + shipping_cost

        try:
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                shipping_address=shipping_address,
                billing_address=billing_address,
                notes=notes
            )

            # Create order items and update inventory
            for item_data in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    subtotal=item_data['subtotal']
                )

                # Update product stock and sold count
                product = item_data['product']
                product.stock -= item_data['quantity']
                product.sold += item_data['quantity']
                product.save()

            # Create initial order status
            OrderStatus.objects.create(
                order=order,
                status='pending',
                message='Order created successfully'
            )

            order_serializer = OrderDetailSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.payment_status == 'paid':
            return Response(
                {'error': 'Paid orders cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore inventory
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.sold -= item.quantity
            product.save()

        order.status = 'cancelled'
        order.save()

        OrderStatus.objects.create(
            order=order,
            status='cancelled',
            message='Order cancelled by user'
        )

        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def from_cart(self, request):
        """从购物车创建订单"""
        cart = Cart.objects.get(user=request.user)

        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shipping_address = request.data.get('shipping_address', '')
        billing_address = request.data.get('billing_address', '')
        shipping_address_id = request.data.get('shipping_address_id')
        billing_address_id = request.data.get('billing_address_id')
        notes = request.data.get('notes', '')

        if shipping_address_id:
            try:
                addr = Address.objects.get(id=shipping_address_id, user=request.user)
                shipping_address = str(addr)
            except Address.DoesNotExist:
                return Response(
                    {'error': 'Shipping address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if billing_address_id:
            try:
                addr = Address.objects.get(id=billing_address_id, user=request.user)
                billing_address = str(addr)
            except Address.DoesNotExist:
                return Response(
                    {'error': 'Billing address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not shipping_address or not billing_address:
            return Response(
                {'error': 'Shipping and billing addresses are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate products and calculate totals
        subtotal = 0
        order_items = []

        for cart_item in cart.items.all():
            product = cart_item.product
            quantity = cart_item.quantity

            if product.stock < quantity:
                return Response(
                    {'error': f'Insufficient stock for {product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price,
                'subtotal': item_subtotal
            })

        with transaction.atomic():
            # Create order
            order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
            tax = subtotal * 0.08  # 8% tax
            shipping_cost = 50 if subtotal > 0 else 0
            total_amount = subtotal + tax + shipping_cost

            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                shipping_address=shipping_address,
                billing_address=billing_address,
                notes=notes
            )

            # Create order items and update inventory
            for item_data in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    subtotal=item_data['subtotal']
                )

                # Update product stock and sold count
                product = item_data['product']
                product.stock -= item_data['quantity']
                product.sold += item_data['quantity']
                product.save()

            # Create initial order status
            OrderStatus.objects.create(
                order=order,
                status='pending',
                message='Order created from cart'
            )

            # Clear the cart
            cart.items.all().delete()

        order_serializer = OrderDetailSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

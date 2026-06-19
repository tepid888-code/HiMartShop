from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.products.models import Category, Product
from apps.stores.models import Store
from apps.orders.models import Order
from apps.logistics.models import ShippingMethod, Shipment, TrackingEvent

class ShipmentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # 创建测试店铺
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )

        # 创建测试分类
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        # 创建测试产品
        self.product = Product.objects.create(
            store=self.store,
            seller=self.user,
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Test Description',
            price=100.00,
            sku='SKU001',
            stock=10
        )

        # 创建测试订单
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD-001',
            subtotal=100.00,
            tax=8.00,
            shipping_cost=50.00,
            total_amount=158.00,
            shipping_address='123 Main St',
            billing_address='123 Main St'
        )

        # 创建配送方式
        self.shipping_method = ShippingMethod.objects.create(
            name='Express Shipping',
            speed='express',
            base_cost=50.00
        )

    def test_create_shipment(self):
        """测试创建发货单"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/logistics/shipments/', {
            'order_id': self.order.id,
            'shipping_method_id': self.shipping_method.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tracking_number', response.data)

    def test_mark_shipped(self):
        """测试标记为已发货"""
        self.client.force_authenticate(user=self.user)

        # 创建发货单
        shipment = Shipment.objects.create(
            order=self.order,
            shipping_method=self.shipping_method,
            tracking_number='TRACK-001',
            shipping_cost=50.00
        )

        # 标记为已发货
        response = self.client.post(f'/api/logistics/shipments/{shipment.id}/mark_shipped/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'shipped')

    def test_mark_delivered(self):
        """测试标记为已送达"""
        self.client.force_authenticate(user=self.user)

        # 创建发货单
        shipment = Shipment.objects.create(
            order=self.order,
            shipping_method=self.shipping_method,
            tracking_number='TRACK-001',
            shipping_cost=50.00,
            status='in_transit'
        )

        # 标记为已送达
        response = self.client.post(f'/api/logistics/shipments/{shipment.id}/mark_delivered/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'delivered')

    def test_update_tracking(self):
        """测试更新追踪信息"""
        self.client.force_authenticate(user=self.user)

        # 创建发货单
        shipment = Shipment.objects.create(
            order=self.order,
            shipping_method=self.shipping_method,
            tracking_number='TRACK-001',
            shipping_cost=50.00
        )

        # 更新追踪
        response = self.client.post(f'/api/logistics/shipments/{shipment.id}/update_tracking/', {
            'event_type': 'in_transit',
            'location': 'Nairobi Distribution Center',
            'description': 'Package in transit'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

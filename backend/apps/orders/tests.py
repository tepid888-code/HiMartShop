import pytest
from rest_framework import status
from apps.orders.models import Order
from apps.products.models import Product


@pytest.mark.django_db
class TestOrderViewSet:
    """订单 ViewSet 测试"""

    def test_create_order(self, authenticated_client, sample_product):
        """测试创建订单"""
        order_data = {
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 1
                }
            ],
            'shipping_address': '123 Main St, Nairobi, Kenya',
            'billing_address': '123 Main St, Nairobi, Kenya',
            'notes': 'Please deliver ASAP'
        }

        response = authenticated_client.post(
            '/api/orders/',
            order_data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_number' in response.data
        assert response.data['status'] == 'pending'

    def test_list_orders(self, authenticated_client):
        """测试订单列表"""
        response = authenticated_client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_order(self, authenticated_client, sample_product):
        """测试获取单个订单"""
        # 先创建订单
        order_data = {
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 1
                }
            ],
            'shipping_address': '123 Main St',
            'billing_address': '123 Main St',
        }

        create_response = authenticated_client.post(
            '/api/orders/',
            order_data,
            format='json'
        )

        if create_response.status_code == status.HTTP_201_CREATED:
            order_id = create_response.data['id']

            # 获取订单
            response = authenticated_client.get(f'/api/orders/{order_id}/')
            assert response.status_code == status.HTTP_200_OK
            assert response.data['id'] == order_id

    def test_cancel_order(self, authenticated_client, sample_product):
        """测试取消订单"""
        # 创建订单
        order_data = {
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 1
                }
            ],
            'shipping_address': '123 Main St',
            'billing_address': '123 Main St',
        }

        create_response = authenticated_client.post(
            '/api/orders/',
            order_data,
            format='json'
        )

        if create_response.status_code == status.HTTP_201_CREATED:
            order_id = create_response.data['id']

            # 取消订单
            response = authenticated_client.patch(f'/api/orders/{order_id}/cancel/')
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'cancelled'

    def test_order_filters_by_status(self, authenticated_client, sample_product):
        """测试按状态过滤订单"""
        response = authenticated_client.get('/api/orders/?status=pending')
        assert response.status_code == status.HTTP_200_OK

    def test_inventory_updated_on_order(self, authenticated_client, sample_product):
        """测试订单时库存更新"""
        initial_stock = sample_product.stock

        order_data = {
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 5
                }
            ],
            'shipping_address': '123 Main St',
            'billing_address': '123 Main St',
        }

        authenticated_client.post(
            '/api/orders/',
            order_data,
            format='json'
        )

        # 刷新产品
        sample_product.refresh_from_db()

        # 检查库存是否减少
        assert sample_product.stock == initial_stock - 5
        assert sample_product.sold == 5

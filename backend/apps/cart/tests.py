from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.products.models import Category, Product
from apps.stores.models import Store
from apps.cart.models import Cart, CartItem

class CartTestCase(TestCase):
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

    def test_get_cart(self):
        """测试获取购物车"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_count'], 0)

    def test_add_to_cart(self):
        """测试添加商品到购物车"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/add/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 2)

    def test_update_cart_item(self):
        """测试更新购物车商品数量"""
        self.client.force_authenticate(user=self.user)

        # 首先添加商品
        add_response = self.client.post('/api/cart/add/', {
            'product_id': self.product.id,
            'quantity': 1
        })
        item_id = add_response.data['id']

        # 更新数量
        update_response = self.client.patch('/api/cart/update_item/', {
            'item_id': item_id,
            'quantity': 5
        })
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['quantity'], 5)

    def test_clear_cart(self):
        """测试清空购物车"""
        self.client.force_authenticate(user=self.user)

        # 添加商品
        self.client.post('/api/cart/add/', {
            'product_id': self.product.id,
            'quantity': 2
        })

        # 清空购物车
        response = self.client.delete('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 验证购物车为空
        get_response = self.client.get('/api/cart/')
        self.assertEqual(get_response.data['item_count'], 0)

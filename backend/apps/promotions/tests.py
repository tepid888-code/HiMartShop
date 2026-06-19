from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from apps.promotions.models import Coupon, CouponUsage
from apps.users.models import User

class CouponTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # 创建有效的百分比优惠券
        self.percentage_coupon = Coupon.objects.create(
            code='SAVE10',
            description='Save 10% on all products',
            discount_type='percentage',
            discount_value=10,
            min_purchase=100,
            max_uses=100,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=30),
            is_active=True
        )

        # 创建固定金额优惠券
        self.fixed_coupon = Coupon.objects.create(
            code='SAVE50',
            description='Save 50 KES',
            discount_type='fixed',
            discount_value=50,
            min_purchase=200,
            max_uses=50,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=30),
            is_active=True
        )

        # 创建过期优惠券
        self.expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type='percentage',
            discount_value=20,
            valid_from=timezone.now() - timedelta(days=30),
            valid_to=timezone.now() - timedelta(days=1),
            is_active=True
        )

    def test_list_coupons(self):
        """测试获取优惠券列表"""
        response = self.client.get('/api/promotions/coupons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 应该只显示有效的优惠券
        self.assertGreater(len(response.data['results']), 0)

    def test_validate_percentage_coupon(self):
        """测试验证百分比优惠券"""
        response = self.client.post('/api/promotions/coupons/validate/', {
            'code': 'SAVE10',
            'amount': 1000
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount_amount']), 100)

    def test_validate_fixed_coupon(self):
        """测试验证固定金额优惠券"""
        response = self.client.post('/api/promotions/coupons/validate/', {
            'code': 'SAVE50',
            'amount': 500
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount_amount']), 50)

    def test_expired_coupon(self):
        """测试过期优惠券"""
        response = self.client.post('/api/promotions/coupons/validate/', {
            'code': 'EXPIRED',
            'amount': 1000
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_coupon_minimum_purchase(self):
        """测试优惠券最低消费限制"""
        response = self.client.post('/api/promotions/coupons/validate/', {
            'code': 'SAVE10',
            'amount': 50
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

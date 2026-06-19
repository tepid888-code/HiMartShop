from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.stores.models import Store
from apps.sellers.models import SellerProfile

class SellerProfileTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='pass123'
        )

        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=self.user
        )

        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            store=self.store,
            verification_status='verified'
        )

    def test_get_seller_profile(self):
        """测试获取卖家资料"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/sellers/profile/my_profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seller_dashboard(self):
        """测试卖家仪表板"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/sellers/profile/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)

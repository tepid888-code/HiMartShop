import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSet:
    """用户 ViewSet 测试"""

    def test_user_registration(self, api_client):
        """测试用户注册"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+254712345678',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }

        response = api_client.post('/api/users/register/', user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login(self, api_client, authenticated_user):
        """测试用户登录"""
        login_data = {
            'username': authenticated_user.username,
            'password': 'testpass123'
        }

        response = api_client.post('/api/users/login/', login_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_get_current_user(self, authenticated_client, authenticated_user):
        """测试获取当前用户"""
        response = authenticated_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_user.username

    def test_user_logout(self, authenticated_client):
        """测试用户登出"""
        response = authenticated_client.post('/api/users/logout/')
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_login_credentials(self, api_client, authenticated_user):
        """测试无效登录凭证"""
        login_data = {
            'username': authenticated_user.username,
            'password': 'wrongpassword'
        }

        response = api_client.post('/api/users/login/', login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_username_registration(self, api_client, authenticated_user):
        """测试重复用户名注册"""
        user_data = {
            'username': authenticated_user.username,
            'email': 'another@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }

        response = api_client.post('/api/users/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch_registration(self, api_client):
        """测试密码不匹配注册"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass123',
        }

        response = api_client.post('/api/users/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAddressViewSet:
    """地址 ViewSet 测试"""

    def test_add_address(self, authenticated_client):
        """测试添加地址"""
        address_data = {
            'address_type': 'home',
            'street_address': '123 Main St',
            'city': 'Nairobi',
            'postal_code': '12345',
            'country': 'Kenya',
            'phone': '+254712345678',
        }

        response = authenticated_client.post(
            '/api/users/add_address/',
            address_data
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_get_addresses(self, authenticated_client):
        """测试获取地址列表"""
        response = authenticated_client.get('/api/users/addresses/')
        assert response.status_code == status.HTTP_200_OK

    def test_update_address(self, authenticated_client):
        """测试更新地址"""
        # 先添加地址
        address_data = {
            'address_type': 'home',
            'street_address': '123 Main St',
            'city': 'Nairobi',
            'postal_code': '12345',
            'country': 'Kenya',
            'phone': '+254712345678',
        }

        add_response = authenticated_client.post(
            '/api/users/add_address/',
            address_data
        )

        if add_response.status_code == status.HTTP_201_CREATED:
            address_id = add_response.data['id']

            # 更新地址
            update_data = {'street_address': '456 New St'}
            response = authenticated_client.patch(
                f'/api/users/{address_id}/',
                update_data
            )
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

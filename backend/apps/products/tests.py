import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from apps.products.models import Product, Category, ProductReview
from apps.users.models import User


@pytest.mark.django_db
class TestProductViewSet:
    """产品 ViewSet 测试"""

    def test_list_products(self, api_client, sample_product):
        """测试产品列表"""
        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)

    def test_product_search(self, api_client, sample_product):
        """测试产品搜索"""
        response = api_client.get(f'/api/products/?search={sample_product.name}')
        assert response.status_code == status.HTTP_200_OK

    def test_product_filter_by_category(self, api_client, sample_product):
        """测试按分类过滤"""
        response = api_client.get(f'/api/products/?category={sample_product.category.id}')
        assert response.status_code == status.HTTP_200_OK

    def test_product_ordering(self, api_client, sample_product):
        """测试排序"""
        response = api_client.get('/api/products/?ordering=-price')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_product(self, api_client, sample_product):
        """测试获取单个产品"""
        response = api_client.get(f'/api/products/{sample_product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_product.id
        assert response.data['name'] == sample_product.name

    def test_product_detail_includes_images(self, api_client, sample_product):
        """测试产品详情包含图片"""
        response = api_client.get(f'/api/products/{sample_product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'images' in response.data

    def test_product_review_create(self, authenticated_client, sample_product):
        """测试创建评价"""
        review_data = {
            'rating': 5,
            'title': 'Great product!',
            'comment': 'This is a great product'
        }
        response = authenticated_client.post(
            f'/api/products/{sample_product.id}/reviews/',
            review_data
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_product_review_list(self, api_client, sample_product):
        """测试评价列表"""
        response = api_client.get(f'/api/products/{sample_product.id}/reviews/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCategoryViewSet:
    """分类 ViewSet 测试"""

    def test_list_categories(self, api_client, sample_category):
        """测试分类列表"""
        response = api_client.get('/api/products/categories/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_category(self, api_client, sample_category):
        """测试获取单个分类"""
        response = api_client.get(f'/api/products/categories/{sample_category.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_category.id


@pytest.mark.django_db
class TestWishlistViewSet:
    """收藏 ViewSet 测试"""

    def test_add_to_wishlist(self, authenticated_client, sample_product):
        """测试添加到收藏"""
        response = authenticated_client.post(
            '/api/products/wishlist/',
            {'product_id': sample_product.id}
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_get_wishlist(self, authenticated_client, sample_product):
        """测试获取收藏列表"""
        # 先添加到收藏
        authenticated_client.post(
            '/api/products/wishlist/',
            {'product_id': sample_product.id}
        )

        # 获取收藏列表
        response = authenticated_client.get('/api/products/wishlist/')
        assert response.status_code == status.HTTP_200_OK

    def test_remove_from_wishlist(self, authenticated_client, sample_product):
        """测试从收藏移除"""
        # 先添加到收藏
        add_response = authenticated_client.post(
            '/api/products/wishlist/',
            {'product_id': sample_product.id}
        )

        if add_response.status_code == status.HTTP_201_CREATED:
            wishlist_item_id = add_response.data['id']

            # 移除
            response = authenticated_client.delete(
                f'/api/products/wishlist/{wishlist_item_id}/'
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

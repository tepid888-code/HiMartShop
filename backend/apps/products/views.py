from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache

from apps.products.models import Category, Product, ProductReview, WishlistItem
from apps.products.serializers import (
    CategorySerializer, ProductSerializer, ProductDetailSerializer,
    ProductReviewSerializer, WishlistSerializer
)
from apps.products.filters import ProductFilter
from apps.common.cache import CachedViewMixin, invalidate_cache


class CategoryViewSet(CachedViewMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    cache_key_prefix = 'categories'
    cache_timeout_list = 3600  # 1小时


class ProductViewSet(CachedViewMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'rating', 'created_at', 'sold']
    ordering = ['-created_at']
    cache_key_prefix = 'products'
    cache_timeout_list = 300  # 5分钟
    cache_timeout_detail = 600  # 10分钟

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)\
            .select_related('category', 'seller', 'store')\
            .prefetch_related('images')\
            .only('id', 'name', 'slug', 'price', 'original_price', 'rating',
                   'review_count', 'category_id', 'store_id', 'created_at',
                   'is_active', 'stock')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductReview.objects.filter(product_id=product_id)\
            .select_related('user')\
            .order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        serializer.save(user=self.request.user, product_id=product_id)
        # 清除相关缓存
        invalidate_cache(f'products:detail:{product_id}')

    def perform_destroy(self, instance):
        product_id = instance.product_id
        instance.delete()
        # 清除相关缓存
        invalidate_cache(f'products:detail:{product_id}')


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(wishlist__user=self.request.user)\
            .select_related('product')\
            .order_by('-added_at')

    def list(self, request, *args, **kwargs):
        cache_key = f'wishlist:user:{request.user.id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        wishlist_items = self.get_queryset()
        serializer = self.get_serializer(wishlist_items, many=True)
        cache.set(cache_key, serializer.data, 1800)  # 30分钟
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=request.user.wishlist,
            product_id=product_id
        )

        if created:
            serializer = self.get_serializer(wishlist_item)
            # 清除缓存
            cache.delete(f'wishlist:user:{request.user.id}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Product already in wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        wishlist_item = self.get_object()
        if wishlist_item.wishlist.user == request.user:
            user_id = request.user.id
            wishlist_item.delete()
            # 清除缓存
            cache.delete(f'wishlist:user:{user_id}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise permissions.PermissionDenied("You can only delete your own wishlist items.")

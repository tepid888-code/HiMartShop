from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'', views.ProductViewSet, basename='product')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:product_id>/reviews/', views.ProductReviewViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='product-reviews-list'),
    path('<int:product_id>/reviews/<int:pk>/', views.ProductReviewViewSet.as_view({
        'delete': 'destroy'
    }), name='product-review-detail'),
]

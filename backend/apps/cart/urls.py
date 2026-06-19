from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.cart.views import CartViewSet

router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

urlpatterns = router.urls

# 自定义操作路由
urlpatterns += [
    path('add/', CartViewSet.as_view({'post': 'add'}), name='cart-add'),
    path('update_item/', CartViewSet.as_view({'patch': 'update_item'}), name='cart-update-item'),
    path('remove_item/', CartViewSet.as_view({'delete': 'remove_item'}), name='cart-remove-item'),
    path('clear/', CartViewSet.as_view({'delete': 'clear'}), name='cart-clear'),
]

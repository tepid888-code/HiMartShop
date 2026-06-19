from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sellers.views import SellerProfileViewSet, SellerWithdrawalViewSet, SellerMessageViewSet

router = DefaultRouter()
router.register(r'profile', SellerProfileViewSet, basename='seller-profile')
router.register(r'withdrawals', SellerWithdrawalViewSet, basename='seller-withdrawal')
router.register(r'messages', SellerMessageViewSet, basename='seller-message')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.logistics.views import (
    ShippingMethodViewSet, ShipmentViewSet, ReturnRequestViewSet
)

router = DefaultRouter()
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-method')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'returns', ReturnRequestViewSet, basename='return-request')

urlpatterns = [
    path('', include(router.urls)),
]

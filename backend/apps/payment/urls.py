from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payment'

router = DefaultRouter()
router.register(r'', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]

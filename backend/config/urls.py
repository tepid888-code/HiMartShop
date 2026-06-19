from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include([
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema')),

        path('users/', include('apps.users.urls')),
        path('products/', include('apps.products.urls')),
        path('orders/', include('apps.orders.urls')),
        path('payment/', include('apps.payment.urls')),
        path('stores/', include('apps.stores.urls')),
        path('cart/', include('apps.cart.urls')),
        path('promotions/', include('apps.promotions.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

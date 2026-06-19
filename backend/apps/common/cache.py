from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework.decorators import action
import hashlib
import json


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = [prefix] + list(str(arg) for arg in args)
    if kwargs:
        key_parts.append(hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest())
    return ':'.join(key_parts)


class CacheListMixin:
    """列表视图缓存 Mixin"""

    cache_timeout = 300  # 5分钟
    cache_key_prefix = 'list'

    def list(self, request, *args, **kwargs):
        # 生成缓存键
        cache_key = get_cache_key(
            self.cache_key_prefix,
            request.user.id,
            request.GET.urlencode()
        )

        # 从缓存获取
        response = cache.get(cache_key)
        if response is not None:
            return response

        # 获取原始响应
        response = super().list(request, *args, **kwargs)

        # 缓存响应
        cache.set(cache_key, response, self.cache_timeout)

        return response


class CacheRetrieveMixin:
    """详情视图缓存 Mixin"""

    cache_timeout = 600  # 10分钟
    cache_key_prefix = 'detail'

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        cache_key = get_cache_key(self.cache_key_prefix, obj.id)

        # 从缓存获取
        data = cache.get(cache_key)
        if data is not None:
            from rest_framework.response import Response
            return Response(data)

        # 获取原始响应
        response = super().retrieve(request, *args, **kwargs)

        # 缓存响应数据
        cache.set(cache_key, response.data, self.cache_timeout)

        return response


def invalidate_cache(pattern: str):
    """根据模式失效缓存"""
    from django_redis import get_redis_connection
    redis_conn = get_redis_connection('default')
    keys = redis_conn.keys(f'{pattern}*')
    if keys:
        redis_conn.delete(*keys)


class CachedViewMixin:
    """完整缓存 Mixin，用于 list 和 retrieve"""

    cache_timeout_list = 300  # 5分钟
    cache_timeout_detail = 600  # 10分钟
    cache_key_prefix = 'cached'

    def get_cache_key_list(self, request):
        return get_cache_key(
            f'{self.cache_key_prefix}:list',
            request.user.id if request.user.is_authenticated else 'anon',
            request.GET.urlencode()
        )

    def get_cache_key_detail(self, obj):
        return get_cache_key(f'{self.cache_key_prefix}:detail', obj.id)

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key_list(request)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            from rest_framework.response import Response
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout_list)
        return response

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        cache_key = self.get_cache_key_detail(obj)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            from rest_framework.response import Response
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout_detail)
        return response

    def perform_create(self, serializer):
        instance = serializer.save()
        # 清除列表缓存
        invalidate_cache(f'{self.cache_key_prefix}:list')
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        # 清除相关缓存
        invalidate_cache(f'{self.cache_key_prefix}:detail:{instance.id}')
        invalidate_cache(f'{self.cache_key_prefix}:list')
        return instance

    def perform_destroy(self, instance):
        # 清除相关缓存
        invalidate_cache(f'{self.cache_key_prefix}:detail:{instance.id}')
        invalidate_cache(f'{self.cache_key_prefix}:list')
        instance.delete()

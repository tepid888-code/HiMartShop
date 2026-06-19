# 性能优化配置示例 - Hi Mart

## 后端性能优化设置

### 1. Django 缓存配置（settings.py）

```python
# Redis 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'himart',
        'TIMEOUT': 300,
    }
}

# 会话缓存
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 页面缓存中间件
MIDDLEWARE = [
    # ...
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

CACHE_MIDDLEWARE_SECONDS = 300
```

### 2. 数据库连接池优化

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'himart_db',
        'USER': 'himart',
        'PASSWORD': 'himart123',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 连接重用时间（秒）
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        },
        'ATOMIC_REQUESTS': True,  # 每个请求一个事务
    }
}
```

### 3. API 分页配置

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

### 4. 查询优化示例

```python
# apps/orders/views.py

from django.db.models import F, Q, Prefetch, Count
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response

class OrderViewSet(viewsets.ModelViewSet):
    # 缓存列表视图 5 分钟
    @cache_page(60 * 5)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        # 优化：使用 select_related 和 prefetch_related
        queryset = Order.objects.select_related(
            'user',
            'payment',
            'shipment'
        ).prefetch_related(
            'items__product',
            'items__product__images',
            'items__product__store'
        ).annotate(
            # 添加注解计算而不是取出后计算
            item_count=Count('items')
        )
        
        # 只选择需要的字段以减少数据传输
        queryset = queryset.only(
            'id', 'order_number', 'status', 'total_amount',
            'created_at', 'user__id', 'user__username'
        )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        # 缓存最近订单
        cache_key = f'recent_orders_user_{request.user.id}'
        orders = cache.get(cache_key)
        
        if orders is None:
            orders = self.get_queryset().filter(
                user=request.user
            )[:10]
            cache.set(cache_key, orders, 300)
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
```

### 5. 批量操作优化

```python
# apps/products/views.py

class ProductViewSet(viewsets.ModelViewSet):
    def perform_bulk_create(self, request):
        """批量创建产品"""
        products_data = request.data
        
        # 使用 bulk_create 一次性插入多个对象
        products = [
            Product(
                name=p['name'],
                price=p['price'],
                store=request.user.store
            )
            for p in products_data
        ]
        
        created = Product.objects.bulk_create(products, batch_size=100)
        
        # 清除缓存
        cache.delete('products_list')
        
        return Response(
            ProductSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED
        )
```

---

## 前端性能优化

### 1. Vite 构建优化配置

```typescript
// vite.config.ts

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  
  build: {
    // 输出目录
    outDir: 'dist',
    
    // 关闭 source maps（生产环境）
    sourcemap: false,
    
    // 最小化配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 删除 console
      },
    },
    
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vue': ['vue', 'vue-router', 'pinia'],
          'vendor': ['axios'],
        },
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash][extname]',
      },
    },
    
    // 优化依赖
    commonjsOptions: {
      include: ['node_modules/**'],
    },
  },
  
  // 开发服务器配置
  server: {
    middlewareMode: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
```

### 2. 懒加载和代码分割

```typescript
// router/index.ts

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/pages/Products.vue'),
    // 预加载关联的产品详情页
    children: [
      {
        path: ':id',
        name: 'ProductDetail',
        component: () => import('@/pages/ProductDetail.vue'),
      },
    ],
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import(/* webpackChunkName: "checkout" */ '@/pages/Checkout.vue'),
  },
]
```

### 3. 图片优化

```vue
<template>
  <!-- 懒加载图片 -->
  <img
    v-lazy="product.image"
    :alt="product.name"
    loading="lazy"
  />
  
  <!-- 响应式图片 -->
  <picture>
    <source
      srcset="product.webp"
      type="image/webp"
    />
    <img
      src="product.jpg"
      :alt="product.name"
    />
  </picture>
</template>
```

### 4. 虚拟滚动优化长列表

```vue
<template>
  <!-- 虚拟滚动：只渲染可见区域的项目 -->
  <div class="products-grid" style="height: 600px; overflow-y: auto">
    <div
      v-for="item in visibleItems"
      :key="item.id"
      class="product-card"
    >
      {{ item.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onScroll } from 'vue'

const items = ref([])
const scrollTop = ref(0)
const itemHeight = 200
const containerHeight = 600

const visibleStart = computed(() => {
  return Math.floor(scrollTop.value / itemHeight)
})

const visibleEnd = computed(() => {
  return Math.ceil((scrollTop.value + containerHeight) / itemHeight)
})

const visibleItems = computed(() => {
  return items.value.slice(visibleStart.value, visibleEnd.value)
})

const handleScroll = (e: Event) => {
  scrollTop.value = (e.target as HTMLElement).scrollTop
}
</script>
```

### 5. Pinia 状态优化

```typescript
// stores/products.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProductsStore = defineStore('products', () => {
  const products = ref([])
  const filters = ref({
    category: null,
    minPrice: 0,
    maxPrice: 10000,
  })
  
  // 使用 computed 而不是 ref 存储派生数据
  const filteredProducts = computed(() => {
    return products.value.filter(p => {
      return p.price >= filters.value.minPrice &&
             p.price <= filters.value.maxPrice &&
             (!filters.value.category || p.category === filters.value.category)
    })
  })
  
  // 使用 computed 计数量
  const totalCount = computed(() => filteredProducts.value.length)
  
  return {
    products,
    filters,
    filteredProducts,
    totalCount,
  }
})
```

---

## Nginx 生产配置

```nginx
# /etc/nginx/sites-available/himart

upstream django {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

# 速率限制
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

server {
    listen 80;
    server_name mail.aitepid.crabdance.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mail.aitepid.crabdance.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 启用 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_comp_level 6;
    gzip_min_length 1024;
    
    # 前端文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        root /var/www/himart/frontend/dist;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }
    
    # API 缓存
    location /api {
        proxy_pass http://django;
        proxy_cache_valid 200 10m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 速率限制
        limit_req zone=api burst=50 nodelay;
    }
    
    # 管理后台
    location /admin {
        proxy_pass http://django;
        limit_req zone=general burst=20 nodelay;
    }
    
    # 前端静态页面
    location / {
        root /var/www/himart/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 监控指标

关键监控指标配置（用于 Prometheus/Grafana）：

```python
# apps/common/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# API 请求计数
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# API 响应时间
api_response_time = Histogram(
    'api_response_duration_seconds',
    'API response time',
    ['method', 'endpoint']
)

# 活跃用户数
active_users = Gauge(
    'active_users_total',
    'Total active users'
)

# 数据库连接数
db_connections = Gauge(
    'db_connections_total',
    'Total database connections'
)
```

---

**最后更新**: 2026-06-19

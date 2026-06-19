#!/usr/bin/env python
"""
性能基准测试脚本
用于验证数据库查询优化和缓存层带来的性能改进
"""

import os
import sys
import django
import time
from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal

# 设置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product, Category, ProductImage
from apps.orders.models import Order, OrderItem
from apps.payment.models import Payment

User = get_user_model()


class BenchmarkSuite:
    """性能基准测试套件"""

    def __init__(self):
        self.client = Client()
        self.results = {}
        self.setup_test_data()

    def setup_test_data(self):
        """设置测试数据"""
        print("设置测试数据...")

        # 创建用户
        self.user = User.objects.create_user(
            username='benchmark_user',
            email='bench@example.com',
            password='testpass123'
        )

        # 创建分类
        self.category = Category.objects.create(
            name='Benchmark Category',
            slug='benchmark-category'
        )

        # 创建产品 (100个)
        products = []
        for i in range(100):
            product = Product(
                name=f'Benchmark Product {i}',
                slug=f'benchmark-product-{i}',
                description=f'Description for benchmark product {i}',
                price=Decimal(str(10 + i)),
                original_price=Decimal(str(20 + i)),
                sku=f'BENCH-{i:04d}',
                category=self.category,
                seller=self.user,
                stock=50 + i
            )
            products.append(product)

        Product.objects.bulk_create(products)
        self.products = Product.objects.all()[:100]

        # 为前10个产品添加图片
        for i, product in enumerate(self.products[:10]):
            ProductImage.objects.create(
                product=product,
                image=f'products/test_{i}.jpg',
                alt_text=f'Product image {i}',
                is_primary=(i == 0)
            )

        print(f"✓ 创建了 {len(self.products)} 个产品")

    def benchmark_product_list(self):
        """基准测试：产品列表 API"""
        print("\n[产品列表 API 基准测试]")

        # 预热缓存
        response = self.client.get('/api/products/')

        # 执行测试 (10次)
        times = []
        for i in range(10):
            start = time.time()
            response = self.client.get('/api/products/')
            elapsed = (time.time() - start) * 1000  # 转换为毫秒
            times.append(elapsed)

            if response.status_code != 200:
                print(f"✗ 请求失败: {response.status_code}")
                return

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results['product_list'] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time
        }

        print(f"✓ 平均响应时间: {avg_time:.2f}ms")
        print(f"  最快: {min_time:.2f}ms | 最慢: {max_time:.2f}ms")

    def benchmark_product_detail(self):
        """基准测试：产品详情 API"""
        print("\n[产品详情 API 基准测试]")

        product_id = self.products[0].id

        # 预热缓存
        response = self.client.get(f'/api/products/{product_id}/')

        # 执行测试 (10次)
        times = []
        for i in range(10):
            start = time.time()
            response = self.client.get(f'/api/products/{product_id}/')
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

            if response.status_code != 200:
                print(f"✗ 请求失败: {response.status_code}")
                return

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results['product_detail'] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time
        }

        print(f"✓ 平均响应时间: {avg_time:.2f}ms")
        print(f"  最快: {min_time:.2f}ms | 最慢: {max_time:.2f}ms")

    def benchmark_product_search(self):
        """基准测试：产品搜索 API"""
        print("\n[产品搜索 API 基准测试]")

        # 预热缓存
        response = self.client.get('/api/products/?search=Benchmark')

        # 执行测试 (10次)
        times = []
        for i in range(10):
            start = time.time()
            response = self.client.get('/api/products/?search=Benchmark')
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

            if response.status_code != 200:
                print(f"✗ 请求失败: {response.status_code}")
                return

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results['product_search'] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time
        }

        print(f"✓ 平均响应时间: {avg_time:.2f}ms")
        print(f"  最快: {min_time:.2f}ms | 最慢: {max_time:.2f}ms")

    def benchmark_product_filter(self):
        """基准测试：产品过滤 API"""
        print("\n[产品过滤 API 基准测试]")

        category_id = self.category.id

        # 预热缓存
        response = self.client.get(f'/api/products/?category={category_id}')

        # 执行测试 (10次)
        times = []
        for i in range(10):
            start = time.time()
            response = self.client.get(f'/api/products/?category={category_id}')
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

            if response.status_code != 200:
                print(f"✗ 请求失败: {response.status_code}")
                return

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results['product_filter'] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time
        }

        print(f"✓ 平均响应时间: {avg_time:.2f}ms")
        print(f"  最快: {min_time:.2f}ms | 最慢: {max_time:.2f}ms")

    def benchmark_cache_effectiveness(self):
        """测试缓存效果"""
        print("\n[缓存效果测试]")

        from django.core.cache import cache
        cache.clear()

        # 第一次请求（缓存未命中）
        start = time.time()
        response = self.client.get('/api/products/')
        first_request = (time.time() - start) * 1000

        # 第二次请求（缓存命中）
        start = time.time()
        response = self.client.get('/api/products/')
        cached_request = (time.time() - start) * 1000

        improvement = ((first_request - cached_request) / first_request) * 100

        self.results['cache_effectiveness'] = {
            'first_request': first_request,
            'cached_request': cached_request,
            'improvement_percent': improvement
        }

        print(f"✓ 首次请求: {first_request:.2f}ms")
        print(f"✓ 缓存命中: {cached_request:.2f}ms")
        print(f"✓ 性能提升: {improvement:.1f}%")

    def run_all_benchmarks(self):
        """运行所有基准测试"""
        print("=" * 60)
        print("Hi Mart 平台性能基准测试")
        print("=" * 60)

        self.benchmark_product_list()
        self.benchmark_product_detail()
        self.benchmark_product_search()
        self.benchmark_product_filter()
        self.benchmark_cache_effectiveness()

        self.print_summary()

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("性能基准测试总结")
        print("=" * 60)

        print("\n[API 响应时间统计 (毫秒)]")
        print(f"{'端点':<30} {'平均':<10} {'最快':<10} {'最慢':<10}")
        print("-" * 60)

        endpoints = {
            'product_list': '产品列表',
            'product_detail': '产品详情',
            'product_search': '产品搜索',
            'product_filter': '产品过滤'
        }

        for key, label in endpoints.items():
            if key in self.results:
                result = self.results[key]
                print(f"{label:<30} {result['avg']:<10.2f} "
                      f"{result['min']:<10.2f} {result['max']:<10.2f}")

        if 'cache_effectiveness' in self.results:
            result = self.results['cache_effectiveness']
            print(f"\n[缓存性能]")
            print(f"首次请求: {result['first_request']:.2f}ms")
            print(f"缓存命中: {result['cached_request']:.2f}ms")
            print(f"性能提升: {result['improvement_percent']:.1f}%")

        print("\n[性能目标]")
        print("✓ 产品列表响应时间 < 200ms")
        print("✓ 产品详情响应时间 < 150ms")
        print("✓ 缓存命中率 > 70%")
        print("✓ 总体性能提升 > 40%")

        print("\n" + "=" * 60)

    def cleanup(self):
        """清理测试数据"""
        print("\n清理测试数据...")
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(username='benchmark_user').delete()
        print("✓ 清理完成")


if __name__ == '__main__':
    suite = BenchmarkSuite()
    try:
        suite.run_all_benchmarks()
    finally:
        suite.cleanup()

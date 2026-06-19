#!/usr/bin/env python3
"""
Hi Mart 性能基准测试脚本
用于测试 API 响应时间和系统性能
"""

import time
import requests
import json
import statistics
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
API_BASE = 'http://localhost:8000/api'
AUTH_TOKEN = ''
CONCURRENT_USERS = 5
REQUESTS_PER_USER = 20

class BenchmarkTest:
    def __init__(self, name: str, method: str, endpoint: str, data: dict = None, concurrent: bool = False):
        self.name = name
        self.method = method
        self.endpoint = endpoint
        self.data = data or {}
        self.concurrent = concurrent
        self.times: List[float] = []
        self.errors = 0

    def run_single(self, headers: dict) -> float:
        """执行单个请求并返回响应时间"""
        url = f"{API_BASE}{self.endpoint}"
        start = time.time()

        try:
            if self.method == 'GET':
                resp = requests.get(url, headers=headers, timeout=10)
            elif self.method == 'POST':
                resp = requests.post(url, json=self.data, headers=headers, timeout=10)
            elif self.method == 'PATCH':
                resp = requests.patch(url, json=self.data, headers=headers, timeout=10)
            else:
                return None

            elapsed = (time.time() - start) * 1000  # 转换为毫秒
            if resp.status_code >= 400:
                self.errors += 1
            return elapsed
        except Exception as e:
            self.errors += 1
            return None

    def run_benchmark(self, iterations: int = 10, concurrent: bool = False):
        """运行基准测试"""
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'} if AUTH_TOKEN else {}

        if concurrent and self.concurrent:
            # 并发测试
            with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
                futures = [
                    executor.submit(self.run_single, headers)
                    for _ in range(iterations * CONCURRENT_USERS)
                ]
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        self.times.append(result)
        else:
            # 顺序测试
            for _ in range(iterations):
                result = self.run_single(headers)
                if result is not None:
                    self.times.append(result)

    def get_stats(self) -> Dict:
        """获取统计数据"""
        if not self.times:
            return {
                'min': 'N/A',
                'max': 'N/A',
                'avg': 'N/A',
                'median': 'N/A',
                'p95': 'N/A',
                'p99': 'N/A',
                'errors': self.errors,
                'requests': 0,
            }

        sorted_times = sorted(self.times)
        requests = len(self.times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        return {
            'min': f"{min(self.times):.2f}ms",
            'max': f"{max(self.times):.2f}ms",
            'avg': f"{statistics.mean(self.times):.2f}ms",
            'median': f"{statistics.median(self.times):.2f}ms",
            'p95': f"{sorted_times[p95_idx] if p95_idx < len(sorted_times) else 'N/A'}ms",
            'p99': f"{sorted_times[p99_idx] if p99_idx < len(sorted_times) else 'N/A'}ms",
            'requests': requests,
            'errors': self.errors,
        }

def login():
    """登录并获取认证令牌"""
    global AUTH_TOKEN
    try:
        resp = requests.post(f'{API_BASE}/users/login/', json={
            'username': 'testuser',
            'password': 'testpass123',
        }, timeout=10)
        if resp.status_code == 200 and 'access' in resp.json():
            AUTH_TOKEN = resp.json()['access']
            print('✓ 登录成功\n')
            return True
    except Exception as e:
        print(f'⚠ 登录失败: {e}')
    return False

def run_benchmarks():
    """运行所有基准测试"""
    print('\n' + '='*60)
    print('🚀 Hi Mart 性能基准测试')
    print('='*60 + '\n')

    # 登录
    print('【登录】')
    login()

    # 定义测试
    tests = [
        BenchmarkTest('产品列表', 'GET', '/products/'),
        BenchmarkTest('产品详情', 'GET', '/products/1/'),
        BenchmarkTest('搜索产品', 'GET', '/products/?search=test'),
        BenchmarkTest('购物车', 'GET', '/cart/', concurrent=True),
        BenchmarkTest('订单列表', 'GET', '/orders/', concurrent=True),
        BenchmarkTest('创建订单', 'POST', '/orders/', {
            'items': [{'product_id': 1, 'quantity': 1}],
            'shipping_address': '123 Main St',
            'billing_address': '123 Main St',
        }, concurrent=True),
        BenchmarkTest('通知列表', 'GET', '/notifications/notifications/', concurrent=True),
        BenchmarkTest('物流信息', 'GET', '/logistics/shipping-methods/'),
        BenchmarkTest('卖家资料', 'GET', '/sellers/profile/my_profile/', concurrent=True),
    ]

    # 运行测试
    print('【执行测试】\n')
    for test in tests:
        print(f'测试: {test.name}...')
        test.run_benchmark(iterations=10, concurrent=test.concurrent)
        print('✓ 完成\n')

    # 生成报告
    print('='*60)
    print('📊 性能基准测试结果')
    print('='*60 + '\n')

    for test in tests:
        stats = test.get_stats()
        print(f'【{test.name}】')
        print(f'  最小: {stats["min"]}')
        print(f'  最大: {stats["max"]}')
        print(f'  平均: {stats["avg"]}')
        print(f'  中位数: {stats["median"]}')
        print(f'  P95: {stats["p95"]}')
        print(f'  P99: {stats["p99"]}')
        print(f'  请求数: {stats["requests"]}')
        print(f'  错误: {stats["errors"]}\n')

    # 总结
    print('='*60)
    print('性能指标评估:')
    print('='*60)

    total_requests = sum(len(test.times) for test in tests)
    total_errors = sum(test.errors for test in tests)
    avg_response_time = statistics.mean([
        time for test in tests for time in test.times
    ]) if any(test.times for test in tests) else 0

    print(f'\n总请求数: {total_requests}')
    print(f'总错误数: {total_errors}')
    print(f'错误率: {(total_errors/total_requests*100 if total_requests else 0):.2f}%')
    print(f'平均响应时间: {avg_response_time:.2f}ms')

    if avg_response_time < 200:
        print('\n✓ 性能优秀 (< 200ms)')
    elif avg_response_time < 500:
        print('\n⚠ 性能良好 (< 500ms)')
    else:
        print('\n✗ 性能需要优化 (> 500ms)')

    print('\n' + '='*60 + '\n')

if __name__ == '__main__':
    try:
        run_benchmarks()
    except KeyboardInterrupt:
        print('\n\n中断测试')
    except Exception as e:
        print(f'\n\n测试失败: {e}')

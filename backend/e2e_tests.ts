/**
 * E2E 测试脚本 - Hi Mart 电商平台
 * 测试完整的购物流程和卖家功能
 */

import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

// 测试用例
interface TestCase {
  name: string
  fn: () => Promise<void>
}

// 测试结果
interface TestResult {
  name: string
  passed: boolean
  duration: number
  error?: string
}

const results: TestResult[] = []

// 辅助函数
const api = axios.create({
  baseURL: API_BASE,
  validateStatus: () => true, // 接受所有状态码
})

let authToken = ''
let userId = 0
let testOrderId = 0

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function runTest(testCase: TestCase) {
  const startTime = performance.now()
  try {
    await testCase.fn()
    const duration = performance.now() - startTime
    results.push({
      name: testCase.name,
      passed: true,
      duration,
    })
    console.log(`✓ ${testCase.name} (${duration.toFixed(2)}ms)`)
  } catch (error: any) {
    const duration = performance.now() - startTime
    results.push({
      name: testCase.name,
      passed: false,
      duration,
      error: error.message,
    })
    console.log(`✗ ${testCase.name}: ${error.message}`)
  }
}

// 测试套件
const testSuite: TestCase[] = [
  // 1. 用户认证
  {
    name: 'User Registration',
    fn: async () => {
      const res = await api.post('/users/register/', {
        username: `testuser_${Date.now()}`,
        email: `test_${Date.now()}@example.com`,
        password: 'TestPass123!',
        first_name: 'Test',
        last_name: 'User',
      })
      if (res.status !== 201 && res.status !== 200) {
        throw new Error(`Registration failed: ${res.status}`)
      }
    },
  },

  {
    name: 'User Login',
    fn: async () => {
      const res = await api.post('/users/login/', {
        username: 'testuser',
        password: 'testpass123',
      })
      if (res.status !== 200) {
        throw new Error(`Login failed: ${res.status}`)
      }
      if (!res.data.access) {
        throw new Error('No access token in response')
      }
      authToken = res.data.access
      api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
    },
  },

  // 2. 产品浏览
  {
    name: 'Fetch Products List',
    fn: async () => {
      const res = await api.get('/products/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch products: ${res.status}`)
      }
      if (!Array.isArray(res.data.results) && !Array.isArray(res.data)) {
        throw new Error('Invalid products response format')
      }
    },
  },

  {
    name: 'Fetch Product Detail',
    fn: async () => {
      const res = await api.get('/products/1/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch product detail: ${res.status}`)
      }
      if (!res.data.id) {
        throw new Error('Invalid product response')
      }
    },
  },

  {
    name: 'Search Products',
    fn: async () => {
      const res = await api.get('/products/?search=test')
      if (res.status !== 200) {
        throw new Error(`Search failed: ${res.status}`)
      }
    },
  },

  // 3. 购物车操作
  {
    name: 'Get Cart',
    fn: async () => {
      const res = await api.get('/cart/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch cart: ${res.status}`)
      }
    },
  },

  {
    name: 'Add Item to Cart',
    fn: async () => {
      const res = await api.post('/cart/add/', {
        product_id: 1,
        quantity: 2,
      })
      if (res.status !== 200 && res.status !== 201) {
        throw new Error(`Failed to add to cart: ${res.status}`)
      }
    },
  },

  {
    name: 'Update Cart Item',
    fn: async () => {
      const res = await api.patch('/cart/update_item/', {
        cart_item_id: 1,
        quantity: 3,
      })
      if (res.status !== 200) {
        throw new Error(`Failed to update cart: ${res.status}`)
      }
    },
  },

  // 4. 优惠券系统
  {
    name: 'Validate Coupon',
    fn: async () => {
      const res = await api.post('/promotions/coupons/validate/', {
        code: 'TEST10',
      })
      // 优惠券可能不存在，这是正常的
      if (res.status !== 200 && res.status !== 400) {
        throw new Error(`Unexpected status: ${res.status}`)
      }
    },
  },

  // 5. 订单操作
  {
    name: 'Create Order',
    fn: async () => {
      const res = await api.post('/orders/', {
        items: [
          { product_id: 1, quantity: 1 },
        ],
        shipping_address: '123 Main St, Nairobi, 00100',
        billing_address: '123 Main St, Nairobi, 00100',
      })
      if (res.status !== 200 && res.status !== 201) {
        throw new Error(`Failed to create order: ${res.status}`)
      }
      if (res.data.id) {
        testOrderId = res.data.id
      }
    },
  },

  {
    name: 'Fetch Orders',
    fn: async () => {
      const res = await api.get('/orders/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch orders: ${res.status}`)
      }
    },
  },

  {
    name: 'Get Order Detail',
    fn: async () => {
      if (!testOrderId) {
        throw new Error('No test order ID available')
      }
      const res = await api.get(`/orders/${testOrderId}/`)
      if (res.status !== 200) {
        throw new Error(`Failed to fetch order detail: ${res.status}`)
      }
    },
  },

  {
    name: 'Track Order',
    fn: async () => {
      if (!testOrderId) {
        throw new Error('No test order ID available')
      }
      const res = await api.get(`/orders/${testOrderId}/track/`)
      if (res.status !== 200) {
        throw new Error(`Failed to track order: ${res.status}`)
      }
    },
  },

  // 6. 支付系统
  {
    name: 'Check Payment Status',
    fn: async () => {
      if (!testOrderId) {
        throw new Error('No test order ID available')
      }
      const res = await api.get(`/payment/${testOrderId}/check_status/`)
      // 支付可能不存在，这是正常的
      if (res.status !== 200 && res.status !== 404) {
        throw new Error(`Unexpected status: ${res.status}`)
      }
    },
  },

  // 7. 通知系统
  {
    name: 'Get Notifications',
    fn: async () => {
      const res = await api.get('/notifications/notifications/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch notifications: ${res.status}`)
      }
    },
  },

  {
    name: 'Get Unread Count',
    fn: async () => {
      const res = await api.get('/notifications/notifications/unread_count/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch unread count: ${res.status}`)
      }
    },
  },

  // 8. 物流系统
  {
    name: 'Get Shipping Methods',
    fn: async () => {
      const res = await api.get('/logistics/shipping-methods/')
      if (res.status !== 200) {
        throw new Error(`Failed to fetch shipping methods: ${res.status}`)
      }
    },
  },

  // 9. 卖家系统
  {
    name: 'Get Seller Profile',
    fn: async () => {
      const res = await api.get('/sellers/profile/my_profile/')
      // 不是所有用户都是卖家，这是正常的
      if (res.status !== 200 && res.status !== 403) {
        throw new Error(`Unexpected status: ${res.status}`)
      }
    },
  },
]

// 主函数
async function runAllTests() {
  console.log('\n🚀 开始 Hi Mart E2E 测试套件\n')
  console.log('═'.repeat(50))

  // 首先登录
  console.log('\n【准备阶段】登录用户...\n')
  try {
    const res = await api.post('/users/login/', {
      username: 'testuser',
      password: 'testpass123',
    })
    if (res.data.access) {
      authToken = res.data.access
      api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
      console.log('✓ 登录成功\n')
    } else {
      console.warn('⚠ 登录失败，将以匿名身份进行测试\n')
    }
  } catch (err) {
    console.warn('⚠ 登录出错，继续测试...\n')
  }

  // 运行测试
  console.log('\n【执行测试】\n')
  for (const testCase of testSuite) {
    await runTest(testCase)
  }

  // 生成报告
  console.log('\n' + '═'.repeat(50))
  console.log('\n📊 测试结果总结\n')

  const passed = results.filter(r => r.passed).length
  const failed = results.filter(r => !r.passed).length
  const totalTime = results.reduce((sum, r) => sum + r.duration, 0)

  console.log(`总计: ${results.length} 个测试`)
  console.log(`✓ 通过: ${passed}`)
  console.log(`✗ 失败: ${failed}`)
  console.log(`⏱ 总耗时: ${totalTime.toFixed(2)}ms`)
  console.log(`⏱ 平均耗时: ${(totalTime / results.length).toFixed(2)}ms`)

  if (failed > 0) {
    console.log('\n【失败测试】\n')
    results.filter(r => !r.passed).forEach(r => {
      console.log(`• ${r.name}`)
      console.log(`  错误: ${r.error}`)
    })
  }

  const passRate = ((passed / results.length) * 100).toFixed(2)
  console.log(`\n通过率: ${passRate}%`)
  console.log('\n' + '═'.repeat(50) + '\n')

  process.exit(failed > 0 ? 1 : 0)
}

// 运行测试
runAllTests().catch(err => {
  console.error('测试执行失败:', err)
  process.exit(1)
})

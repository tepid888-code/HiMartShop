import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/pages/Products.vue')
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/pages/ProductDetail.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/pages/Cart.vue')
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/pages/Checkout.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue')
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/pages/Orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/pages/OrderDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payment/:id',
    name: 'Payment',
    component: () => import('@/pages/Payment.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/account',
    name: 'Account',
    component: () => import('@/pages/Account.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/seller/dashboard',
    name: 'SellerDashboard',
    component: () => import('@/pages/SellerDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/seller/withdrawals',
    name: 'SellerWithdrawals',
    component: () => import('@/pages/SellerWithdrawals.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/seller/messages',
    name: 'SellerMessages',
    component: () => import('@/pages/SellerMessages.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/pages/Notifications.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/logistics',
    name: 'Logistics',
    component: () => import('@/pages/Logistics.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(
  (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const authStore = useAuthStore()

    // 检查路由是否需要认证
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      // 未认证且需要认证，重定向到登录
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
    } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
      // 已认证且访问登录/注册页，重定向到首页
      next({ name: 'Home' })
    } else {
      next()
    }
  }
)

export default router

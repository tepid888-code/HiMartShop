<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-md sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center space-x-2">
            <span class="text-2xl font-bold text-indigo-600">Hi Mart</span>
          </RouterLink>

          <!-- 导航菜单 -->
          <div class="hidden md:flex space-x-8">
            <RouterLink
              to="/products"
              class="text-gray-700 hover:text-indigo-600 transition"
              active-class="text-indigo-600"
            >
              商品
            </RouterLink>
          </div>

          <!-- 用户菜单 -->
          <div class="flex items-center space-x-4">
            <!-- 购物车图标 -->
            <RouterLink
              to="/cart"
              class="relative text-gray-700 hover:text-indigo-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293a1 1 0 00.117 1.497A6 6 0 0012 21c1.657 0 3.233-.488 4.555-1.338"></path>
              </svg>
              <span v-if="cartStore.itemCount" class="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {{ cartStore.itemCount }}
              </span>
            </RouterLink>

            <!-- 用户账户 -->
            <div v-if="authStore.isAuthenticated" class="relative group">
              <button class="text-gray-700 hover:text-indigo-600 flex items-center space-x-2">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <span>{{ authStore.user?.username }}</span>
              </button>
              <!-- 下拉菜单 -->
              <div class="hidden group-hover:block absolute right-0 w-48 bg-white rounded-lg shadow-lg py-2 mt-2">
                <RouterLink
                  to="/account"
                  class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                >
                  账户信息
                </RouterLink>
                <RouterLink
                  to="/orders"
                  class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                >
                  我的订单
                </RouterLink>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100"
                >
                  登出
                </button>
              </div>
            </div>

            <!-- 登录/注册按钮 -->
            <div v-else class="flex space-x-2">
              <RouterLink
                to="/login"
                class="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
              >
                登录
              </RouterLink>
              <RouterLink
                to="/register"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                注册
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <router-view />

    <!-- 页脚 -->
    <footer class="bg-gray-900 text-white py-12 mt-12">
      <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-4 gap-8 mb-8">
          <div>
            <h3 class="text-lg font-semibold mb-4">关于Hi Mart</h3>
            <p class="text-gray-400 text-sm">肯尼亚领先的在线购物平台，为您提供优质商品和服务。</p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">快速链接</h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-gray-400 hover:text-white">关于我们</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">帮助中心</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">联系我们</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">政策</h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-gray-400 hover:text-white">隐私政策</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">服务条款</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">退货政策</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">联系信息</h3>
            <ul class="space-y-2 text-sm text-gray-400">
              <li>邮箱: info@himart.ke</li>
              <li>电话: +254 123 456 789</li>
              <li>地址: 肯尼亚，内罗毕</li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2026 Hi Mart Kenya. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h1 class="text-3xl font-bold text-center text-gray-900 mb-2">Hi Mart</h1>
        <p class="text-center text-gray-600 mb-8">肯尼亚在线购物平台</p>

        <!-- 错误提示 -->
        <div v-if="authStore.error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700">{{ authStore.error.message }}</p>
        </div>

        <!-- 登录表单 -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- 用户名 -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
              用户名
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              placeholder="输入用户名"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username }}</p>
          </div>

          <!-- 密码 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              密码
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              placeholder="输入密码"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password }}</p>
          </div>

          <!-- 记住我 -->
          <div class="flex items-center">
            <input
              id="remember"
              v-model="formData.rememberMe"
              type="checkbox"
              class="w-4 h-4 text-indigo-600 rounded"
              :disabled="authStore.loading"
            />
            <label for="remember" class="ml-2 text-sm text-gray-600">
              记住我
            </label>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition duration-200"
          >
            <span v-if="!authStore.loading">登 录</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              登 录 中...
            </span>
          </button>
        </form>

        <!-- 注册链接 -->
        <p class="text-center text-gray-600 mt-6">
          还没有账户？
          <RouterLink to="/register" class="text-indigo-600 hover:text-indigo-700 font-semibold">
            立即注册
          </RouterLink>
        </p>

        <!-- 演示账户提示 -->
        <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-800">
            <span class="font-semibold">演示账户:</span> 注册后即可使用
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = reactive({
  username: '',
  password: '',
  rememberMe: true,
})

const errors = reactive({
  username: '',
  password: '',
})

const validateForm = () => {
  errors.username = ''
  errors.password = ''

  if (!formData.username.trim()) {
    errors.username = '请输入用户名'
    return false
  }

  if (!formData.password) {
    errors.password = '请输入密码'
    return false
  }

  if (formData.password.length < 6) {
    errors.password = '密码至少6个字符'
    return false
  }

  return true
}

const handleLogin = async () => {
  authStore.clearError()

  if (!validateForm()) {
    return
  }

  try {
    await authStore.login(formData.username, formData.password)
    router.push('/products')
  } catch (error) {
    console.error('登录失败:', error)
  }
}
</script>

<style scoped>
/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

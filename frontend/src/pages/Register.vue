<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-8">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h1 class="text-3xl font-bold text-center text-gray-900 mb-2">创建账户</h1>
        <p class="text-center text-gray-600 mb-8">加入Hi Mart购物社区</p>

        <!-- 错误提示 -->
        <div v-if="authStore.error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700 text-sm">{{ authStore.error.message }}</p>
        </div>

        <!-- 注册表单 -->
        <form @submit.prevent="handleRegister" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="3-20个字符"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓</label>
            <input
              v-model="form.first_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">名</label>
            <input
              v-model="form.last_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">电话</label>
            <input
              v-model="form.phone"
              type="tel"
              placeholder="+254..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="至少8个字符"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              v-model="form.password_confirm"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
              :disabled="authStore.loading"
            />
            <p v-if="errors.password_confirm" class="text-red-500 text-sm mt-1">{{ errors.password_confirm }}</p>
          </div>

          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition"
          >
            {{ authStore.loading ? '创建中...' : '创建账户' }}
          </button>
        </form>

        <p class="text-center text-gray-600 mt-6 text-sm">
          已有账户？
          <RouterLink to="/login" class="text-indigo-600 hover:text-indigo-700 font-semibold">
            登录
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  password: '',
  password_confirm: '',
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})

const validateForm = () => {
  errors.username = ''
  errors.email = ''
  errors.password = ''
  errors.password_confirm = ''

  if (!form.username.trim() || form.username.length < 3) {
    errors.username = '用户名至少3个字符'
    return false
  }

  if (!form.email.includes('@')) {
    errors.email = '请输入有效邮箱'
    return false
  }

  if (form.password.length < 8) {
    errors.password = '密码至少8个字符'
    return false
  }

  if (form.password !== form.password_confirm) {
    errors.password_confirm = '密码不匹配'
    return false
  }

  return true
}

const handleRegister = async () => {
  authStore.clearError()

  if (!validateForm()) return

  try {
    await authStore.register(form)
    router.push('/products')
  } catch (error) {
    console.error('注册失败:', error)
  }
}
</script>

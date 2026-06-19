import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import { usersAPI } from '@/api/users'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  phone?: string
}

interface AuthError {
  message: string
  field?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref<AuthError | null>(null)

  const getUserFromStorage = () => {
    const stored = localStorage.getItem('user')
    if (stored) {
      user.value = JSON.parse(stored)
      isAuthenticated.value = true
    }
  }

  const setTokens = (access: string, refresh: string) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`
  }

  const login = async (username: string, password: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await usersAPI.login(username, password)
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      user.value = response.data.user
      isAuthenticated.value = true
      setTokens(response.data.access, response.data.refresh)
      return response.data
    } catch (err: any) {
      isAuthenticated.value = false
      error.value = {
        message: err.response?.data?.detail || '登录失败，请重试。',
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: {
    username: string
    email: string
    first_name: string
    last_name: string
    phone: string
    password: string
    password_confirm: string
  }) => {
    loading.value = true
    error.value = null
    try {
      const response = await usersAPI.register(userData)
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      user.value = response.data.user
      isAuthenticated.value = true
      setTokens(response.data.access, response.data.refresh)
      return response.data
    } catch (err: any) {
      isAuthenticated.value = false
      error.value = {
        message: err.response?.data?.detail || '注册失败，请重试。',
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await usersAPI.logout()
    } catch (err) {
      console.error('退出登录API调用失败:', err)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      user.value = null
      isAuthenticated.value = false
      delete api.defaults.headers.common['Authorization']
    }
  }

  const getCurrentUser = async () => {
    try {
      const response = await usersAPI.getProfile()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (err) {
      console.error('获取用户信息失败:', err)
      throw err
    }
  }

  const updateProfile = async (data: any) => {
    loading.value = true
    error.value = null
    try {
      const response = await usersAPI.updateProfile(data)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (err: any) {
      error.value = {
        message: err.response?.data?.detail || '更新失败，请重试。',
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  getUserFromStorage()

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    register,
    getCurrentUser,
    updateProfile,
    clearError,
    getUserFromStorage,
  }
})

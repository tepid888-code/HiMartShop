import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  phone?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)

  const getUserFromStorage = () => {
    const stored = localStorage.getItem('user')
    if (stored) {
      user.value = JSON.parse(stored)
      isAuthenticated.value = true
    }
  }

  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      const response = await api.post('/users/login/', { username, password })
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      user.value = response.data.user
      isAuthenticated.value = true
      return response.data
    } catch (error) {
      isAuthenticated.value = false
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    user.value = null
    isAuthenticated.value = false
  }

  const register = async (userData: any) => {
    loading.value = true
    try {
      const response = await api.post('/users/register/', userData)
      return response.data
    } finally {
      loading.value = false
    }
  }

  getUserFromStorage()

  return {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    register,
    getUserFromStorage,
  }
})

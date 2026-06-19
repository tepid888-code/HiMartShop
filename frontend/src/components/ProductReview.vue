<template>
  <div class="space-y-6">
    <!-- Review Form -->
    <div v-if="authStore.isAuthenticated" class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">写一条评价</h3>
      <form @submit.prevent="submitReview" class="space-y-4">
        <!-- Rating -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">评分</label>
          <div class="flex gap-2">
            <button
              v-for="i in 5"
              :key="i"
              type="button"
              @click="newReview.rating = i"
              :class="['text-3xl transition', i <= newReview.rating ? 'text-yellow-400' : 'text-gray-300']"
            >
              ★
            </button>
          </div>
        </div>

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
          <input
            v-model="newReview.title"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
            placeholder="评价标题"
          />
        </div>

        <!-- Comment -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">评价内容</label>
          <textarea
            v-model="newReview.comment"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
            rows="4"
            placeholder="分享您对这个产品的看法..."
          ></textarea>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition"
        >
          {{ loading ? '提交中...' : '提交评价' }}
        </button>
      </form>
    </div>

    <!-- Reviews List -->
    <div v-if="reviews.length > 0" class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-900">用户评价 ({{ reviews.length }})</h3>
      <div v-for="review in reviews" :key="review.id" class="bg-white rounded-lg shadow p-6">
        <!-- Author -->
        <div class="flex items-center justify-between mb-2">
          <span class="font-semibold text-gray-900">{{ review.user.username }}</span>
          <span class="text-sm text-gray-500">{{ formatDate(review.created_at) }}</span>
        </div>

        <!-- Rating -->
        <div class="flex items-center gap-1 mb-2">
          <span v-for="i in 5" :key="i" :class="['text-sm', i <= review.rating ? 'text-yellow-400' : 'text-gray-300']">
            ★
          </span>
          <span class="text-sm font-semibold text-gray-700 ml-2">{{ review.rating }}.0</span>
        </div>

        <!-- Title -->
        <h4 class="font-semibold text-gray-900 mb-1">{{ review.title }}</h4>

        <!-- Comment -->
        <p class="text-gray-700 mb-3">{{ review.comment }}</p>

        <!-- Delete Button -->
        <button
          v-if="authStore.user?.id === review.user.id"
          @click="deleteReview(review.id)"
          class="text-sm text-red-600 hover:text-red-700 font-semibold"
        >
          删除
        </button>
      </div>
    </div>

    <!-- No Reviews -->
    <div v-else class="bg-gray-50 rounded-lg p-6 text-center">
      <p class="text-gray-600">暂无评价</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { productsAPI } from '@/api/products'

const props = defineProps({
  productId: {
    type: Number,
    required: true,
  },
})

const authStore = useAuthStore()

const reviews = ref<any[]>([])
const loading = ref(false)
const newReview = ref({
  rating: 5,
  title: '',
  comment: '',
})

onMounted(async () => {
  await fetchReviews()
})

const fetchReviews = async () => {
  try {
    const response = await productsAPI.getReviews(props.productId)
    reviews.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch reviews:', error)
  }
}

const submitReview = async () => {
  if (!newReview.value.title || !newReview.value.comment) {
    alert('请填写标题和内容')
    return
  }

  try {
    loading.value = true
    await productsAPI.createReview(props.productId, newReview.value)
    await fetchReviews()
    newReview.value = { rating: 5, title: '', comment: '' }
  } catch (error) {
    console.error('Failed to submit review:', error)
    alert('提交评价失败')
  } finally {
    loading.value = false
  }
}

const deleteReview = async (reviewId: number) => {
  if (confirm('确定要删除这条评价吗？')) {
    try {
      await productsAPI.deleteReview(props.productId, reviewId)
      await fetchReviews()
    } catch (error) {
      console.error('Failed to delete review:', error)
    }
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-6">
    <!-- Categories -->
    <div class="mb-6">
      <h3 class="font-semibold text-gray-900 mb-3">分类</h3>
      <div class="space-y-2">
        <label class="flex items-center">
          <input
            type="radio"
            :value="null"
            v-model="selectedCategory"
            class="text-indigo-600"
          />
          <span class="ml-2 text-gray-700">全部</span>
        </label>
        <label v-for="category in categories" :key="category.id" class="flex items-center">
          <input
            type="radio"
            :value="category.id"
            v-model="selectedCategory"
            class="text-indigo-600"
          />
          <span class="ml-2 text-gray-700">{{ category.name }}</span>
        </label>
      </div>
    </div>

    <!-- Price Range -->
    <div class="mb-6">
      <h3 class="font-semibold text-gray-900 mb-3">价格范围</h3>
      <div class="space-y-2">
        <div>
          <label class="text-sm text-gray-600">最低价格</label>
          <input
            v-model.number="minPrice"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
            min="0"
            max="10000"
          />
        </div>
        <div>
          <label class="text-sm text-gray-600">最高价格</label>
          <input
            v-model.number="maxPrice"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
            min="0"
            max="10000"
          />
        </div>
      </div>
    </div>

    <!-- Rating Filter -->
    <div class="mb-6">
      <h3 class="font-semibold text-gray-900 mb-3">评分</h3>
      <div class="space-y-2">
        <label v-for="rating in [5, 4, 3, 2, 1]" :key="rating" class="flex items-center">
          <input
            type="radio"
            :value="rating"
            v-model.number="minRating"
            class="text-indigo-600"
          />
          <span class="ml-2 text-gray-700">
            <span v-for="i in 5" :key="i" class="text-yellow-400 text-sm">★</span>
            {{ rating }}星及以上
          </span>
        </label>
        <label class="flex items-center">
          <input
            type="radio"
            :value="0"
            v-model.number="minRating"
            class="text-indigo-600"
          />
          <span class="ml-2 text-gray-700">全部</span>
        </label>
      </div>
    </div>

    <!-- Buttons -->
    <div class="flex gap-2">
      <button
        @click="applyFilters"
        class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-lg transition"
      >
        应用筛选
      </button>
      <button
        @click="resetFilters"
        class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-2 rounded-lg transition"
      >
        重置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useProductsStore } from '@/stores/products'

const productsStore = useProductsStore()

const selectedCategory = ref<number | null>(null)
const minPrice = ref(0)
const maxPrice = ref(10000)
const minRating = ref(0)

const categories = ref(productsStore.categories)

const applyFilters = () => {
  productsStore.fetchProducts({
    category: selectedCategory.value,
    min_price: minPrice.value,
    max_price: maxPrice.value,
    page: 1,
  })
}

const resetFilters = () => {
  selectedCategory.value = null
  minPrice.value = 0
  maxPrice.value = 10000
  minRating.value = 0
  applyFilters()
}
</script>

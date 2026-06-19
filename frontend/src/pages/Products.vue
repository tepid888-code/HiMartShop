<template>
  <div class="bg-gray-50 min-h-screen">
    <!-- Search Section -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex gap-4">
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            type="text"
            placeholder="搜索产品..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
          />
          <button
            @click="handleSearch"
            class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-lg transition"
          >
            搜索
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-4 gap-6">
        <!-- Sidebar -->
        <div class="col-span-1">
          <FilterSidebar ref="filterSidebar" />
        </div>

        <!-- Products -->
        <div class="col-span-3">
          <!-- Sorting -->
          <div class="flex items-center justify-between mb-6">
            <span class="text-gray-700">共找到 {{ productsStore.pagination.count }} 个产品</span>
            <select
              v-model="productsStore.filters.ordering"
              @change="handleSortChange"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-transparent outline-none"
            >
              <option value="-created_at">最新发布</option>
              <option value="-sold">最多销量</option>
              <option value="price">价格从低到高</option>
              <option value="-price">价格从高到低</option>
              <option value="-rating">评分最高</option>
            </select>
          </div>

          <!-- Loading State -->
          <div v-if="productsStore.loading" class="text-center py-12">
            <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>

          <!-- Products Grid -->
          <div v-else-if="productsStore.products.length > 0" class="grid grid-cols-3 gap-6 mb-8">
            <ProductCard
              v-for="product in productsStore.products"
              :key="product.id"
              :product="product"
            />
          </div>

          <!-- No Products -->
          <div v-else class="text-center py-12">
            <p class="text-gray-600 text-lg">暂无产品</p>
          </div>

          <!-- Pagination -->
          <div v-if="productsStore.pagination.total_pages > 1" class="flex justify-center gap-2">
            <button
              @click="previousPage"
              :disabled="productsStore.pagination.current_page === 1"
              class="px-4 py-2 border border-gray-300 rounded-lg disabled:text-gray-400 disabled:bg-gray-50 hover:bg-gray-50"
            >
              上一页
            </button>

            <span class="px-4 py-2">
              第 {{ productsStore.pagination.current_page }} / {{ productsStore.pagination.total_pages }} 页
            </span>

            <button
              @click="nextPage"
              :disabled="productsStore.pagination.current_page === productsStore.pagination.total_pages"
              class="px-4 py-2 border border-gray-300 rounded-lg disabled:text-gray-400 disabled:bg-gray-50 hover:bg-gray-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import ProductCard from '@/components/ProductCard.vue'
import FilterSidebar from '@/components/FilterSidebar.vue'

const productsStore = useProductsStore()
const searchQuery = ref('')

onMounted(async () => {
  await productsStore.fetchCategories()
  await productsStore.fetchProducts()
  await productsStore.fetchWishlist()
})

const handleSearch = () => {
  productsStore.fetchProducts({
    search: searchQuery.value,
    page: 1,
  })
}

const handleSortChange = () => {
  productsStore.fetchProducts({ page: 1 })
}

const previousPage = () => {
  if (productsStore.pagination.current_page > 1) {
    productsStore.fetchProducts({
      page: productsStore.pagination.current_page - 1,
    })
  }
}

const nextPage = () => {
  if (productsStore.pagination.current_page < productsStore.pagination.total_pages) {
    productsStore.fetchProducts({
      page: productsStore.pagination.current_page + 1,
    })
  }
}
</script>


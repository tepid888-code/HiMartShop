<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Breadcrumb -->
      <nav class="flex mb-8 text-sm">
        <RouterLink to="/" class="text-indigo-600 hover:text-indigo-700">首页</RouterLink>
        <span class="mx-2 text-gray-500">/</span>
        <RouterLink to="/products" class="text-indigo-600 hover:text-indigo-700">产品</RouterLink>
        <span class="mx-2 text-gray-500">/</span>
        <span class="text-gray-900" v-if="product">{{ product.name }}</span>
      </nav>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Product Detail -->
      <div v-else-if="product" class="grid grid-cols-2 gap-8 mb-12">
        <!-- Images -->
        <div>
          <ImageCarousel :images="product.images" />
        </div>

        <!-- Info -->
        <div class="space-y-6">
          <!-- Title -->
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
            <div class="flex items-center gap-4">
              <div class="flex text-yellow-400">
                <span v-for="i in 5" :key="i" class="text-2xl">★</span>
              </div>
              <span class="text-lg text-gray-600">({{ product.review_count }} 条评价)</span>
            </div>
          </div>

          <!-- Price -->
          <div>
            <span class="text-4xl font-bold text-indigo-600">¥{{ product.price }}</span>
            <span v-if="product.original_price" class="text-lg text-gray-500 line-through ml-4">
              ¥{{ product.original_price }}
            </span>
          </div>

          <!-- Stock Status -->
          <div>
            <span
              :class="[
                'inline-block text-lg font-semibold px-4 py-2 rounded',
                product.stock > 0
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              ]"
            >
              {{ product.stock > 0 ? `库存充足 (${product.stock})` : '缺货' }}
            </span>
          </div>

          <!-- Seller -->
          <div class="border-t border-b py-4">
            <p class="text-gray-600">
              <span class="font-semibold">卖家:</span> {{ product.seller?.username }}
            </p>
            <p class="text-gray-600">
              <span class="font-semibold">商店:</span> {{ product.store_name }}
            </p>
            <p class="text-gray-600">
              <span class="font-semibold">条件:</span> {{ getConditionLabel(product.condition) }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex gap-4">
            <button
              @click="addToCart"
              :disabled="product.stock === 0"
              class="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
            >
              加入购物车
            </button>
            <button
              @click="toggleWishlist"
              :class="[
                'flex-1 font-semibold py-3 rounded-lg transition border-2',
                isInWishlist
                  ? 'bg-red-50 border-red-600 text-red-600 hover:bg-red-100'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
            >
              {{ isInWishlist ? '❤ 收藏' : '♡ 收藏' }}
            </button>
          </div>

          <!-- Description -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">产品描述</h3>
            <p class="text-gray-700 leading-relaxed">{{ product.description }}</p>
          </div>
        </div>
      </div>

      <!-- Reviews Section -->
      <div v-if="product" class="bg-white rounded-lg shadow p-8">
        <ProductReview :product-id="productId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import ImageCarousel from '@/components/ImageCarousel.vue'
import ProductReview from '@/components/ProductReview.vue'

const route = useRoute()
const productsStore = useProductsStore()
const cartStore = useCartStore()

const productId = parseInt(route.params.id as string)
const loading = ref(false)

const product = computed(() => productsStore.currentProduct)

const isInWishlist = computed(() => {
  return productsStore.isInWishlist(productId)
})

onMounted(async () => {
  loading.value = true
  try {
    await productsStore.fetchProductDetail(productId)
    await productsStore.fetchWishlist()
  } finally {
    loading.value = false
  }
})

const addToCart = () => {
  if (product.value) {
    cartStore.addItem({
      id: product.value.id,
      name: product.value.name,
      price: product.value.price,
      image: product.value.images?.[0]?.image,
    })
    alert('产品已添加到购物车')
  }
}

const toggleWishlist = async () => {
  await productsStore.toggleWishlist(productId)
}

const getConditionLabel = (condition: string) => {
  const labels: { [key: string]: string } = {
    new: '全新',
    used: '二手',
    refurbished: '翻新',
  }
  return labels[condition] || condition
}
</script>


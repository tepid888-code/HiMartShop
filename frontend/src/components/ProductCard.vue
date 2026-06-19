<template>
  <div class="bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden">
    <!-- Image -->
    <div class="relative h-48 bg-gray-200 overflow-hidden group cursor-pointer">
      <img
        v-if="primaryImage"
        :src="primaryImage"
        :alt="product.name"
        class="w-full h-full object-cover group-hover:scale-105 transition"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </div>

      <!-- Wishlist Button -->
      <button
        @click="toggleWishlist"
        class="absolute top-2 right-2 bg-white rounded-full p-2 shadow hover:shadow-lg transition"
      >
        <svg
          :class="['w-6 h-6 transition', isWishlisted ? 'fill-red-500 text-red-500' : 'text-gray-400']"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="p-4">
      <!-- Name -->
      <h3 class="font-semibold text-gray-900 truncate mb-2">{{ product.name }}</h3>

      <!-- Rating -->
      <div class="flex items-center mb-3">
        <div class="flex text-yellow-400">
          <span v-for="i in 5" :key="i" class="text-sm">★</span>
        </div>
        <span class="ml-2 text-sm text-gray-600">{{ product.rating }} ({{ product.review_count }})</span>
      </div>

      <!-- Price -->
      <div class="flex items-baseline gap-2 mb-3">
        <span class="text-lg font-bold text-indigo-600">¥{{ product.price }}</span>
        <span v-if="product.original_price" class="text-sm text-gray-500 line-through">
          ¥{{ product.original_price }}
        </span>
      </div>

      <!-- Stock Status -->
      <div class="mb-3">
        <span
          :class="[
            'text-xs font-semibold px-2 py-1 rounded',
            product.stock > 0
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          ]"
        >
          {{ product.stock > 0 ? `库存: ${product.stock}` : '缺货' }}
        </span>
      </div>

      <!-- Add to Cart Button -->
      <button
        @click="addToCart"
        :disabled="product.stock === 0"
        class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition"
      >
        加入购物车
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const cartStore = useCartStore()
const productsStore = useProductsStore()

const primaryImage = computed(() => {
  if (props.product.images && props.product.images.length > 0) {
    const primary = props.product.images.find((img: any) => img.is_primary)
    return primary?.image || props.product.images[0]?.image
  }
  return null
})

const isWishlisted = computed(() => {
  return productsStore.isInWishlist(props.product.id)
})

const addToCart = () => {
  cartStore.addItem(props.product)
}

const toggleWishlist = async () => {
  await productsStore.toggleWishlist(props.product.id)
}
</script>

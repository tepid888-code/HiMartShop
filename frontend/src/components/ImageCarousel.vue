<template>
  <div class="space-y-4">
    <!-- Main Image -->
    <div class="relative bg-gray-100 rounded-lg overflow-hidden h-96">
      <img
        v-if="images[currentIndex]"
        :src="images[currentIndex].image"
        :alt="images[currentIndex].alt_text"
        class="w-full h-full object-contain"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-24 h-24 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </div>

      <!-- Navigation Arrows -->
      <button
        v-if="images.length > 1"
        @click="previousImage"
        class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-2 shadow hover:shadow-lg transition"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
      </button>

      <button
        v-if="images.length > 1"
        @click="nextImage"
        class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-2 shadow hover:shadow-lg transition"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </button>

      <!-- Image Counter -->
      <div class="absolute bottom-4 right-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded text-sm">
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>
    </div>

    <!-- Thumbnail Gallery -->
    <div v-if="images.length > 1" class="flex gap-2 overflow-x-auto pb-2">
      <button
        v-for="(image, index) in images"
        :key="index"
        @click="currentIndex = index"
        :class="[
          'flex-shrink-0 w-20 h-20 rounded border-2 transition',
          currentIndex === index ? 'border-indigo-600' : 'border-gray-300 hover:border-gray-400'
        ]"
      >
        <img :src="image.image" :alt="image.alt_text" class="w-full h-full object-cover rounded" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => [],
  },
})

const currentIndex = ref(0)

const images = computed(() => {
  return props.images || []
})

const previousImage = () => {
  currentIndex.value = (currentIndex.value - 1 + images.value.length) % images.value.length
}

const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % images.value.length
}
</script>

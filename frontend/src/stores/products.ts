import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productsAPI } from '@/api/products'

interface Product {
  id: number
  name: string
  slug: string
  price: number
  original_price?: number
  rating: number
  review_count: number
  category: number
  store: number
  is_active: boolean
  created_at: string
}

interface ProductDetail extends Product {
  description: string
  images: any[]
  sku: string
  condition: string
  stock: number
  sold: number
  seller: any
  category_name: string
  store_name: string
}

interface Category {
  id: number
  name: string
  slug: string
  description: string
  image?: string
  parent?: number
  children?: Category[]
}

interface Filters {
  category: number | null
  min_price: number
  max_price: number
  search: string
  ordering: string
  page: number
  page_size: number
}

export const useProductsStore = defineStore('products', () => {
  const products = ref<Product[]>([])
  const currentProduct = ref<ProductDetail | null>(null)
  const categories = ref<Category[]>([])
  const wishlist = ref<any[]>([])

  const filters = ref<Filters>({
    category: null,
    min_price: 0,
    max_price: 10000,
    search: '',
    ordering: '-created_at',
    page: 1,
    page_size: 20,
  })

  const pagination = ref({
    count: 0,
    current_page: 1,
    total_pages: 1,
  })

  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCategories = async () => {
    try {
      loading.value = true
      const response = await productsAPI.getCategories()
      categories.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch categories'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProducts = async (newFilters?: Partial<Filters>) => {
    try {
      loading.value = true
      if (newFilters) {
        filters.value = { ...filters.value, ...newFilters }
      }

      const params = {
        page: filters.value.page,
        page_size: filters.value.page_size,
        ordering: filters.value.ordering,
      }

      if (filters.value.category) {
        Object.assign(params, { category: filters.value.category })
      }
      if (filters.value.min_price > 0) {
        Object.assign(params, { min_price: filters.value.min_price })
      }
      if (filters.value.max_price < 10000) {
        Object.assign(params, { max_price: filters.value.max_price })
      }
      if (filters.value.search) {
        Object.assign(params, { search: filters.value.search })
      }

      const response = await productsAPI.getProducts(params)
      products.value = response.data.results || response.data
      pagination.value = {
        count: response.data.count || 0,
        current_page: filters.value.page,
        total_pages: Math.ceil((response.data.count || 0) / filters.value.page_size),
      }
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch products'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProductDetail = async (id: number) => {
    try {
      loading.value = true
      const response = await productsAPI.getProductDetail(id)
      currentProduct.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch product details'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchWishlist = async () => {
    try {
      const response = await productsAPI.getWishlist()
      wishlist.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch wishlist'
    }
  }

  const addToWishlist = async (productId: number) => {
    try {
      const response = await productsAPI.addToWishlist(productId)
      wishlist.value.push(response.data)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to add to wishlist'
      throw err
    }
  }

  const removeFromWishlist = async (wishlistItemId: number) => {
    try {
      await productsAPI.removeFromWishlist(wishlistItemId)
      wishlist.value = wishlist.value.filter(item => item.id !== wishlistItemId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to remove from wishlist'
      throw err
    }
  }

  const toggleWishlist = async (productId: number) => {
    const found = wishlist.value.find(item => item.product?.id === productId)
    if (found) {
      await removeFromWishlist(found.id)
    } else {
      await addToWishlist(productId)
    }
  }

  const isInWishlist = computed(() => {
    return (productId: number) => wishlist.value.some(item => item.product?.id === productId)
  })

  return {
    products,
    currentProduct,
    categories,
    filters,
    pagination,
    loading,
    error,
    wishlist,
    fetchCategories,
    fetchProducts,
    fetchProductDetail,
    fetchWishlist,
    addToWishlist,
    removeFromWishlist,
    toggleWishlist,
    isInWishlist,
  }
})

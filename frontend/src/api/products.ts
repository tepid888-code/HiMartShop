import api from './client'

export const productsAPI = {
  // Categories
  getCategories: () => api.get('/products/categories/'),
  getCategoryDetail: (id: number) => api.get(`/products/categories/${id}/`),

  // Products
  getProducts: (params: any) => api.get('/products/', { params }),
  getProductDetail: (id: number) => api.get(`/products/${id}/`),

  // Reviews
  getReviews: (productId: number, page: number = 1) =>
    api.get(`/products/${productId}/reviews/`, { params: { page } }),
  createReview: (productId: number, data: any) =>
    api.post(`/products/${productId}/reviews/`, data),
  deleteReview: (productId: number, reviewId: number) =>
    api.delete(`/products/${productId}/reviews/${reviewId}/`),

  // Wishlist
  getWishlist: () => api.get('/products/wishlist/'),
  addToWishlist: (productId: number) =>
    api.post('/products/wishlist/', { product_id: productId }),
  removeFromWishlist: (wishlistItemId: number) =>
    api.delete(`/products/wishlist/${wishlistItemId}/`),
}

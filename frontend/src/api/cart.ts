import api from './client'

export const cartAPI = {
  // 获取购物车
  getCart: () => api.get('/cart/'),

  // 添加到购物车
  addToCart: (productId: number, quantity: number = 1) =>
    api.post('/cart/add/', { product_id: productId, quantity }),

  // 更新购物车项目
  updateCartItem: (itemId: number, quantity: number) =>
    api.patch('/cart/update_item/', { item_id: itemId, quantity }),

  // 移除购物车项目
  removeCartItem: (itemId: number) =>
    api.delete('/cart/remove_item/', { data: { item_id: itemId } }),

  // 清空购物车
  clearCart: () =>
    api.delete('/cart/clear/'),
}

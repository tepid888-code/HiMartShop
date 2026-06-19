import api from './client'

export const promotionsAPI = {
  // 获取可用优惠券
  getCoupons: (params?: any) =>
    api.get('/promotions/coupons/', { params }),

  // 验证优惠券（不需要认证）
  validateCoupon: (code: string, amount: number) =>
    api.post('/promotions/coupons/validate/', { code, amount }),

  // 应用优惠券（需要认证）
  applyCoupon: (code: string, amount: number) =>
    api.post('/promotions/coupons/apply/', { code, amount }),
}

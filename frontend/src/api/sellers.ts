import api from './client'

export const sellersAPI = {
  // 卖家资料
  getMyProfile: () => api.get('/sellers/profile/my_profile/'),

  // 卖家仪表板
  getDashboard: () => api.get('/sellers/profile/dashboard/'),

  // 提现管理
  requestWithdrawal: (data: any) =>
    api.post('/sellers/withdrawals/request_withdrawal/', data),

  // 消息管理
  replyToMessage: (id: number, data: any) =>
    api.post(`/sellers/messages/${id}/reply/`, data),
}

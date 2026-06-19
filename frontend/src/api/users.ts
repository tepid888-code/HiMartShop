import api from './client'

export const usersAPI = {
  register: (data: {
    username: string
    email: string
    first_name: string
    last_name: string
    phone: string
    password: string
    password_confirm: string
  }) => api.post('/users/register/', data),

  login: (username: string, password: string) =>
    api.post('/users/login/', { username, password }),

  logout: () => api.post('/users/logout/'),

  getProfile: () => api.get('/users/me/'),

  updateProfile: (data: any) => api.patch('/users/me/', data),

  getAddresses: () => api.get('/users/me/addresses/'),

  addAddress: (data: any) => api.post('/users/me/add_address/', data),

  updateAddress: (id: number, data: any) => api.patch(`/users/addresses/${id}/`, data),

  deleteAddress: (id: number) => api.delete(`/users/addresses/${id}/`),
}

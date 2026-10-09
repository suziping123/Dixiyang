import http from '@/utils/http'

export interface AdminTotals {
  users: number
  novels: number
  posts: number
  sessions: number
}

export interface AdminStats {
  totals: AdminTotals
  postCategories: { category: string; count: number }[]
  postTrend: { date: string; count: number }[]
}

export interface AdminUserItem {
  id: number
  username: string
  nickname: string
  email: string
  role: 'user' | 'admin'
  createTime: string
}

export const getAdminStats = () => http.get('/admin/stats')

export const getAdminUsers = (page = 1, pageSize = 20, keyword?: string) =>
  http.get('/admin/users', { params: { page, pageSize, keyword: keyword || undefined } })

export const updateUserRole = (userId: number, role: 'user' | 'admin') =>
  http.put(`/admin/users/${userId}/role`, { role })

// 管理后台 API（仅后台 token 可用；用户端 token 一律被后端拒绝）
import http from './http'

export interface AdminLoginUser {
  userId: number
  username: string
  nickname: string
  email: string
  role: string
}

export interface AdminSession {
  token: string
  user: AdminLoginUser
}

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

/** 后台登录（独立端点：仅 role=admin 放行，独立会话不顶用户端） */
export const adminLogin = (username: string, password: string) =>
  http.post('/admin/auth/login', { username, password })

export const getAdminStats = () => http.get('/admin/stats')

export const getAdminUsers = (page = 1, pageSize = 20, keyword?: string) =>
  http.get('/admin/users', { params: { page, pageSize, keyword: keyword || undefined } })

export const updateUserRole = (userId: number, role: 'user' | 'admin') =>
  http.put(`/admin/users/${userId}/role`, { role })

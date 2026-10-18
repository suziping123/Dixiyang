/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-10-09 21:18:55
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-10-18 21:25:06
 * @FilePath: \Dixiyang\dixiyang-vue\Dixiyang-vue3\src\api\adminApi.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
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

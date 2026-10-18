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

// ---------- 内容管理：广场帖子 ----------

export interface AdminPostItem {
  id: number
  category: string
  title: string
  summary: string | null
  authorId: number
  authorName: string
  status: 'published' | 'removed'
  adminRemoved: boolean
  viewCount: number
  likeCount: number
  commentCount: number
  collectCount: number
  createTime: string
}

export interface AdminPostDetail extends AdminPostItem {
  content: string
  images: string[]
  tags: string[]
  attachment: { type: string; meta: string | null } | null
  updateTime: string
}

export interface AdminCommentItem {
  id: number
  postId: number
  authorId: number
  authorName: string
  content: string
  createTime: string
}

export const getAdminPosts = (params: {
  page?: number
  pageSize?: number
  status?: string
  category?: string
  keyword?: string
}) =>
  http.get('/admin/posts', {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 20,
      status: params.status || undefined,
      category: params.category || undefined,
      keyword: params.keyword || undefined,
    },
  })

export const getAdminPost = (id: number) => http.get(`/admin/posts/${id}`)

export const setAdminPostStatus = (id: number, status: 'published' | 'removed') =>
  http.put(`/admin/posts/${id}/status`, { status })

export const deleteAdminPost = (id: number) => http.delete(`/admin/posts/${id}`)

export const getAdminPostComments = (id: number, page = 1, pageSize = 20) =>
  http.get(`/admin/posts/${id}/comments`, { params: { page, pageSize } })

export const deleteAdminComment = (id: number) => http.delete(`/admin/comments/${id}`)

// ---------- 内容管理：灵感墙便签 ----------

export interface AdminStickyItem {
  id: number
  userId: number
  userName: string
  color: string
  done: boolean
  inPool: boolean
  content: string
  images: string[]
  createTime: string
  updateTime: string
}

export const getAdminSticky = (params: { page?: number; pageSize?: number; keyword?: string; done?: boolean | null }) =>
  http.get('/admin/sticky', {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 20,
      keyword: params.keyword || undefined,
      done: params.done ?? undefined,
    },
  })

export const deleteAdminSticky = (id: number) => http.delete(`/admin/sticky/${id}`)

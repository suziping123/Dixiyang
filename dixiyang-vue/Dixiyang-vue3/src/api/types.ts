// API 响应基础类型
export interface ApiResponse<T = unknown> {
  code: number
  msg: string
  data: T
}

// 登录响应数据
export interface LoginResponse {
  token: string
  userId: number
  username: string
  nickname: string
  email?: string
}

// 注册响应数据
export interface RegisterResponse {
  userId: number
  username: string
  nickname: string
}

// 分页响应类型
export interface PageResponse<T = unknown> {
  records: T[]
  total: number
  page: number
  pageSize: number
}

// 小说相关类型
export interface Novel {
  id?: number
  title: string
  author?: string
  description?: string
  cover?: string
  userId?: number
  createdAt?: string
  updatedAt?: string
}

// 角色相关类型
export interface Character {
  id?: number
  novelId?: number
  name: string
  avatar?: string
  description?: string
  personality?: string
  background?: string
  extra?: string | Record<string, unknown>
}

// 故事情节节点类型
export interface StoryNode {
  id?: number
  novelId?: number
  title: string
  content?: string
  positionX?: number
  positionY?: number
  parentId?: number
  orderNum?: number
}

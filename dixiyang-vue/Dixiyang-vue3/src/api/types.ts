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

// 分页返回结果类型（对齐后端 MyBatis-Plus）
export interface PageResult<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

// 小说相关类型（后端 NovelVO 使用 @JsonProperty 返回 snake_case）
export interface Novel {
  id: number
  title: string
  pen_name: string
  description: string
  cover_url: string
  createTime?: string
  updateTime?: string
  char_count?: number
  node_count?: number
  relation_count?: number
}

// 小说创建 DTO
export interface NovelDTO {
  title: string
  penName: string
  description: string
  coverUrl?: string
}

// 角色相关类型（对齐后端 CharacterVO）
export interface Character {
  id: number
  novelId: number
  name: string
  gender?: string
  age?: number
  appearance?: string
  background?: string
  personality?: string
  extra?: Record<string, unknown>
  createTime?: string
}

// 角色创建 DTO
export interface CharacterDTO {
  novelId: number
  name: string
  gender?: string
  age?: number
  appearance?: string
  background?: string
  personality?: string
  extra?: string
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

// 时间线类型
export interface Timeline {
  id?: number
  novelId: number
  name: string
  parentId?: number | null
  description?: string
  createTime?: string
}

// 时间线故事节点（扩展类型）
export interface TimelineNode {
  id: number
  novelId: number
  timelineId: number
  title: string
  content: string
  eventDate: string
  eventType: 'birth' | 'war' | 'politics' | 'major'
  importance: number
  characterNames: string
  tags: string
}

// ===== 小说编辑器：卷 =====
export interface Volume {
  id: number
  novel_id: number
  title: string
  sort_order: number
  description?: string
  create_time?: string
  update_time?: string
}

export interface VolumeDTO {
  title: string
  sort_order?: number
  description?: string
}

// ===== 小说编辑器：章节 =====
export interface Chapter {
  id: number
  novel_id: number
  volume_id?: number | null
  title: string
  sort_order: number
  content_path?: string | null
  content_hash?: string | null
  content_size: number
  version: number
  local_version: number
  word_count: number
  create_time?: string
  update_time?: string
}

export interface ChapterDTO {
  novel_id: number
  volume_id?: number | null
  title: string
  sort_order?: number
}

// 云端正文
export interface ChapterContent {
  chapterId: number
  title: string
  version: number
  contentHash: string | null
  content: string
  wordCount: number
  updatedAt: string | null
}

// 保存正文结果
export interface SaveContentResult {
  chapterId: number
  version: number
  contentHash: string
  contentPath?: string
  wordCount?: number
  hasConflict: boolean
  serverVersion?: number
  serverHash?: string
}

// 冲突检测结果
export interface ConflictResult {
  hasConflict: boolean
  serverVersion: number
  serverHash: string
}

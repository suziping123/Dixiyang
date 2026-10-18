// 后台专用 axios 实例：独立 token 键（admin_token）+ 后台登录态失效处理（回后台登录页，不影响用户端）
import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { clearAdminSession, getAdminToken } from '../utils/session'

const http: AxiosInstance = axios.create({ baseURL: '/api', timeout: 10000 })

// 控制台为 hash 路由，登录页地址固定为 #/login
const LOGIN_HASH = '#/login'
let redirecting = false

// hash 变化（已被路由带到登录页）后解除防重复跳转锁
window.addEventListener('hashchange', () => {
  if (window.location.hash === LOGIN_HASH) redirecting = false
})

// 从后端响应体提取提示（FastAPI: detail / 业务: msg）
function extractMessage(data: unknown): string | undefined {
  if (!data || typeof data !== 'object') return undefined
  const obj = data as Record<string, unknown>
  const text = obj.msg ?? obj.message ?? obj.detail
  return typeof text === 'string' && text.trim() ? text : undefined
}

/** 后台登录态失效：清后台会话并回后台登录页（401=未登录/被顶号；403=非后台令牌/权限不足） */
function handleAdminAuthFail(message?: string) {
  clearAdminSession()
  if (window.location.hash === LOGIN_HASH) return
  if (redirecting) return
  redirecting = true
  if (message) ElMessage.warning(message)
  window.location.hash = LOGIN_HASH
}

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAdminToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    // 字符串响应直接返回（与用户端一致）
    if (typeof res === 'string') return res
    // 业务码 401（后端 Result.unauthorized）：会话失效
    if (res && typeof res === 'object' && (res as { code?: number }).code === 401) {
      handleAdminAuthFail(extractMessage(res))
      return Promise.reject(new Error((res as { msg?: string }).msg || '后台会话已失效'))
    }
    return res
  },
  (error) => {
    const status = error.response?.status
    // HTTP 401/403（require_admin 依赖拒绝）：统一按登录态失效处理
    if (status === 401 || status === 403) {
      handleAdminAuthFail(extractMessage(error.response?.data))
      return Promise.reject(new Error('后台登录态已失效'))
    }
    // 规范 JSON 错误透传（与用户端一致）
    if (error.response && error.response.data) {
      return Promise.resolve(error.response.data)
    }
    return Promise.resolve({ code: -1, msg: error.message || '网络异常，请重试', data: null })
  },
)

// 演示模式（GitHub Pages）：复用用户端同一套 mock 适配器，请求不出网
if (import.meta.env.VITE_DEMO === '1') {
  import('@/utils/demo/adapter')
    .then((m) => m.installDemoAdapter(http))
    .catch(() => {})
}

export default http

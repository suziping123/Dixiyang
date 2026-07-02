// src/utils/http.ts
import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import type { ApiResponse } from '@/api/types'

const http: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：自动携带 Token
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器（重点修复：区分业务成功/失败）
http.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    // 1. 字符串直接返回（兼容聊天接口）
    if (typeof res === 'string') {
      return res
    }
    // 2. 对象直接返回，无论 code 是 200 还是 500，都由调用者自己判断
    return res
  },
  (error) => {
    // HTTP 状态码非 2xx（如 404、500、超时等）：这才是真正的网络/服务器异常
    // 但即使如此，如果后端依然返回了规范的 JSON（如 { code, msg }），我们也透传下去
    if (error.response && error.response.data) {
      // 后端返回了规范的业务数据，透传给调用者（走 resolve）
      return Promise.resolve(error.response.data)
    }
    // 真正的网络问题（断网、超时等），构造一个标准的业务错误对象返回
    return Promise.resolve({
      code: -1,
      msg: error.message || '网络异常，请重试',
      data: null
    } as ApiResponse<null>)
  }
)

// 类型断言辅助函数 - 用于处理拦截器转换后的响应
export function assertApiResponse<T>(response: unknown): ApiResponse<T> {
  return response as ApiResponse<T>
}

// 类型断言辅助函数 - 用于字符串响应（聊天接口）
export function assertStringResponse(response: unknown): string {
  return response as string
}

export default http

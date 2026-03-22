// src/utils/http.ts
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：自动携带 Token
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器（重点修复：区分业务成功/失败）
http.interceptors.response.use(
  (response) => {
    const res = response.data
    // 业务成功（code=200）：正常返回
    if (res.code === 200) {
      return res
    }
    // 业务失败（比如code=400，标题重复）：抛出自定义错误，让catch捕获
    return Promise.reject(new Error(res.msg || '操作失败'))
  },
  (error) => {
    // 网络错误/服务器错误（比如500）：提取错误信息
    const errMsg = error.response?.data?.msg || error.message || '网络异常，请重试'
    return Promise.reject(new Error(errMsg))
  }
)

export default http

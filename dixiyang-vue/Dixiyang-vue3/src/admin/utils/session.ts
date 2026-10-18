// 后台会话工具：独立存储键（admin_*），与用户端登录态（token/username/...）零冲突——
// 同一浏览器可同时登录用户端与后台，互不顶号
import { isTokenValid } from '@/utils/auth'

export function getAdminToken(): string | null {
  return localStorage.getItem('admin_token')
}

export function hasValidAdminToken(): boolean {
  return isTokenValid(getAdminToken())
}

export function setAdminSession(token: string, username: string, nickname: string): void {
  localStorage.setItem('admin_token', token)
  localStorage.setItem('admin_username', username)
  localStorage.setItem('admin_nickname', nickname)
}

export function clearAdminSession(): void {
  ;['admin_token', 'admin_username', 'admin_nickname'].forEach((k) => localStorage.removeItem(k))
}

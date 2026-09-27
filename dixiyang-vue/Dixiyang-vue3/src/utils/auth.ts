// 登录态工具：token 有效性校验与本地登录态清理

/** 校验 JWT 是否有效（存在、非脏值、未过期） */
export function isTokenValid(token: string | null): boolean {
  if (!token || token === 'undefined' || token === 'null') return false
  try {
    const base64 = token.split('.')[1]?.replace(/-/g, '+').replace(/_/g, '/')
    if (!base64) return false
    const payload = JSON.parse(atob(base64)) as { exp?: number }
    if (typeof payload.exp === 'number' && payload.exp * 1000 <= Date.now()) return false
    return true
  } catch {
    return false
  }
}

/** 清除本地登录态（仅登录相关字段，保留主题等其它配置） */
export function clearAuth(): void {
  ;['token', 'username', 'userId', 'nickname', 'email'].forEach((k) => localStorage.removeItem(k))
}

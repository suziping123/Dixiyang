import { ElMessage } from 'element-plus'

/** 解包 Result 结构：code===200 返回 data，否则提示 msg 并返回 null */
export function unwrap<T>(res: unknown): T | null {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

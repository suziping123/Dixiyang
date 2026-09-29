/**
 * 错误文案映射：后端/网络原始错误 → 用户可读的友好文案
 *
 * 约定：原始信息只写 console，绝不直接上屏（避免暴露技术细节）。
 * 优先级：精确匹配 → 关键词匹配 → 兜底文案。
 */

/** 精确匹配表：后端常见原话 */
const EXACT: Record<string, string> = {
  '用户不存在': '账号不存在，请检查后重试',
  '密码错误': '账号或密码不正确',
  '用户名或密码错误': '账号或密码不正确',
  '验证码错误': '验证码不正确，请重新输入',
  '验证码已过期': '验证码已过期，请重新获取',
  '邮箱已被注册': '该邮箱已被注册',
  '用户名已被注册': '该用户名已被注册',
  '登录已过期': '登录已过期，请重新登录',
  '网络异常，请重试': '网络异常，请稍后重试',
}

/** 关键词匹配表：[正则, 友好文案]，按顺序短路 */
const KEYWORDS: Array<[RegExp, string]> = [
  [/验证码|verify\s*code|captcha/i, '验证码不正确或已过期，请重新获取'],
  [/密码|password/i, '账号或密码不正确'],
  [/登录已过期|未登录|unauthorized|token/i, '登录已过期，请重新登录'],
  [/权限|forbidden|无权/i, '暂无权限执行该操作'],
  [/不存在|not\s*found|已删除/i, '目标不存在或已被删除'],
  [/已存在|重复|duplicate|conflict/i, '该记录已存在，请勿重复提交'],
  [/邮箱|email/i, '邮箱格式不正确'],
  [/超时|timeout|网络|network|ECONN/i, '网络异常，请稍后重试'],
  [/服务器|server|500|502|503/i, '服务器开小差了，请稍后重试'],
]

const FALLBACK = '操作失败，请稍后再试'

/**
 * 把原始错误转成用户可读文案；原始信息仅写入 console
 * @param raw 后端 msg / Error.message 等原始文本
 * @param fallback 兜底文案（默认「操作失败，请稍后再试」）
 */
export function friendlyError(raw?: string | null, fallback: string = FALLBACK): string {
  const text = (raw ?? '').trim()
  if (!text) return fallback
  // 原始信息只进控制台，不上屏
  console.error('[errorText]', text)

  if (EXACT[text]) return EXACT[text]
  for (const [re, msg] of KEYWORDS) {
    if (re.test(text)) return msg
  }
  return fallback
}

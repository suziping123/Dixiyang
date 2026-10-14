// 演示模式 axios 适配器：请求不出网，按 URL 返回 mock 响应（含 150-350ms 模拟延迟）
// 未命中的接口统一兜底 {code:200,data:null}（页面不炸），console.info 留痕便于补 mock
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { makeDemoToken } from './index'
import { DEMO_NOVELS, DEMO_USER } from './mockData'

type Body = { code: number; msg: string; data: unknown }

const ok = (data: unknown, msg = 'ok'): Body => ({ code: 200, msg, data })
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** 从 adapter 配置中取 JSON 请求体（axios 已序列化为字符串） */
function jsonBody(config: AxiosRequestConfig): Record<string, unknown> {
  if (typeof config.data === 'string') {
    try {
      return JSON.parse(config.data) as Record<string, unknown>
    } catch {
      return {}
    }
  }
  return (config.data as Record<string, unknown>) ?? {}
}

/** 路由表：方法不敏感，按 URL 正则匹配 */
const routes: Array<[RegExp, (config: AxiosRequestConfig) => Body | Promise<Body>]> = [
  // ── 认证 ──
  [/^\/auth\/login$/, () => ok({ token: makeDemoToken(), user: DEMO_USER })],
  [/^\/auth\/login-by-code$/, () => ok({ token: makeDemoToken(), user: DEMO_USER })],
  [/^\/auth\/send-code$/, () => ok(null, '演示模式：验证码已"发送"，任意 6 位数字均可通过')],
  [/^\/auth\/register$/, () => ok({ userId: 2, username: '新用户', nickname: '新用户' }, '演示模式：注册成功（假）')],
  // ── 小说 ──
  [
    /^\/novel\/listall$/,
    (config) => {
      const p = (config.params ?? {}) as Record<string, number>
      const pageNum = Number(p.page ?? p.current ?? 1)
      const size = Number(p.pageSize ?? p.page_size ?? 10)
      const start = (pageNum - 1) * size
      const records = DEMO_NOVELS.slice(start, start + size)
      return ok({ records, total: DEMO_NOVELS.length, size, current: pageNum, pages: 1 })
    },
  ],
  [/^\/novel\/create$/, () => ok({ ...DEMO_NOVELS[0], id: Date.now() % 100000 }, '演示模式：创建成功（假）')],
  [/^\/novel\/delete\/\d+$/, () => ok(null, '演示模式：删除成功（假）')],
  [/^\/novel\/\d+$/, () => ok(DEMO_NOVELS[0])],
  // ── 上传（假 URL，页面显示占位）──
  [/^\/upload\//, () => ok('', '演示模式：上传完成（假）')],
]

export function installDemoAdapter(http: AxiosInstance): void {
  http.defaults.adapter = async (config: InternalAxiosRequestConfig): Promise<AxiosResponse> => {
    await sleep(150 + Math.random() * 200)
    const url = (config.url || '').replace(/^\/api/, '').split('?')[0] ?? ''
    for (const [re, handler] of routes) {
      if (re.test(url)) {
        const body = await handler(config)
        return { data: body, status: 200, statusText: 'OK', headers: {}, config }
      }
    }
    console.info(`[demo] 未实现接口，已兜底空数据: ${config.method?.toUpperCase()} ${url}`)
    return { data: ok(null, '演示模式'), status: 200, statusText: 'OK', headers: {}, config }
  }
  console.info('%c[demo] 演示模式已激活：API 请求走本地 mock，不发真实请求', 'color:#d64545')
}

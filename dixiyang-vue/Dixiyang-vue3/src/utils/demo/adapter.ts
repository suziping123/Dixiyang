// 演示模式 axios 适配器：请求不出网，按 URL 返回 mock 响应（含 150-350ms 模拟延迟）
// 未命中的接口统一兜底 {code:200,data:null}（页面不炸），console.info 留痕便于补 mock
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { makeDemoToken } from './index'
import { DEMO_NOVELS, DEMO_USER } from './mockData'
import {
  DEMO_AI_COMPLETION,
  DEMO_CHAPTERS,
  DEMO_CHAPTER_CONTENT,
  DEMO_CHARACTERS,
  DEMO_NODES,
  DEMO_RAG_DOCUMENTS,
  DEMO_RAG_STATS,
  DEMO_TIMELINES,
  DEMO_VOLUMES,
} from './mockNovel'

import { DEMO_SESSIONS, DEMO_SESSION_MESSAGES } from './mockSocial'
import { installChatStreamStub } from './fetchStub'

type Body = { code: number; msg: string; data: unknown }

const ok = (data: unknown, msg = 'ok'): Body => ({ code: 200, msg, data })
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
const isPost = (config: AxiosRequestConfig) => (config.method ?? 'get').toUpperCase() === 'POST'

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
  // ── 卷 ──
  [/^\/volumes\/novel\/\d+$/, (c) => (isPost(c) ? ok({ id: 9, novel_id: 101, title: '新卷（假）', sort_order: 9 }, '演示模式：创建成功（假）') : ok(DEMO_VOLUMES))],
  [/^\/volumes\/\d+$/, () => ok(null, '演示模式：删除成功（假）')],
  // ── 章节（含正文读写与 AI 补全）──
  [/^\/chapters\/novel\/\d+$/, (c) => (isPost(c) ? ok({ id: 99, novel_id: 101, title: '新章节（假）', sort_order: 99, version: 1, local_version: 1, word_count: 0 }, '演示模式：创建成功（假）') : ok(DEMO_CHAPTERS))],
  [
    /^\/chapters\/\d+\/content$/,
    (c) =>
      isPost(c)
        ? ok({ chapterId: 11, version: 4, contentHash: 'h-demo', hasConflict: false }, '演示模式：已保存（假，不落盘）')
        : ok(DEMO_CHAPTER_CONTENT),
  ],
  [/^\/chapters\/\d+$/, () => ok(DEMO_CHAPTERS[0])],
  [/^\/ai\/completion$/, () => ok(DEMO_AI_COMPLETION)],
  // ── 角色 ──
  [/^\/novelCharacter\/all\/\d+$/, () => ok(DEMO_CHARACTERS)],
  [/^\/novelCharacter\/list\/\d+$/, () => ok({ records: DEMO_CHARACTERS, total: DEMO_CHARACTERS.length, size: 100, current: 1, pages: 1 })],
  [/^\/novelCharacter\/create$/, () => ok(DEMO_CHARACTERS[0], '演示模式：创建成功（假）')],
  [/^\/novelCharacter\/update\/\d+$/, () => ok(DEMO_CHARACTERS[0], '演示模式：已保存（假）')],
  [/^\/novelCharacter\/delete\/\d+$/, () => ok(null, '演示模式：删除成功（假）')],
  // ── 时间线 ──
  [/^\/timeline\/all\/\d+$/, () => ok(DEMO_TIMELINES)],
  [/^\/timeline\/create$/, () => ok({ id: 309, novelId: 101, name: '新时间线（假）' }, '演示模式：创建成功（假）')],
  [/^\/timeline\/update\/\d+$/, () => ok(DEMO_TIMELINES[0], '演示模式：已保存（假）')],
  [/^\/timeline\/delete\/\d+$/, () => ok(null, '演示模式：删除成功（假）')],
  // ── 故事节点 ──
  [/^\/storyNode\/all\/\d+$/, () => ok(DEMO_NODES)],
  [/^\/storyNode\/timeline\/\d+$/, () => ok(DEMO_NODES)],
  [/^\/storyNode\/create$/, () => ok(DEMO_NODES[0], '演示模式：创建成功（假）')],
  [/^\/storyNode\/update\/\d+$/, () => ok(DEMO_NODES[0], '演示模式：已保存（假）')],
  [/^\/storyNode\/delete\/\d+$/, () => ok(null, '演示模式：删除成功（假）')],
  // ── RAG 知识库 ──
  [/^\/rag\/stats$/, () => ok(DEMO_RAG_STATS)],
  [/^\/rag\/documents$/, () => ok(DEMO_RAG_DOCUMENTS)],
  [/^\/rag\/search$/, () => ok({ query: '江末', results: DEMO_RAG_DOCUMENTS.ids.map((id, i) => ({ id, content: DEMO_RAG_DOCUMENTS.documents[i], metadata: DEMO_RAG_DOCUMENTS.metadatas[i], score: 0.92 - i * 0.07 })), total: 4 })],
  // ── RAG 助手：会话历史（流式对话本身由 fetchStub 处理）──
  [/^\/chatHistory\/sessions$/, () => ok(DEMO_SESSIONS)],
  [/^\/chatHistory\/session\/[^/]+$/, (c) => (isPost(c) ? ok(null) : ok(DEMO_SESSION_MESSAGES['demo-s1']))],
  [/^\/chatHistory\/message\/[^/]+$/, () => ok(null, '演示模式：已保存（假）')],
  [/^\/chatHistory\/version\/[^/]+$/, () => ok(null, '演示模式：已删除（假）')],
  [/^\/chatHistory\/delete-current\/[^/]+$/, () => ok({ content: '（演示模式）已回退到上一版本（假）' })],
  [/^\/chatHistory\/generate-title\/[^/]+$/, () => ok('关于废土聚落的讨论（假标题）')],
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
  installChatStreamStub()
}

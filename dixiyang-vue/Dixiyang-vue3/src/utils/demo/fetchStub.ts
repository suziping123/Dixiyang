// 演示模式：SSE 流式聊天打桩
// /chat/stream、/chat/regenerate 走原生 fetch（不经过 axios adapter），这里覆写 window.fetch：
// 命中这两个 URL 时返回本地构造的 ReadableStream（thinking → rag_references → 分段 content → done），
// 其余请求原样透传给真实 fetch。仅在 VITE_DEMO=1 构建中安装。
import { DEMO_STREAM_REPLY } from './mockSocial'

const SSE_ENDPOINTS = ['/api/chat/stream', '/api/chat/regenerate']

export function installChatStreamStub(): void {
  const originalFetch = window.fetch.bind(window)
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    if (!SSE_ENDPOINTS.some((ep) => url.includes(ep))) return originalFetch(input, init)

    let sessionId = 'demo-s1'
    let useRag = false
    try {
      const body = JSON.parse(String(init?.body ?? '{}')) as { sessionId?: string; useRag?: boolean }
      if (body.sessionId) sessionId = body.sessionId
      useRag = body.useRag === true
    } catch {
      /* body 解析失败用默认值 */
    }

    const encoder = new TextEncoder()
    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        const push = (payload: unknown) => controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`))
        const wait = (ms: number) => new Promise((r) => setTimeout(r, ms))

        for (const delta of DEMO_STREAM_REPLY.thinking.match(/.{1,12}/g) ?? []) {
          push({ type: 'thinking', delta })
          await wait(30)
        }
        if (useRag) push({ type: 'rag_references', references: DEMO_STREAM_REPLY.references })
        await wait(150)
        for (const para of DEMO_STREAM_REPLY.content) {
          for (const delta of para.match(/.{1,6}/g) ?? []) {
            push({ type: 'content', delta })
            await wait(45)
          }
        }
        push({ type: 'done', sessionId })
        controller.close()
      },
      cancel() {
        /* 前端 AbortController 中断：静默结束 */
      },
    })
    return new Response(stream, { status: 200, headers: { 'Content-Type': 'text/event-stream' } })
  }
}

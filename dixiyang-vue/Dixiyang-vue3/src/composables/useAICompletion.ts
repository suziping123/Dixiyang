import { ref, getCurrentScope, onScopeDispose } from 'vue'
import type { Ref } from 'vue'
import http, { assertApiResponse } from '@/utils/http'

export type AIState = 'ready' | 'thinking' | 'error' | 'disconnected'

interface CompletionResponse {
  text: string
  model: string
  requestId: string
  latency: number
  finishReason: string
}

const AUTO_IDLE_MS = 700 // 停止输入后多久考虑自动补全
const COOLDOWN_MS = 3000 // 两次补全最小间隔
const MAX_BEFORE = 2000
const MAX_AFTER = 200

/** 请求时的上下文快照，用于接受前的有效性校验 */
interface GhostSnapshot {
  text: string
  /** 请求时的完整光标前文本 */
  prefix: string
  /** 请求时的光标位置 */
  cursorPos: number
  /** 请求时的文档长度 */
  docLen: number
  requestId: string
}

/** 设定上下文勾选（由 AIContextPanel 提供，未启用时全为空数组） */
export interface CompletionContextIds {
  novelId: number
  characterIds: number[]
  storyNodeIds: number[]
  timelineIds: number[]
}

export interface CompletionSource {
  chapterId: number
  chapterTitle: string
  getTextBefore: (max: number) => string
  getTextAfter: (max: number) => string
  getCursorPos: () => number
  getDoc: () => string
  getContext: () => CompletionContextIds
}

export function useAICompletion() {
  const aiState: Ref<AIState> = ref('ready')
  const ghostText = ref('')

  let snapshot: GhostSnapshot | null = null
  let pending = false
  let lastRequestAt = 0
  let idleTimer: ReturnType<typeof setTimeout> | null = null
  let source: CompletionSource | null = null

  function bind(s: CompletionSource): void {
    source = s
  }

  function clear(): void {
    ghostText.value = ''
    snapshot = null
  }

  async function request(manual: boolean): Promise<void> {
    if (!source || pending) return
    if (ghostText.value) return // 已有补全，先处理掉
    const now = Date.now()
    if (!manual && now - lastRequestAt < COOLDOWN_MS) return

    const cursorBefore = source.getTextBefore(MAX_BEFORE)
    const cursorAfter = source.getTextAfter(MAX_AFTER)
    const cursorPos = source.getCursorPos()
    const doc = source.getDoc()

    // 自动触发条件（手动触发始终允许）：非空文档即可，光标位置不限
    if (!doc.trim()) return

    pending = true
    lastRequestAt = now
    aiState.value = 'thinking'
    const reqId = String(now)
    try {
      const res = await http.post('/ai/completion', {
        chapterId: source.chapterId,
        chapterTitle: source.chapterTitle,
        cursorBefore,
        cursorAfter,
        maxTokens: 80,
        ...source.getContext(),
      })
      const body = assertApiResponse<CompletionResponse | null>(res)
      // 仅当期间用户没有继续输入（光标前文本未变）才展示补全
      const stillValid =
        source.getTextBefore(MAX_BEFORE) === cursorBefore &&
        source.getCursorPos() === cursorPos &&
        ghostText.value === ''

      if (body.code === 200 && body.data?.text && stillValid) {
        snapshot = {
          text: body.data.text,
          prefix: cursorBefore,
          cursorPos,
          docLen: doc.length,
          requestId: body.data.requestId || reqId,
        }
        ghostText.value = body.data.text
        aiState.value = 'ready'
      } else if (body.code === 200 && !body.data?.text) {
        aiState.value = 'ready'
      } else {
        aiState.value = 'error'
        setTimeout(() => {
          if (aiState.value === 'error') aiState.value = 'ready'
        }, 2500)
      }
    } catch {
      // AI 失败不影响写作：静默降级
      aiState.value = 'error'
      setTimeout(() => {
        if (aiState.value === 'error') aiState.value = 'ready'
      }, 2500)
    } finally {
      pending = false
    }
  }

  /** 文档变化：补全失效 + 停止输入后自动触发 */
  function onDocChange(): void {
    if (ghostText.value) clear()
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = setTimeout(() => {
      idleTimer = null
      void request(false)
    }, AUTO_IDLE_MS)
  }

  /** 接受：校验补全仍有效，返回待插入文本 */
  function accept(): string | null {
    if (!ghostText.value || !snapshot || !source) return null
    const cursorBefore = source.getTextBefore(MAX_BEFORE)
    // 有效性：光标前文本仍以请求时的前缀为前，光标未大幅移动，补全文本匹配
    const cursorOk = Math.abs(source.getCursorPos() - snapshot.cursorPos) <= 2
    if (!cursorBefore.startsWith(snapshot.prefix.slice(-100)) && cursorBefore !== snapshot.prefix) {
      clear()
      return null
    }
    if (!cursorOk) {
      clear()
      return null
    }
    const text = snapshot.text
    clear()
    return text
  }

  function reject(): void {
    clear()
  }

  function dispose(): void {
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = null
    source = null
  }

  if (getCurrentScope()) onScopeDispose(dispose)

  return { aiState, ghostText, bind, request, onDocChange, accept, reject, dispose }
}

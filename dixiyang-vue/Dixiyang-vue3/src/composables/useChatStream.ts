import { ref, readonly } from 'vue'
import http, { handleUnauthorized } from '@/utils/http'
import { friendlyError } from '@/utils/errorText'

// 401 统一处理（被其他设备顶号/过期）：提取后端文案 → 清登录态并跳登录页
async function guard401(response: Response): Promise<void> {
  if (response.status !== 401) return
  let message = '账号已在其他设备登录'
  try {
    const data = (await response.clone().json()) as Record<string, unknown>
    const text = data?.msg ?? data?.message ?? data?.detail
    if (typeof text === 'string' && text.trim()) message = text
  } catch { /* 响应体非 JSON 时用默认文案 */ }
  handleUnauthorized(message)
  throw new Error(message)
}

export interface RagReference {
  source: string
  title: string
  content: string
  score: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  references?: RagReference[]
  timestamp: Date
  edited?: boolean
  version?: number
  versions?: string[] // 改前快照历史（每次编辑前的内容，≤6；content 恒为最新，可浏览/恢复/删除）
  paired?: string[] // 与提问版本成对的"当时回答"（仅 assistant，编辑提问重新生成时由后端存档）
  editing?: boolean  // 前端编辑态
  editDraft?: string // 临时编辑草稿
}

export interface ChatSession {
  sessionId: string
  title: string
  createTime?: string
  updateTime?: string
}

function genId(): string {
  return crypto.randomUUID?.() ?? Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

export function useChatStream(userId?: number) {
  const messages = ref<ChatMessage[]>([])
  const currentContent = ref('')
  const currentThinking = ref('')
  const currentReferences = ref<RagReference[]>([])
  const isStreaming = ref(false)
  const currentSessionId = ref('')
  const sessions = ref<ChatSession[]>([])
  let abortController: AbortController | null = null

  // 聊天落盘以后端为唯一写入点（/chat/stream、/chat/regenerate 流完成时写链），
  // 前端不再调 batchSave 追加，避免同一回答双写导致重复消息/版本条状态分叉

  const loadSessions = async (novelId?: string | number) => {
    if (!novelId) return
    try {
      const res = await http.get('/chatHistory/sessions', {
        params: { novelId }
      })
      sessions.value = (res.data ?? []).map((s: ChatSession) => ({
        sessionId: s.sessionId,
        title: s.title,
        createTime: s.createTime,
        updateTime: s.updateTime
      }))
    } catch { sessions.value = [] }
  }

  const loadSessionMessages = async (sessionId: string) => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    currentContent.value = ''
    currentThinking.value = ''
    isStreaming.value = false
    currentSessionId.value = sessionId
    try {
      const res = await http.get(`/chatHistory/session/${sessionId}`)
      messages.value = (res.data ?? []).map((m: { role: string; content: string; thinking?: string; references?: RagReference[]; createTime?: string; edited?: boolean; version?: number; versions?: string[]; paired?: string[] }) => ({
        role: m.role,
        content: m.content,
        thinking: m.thinking ?? undefined,
        references: m.references ?? undefined,
        timestamp: m.createTime ? new Date(m.createTime) : new Date(),
        edited: m.edited ?? undefined,
        version: m.version ?? undefined,
        versions: Array.isArray(m.versions) ? m.versions : undefined,
        paired: Array.isArray(m.paired) ? m.paired : undefined
      }))
    } catch { messages.value = [] }
  }

  const newSession = (): boolean => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    const existing = sessions.value.find(s => s.title === '新对话')
    if (existing) {
      currentSessionId.value = existing.sessionId
      messages.value = []
      currentContent.value = ''
      currentThinking.value = ''
      isStreaming.value = false
      return false
    }
    const id = genId()
    currentSessionId.value = id
    messages.value = []
    currentContent.value = ''
    currentThinking.value = ''
    isStreaming.value = false
    sessions.value = [
      { sessionId: id, title: '新对话', createTime: new Date().toISOString() },
      ...sessions.value
    ]
    return true
  }

  const sendMessage = async (
    message: string,
    context: {
      useRag?: boolean
      novelId?: string | number
      characterIds?: (string | number)[]
      storyNodeIds?: (string | number)[]
      includeCharacters?: boolean
      includeStory?: boolean
      conversationMode?: 'WRITE' | 'DISCUSS' | 'ANALYZE' | 'BRAINSTORM' | 'ASK'
    }
  ) => {
    if (!message.trim() || isStreaming.value) return

    if (!currentSessionId.value) currentSessionId.value = genId()

    const userMsg: ChatMessage = { role: 'user', content: message, timestamp: new Date() }
    messages.value.push(userMsg)

    isStreaming.value = true
    currentContent.value = ''
    currentThinking.value = ''
    currentReferences.value = []

    const controller = new AbortController()
    abortController = controller

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          message,
          useRag: context.useRag ?? true,
          novelId: context.novelId,
          characterIds: context.characterIds ?? [],
          storyNodeIds: context.storyNodeIds ?? [],
          includeCharacters: context.includeCharacters ?? true,
          includeStory: context.includeStory ?? true,
          conversationMode: context.conversationMode ?? 'WRITE',
          sessionId: currentSessionId.value || undefined
        }),
        signal: controller.signal
      })

      await guard401(response)
      if (!response.ok) throw new Error(`请求失败 (${response.status})`)
      if (!response.body) throw new Error('响应无数据')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n')
        buffer = parts.pop() ?? ''
        for (const line of parts) {
          if (!line.startsWith('data:')) continue
          const jsonStr = line[5] === ' ' ? line.slice(6) : line.slice(5)
          if (!jsonStr.trim()) continue
          try {
            const data = JSON.parse(jsonStr)
            if (data.type === 'content') currentContent.value += data.delta || ''
            else if (data.type === 'thinking') currentThinking.value += data.delta || ''
            else if (data.type === 'rag_references') {
              const refs = data.references ?? []
              currentReferences.value.push(...refs)
            }
            else if (data.type === 'done') {
              if (data.sessionId) currentSessionId.value = data.sessionId
            }
            else if (data.type === 'error') throw new Error(data.message || '未知错误')
          } catch (e) {
            if (e instanceof SyntaxError) continue
            throw e
          }
        }
      }

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: currentContent.value,
        thinking: currentThinking.value || undefined,
        references: currentReferences.value.length > 0 ? currentReferences.value : undefined,
        timestamp: new Date()
      }
      messages.value.push(assistantMsg)
      currentContent.value = ''
      currentThinking.value = ''
      currentReferences.value = []
      // 立即解锁流式态：标题生成/会话列表刷新不再让 typing 指示器残留在已完成回答下方
      isStreaming.value = false
      abortController = null

      const isFirstExchange = messages.value.filter(m => m.role === 'assistant').length === 1
      if (isFirstExchange) {
        await generateTitle(context.novelId)
      }
      await loadSessions(context.novelId)

    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        if (currentContent.value) {
          messages.value.push({
            role: 'assistant',
            content: currentContent.value,
            thinking: currentThinking.value || undefined,
            references: currentReferences.value.length > 0 ? currentReferences.value : undefined,
            timestamp: new Date()
          })
        }
      } else {
        messages.value.push({
          role: 'assistant',
          content: `抱歉，${friendlyError((error as Error).message, '请求失败，请稍后再试')}`,
          timestamp: new Date()
        })
      }
    } finally {
      isStreaming.value = false
      abortController = null
      currentReferences.value = []
    }
  }

  const cancelStream = () => abortController?.abort()

  const clearMessages = () => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    messages.value = []
    currentContent.value = ''
    currentThinking.value = ''
    currentReferences.value = []
    currentSessionId.value = ''
    isStreaming.value = false
  }

  const regenerateMessage = async (
    messageIndex: number,
    context: {
      useRag?: boolean
      novelId?: string | number
      characterIds?: (string | number)[]
      storyNodeIds?: (string | number)[]
      includeCharacters?: boolean
      includeStory?: boolean
      conversationMode?: 'WRITE' | 'DISCUSS' | 'ANALYZE' | 'BRAINSTORM' | 'ASK'
    },
    // 编辑提问场景：旧回答成对存档（旧 paired + 改前回答）；不传则原样保留被截断回答的 paired
    prevPaired?: string[]
  ) => {
    if (isStreaming.value || !currentSessionId.value) return

    const replaced = messages.value[messageIndex]
    const keepPaired = prevPaired ??
      (replaced?.role === 'assistant' ? replaced.paired : undefined)

    // 截断本地消息（从 messageIndex 开始删除）
    messages.value = messages.value.slice(0, messageIndex)

    isStreaming.value = true
    currentContent.value = ''
    currentThinking.value = ''
    currentReferences.value = []

    const controller = new AbortController()
    abortController = controller

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/chat/regenerate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          sessionId: currentSessionId.value,
          regenerateIndex: messageIndex,
          message: '',
          prevAnswerVersions: keepPaired ?? null,
          useRag: context.useRag ?? true,
          novelId: context.novelId,
          characterIds: context.characterIds ?? [],
          storyNodeIds: context.storyNodeIds ?? [],
          includeCharacters: context.includeCharacters ?? true,
          includeStory: context.includeStory ?? true,
          conversationMode: context.conversationMode ?? 'WRITE'
        }),
        signal: controller.signal
      })

      await guard401(response)
      if (!response.ok) throw new Error(`请求失败 (${response.status})`)
      if (!response.body) throw new Error('响应无数据')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n')
        buffer = parts.pop() ?? ''
        for (const line of parts) {
          if (!line.startsWith('data:')) continue
          const jsonStr = line[5] === ' ' ? line.slice(6) : line.slice(5)
          if (!jsonStr.trim()) continue
          const data = JSON.parse(jsonStr)
          if (data.type === 'content') currentContent.value += data.delta || ''
          else if (data.type === 'thinking') currentThinking.value += data.delta || ''
          else if (data.type === 'rag_references') {
            const refs = data.references ?? []
            currentReferences.value.push(...refs)
          }
          else if (data.type === 'done') {
            if (data.sessionId) currentSessionId.value = data.sessionId
          }
          else if (data.type === 'error') throw new Error(data.message || '未知错误')
        }
      }

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: currentContent.value,
        thinking: currentThinking.value || undefined,
        references: currentReferences.value.length > 0 ? currentReferences.value : undefined,
        ...(keepPaired && keepPaired.length ? { paired: keepPaired } : {}),
        timestamp: new Date()
      }
      messages.value.push(assistantMsg)
      currentContent.value = ''
      currentThinking.value = ''
      currentReferences.value = []
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        messages.value.push({
          role: 'assistant',
          content: `重新生成失败：${friendlyError((error as Error).message, '请稍后再试')}`,
          timestamp: new Date()
        })
      }
    } finally {
      isStreaming.value = false
      abortController = null
      currentReferences.value = []
    }
  }

  // 编辑消息（AI 回答/提问均持久化）。返回 null=成功，否则为错误提示
  const editMessage = async (index: number, newContent: string, role: 'user' | 'assistant' = 'assistant', truncateAfter = false): Promise<string | null> => {
    if (!currentSessionId.value || !userId) return '会话未就绪，请刷新后重试'
    const m = messages.value[index]
    if (!m) return '消息不存在'
    try {
      const res = await http.put(`/chatHistory/message/${currentSessionId.value}`, {
        messageIndex: index, role, content: newContent, truncateAfter
      }) as unknown as { code?: number; msg?: string }
      // 拦截器对业务错误也 resolve（code≠200），必须显式检查——
      // 否则后端替换/截断失败时本地照改，导致本地与链索引分叉
      if (res && typeof res === 'object' && typeof res.code === 'number' && res.code !== 200) {
        return res.msg || '编辑保存失败，请稍后再试'
      }
    } catch (e) {
      return friendlyError((e as Error).message, '编辑失败，请稍后再试')
    }
    // 快照"改前内容"进历史（左右切换可看改之前的样子），content 更新为最新
    const versions = [...(m.versions ?? []), m.content]
    messages.value[index] = { ...m, content: newContent, edited: true, versions }
    return null
  }

  // 恢复历史版本为当前对话内容（不占编辑配额）。field: versions=独立历史 / paired=成对回答存档
  const restoreVersion = async (index: number, versionIndex: number, field: 'versions' | 'paired' = 'versions'): Promise<string | null> => {
    const m = messages.value[index]
    const src = (field === 'paired' ? m?.paired : m?.versions) ?? []
    if (!m || versionIndex < 0 || versionIndex >= src.length) return '版本不存在'
    if (!currentSessionId.value || !userId) return '会话未就绪，请刷新后重试'
    try {
      const res = await http.post(`/chatHistory/restore-version/${currentSessionId.value}`, {
        messageIndex: index, versionIndex, field
      }) as unknown as { code?: number; msg?: string }
      if (res && typeof res === 'object' && typeof res.code === 'number' && res.code !== 200) {
        return res.msg || '恢复失败，请稍后再试'
      }
    } catch (e) {
      return friendlyError((e as Error).message, '恢复失败，请稍后再试')
    }
    messages.value[index] = { ...m, content: src[versionIndex] ?? m.content }
    return null
  }

  // 删除一个历史版本（编辑配额减一）。历史与当前内容解耦，删除不影响 content（与后端一致）
  const deleteVersion = async (index: number, versionIndex: number, field: 'versions' | 'paired' = 'versions'): Promise<string | null> => {
    const m = messages.value[index]
    const src = (field === 'paired' ? m?.paired : m?.versions) ?? []
    if (!m || versionIndex < 0 || versionIndex >= src.length) return '版本不存在'
    if (!currentSessionId.value || !userId) return '会话未就绪，请刷新后重试'
    try {
      const res = await http.delete(`/chatHistory/version/${currentSessionId.value}`, {
        data: { messageIndex: index, versionIndex, field }
      }) as unknown as { code?: number; msg?: string }
      if (res && typeof res === 'object' && typeof res.code === 'number' && res.code !== 200) {
        return res.msg || '删除失败，请稍后再试'
      }
    } catch (e) {
      return friendlyError((e as Error).message, '删除失败，请稍后再试')
    }
    const next = [...src]
    next.splice(versionIndex, 1)
    messages.value[index] = { ...m, ...(field === 'paired' ? { paired: next } : { versions: next }) }
    return null
  }

  const truncateMessages = (keepCount: number) => {
    if (keepCount < 0) return
    messages.value = messages.value.slice(0, keepCount)
  }

  const generateTitle = async (novelId?: string | number) => {
    try {
      const res = await http.post(`/chatHistory/generate-title/${currentSessionId.value}`)
      const newTitle = res.data as string
      if (newTitle) {
        const s = sessions.value.find(s => s.sessionId === currentSessionId.value)
        if (s) s.title = newTitle
      }
    } catch { /* silent */ }
  }

  const deleteSession = async (sessionId: string, novelId?: string | number) => {
    try {
      await http.delete(`/chatHistory/session/${sessionId}`)
      sessions.value = sessions.value.filter(s => s.sessionId !== sessionId)
      loadSessions(novelId)
      if (currentSessionId.value === sessionId) clearMessages()
    } catch { /* silent */ }
  }

  return {
    messages: readonly(messages),
    currentContent: readonly(currentContent),
    currentThinking: readonly(currentThinking),
    currentReferences: readonly(currentReferences),
    isStreaming: readonly(isStreaming),
    currentSessionId: readonly(currentSessionId),
    sessions: readonly(sessions),
    sendMessage,
    cancelStream,
    clearMessages,
    loadSessions,
    loadSessionMessages,
    newSession,
    deleteSession,
    regenerateMessage,
    editMessage,
    restoreVersion,
    deleteVersion,
    truncateMessages
  }
}

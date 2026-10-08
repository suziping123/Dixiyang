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
  versions?: string[] // 编辑版本历史（只存改后内容，≤6，可浏览/恢复/删除）
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

  const saveToBackend = async (msgs: ChatMessage[], novelId?: string | number) => {
    if (!currentSessionId.value || !userId) return
    try {
      await http.post('/chatHistory/batchSave', {
        sessionId: currentSessionId.value,
        novelId: novelId ?? null,
        messages: msgs.map(m => ({
          role: m.role,
          content: m.content,
          thinking: m.thinking ?? null,
          references: m.references ?? null,
          createTime: m.timestamp.toISOString()
        }))
      })
    } catch { /* silent */ }
  }

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
      messages.value = (res.data ?? []).map((m: { role: string; content: string; thinking?: string; references?: RagReference[]; createTime?: string; edited?: boolean; version?: number; versions?: string[] }) => ({
        role: m.role,
        content: m.content,
        thinking: m.thinking ?? undefined,
        references: m.references ?? undefined,
        timestamp: m.createTime ? new Date(m.createTime) : new Date(),
        edited: m.edited ?? undefined,
        version: m.version ?? undefined,
        versions: Array.isArray(m.versions) ? m.versions : undefined
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

      const isFirstExchange = messages.value.filter(m => m.role === 'assistant').length === 1
      await saveToBackend([userMsg, assistantMsg], context.novelId)
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
    }
  ) => {
    if (isStreaming.value || !currentSessionId.value) return

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
        timestamp: new Date()
      }
      messages.value.push(assistantMsg)
      currentContent.value = ''
      currentThinking.value = ''
      currentReferences.value = []

      saveToBackend([assistantMsg], context.novelId)
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
      await http.put(`/chatHistory/message/${currentSessionId.value}`, {
        messageIndex: index, role, content: newContent, truncateAfter
      })
    } catch (e) {
      return friendlyError((e as Error).message, '编辑失败，请稍后再试')
    }
    const versions = [...(m.versions ?? []), newContent]
    messages.value[index] = { ...m, content: newContent, edited: true, versions }
    return null
  }

  // 恢复历史版本为当前对话内容（不占编辑配额）
  const restoreVersion = async (index: number, versionIndex: number): Promise<string | null> => {
    const m = messages.value[index]
    if (!m?.versions?.[versionIndex]) return '版本不存在'
    if (!currentSessionId.value || !userId) return '会话未就绪，请刷新后重试'
    try {
      await http.post(`/chatHistory/restore-version/${currentSessionId.value}`, {
        messageIndex: index, versionIndex
      })
    } catch (e) {
      return friendlyError((e as Error).message, '恢复失败，请稍后再试')
    }
    messages.value[index] = { ...m, content: m.versions[versionIndex] ?? m.content }
    return null
  }

  // 删除一个历史版本（编辑配额减一）。本地回退规则与后端一致
  const deleteVersion = async (index: number, versionIndex: number): Promise<string | null> => {
    const m = messages.value[index]
    if (!m?.versions?.[versionIndex]) return '版本不存在'
    if (!currentSessionId.value || !userId) return '会话未就绪，请刷新后重试'
    try {
      await http.delete(`/chatHistory/version/${currentSessionId.value}`, {
        data: { messageIndex: index, versionIndex }
      })
    } catch (e) {
      return friendlyError((e as Error).message, '删除失败，请稍后再试')
    }
    const versions = [...m.versions]
    const deleted = versions.splice(versionIndex, 1)[0] ?? ''
    let content = m.content
    if (content === deleted && versions.length) content = versions[versions.length - 1] ?? content
    messages.value[index] = { ...m, content, versions }
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

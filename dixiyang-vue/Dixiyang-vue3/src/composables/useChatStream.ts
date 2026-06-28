import { ref, readonly } from 'vue'
import http from '@/utils/http'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  timestamp: Date
  edited?: boolean
  version?: number
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
    currentSessionId.value = sessionId
    try {
      const res = await http.get(`/chatHistory/session/${sessionId}`)
      messages.value = (res.data ?? []).map((m: { role: string; content: string; thinking?: string; createTime: string; edited?: boolean; version?: number }) => ({
        role: m.role,
        content: m.content,
        thinking: m.thinking ?? undefined,
        timestamp: new Date(m.createTime),
        edited: m.edited ?? undefined,
        version: m.version ?? undefined
      }))
    } catch { messages.value = [] }
  }

  const newSession = () => {
    currentSessionId.value = genId()
    messages.value = []
    currentContent.value = ''
    currentThinking.value = ''
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
    }
  ) => {
    if (!message.trim() || isStreaming.value) return

    if (!currentSessionId.value) currentSessionId.value = genId()

    const userMsg: ChatMessage = { role: 'user', content: message, timestamp: new Date() }
    messages.value.push(userMsg)

    isStreaming.value = true
    currentContent.value = ''
    currentThinking.value = ''

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
          sessionId: currentSessionId.value || undefined
        }),
        signal: controller.signal
      })

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
        timestamp: new Date()
      }
      messages.value.push(assistantMsg)
      currentContent.value = ''
      currentThinking.value = ''

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
            timestamp: new Date()
          })
        }
      } else {
        messages.value.push({
          role: 'assistant',
          content: `抱歉，请求失败：${(error as Error).message}`,
          timestamp: new Date()
        })
      }
    } finally {
      isStreaming.value = false
      abortController = null
    }
  }

  const cancelStream = () => abortController?.abort()

  const clearMessages = () => {
    messages.value = []
    currentContent.value = ''
    currentThinking.value = ''
    currentSessionId.value = ''
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
    }
  ) => {
    if (isStreaming.value || !currentSessionId.value) return

    // 截断本地消息（从 messageIndex 开始删除）
    messages.value = messages.value.slice(0, messageIndex)

    isStreaming.value = true
    currentContent.value = ''
    currentThinking.value = ''

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
          includeStory: context.includeStory ?? true
        }),
        signal: controller.signal
      })

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
          else if (data.type === 'error') throw new Error(data.message || '未知错误')
        }
      }

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: currentContent.value,
        thinking: currentThinking.value || undefined,
        timestamp: new Date()
      }
      messages.value.push(assistantMsg)
      currentContent.value = ''
      currentThinking.value = ''

      saveToBackend([assistantMsg], context.novelId)
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        messages.value.push({
          role: 'assistant',
          content: `重新生成失败：${(error as Error).message}`,
          timestamp: new Date()
        })
      }
    } finally {
      isStreaming.value = false
      abortController = null
    }
  }

  const editMessage = async (index: number, newContent: string) => {
    if (!currentSessionId.value || !userId) return false
    const m = messages.value[index]
    if (!m) return false
    try {
      await http.put(`/chatHistory/message/${currentSessionId.value}`, {
        messageIndex: index, role: 'assistant', content: newContent
      })
      messages.value[index] = {
        role: m.role, content: newContent,
        thinking: m.thinking, timestamp: m.timestamp,
        edited: true, version: (m.version ?? 0) + 1
      }
      return true
    } catch {
      return false
    }
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
    editMessage
  }
}

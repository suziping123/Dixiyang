<template>
  <div class="rag-page">
    <div class="bg-gradient-animation"></div>

    <FloatingNav />

    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">RAG 智能创作助手</h1>
        <p class="page-subtitle">基于你的创作宇宙，智能生成与角色相关的故事内容</p>
      </div>
    </header>

    <div class="rag-container">
      <!-- 最左侧：历史会话 -->
      <aside class="session-panel">
        <div class="session-header">
          <h3>历史会话</h3>
          <div class="session-actions">
            <button class="new-btn" @click="loadSessions(selectedNovel?.id)" title="刷新列表">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
            </button>
            <button class="new-btn" @click="handleNewSession" title="新建对话">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
          </div>
        </div>
        <div class="session-list">
          <div
            v-for="s in sessions"
            :key="s.sessionId"
            class="session-item"
            :class="{ active: s.sessionId === currentSessionId }"
            @click="handleSelectSession(s.sessionId)"
          >
            <span class="session-title">{{ s.title }}</span>
            <button class="del-btn" @click.stop="handleDeleteSession(s.sessionId)" title="删除">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
            </button>
          </div>
        </div>
        <div class="session-empty" v-if="sessions.length === 0">
          <span>暂无历史记录</span>
        </div>
      </aside>

      <!-- 左侧：上下文选择面板 -->
      <aside class="context-panel">
        <div class="panel-section">
          <h3>选择小说</h3>
          <div class="selector-list">
            <div
              v-for="novel in novels"
              :key="novel.id"
              class="selector-item"
              :class="{ active: selectedNovel?.id === novel.id }"
              @click="selectNovel(novel)"
            >
              <span class="item-title">{{ novel.title }}</span>
              <span class="item-badge">{{ novel.char_count || 0 }} 角色</span>
            </div>
          </div>
        </div>

        <div class="panel-section" v-if="selectedNovel">
          <h3>选择角色</h3>
          <div class="selector-list">
            <div
              v-for="char in characters"
              :key="char.id"
              class="selector-item"
              :class="{ active: selectedCharacters.includes(char.id) }"
              @click="toggleCharacter(char)"
            >
              <span class="item-title">{{ char.name }}</span>
              <span class="item-tag" :style="{ background: genderStyle(char.gender).bg, color: genderStyle(char.gender).color }">{{ genderLabel(char.gender) }}</span>
            </div>
          </div>
        </div>

        <div class="panel-section" v-if="selectedNovel">
          <h3>故事节点</h3>
          <div class="selector-list">
            <div
              v-for="node in storyNodes"
              :key="node.id"
              class="selector-item"
              :class="{ active: selectedNodes.includes(node.id) }"
              @click="toggleNode(node)"
            >
              <span class="item-title">{{ node.title }}</span>
              <span class="item-tag type-tag" :class="node.eventType">{{ eventTypeLabel(node.eventType) }}</span>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3>生成选项</h3>
          <div class="options-group">
            <label class="option-item">
              <input type="checkbox" v-model="options.useRag" />
              <span>启用 RAG 检索</span>
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="options.includeCharacters" />
              <span>包含角色信息</span>
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="options.includeStory" />
              <span>包含故事节点</span>
            </label>
          </div>
        </div>

        <div class="panel-section">
          <h3>对话模式</h3>
          <div class="mode-buttons">
            <button
              v-for="mode in conversationModes"
              :key="mode.value"
              class="mode-btn"
              :class="{ active: options.conversationMode === mode.value }"
              @click="options.conversationMode = mode.value as any"
              :title="mode.desc"
            >
              <el-icon :size="14"><component :is="mode.icon" /></el-icon>
              <span>{{ mode.label }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧：聊天区域 -->
      <main class="chat-area">
        <div class="chat-header">
          <div class="chat-info">
            <h2>创作对话</h2>
            <p v-if="selectedNovel">当前语境：{{ selectedNovel.title }}</p>
          </div>
          <div class="chat-stats">
            <span class="stat-badge">已选 {{ selectedCharacters.length }} 角色</span>
            <span class="stat-badge">已选 {{ selectedNodes.length }} 节点</span>
          </div>
        </div>

          <div class="messages-container" ref="messagesRef">
            <div class="welcome-message" v-if="messages.length === 0 && !isStreaming">
              <div class="welcome-icon">✨</div>
              <h3>开始你的创作之旅</h3>
              <p>选择左侧的小说、角色和故事节点，我将基于这些信息为你提供创作帮助</p>
              <div class="suggestions">
                <button
                  v-for="suggestion in suggestions"
                  :key="suggestion"
                  class="suggestion-btn"
                  @click="useSuggestion(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>

            <ChatMessage
              v-for="(msg, index) in messages"
              :key="index"
              :message="msg"
              :index="index"
              :is-editing="isUserEditing && editedUserMessageIndex === index"
              :on-edit="(idx: number) => openEditModal(idx)"
              @regenerate="handleRegenerate(index)"
              @userEdit="handleUserEdit(index, $event)"
              @userEditSave="handleUserEditSave"
              @userEditCancel="cancelUserEdit"
              @extractSettings="handleExtractSettings(index)"
              class="message-item-wrapper"
            />

            <!-- 正在流式输出的消息 -->
            <template v-if="isStreaming">
              <ChatMessage
                v-if="currentContent || currentThinking"
                :message="{ role: 'assistant', content: '', timestamp: new Date() }"
    :streaming-content="currentContent"
    :streaming-thinking="currentThinking"
    :streaming-references="currentReferences"
    :is-streaming="true"
              />
              <div v-else class="message-item assistant">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                  <div class="typing-indicator">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                </div>
              </div>
            </template>
          </div>

        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              placeholder="输入你的创作需求或问题..."
              @keydown.enter="handleSend"
              @input="autoResize"
              :disabled="isStreaming"
              rows="1"
              ref="textareaRef"
            ></textarea>
            <button
              v-if="isStreaming"
              class="cancel-btn"
              @click="cancelStream"
              title="停止生成"
            >
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
            </button>
            <button
              v-else
              class="send-btn"
              @click="sendStreamMessage"
              :disabled="!inputMessage.trim()"
            >
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </div>
          <div class="input-hint">
            <span>提示：选择角色和节点可以获得更精准的创作建议</span>
          </div>
        </div>
      </main>
    </div>
  </div>
  <EditMessageModal ref="editModalRef" @save="handleEditSave" />
  <CharacterSettingsDialog
    v-model="showSettingsDialog"
    :conversation="settingsConversation"
    :novel-id="selectedNovel?.id"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useChatStream } from '@/composables/useChatStream'
import { useUserStore } from '@/stores/UserStore'
import FloatingNav from '@/components/FloatingNav.vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import EditMessageModal from '@/components/chat/EditMessageModal.vue'
import CharacterSettingsDialog from '@/components/CharacterSettingsDialog.vue'
import http from '@/utils/http'
import { confirmDelete } from '@/utils/confirm'
import { eventTypeLabel, eventTypeConfig, genderLabel, genderStyle } from '@/utils/storyMappings'

const userStore = useUserStore()
const userId = userStore.userId || (() => {
  const stored = localStorage.getItem('userInfo')
  return stored ? JSON.parse(stored).id : undefined
})()

const {
  messages, currentContent, currentThinking, currentReferences, isStreaming,
  currentSessionId, sessions,
  sendMessage, cancelStream, loadSessions, loadSessionMessages,
  newSession, deleteSession, regenerateMessage,
  editMessage, replaceUserMessage, truncateMessages
} = useChatStream(userId)

const editingMessageIndex = ref<number>(-1)
const editingUserMessageContent = ref<string>('')
const editedUserMessageIndex = ref<number>(-1)
const isUserEditing = ref<boolean>(false)

const novels = ref<any[]>([])
const characters = ref<any[]>([])
const storyNodes = ref<any[]>([])
const selectedNovel = ref<any>(null)
const selectedCharacters = ref<number[]>([])
const selectedNodes = ref<number[]>([])
const inputMessage = ref('')
const messagesRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const editModalRef = ref<InstanceType<typeof EditMessageModal> | null>(null)

const saveEditedUserMessages = async (userId?: number) => {
  if (!currentSessionId.value || !userId) return
  try {
    await http.post('/chatHistory/batchSave', {
      sessionId: currentSessionId.value,
      novelId: selectedNovel.value?.id ?? null,
      messages: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        thinking: m.thinking ?? null,
        createTime: m.timestamp.toISOString()
      }))
    })
  } catch { /* silent */ }
}

const options = ref({
  useRag: true,
  includeCharacters: true,
  includeStory: true,
  conversationMode: 'WRITE' as 'WRITE' | 'DISCUSS' | 'ANALYZE' | 'BRAINSTORM' | 'ASK'
})

// 设定助手弹窗状态
const showSettingsDialog = ref(false)
const settingsConversation = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([])

import {
  Edit,
  ChatDotRound,
  Search,
  MagicStick,
  Help
} from '@element-plus/icons-vue'

const conversationModes = [
  { value: 'WRITE', label: '创作', icon: Edit, desc: '按设定写剧情/对话/描写' },
  { value: 'DISCUSS', label: '讨论', icon: ChatDotRound, desc: '回答设定相关问题' },
  { value: 'ANALYZE', label: '分析', icon: Search, desc: '分析角色/剧情逻辑' },
  { value: 'BRAINSTORM', label: '头脑风暴', icon: MagicStick, desc: '发散思考找灵感' },
  { value: 'ASK', label: '提问', icon: Help, desc: '快速精准回答' }
]

const suggestions = [
  '帮我生成一段角色对话',
  '分析这个角色的性格特点',
  '续写当前故事节点',
  '建议角色之间的互动场景'
]

const loadNovels = async () => {
  try {
    const res = await http.get('/novel/listall', { params: { page: 1, pageSize: 100 } })
    novels.value = res.data?.records || res.data || []
  } catch (error) {
    console.error('加载小说失败:', error)
  }
}

const selectNovel = async (novel: any) => {
  selectedNovel.value = novel
  selectedCharacters.value = []
  selectedNodes.value = []
  try {
    const res = await http.get(`/novelCharacter/all/${novel.id}`)
    characters.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载角色失败:', error)
    characters.value = []
  }
  try {
    const res = await http.get(`/storyNode/all/${novel.id}`)
    storyNodes.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载故事节点失败:', error)
    storyNodes.value = []
  }
  await loadSessions(novel.id)
}

const toggleCharacter = (char: any) => {
  const idx = selectedCharacters.value.indexOf(char.id)
  if (idx > -1) selectedCharacters.value.splice(idx, 1)
  else selectedCharacters.value.push(char.id)
}

const toggleNode = (node: any) => {
  const idx = selectedNodes.value.indexOf(node.id)
  if (idx > -1) selectedNodes.value.splice(idx, 1)
  else selectedNodes.value.push(node.id)
}

const sendStreamMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isStreaming.value) return
  inputMessage.value = ''
  scrollToBottom()
  await sendMessage(message, {
    useRag: options.value.useRag,
    novelId: selectedNovel.value?.id,
    characterIds: selectedCharacters.value,
    storyNodeIds: selectedNodes.value,
    includeCharacters: options.value.includeCharacters,
    includeStory: options.value.includeStory,
    conversationMode: options.value.conversationMode
  })
  scrollToBottom()
}

const handleSend = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendStreamMessage()
  }
}

const useSuggestion = (text: string) => {
  inputMessage.value = text
  textareaRef.value?.focus()
}

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const handleNewSession = () => {
  const created = newSession()
  if (!created) ElMessage.info('已有新对话，已切换到该对话')
}

const handleSelectSession = async (sessionId: string) => {
  await loadSessionMessages(sessionId)
  nextTick(scrollToBottom)
}

const handleUserEdit = (index: number, content: string) => {
  const msg = messages.value[index]
  if (!msg || msg.role !== 'user') return
  editedUserMessageIndex.value = index
  editingUserMessageContent.value = content
  isUserEditing.value = true
}

const handleUserEditSave = async (content: string) => {
  const idx = editedUserMessageIndex.value
  if (idx < 0 || !content.trim()) return
  replaceUserMessage(idx, content)
  truncateMessages(idx + 1)
  isUserEditing.value = false
  editedUserMessageIndex.value = -1
  inputMessage.value = content
  await sendStreamMessage()
}

const cancelUserEdit = () => {
  isUserEditing.value = false
  editedUserMessageIndex.value = -1
}

const openEditModal = (index: number) => {
  const msg = messages.value[index]
  if (!msg || msg.role !== 'assistant') return
  editingMessageIndex.value = index
  editModalRef.value?.open(msg.content)
}

const handleEditSave = async (newContent: string) => {
  const idx = editingMessageIndex.value
  if (idx < 0) return
  const ok = await editMessage(idx, newContent)
  if (ok) editingMessageIndex.value = -1
}

const handleRegenerate = async (index: number) => {
  scrollToBottom()
  await regenerateMessage(index, {
    useRag: options.value.useRag,
    novelId: selectedNovel.value?.id,
    characterIds: selectedCharacters.value,
    storyNodeIds: selectedNodes.value,
    includeCharacters: options.value.includeCharacters,
    includeStory: options.value.includeStory,
    conversationMode: options.value.conversationMode
  })
  scrollToBottom()
}

const handleExtractSettings = (index: number) => {
  // 截取上下文：当前消息前后各2条
  const start = Math.max(0, index - 2)
  const end = Math.min(messages.value.length, index + 3)
  const context = messages.value.slice(start, end).map(m => ({
    role: m.role as 'user' | 'assistant',
    content: m.content
  }))
  settingsConversation.value = context
  showSettingsDialog.value = true
}

const handleDeleteSession = async (sessionId: string) => {
  const session = sessions.value.find(s => s.sessionId === sessionId)
  const title = session?.title || '未命名会话'
  const confirmed = await confirmDelete(`确定删除对话「${title}」吗？此操作不可恢复。`)
  if (!confirmed) return
  await deleteSession(sessionId, selectedNovel.value?.id)
}

onMounted(async () => {
  await loadNovels()
})
</script>

<style scoped>
.rag-page {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
}

.bg-gradient-animation {
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: transparent;
  z-index: 0;
  animation: rotate 30s linear infinite;
  transition: opacity 0.3s ease;
}

.bg-gradient-animation.paused {
  animation-play-state: paused;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.page-header {
  z-index: 10;
  padding: 30px 40px;
  border-bottom: 1px solid var(--glass-border);
  background: rgba(10, 10, 12, 0.8);
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 900;
  margin: 0;
  background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  margin: 8px 0 0 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.rag-container {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 1600px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  padding: 20px;
  gap: 12px;
}

/* 历史会话面板 */
.session-panel {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 16px;
  overflow: hidden;
  position: relative;
  contain: paint;
}
.session-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: inherit;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.session-header h3 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--neon-cyan);
}

.new-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  backface-visibility: hidden;
}

.new-btn:hover {
  background: rgba(59,130,246,0.2);
  color: var(--neon-cyan);
  border-color: var(--neon-cyan);
}

.new-btn .btn-icon {
  transition: transform 0.3s ease;
}

.new-btn:hover .btn-icon {
  transform: rotate(180deg);
}

.session-actions {
  display: flex;
  gap: 6px;
  transform: translateZ(0);
}

.btn-icon {
  width: 18px;
  height: 18px;
  display: block;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backface-visibility: hidden;
}

.session-item:hover {
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.3);
}

.session-item.active {
  background: rgba(59,130,246,0.15);
  outline-color: rgba(59,130,246,0.3);
}

.session-title {
  font-size: 0.82rem;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.del-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0s linear 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.session-item:hover .del-btn {
  opacity: 1;
  visibility: visible;
  transition: opacity 0.2s, visibility 0s linear 0s;
}



.del-btn:hover {
  color: #ef4444;
  background: rgba(239,68,68,0.15);
}

.del-btn .btn-icon {
  width: 14px;
  height: 14px;
}

.session-empty {
  text-align: center;
  padding: 20px 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.context-panel {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 8px;
}

.panel-section {
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 16px;
  position: relative;
  contain: paint;
}
.panel-section::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: inherit;
}

.panel-section h3 {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  color: var(--neon-cyan);
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.selector-item {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-item:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.selector-item.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: var(--neon-blue);
}

.item-title {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.item-badge, .item-tag {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}
.type-tag.birth { background: rgba(59,130,246,0.15); color: #60a5fa; }
.type-tag.war { background: rgba(239,68,68,0.15); color: #f87171; }
.type-tag.politics { background: rgba(168,85,247,0.15); color: #c084fc; }
.type-tag.major { background: rgba(16,185,129,0.15); color: #34d399; }

.options-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.option-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--neon-blue);
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  min-width: 0;
  position: relative;
  contain: paint;
}
.chat-area::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: inherit;
}
.chat-area::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: inherit;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-info h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.chat-info p {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.chat-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  background: rgba(59, 130, 246, 0.2);
  color: var(--neon-cyan);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.welcome-message h3 {
  margin: 0 0 10px 0;
  font-size: 1.3rem;
  color: var(--text-primary);
}

.welcome-message p {
  margin: 0 0 24px 0;
  font-size: 0.95rem;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.suggestion-btn {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: var(--neon-cyan);
  padding: 10px 18px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
}

.suggestion-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message-item.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.message-item.user .message-avatar {
  background: rgba(168, 85, 247, 0.2);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.typing-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--neon-blue);
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 20px;
  border-top: 1px solid var(--glass-border);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 14px 18px;
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 0.95rem;
  resize: vertical;
  min-height: 50px;
  max-height: 400px;
  line-height: 1.5;
  transition: all 0.3s;
  overflow-y: auto;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--neon-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-wrapper textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 24px;
  height: 24px;
}

.cancel-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.cancel-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
}

.cancel-btn svg {
  width: 20px;
  height: 20px;
}

.input-hint {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: center;
}

.mode-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-on-glass);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--accent-primary);
}

.mode-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
  box-shadow: 0 0 8px rgba(var(--accent-primary-rgb, 99, 102, 241), 0.4);
}

.session-list::-webkit-scrollbar,
.context-panel::-webkit-scrollbar,
.messages-container::-webkit-scrollbar,
.selector-list::-webkit-scrollbar {
  width: 6px;
}

.session-list::-webkit-scrollbar-track,
.context-panel::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track,
.selector-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb,
.context-panel::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb,
.selector-list::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb:hover,
.context-panel::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover,
.selector-list::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

@media (max-width: 1200px) {
  .session-panel { width: 180px; }
  .context-panel { width: 240px; }
}

@media (max-width: 1024px) {
  .rag-container {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 120px);
  }
  .session-panel {
    width: 100%;
    max-height: 150px;
  }
  .session-list {
    flex-direction: row;
    overflow-x: auto;
  }
  .session-item { white-space: nowrap; flex-shrink: 0; }
  .context-panel { width: 100%; max-height: 300px; }
  .chat-area { min-height: 500px; }
}

@media (max-width: 768px) {
  .page-header { padding: 20px; }
  .rag-container { padding: 10px; }
  .chat-header { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>

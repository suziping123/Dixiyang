<template>
  <div class="rag-page">
    <div class="bg-gradient-animation"></div>

    <FloatingNav />

    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">✧ RAG 智能创作助手</h1>
        <p class="page-subtitle">基于你的创作宇宙，智能生成与角色相关的故事内容</p>
      </div>
    </header>

    <div class="rag-container">
      <!-- 左侧：上下文选择面板 -->
      <aside class="context-panel">
        <div class="panel-section">
          <h3>📚 选择小说</h3>
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
          <h3>👤 选择角色</h3>
          <div class="selector-list">
            <div
              v-for="char in characters"
              :key="char.id"
              class="selector-item"
              :class="{ active: selectedCharacters.includes(char.id) }"
              @click="toggleCharacter(char)"
            >
              <span class="item-title">{{ char.name }}</span>
              <span class="item-tag">{{ char.gender || '未知' }}</span>
            </div>
          </div>
        </div>

        <div class="panel-section" v-if="selectedNovel">
          <h3>⏳ 故事节点</h3>
          <div class="selector-list">
            <div
              v-for="node in storyNodes"
              :key="node.id"
              class="selector-item"
              :class="{ active: selectedNodes.includes(node.id) }"
              @click="toggleNode(node)"
            >
              <span class="item-title">{{ node.title }}</span>
              <span class="item-tag">{{ node.status || '未知' }}</span>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3>⚙️ 生成选项</h3>
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
      </aside>

      <!-- 右侧：聊天区域 -->
      <main class="chat-area">
        <div class="chat-header">
          <div class="chat-info">
            <h2>💬 创作对话</h2>
            <p v-if="selectedNovel">当前语境：{{ selectedNovel.title }}</p>
          </div>
          <div class="chat-stats">
            <span class="stat-badge">已选 {{ selectedCharacters.length }} 角色</span>
            <span class="stat-badge">已选 {{ selectedNodes.length }} 节点</span>
          </div>
        </div>

        <div class="messages-container" ref="messagesRef">
          <div class="welcome-message" v-if="messages.length === 0">
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

          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-item"
            :class="msg.role"
          >
            <div class="message-avatar">
              <span v-if="msg.role === 'user'">👤</span>
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>

          <div v-if="isLoading" class="message-item assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              placeholder="输入你的创作需求或问题..."
              @keydown.enter="handleSend"
              :disabled="isLoading"
              rows="1"
              ref="textareaRef"
            ></textarea>
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="isLoading || !inputMessage.trim()"
            >
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </div>
          <div class="input-hint">
            <span>💡 提示：选择角色和节点可以获得更精准的创作建议</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import FloatingNav from '@/components/FloatingNav.vue'
import http, { assertStringResponse } from '@/utils/http'

const router = useRouter()
const bgConfig = useBackgroundConfig()

// 状态管理
const novels = ref<any[]>([])
const characters = ref<any[]>([])
const storyNodes = ref<any[]>([])
const selectedNovel = ref<any>(null)
const selectedCharacters = ref<number[]>([])
const selectedNodes = ref<number[]>([])
const messages = ref<Array<{role: 'user' | 'assistant', content: string, timestamp: Date}>>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const options = ref({
  useRag: true,
  includeCharacters: true,
  includeStory: true
})

const suggestions = [
  '帮我生成一段角色对话',
  '分析这个角色的性格特点',
  '续写当前故事节点',
  '建议角色之间的互动场景'
]

// 加载小说列表
const loadNovels = async () => {
  try {
    const res = await http.get('/novel/listall', { params: { page: 1, pageSize: 100 } })
    novels.value = res.data?.records || res.data || []
  } catch (error) {
    console.error('加载小说失败:', error)
  }
}

// 选择小说
const selectNovel = async (novel: any) => {
  selectedNovel.value = novel
  selectedCharacters.value = []
  selectedNodes.value = []

  // 加载该小说的角色 - /novelCharacter/all 返回直接列表
  try {
    const res = await http.get(`/novelCharacter/all/${novel.id}`)
    characters.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载角色失败:', error)
    characters.value = []
  }

  // 加载该小说的故事节点
  try {
    const res = await http.get(`/storyNode/all/${novel.id}`)
    storyNodes.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载故事节点失败:', error)
    storyNodes.value = []
  }
}

// 切换角色选择
const toggleCharacter = (char: any) => {
  const idx = selectedCharacters.value.indexOf(char.id)
  if (idx > -1) {
    selectedCharacters.value.splice(idx, 1)
  } else {
    selectedCharacters.value.push(char.id)
  }
}

// 切换节点选择
const toggleNode = (node: any) => {
  const idx = selectedNodes.value.indexOf(node.id)
  if (idx > -1) {
    selectedNodes.value.splice(idx, 1)
  } else {
    selectedNodes.value.push(node.id)
  }
}

// 构建上下文提示
const buildContextPrompt = () => {
  let context = ''

  if (selectedNovel.value && options.value.includeCharacters) {
    const selectedChars = characters.value.filter(c => selectedCharacters.value.includes(c.id))
    if (selectedChars.length > 0) {
      context += '【角色信息】\n'
      selectedChars.forEach(char => {
        context += `- ${char.name}（${char.gender || '性别未知'}，${char.age || '年龄未知'}岁）:\n`
        if (char.appearance) context += `  * 外貌：${char.appearance}\n`
        if (char.personality) context += `  * 性格：${char.personality}\n`
        if (char.background) context += `  * 背景：${char.background}\n`
      })
      context += '\n'
    }
  }

  if (selectedNovel.value && options.value.includeStory) {
    const selectedNds = storyNodes.value.filter(n => selectedNodes.value.includes(n.id))
    if (selectedNds.length > 0) {
      context += '【故事节点】\n'
      selectedNds.forEach(node => {
        context += `- ${node.title}:\n`
        if (node.content) context += `  内容：${node.content}\n`
      })
      context += '\n'
    }
  }

  return context
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })
  inputMessage.value = ''
  scrollToBottom()

  try {
      isLoading.value = true

      try {
        // 【优化架构】仅传 ID，让后端从数据库查数据构建上下文
        // 好处：1.减少网络传输 2.数据一致性 3.可加Redis缓存
        const response = await http.post('/chat', {
          message: message,
          useRag: options.value.useRag,
          novelId: selectedNovel.value?.id,
          characterIds: selectedCharacters.value,
          storyNodeIds: selectedNodes.value,
          includeCharacters: options.value.includeCharacters,
          includeStory: options.value.includeStory
        })

        messages.value.push({
          role: 'assistant',
          content: assertStringResponse(response),
          timestamp: new Date()
        })
      } catch {
        // RAG请求失败，尝试降级模式（关闭RAG）

        const fallbackResponse = await http.post('/chat', {
          message: message,
          useRag: false,
          novelId: selectedNovel.value?.id,
          characterIds: selectedCharacters.value,
          storyNodeIds: selectedNodes.value,
          includeCharacters: options.value.includeCharacters,
          includeStory: options.value.includeStory
        })

        messages.value.push({
          role: 'assistant',
          content: assertStringResponse(fallbackResponse),
          timestamp: new Date()
        })
      }

    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，生成内容失败，请稍后重试。',
      timestamp: new Date()
    })
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

const handleSend = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const useSuggestion = (text: string) => {
  inputMessage.value = text
  textareaRef.value?.focus()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const formatMessage = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/【(.*?)】/g, '<strong>【$1】</strong>')
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadNovels()
})
</script>

<style scoped>
.rag-page {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
}

/* 背景动画 */
.bg-gradient-animation {
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.12) 0%, transparent 50%),
  radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
  radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
  radial-gradient(circle at center, #1e1b4b 0%, #0a0a0c 70%);
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

/* 页面头部 */
.page-header {
  position: relative;
  z-index: 10;
  padding: 30px 40px;
  background: rgba(10, 10, 12, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--glass-border);
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

/* 主容器 */
.rag-container {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 1600px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  padding: 20px;
  gap: 20px;
}

/* 左侧面板 */
.context-panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 8px;
}

.panel-section {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 16px;
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

/* 选项组 */
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

/* 右侧聊天区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
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

/* 消息容器 */
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

/* 消息项 */
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

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-item.assistant .message-text {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  border-bottom-left-radius: 4px;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: var(--text-primary);
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 6px;
  padding: 0 4px;
}

/* 打字指示器 */
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

/* 输入区域 */
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
  resize: none;
  min-height: 50px;
  max-height: 150px;
  line-height: 1.5;
  transition: all 0.3s;
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

.input-hint {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: center;
}

/* 滚动条样式 */
.context-panel::-webkit-scrollbar,
.messages-container::-webkit-scrollbar,
.selector-list::-webkit-scrollbar {
  width: 6px;
}

.context-panel::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track,
.selector-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.context-panel::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb,
.selector-list::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 3px;
}

.context-panel::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover,
.selector-list::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* 响应式 */
@media (max-width: 1024px) {
  .rag-container {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 120px);
  }

  .context-panel {
    width: 100%;
    max-height: 300px;
  }

  .chat-area {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px;
  }

  .rag-container {
    padding: 10px;
  }

  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>

<template>
  <div class="message-item" :class="message.role">
    <div class="message-avatar">
      <span v-if="message.role === 'user'">👤</span>
      <span v-else>🤖</span>
    </div>
    <div class="message-body">
      <div class="message-bubble">
        <div v-if="message.thinking || streamingThinking" class="thinking-block">
          <details :open="isStreaming && !!streamingThinking">
            <summary class="thinking-toggle">
              <span class="thinking-icon">💭</span>
              <span class="thinking-label">思考过程</span>
              <span class="thinking-badge">{{ message.thinking?.length || streamingThinking?.length || 0 }} 字符</span>
            </summary>
            <div class="thinking-content" v-html="renderMarkdown(message.thinking || streamingThinking || '')"></div>
          </details>
        </div>
        <div class="message-content" v-html="renderMarkdown(message.content || streamingContent || '')"></div>
        <div v-if="message.edited" class="edited-badge">✏️ 已编辑</div>
      </div>
      <div class="message-meta">
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        <span v-if="isStreaming" class="streaming-dot"></span>
        <div v-if="message.role === 'assistant' && !isStreaming" class="message-actions">
          <button class="action-btn" @click="$emit('regenerate')" title="重新生成">🔄</button>
          <button class="action-btn" @click="$emit('edit')" title="编辑回答">✏️</button>
        </div>
        <span v-if="message.version && message.version > 1" class="version-badge">v{{ message.version }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })

const renderer = new marked.Renderer()
renderer.code = ({ text, lang }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : ''
  let highlighted = text
  if (language) {
    try { highlighted = hljs.highlight(text, { language }).value }
    catch { highlighted = hljs.highlightAuto(text).value }
  } else {
    highlighted = hljs.highlightAuto(text).value
  }
  return `<pre><code class="hljs${language ? ` language-${language}` : ''}">${highlighted}</code></pre>`
}
marked.setOptions({ renderer })

const renderMarkdown = (text: string) => {
  const raw = marked.parse(text) as string
  return DOMPurify.sanitize(raw, {
    ADD_TAGS: ['details', 'summary'],
    ADD_ATTR: ['open']
  })
}

interface Props {
  message: {
    role: 'user' | 'assistant'
    content: string
    thinking?: string
    timestamp: Date
    edited?: boolean
    version?: number
  }
  streamingContent?: string
  streamingThinking?: string
  isStreaming?: boolean
}

defineProps<Props>()
defineEmits<{
  regenerate: []
  edit: []
}>()

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.message-item {
  display: flex;
  gap: 12px;
  max-width: 85%;
}
.message-item.user { align-self: flex-end; flex-direction: row-reverse; }

.message-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 1.2rem;
}
.message-item.user .message-avatar { background: rgba(168, 85, 247, 0.2); }

.message-body { flex: 1; min-width: 0; }

.message-bubble {
  padding: 14px 18px;
  border-radius: 20px;
  line-height: 1.7;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
.message-item.assistant .message-bubble {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  border-bottom-left-radius: 4px;
}
.message-item.user .message-bubble {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: var(--text-primary);
  border-bottom-right-radius: 4px;
}

.message-content :deep(p) { margin: 0 0 8px; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(pre) {
  margin: 8px 0; padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3); border-radius: 10px;
  overflow-x: auto; font-size: 0.85rem;
}
.message-content :deep(code) {
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.85em;
  padding: 2px 6px; background: rgba(0,0,0,0.2); border-radius: 4px;
}
.message-content :deep(pre code) { padding: 0; background: none; }
.message-content :deep(ul), .message-content :deep(ol) { padding-left: 20px; margin: 4px 0; }
.message-content :deep(blockquote) {
  margin: 8px 0; padding: 8px 14px;
  border-left: 3px solid var(--neon-blue, #4b8bf5);
  background: rgba(59, 130, 246, 0.06);
  border-radius: 0 8px 8px 0;
}
.message-content :deep(table) { width: 100%; border-collapse: collapse; margin: 8px 0; }
.message-content :deep(th), .message-content :deep(td) {
  padding: 8px 12px; border: 1px solid rgba(255,255,255,0.1); text-align: left;
}
.message-content :deep(th) { background: rgba(59,130,246,0.1); font-weight: 600; }
.message-content :deep(h1), .message-content :deep(h2),
.message-content :deep(h3), .message-content :deep(h4) { margin: 16px 0 8px; color: var(--text-primary); }
.message-content :deep(h1) { font-size: 1.3rem; }
.message-content :deep(h2) { font-size: 1.15rem; }
.message-content :deep(h3) { font-size: 1.05rem; }
.message-content :deep(hr) { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0; }
.message-content :deep(a) { color: var(--neon-cyan, #28c4d4); text-decoration: underline; }
.message-content :deep(img) { max-width: 100%; border-radius: 8px; margin: 8px 0; }

.thinking-block { margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; }

.thinking-toggle {
  cursor: pointer; display: flex; align-items: center;
  gap: 6px; font-size: 0.85rem; color: var(--neon-purple, #a855f7);
  padding: 4px 0; user-select: none;
}
.thinking-toggle::-webkit-details-marker { display: none; }
.thinking-toggle::before {
  content: '▶'; display: inline-block;
  transition: transform 0.2s; font-size: 0.75rem; margin-right: 4px;
}
details[open] > .thinking-toggle::before { transform: rotate(90deg); }

.thinking-icon { font-size: 0.9rem; }
.thinking-label { font-weight: 600; }
.thinking-badge {
  font-size: 0.75rem; color: var(--text-muted);
  background: rgba(255,255,255,0.05); padding: 1px 8px;
  border-radius: 8px; margin-left: auto;
}
.thinking-content {
  margin-top: 8px; padding: 12px; border-radius: 8px;
  background: rgba(168, 85, 247, 0.05);
  border: 1px solid rgba(168, 85, 247, 0.15);
  font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;
}
.thinking-content :deep(pre) { background: rgba(0,0,0,0.2); }
.thinking-content :deep(code) { background: rgba(168,85,247,0.1); }

.edited-badge {
  display: inline-block; font-size: 0.75rem; color: var(--neon-cyan, #28c4d4);
  margin-top: 8px; padding: 2px 8px;
  background: rgba(40, 196, 212, 0.1); border-radius: 8px;
}

.message-meta {
  display: flex; align-items: center; gap: 6px;
  margin-top: 6px; padding: 0 4px;
}
.message-time { font-size: 0.75rem; color: var(--text-muted); }

.streaming-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--neon-cyan, #28c4d4);
  animation: blink 1s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.message-actions { display: flex; gap: 2px; margin-left: auto; }
.action-btn {
  padding: 2px 6px; border: none; border-radius: 4px;
  background: transparent; color: var(--text-muted);
  cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
  opacity: 0;
}
.message-item:hover .action-btn { opacity: 0.6; }
.action-btn:hover { opacity: 1 !important; background: rgba(255,255,255,0.05); }

.version-badge {
  font-size: 0.7rem; color: var(--text-muted);
  background: rgba(255,255,255,0.05); padding: 0 6px; border-radius: 4px;
}
</style>

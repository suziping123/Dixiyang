<template>
  <div class="message-item" :class="[message.role, { 'user-editing-mode': isEditing }]">
    <div class="message-avatar">
      <el-icon v-if="message.role === 'user'"><UserFilled /></el-icon>
      <el-icon v-else><MagicStick /></el-icon>
    </div>
    <div class="message-body">
      <div class="message-bubble" :class="{ 'is-browsing': browseIndex !== null }">
        <div v-if="message.thinking || streamingThinking" class="thinking-block">
          <details :open="isStreaming && !!streamingThinking">
            <summary class="thinking-toggle">
              <span class="thinking-icon"><el-icon><Loading /></el-icon></span>
              <span class="thinking-label">思考过程</span>
              <span class="thinking-badge">{{ message.thinking?.length || streamingThinking?.length || 0 }} 字符</span>
            </summary>
            <div class="thinking-content" v-html="renderMarkdown(message.thinking || streamingThinking || '')"></div>
          </details>
        </div>
        <div class="message-content" v-if="!isEditing" v-html="renderMarkdown(displayContent || streamingContent || '')"></div>
        <textarea
          v-else
          class="user-edit-textarea"
          :value="editDraft"
          @input="editDraft = ($event.target as HTMLTextAreaElement).value"
          placeholder="输入要修改的内容..."
        ></textarea>
        <!-- 单一切换器：挂在用户消息上；AI 消息不出条，由 browseMap 联动切换内容+描边 -->
        <div v-if="message.role === 'user' && versionCount > 0 && !isEditing" class="version-bar">
          <button type="button" class="vbtn" @click="prevVersion" title="上一个版本">‹</button>
          <span class="vpos">{{ positionLabel }}</span>
          <button type="button" class="vbtn" @click="nextVersion" title="下一个版本">›</button>
          <template v-if="browseIndex !== null">
            <button type="button" class="vbtn vbtn-restore" @click="handleRestore" title="恢复此版本为对话内容">恢复此版本</button>
            <button type="button" class="vbtn vbtn-del" @click="handleDelete" title="删除此版本（编辑次数减一）">删除</button>
          </template>
        </div>
      </div>
      <div v-if="displayReferences.length > 0" class="references-block">
        <div class="references-title">
          <el-icon><Collection /></el-icon>
          参考来源</div>
        <div class="references-list">
          <div v-for="(ref, ri) in displayReferences.slice(0, 5)" :key="ri" class="reference-item" @click="openSource(ref)">
            <span class="ref-source">{{ ref.source }}</span>
            <span class="ref-title">{{ ref.title }}</span>
            <span class="ref-score">{{ (ref.score * 100).toFixed(1) }}%</span>
          </div>
          <div v-if="displayReferences.length > 5" class="ref-more">还有 {{ displayReferences.length - 5 }} 个参考来源...</div>
        </div>
      </div>
      <div class="message-meta">
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        <span v-if="isStreaming" class="streaming-dot"></span>
        <div v-if="message.role === 'assistant' && !isStreaming" class="message-actions">
          <button class="action-btn" @click="$emit('regenerate')" title="重新生成">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
          </button>
          <button class="action-btn pencil-btn" @click="handleEdit" title="编辑回答">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
          </button>
          <button class="action-btn extract-btn" @click="$emit('extractSettings', index ?? 0)" title="总结为设定">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13zM6 20V4h5v7h7v9H6z"/><path d="M8 15h8v2H8zm0-4h8v2H8z"/></svg>
          </button>
        </div>
        <div v-if="message.role === 'user' && !isEditing" class="message-actions">
          <button class="action-btn user-edit-btn" @click="$emit('userEdit', message.content)" title="编辑消息">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
          </button>
        </div>
      </div>
      <div v-if="isEditing" class="user-edit-actions">
        <button class="user-edit-btn-confirm" @click="$emit('userEditSave', editDraft)">确认</button>
        <button class="user-edit-btn-cancel" @click="$emit('userEditCancel')">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { renderMarkdown } from '@/utils/markdown'
import { Collection, UserFilled, MagicStick } from '@element-plus/icons-vue'

interface Props {
  message: {
    role: 'user' | 'assistant'
    content: string
    thinking?: string
    references?: { source: string; title: string; content: string; score: number }[]
    timestamp: Date
    edited?: boolean
    version?: number
    versions?: string[]
    paired?: string[]
  }
  index?: number
  streamingContent?: string
  streamingThinking?: string
  streamingReferences?: { source: string; title: string; content: string; score: number }[]
  isStreaming?: boolean
  isEditing?: boolean
  onEdit?: (index: number) => void
  // 受控浏览态：由父组件统一持有，驱动提问↔回答成对联动
  browseIndex?: number | null
  // 版本条内容源：paired=与提问成对的存档（回答默认优先）/ versions=独立编辑历史
  browseSource?: 'versions' | 'paired'
}

import { ref, watch, computed } from 'vue'
import { confirmDelete } from '@/utils/confirm'

const props = defineProps<Props>()
const emit = defineEmits<{
  regenerate: []
  edit: [index: number]
  userEdit: [content: string]
  userEditSave: [content: string]
  userEditCancel: []
  extractSettings: [index: number]
  // 单参数：内联模板 $event 只取第一个 emit 参数，index 由父组件 v-for 提供
  restoreVersion: [versionIndex: number]
  deleteVersion: [versionIndex: number]
  'update:browseIndex': [index: number | null]
}>()

const editDraft = ref('')

// 版本浏览（受控）：null=查看当前内容，否则查看 versionList[i]
const browseIndex = computed<number | null>({
  get: () => props.browseIndex ?? null,
  set: (v) => emit('update:browseIndex', v)
})

// 版本条内容源：回答有 paired（编辑提问产生的成对存档）时优先，否则用独立编辑历史
const versionList = computed<string[]>(() => {
  if (props.browseSource === 'paired') return props.message.paired ?? []
  return props.message.versions ?? []
})

const versionCount = computed(() => versionList.value.length)

const displayContent = computed(() => {
  if (browseIndex.value === null) return props.message.content
  return versionList.value[browseIndex.value] ?? props.message.content
})

// 总位置数 = 历史版本数 + 当前（显示数字必须与实际可切换格数一致，否则"看似2个却能切3个"）
const totalSlots = computed(() => versionCount.value + 1)

const positionLabel = computed(() => {
  if (browseIndex.value === null) return `当前 1/${totalSlots.value}`
  // 序列：第1格=当前，第2格=最近改前，…，末格=最早原文
  return `${browseIndex.value + 2}/${totalSlots.value}`
})

const prevVersion = () => {
  const n = versionCount.value
  if (!n) return
  if (browseIndex.value === null) browseIndex.value = n - 1
  else if (browseIndex.value > 0) browseIndex.value--
  else browseIndex.value = null
}

const nextVersion = () => {
  const n = versionCount.value
  if (!n) return
  if (browseIndex.value === null) browseIndex.value = 0
  else if (browseIndex.value < n - 1) browseIndex.value++
  else browseIndex.value = null
}

const handleRestore = () => {
  if (browseIndex.value === null) return
  emit('restoreVersion', browseIndex.value)
  browseIndex.value = null
}

const handleDelete = async () => {
  if (browseIndex.value === null) return
  const versionIndex = browseIndex.value
  const ok = await confirmDelete('删除该历史版本？编辑次数将减一，可继续修改', '警告')
  if (!ok) return
  emit('deleteVersion', versionIndex)
  browseIndex.value = null
}

// 版本列表变化（编辑新增/删除）后越界回退到当前（通知父组件）
watch(versionCount, (n) => {
  if (browseIndex.value !== null && browseIndex.value >= n) emit('update:browseIndex', null)
})

const displayReferences = computed(() => {
  return props.streamingReferences && props.streamingReferences.length > 0
    ? props.streamingReferences
    : (props.message.references ?? [])
})

watch(() => props.isEditing, (val) => {
  if (val) editDraft.value = props.message.content
})

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleEdit = () => {
  if (props.index !== undefined && props.onEdit) {
    props.onEdit(props.index)
  }
}

const openSource = (ref: { source: string; title: string; content: string; score: number }) => {
  // 点击参考气泡时复制来源信息到剪贴板，方便用户查阅
  const text = `来源: ${ref.source}\n标题: ${ref.title}\n内容: ${ref.content}`
  navigator.clipboard?.writeText(text).catch(() => {})
}

</script>

<style scoped>
.message-item {
  display: flex;
  gap: 12px;
  max-width: 85%;
}
.message-item.user { align-self: flex-end; flex-direction: row-reverse; }

.user-editing-mode .message-bubble {
  border: 2px solid #28c4d4;
  background: rgba(40, 196, 212, 0.05);
}

.user-edit-textarea {
  width: 100%;
  min-height: 60px;
  padding: 12px;
  border: 1px solid rgba(40, 196, 212, 0.4);
  border-radius: 8px;
  background: rgba(0,0,0,0.2);
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.7;
  resize: vertical;
  font-family: inherit;
  margin-top: 8px;
}

.user-edit-textarea:focus {
  outline: none;
  border-color: #28c4d4;
  box-shadow: 0 0 0 2px rgba(40,196,212,0.15);
}

.user-edit-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

.user-edit-btn-confirm {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: #28c4d4;
  color: white;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.user-edit-btn-confirm:hover {
  background: #0ea5e9;
  transform: scale(1.05);
}

.user-edit-btn-cancel {
  padding: 6px 12px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.user-edit-btn-cancel:hover {
  background: rgba(255,255,255,0.05);
}

.user-edit-hint {
  font-size: 0.75rem;
  color: #28c4d4;
  margin-top: 4px;
  display: block;
}

.message-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  color: var(--neon-cyan, #28c4d4);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 1.2rem;
}
.message-item.user .message-avatar { background: rgba(168, 85, 247, 0.2); color: var(--neon-purple, #a855f7); }

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
  border-top-left-radius: 4px;
}
.message-item.user .message-bubble {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: var(--text-primary);
  border-top-right-radius: 4px;
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

.references-block {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.references-title {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.references-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.reference-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.12);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.reference-item:hover {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.25);
}

.ref-source {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.15);
  color: var(--neon-cyan, #28c4d4);
  flex-shrink: 0;
}

.ref-title {
  flex: 1;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ref-score {
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.ref-more {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  padding: 4px 0;
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

.message-actions { display: flex; gap: 6px; margin-left: auto; align-items: center; }
.action-btn {
  padding: 6px 10px; border: none; border-radius: 6px;
  background: transparent; color: var(--text-muted);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; width: 36px; height: 36px; position: relative;
}
.action-btn svg { width: 18px; height: 18px; display: block; position: relative; z-index: 1; }
.message-item:hover .action-btn { opacity: 0.7; }
.action-btn:hover { opacity: 1 !important; background: rgba(255,255,255,0.08); transform: scale(1.05); }
.action-btn:hover svg { animation: spin-write 1s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }

@keyframes spin-write {
  0% { transform: rotate(0deg) scale(1); }
  30% { transform: rotate(190deg) scale(1.1); }
  55% { transform: rotate(170deg) scale(0.95); }
  75% { transform: rotate(185deg) scale(1.02); }
  100% { transform: rotate(180deg) scale(1); }
}

.pencil-btn::after {
  content: ''; position: absolute; pointer-events: none;
  left: 12px; bottom: 10px; height: 1.5px; width: 0;
  background: linear-gradient(90deg, var(--neon-cyan, #28c4d4), transparent);
  border-radius: 1px; opacity: 0;
}
.pencil-btn:hover::after { animation: ink-trail 1s ease-out reverse; }
.pencil-btn:hover svg { animation: pencil-nudge 0.5s ease-out verse; color: var(--neon-cyan, #ffffff); }

@keyframes pencil-nudge {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(180deg); }
  50% { transform: rotate(180deg); }
  75% { transform: rotate(160deg); }
  100% { transform: rotate(360deg); }
}
@keyframes ink-trail {
  0% { width: 0; opacity: 0; }
  45% { width: 10px; opacity: 0.75; }
  100% { width: 25px; opacity: 1; }
}

.extract-btn:hover svg { animation: none; color: var(--neon-cyan, #28c4d4); }

/* 版本切换条：编辑过（versions≥1）的气泡底部常显 */
.version-bar {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  margin-top: 10px; padding-top: 8px;
  border-top: 1px dashed rgba(255,255,255,0.12);
}
.vbtn {
  min-width: 26px; height: 26px; padding: 0 8px;
  border: 1px solid rgba(255,255,255,0.14); border-radius: 6px;
  background: rgba(255,255,255,0.04); color: var(--text-secondary);
  cursor: pointer; font-size: 0.8rem; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.vbtn:hover { background: rgba(255,255,255,0.1); color: var(--text-primary); }
.vpos {
  font-size: 0.75rem; color: var(--text-muted);
  min-width: 96px; text-align: center;
}
.vbtn-restore {
  color: var(--neon-cyan, #28c4d4);
  border-color: rgba(40,196,212,0.35);
}
.vbtn-restore:hover { background: rgba(40,196,212,0.12); color: var(--neon-cyan, #28c4d4); }
.vbtn-del {
  color: var(--danger, #f56c6c);
  border-color: rgba(245,108,108,0.35);
}
.vbtn-del:hover { background: rgba(245,108,108,0.12); color: var(--danger, #f56c6c); }
.is-browsing { outline: 1px solid rgba(40,196,212,0.45); }
</style>

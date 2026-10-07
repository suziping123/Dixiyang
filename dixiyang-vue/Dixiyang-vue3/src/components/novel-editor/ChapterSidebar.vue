<template>
  <aside class="chapter-sidebar">
    <!-- 同步状态 -->
    <section class="panel">
      <h3 class="panel-title">同步状态</h3>
      <div class="sync-status" :data-state="syncState">
        <span class="sync-dot"></span>
        <span class="sync-label">{{ syncLabel }}</span>
      </div>
      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-key">云端版本</span>
          <span class="meta-val">v{{ serverVersion }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-key">字数</span>
          <span class="meta-val">{{ wordCount }}</span>
        </div>
        <div class="meta-item" v-if="chapter?.update_time">
          <span class="meta-key">更新于</span>
          <span class="meta-val">{{ formatTime(chapter.update_time) }}</span>
        </div>
      </div>
      <button
        class="save-cloud-btn"
        :disabled="!canSaveCloud"
        :class="{ dirty: isDirty }"
        @click="$emit('save-cloud')"
      >
        <span v-if="syncState === 'uploading'" class="spinner"></span>
        {{ syncState === 'uploading' ? '正在上传…' : '保存到云端' }}
      </button>
      <p v-if="isDirty && syncState !== 'uploading'" class="dirty-hint">
        本地有未上传到云端的修改
      </p>
    </section>

    <!-- AI 辅助 -->
    <section class="panel">
      <h3 class="panel-title">AI 补全 · Ctrl+Space</h3>
      <div class="ai-status" :data-state="aiState">
        <span class="sync-dot"></span>
        <span class="sync-label">{{ aiLabel }}</span>
      </div>
      <button class="ai-trigger-btn" :disabled="aiState === 'thinking' || aiState === 'disconnected'" @click="$emit('ai-trigger')">
        请求补全
      </button>
      <p class="ai-note">补全仅以幽灵文本展示，Tab 接受，Esc 取消，继续输入自动失效。</p>
      <slot name="ai-context" />
    </section>

    <!-- 章节信息 -->
    <section class="panel" v-if="chapter">
      <h3 class="panel-title">章节信息</h3>
      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-key">章节 ID</span>
          <span class="meta-val">{{ chapter.id }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-key">内容大小</span>
          <span class="meta-val">{{ formatSize(chapter.content_size) }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-key">正文存储</span>
          <span class="meta-val">{{ chapter.content_path ? '文件存储' : '未保存' }}</span>
        </div>
      </div>
    </section>

    <div v-else class="empty-hint">从左侧选择或新建章节</div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Chapter } from '@/api/types'

export type SyncState = 'local-clean' | 'local-dirty' | 'uploading' | 'uploaded' | 'conflict' | 'upload-failed'
export type AIState = 'ready' | 'thinking' | 'error' | 'disconnected'

const props = defineProps<{
  chapter: Chapter | null
  syncState: SyncState
  serverVersion: number
  isDirty: boolean
  wordCount: number
  aiState: AIState
}>()

defineEmits<{
  'save-cloud': []
  'ai-trigger': []
}>()

const SYNC_LABELS: Record<SyncState, string> = {
  'local-clean': '已保存到本地 · 与云端一致',
  'local-dirty': '有未上传修改',
  uploading: '正在上传…',
  uploaded: '已保存到云端',
  conflict: '与云端版本冲突',
  'upload-failed': '上传失败',
}

const AI_LABELS: Record<AIState, string> = {
  ready: 'AI 就绪',
  thinking: 'AI 思考中…',
  error: 'AI 补全失败',
  disconnected: 'AI 未连接',
}

const syncLabel = computed(() => SYNC_LABELS[props.syncState])
const aiLabel = computed(() => AI_LABELS[props.aiState])
const canSaveCloud = computed(
  () => props.chapter !== null && (props.isDirty || props.syncState === 'conflict') && props.syncState !== 'uploading',
)

function formatTime(iso: string): string {
  try {
    const d = new Date(iso)
    return `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

function formatSize(size: number): string {
  if (!size) return '0 B'
  if (size < 1024) return `${size} B`
  return `${(size / 1024).toFixed(1)} KB`
}
</script>

<style scoped>
.chapter-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  /* 玻璃面板：与左侧树对称，背景区透出但不影响读字 */
  background: rgba(12, 14, 19, 0.45);
  backdrop-filter: blur(18px) saturate(1.15);
  -webkit-backdrop-filter: blur(18px) saturate(1.15);
  border-left: 1px solid var(--surface-glass-border);
  overflow-y: auto;
  padding: 16px 14px;
  gap: 14px;
}

.panel {
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-md);
  padding: 14px;
}
.panel-title {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-secondary);
  margin: 0 0 10px;
}

.sync-status,
.ai-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.sync-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}
.sync-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.sync-status[data-state='local-clean'] .sync-dot,
.sync-status[data-state='uploaded'] .sync-dot {
  background: var(--accent-cyan);
}
.sync-status[data-state='local-dirty'] .sync-dot {
  background: var(--warning);
}
.sync-status[data-state='uploading'] .sync-dot {
  background: var(--accent-primary);
  animation: pulse 1s infinite;
}
.sync-status[data-state='conflict'] .sync-dot,
.sync-status[data-state='upload-failed'] .sync-dot {
  background: var(--danger);
}
.ai-status[data-state='ready'] .sync-dot {
  background: var(--accent-cyan);
}
.ai-status[data-state='thinking'] .sync-dot {
  background: var(--accent-primary);
  animation: pulse 1s infinite;
}
.ai-status[data-state='error'] .sync-dot,
.ai-status[data-state='disconnected'] .sync-dot {
  background: var(--danger);
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.meta-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}
.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
}
.meta-key {
  color: var(--text-muted);
}
.meta-val {
  color: var(--text-secondary);
}

.save-cloud-btn {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.save-cloud-btn.dirty {
  border-color: var(--accent-primary);
  color: #fff;
  background: var(--accent-soft-strong);
}
.save-cloud-btn.dirty:hover {
  background: var(--accent-primary);
}
.save-cloud-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.dirty-hint {
  margin: 8px 0 0;
  font-size: 0.74rem;
  color: var(--warning);
  text-align: center;
}

.ai-trigger-btn {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}
.ai-trigger-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--text-primary);
}
.ai-trigger-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.ai-note {
  margin: 10px 0 0;
  font-size: 0.72rem;
  line-height: 1.6;
  color: var(--text-disabled);
}

.empty-hint {
  text-align: center;
  color: var(--text-disabled);
  font-size: 0.82rem;
  padding: 40px 0;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<template>
  <el-dialog
    v-model="visible"
    title="AI 设定助手"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="settings-dialog">
      <!-- 左侧：对话上下文 -->
      <div class="dialog-left">
        <div class="section-title">对话上下文</div>
        <div class="conversation-preview">
          <div
            v-for="(msg, i) in contextMessages"
            :key="i"
            class="context-msg"
            :class="msg.role"
          >
            <span class="msg-role">{{ msg.role === 'user' ? '👤 用户' : '🤖 AI' }}</span>
            <div class="msg-content">{{ msg.content }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧：JSON 预览 -->
      <div class="dialog-right">
        <div class="section-header">
          <span class="section-title">提取的设定</span>
          <el-button
            v-if="!isEditing"
            type="primary"
            link
            @click="isEditing = true"
          >
            编辑
          </el-button>
          <el-button
            v-else
            type="primary"
            link
            @click="isEditing = false"
          >
            预览
          </el-button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>AI 正在分析对话...</span>
        </div>

        <!-- 预览模式 -->
        <div v-else-if="!isEditing" class="json-preview">
          <pre v-if="settings && Object.keys(settings).length > 0">{{ JSON.stringify(settings, null, 2) }}</pre>
          <div v-else class="empty-state">未提取到设定信息</div>
        </div>

        <!-- 编辑模式 -->
        <textarea
          v-else
          class="json-editor"
          v-model="editText"
          placeholder="JSON 设定数据..."
        ></textarea>

        <!-- 角色关联 -->
        <div class="character-select">
          <span class="select-label">关联角色：</span>
          <el-select
            v-model="selectedCharacterId"
            placeholder="选择角色"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="char in characters"
              :key="char.id"
              :label="char.name"
              :value="char.id"
            />
          </el-select>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">打回</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import http from '@/utils/http'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Character {
  id: number
  name: string
}

const props = defineProps<{
  modelValue: boolean
  conversation: Message[]
  novelId?: number | string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const visible = ref(props.modelValue)
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const settings = ref<Record<string, unknown> | null>(null)
const editText = ref('')
const selectedCharacterId = ref<number | null>(null)
const characters = ref<Character[]>([])
const contextMessages = ref<Message[]>([])

// 监听 visible 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    init()
  }
})

// 监听 visible 内部变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function init() {
  // 截取上下文（前后各2条）
  const conv = props.conversation || []
  const len = conv.length
  const start = Math.max(0, len - 5)
  contextMessages.value = conv.slice(start)

  // 加载角色列表
  if (props.novelId) {
    try {
      const res = await http.get(`/novelCharacter/all/${props.novelId}`)
      characters.value = res.data || []
    } catch {
      characters.value = []
    }
  }

  // 自动提取设定
  await extractSettings()
}

async function extractSettings() {
  if (contextMessages.value.length === 0) return

  loading.value = true
  settings.value = null
  isEditing.value = false

  try {
    const conversation = contextMessages.value
      .map(m => `${m.role === 'user' ? '用户' : 'AI'}：${m.content}`)
      .join('\n')

    const res = await http.post('/novelCharacter/extractSettings', {
      conversation
    })

    settings.value = res.data?.settings || {}
    editText.value = JSON.stringify(settings.value, null, 2)
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '提取失败'
    ElMessage.error(message)
    settings.value = {}
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!selectedCharacterId.value) {
    ElMessage.warning('请选择要关联的角色')
    return
  }

  let dataToSave: Record<string, unknown>

  if (isEditing.value) {
    try {
      dataToSave = JSON.parse(editText.value)
    } catch {
      ElMessage.error('JSON 格式错误')
      return
    }
  } else {
    dataToSave = settings.value || {}
  }

  if (!dataToSave || Object.keys(dataToSave).length === 0) {
    ElMessage.warning('没有要保存的设定')
    return
  }

  saving.value = true
  try {
    await http.post('/novelCharacter/saveSettings', {
      characterId: selectedCharacterId.value,
      settings: dataToSave
    })
    ElMessage.success('设定保存成功')
    emit('saved')
    visible.value = false
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '保存失败'
    ElMessage.error(message)
  } finally {
    saving.value = false
  }
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.settings-dialog {
  display: flex;
  gap: 16px;
  min-height: 400px;
}

.dialog-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dialog-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-on-card);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.conversation-preview {
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--surface-glass-border);
  border-radius: 8px;
  padding: 12px;
  background: var(--surface-glass);
  max-height: 350px;
}

.context-msg {
  margin-bottom: 12px;
}

.context-msg:last-child {
  margin-bottom: 0;
}

.msg-role {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: block;
}

.msg-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-on-card);
  white-space: pre-wrap;
  word-break: break-word;
}

.json-preview {
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--surface-glass-border);
  border-radius: 8px;
  padding: 12px;
  background: var(--surface-glass);
  max-height: 300px;
}

.json-preview pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-on-card);
  white-space: pre-wrap;
  word-break: break-word;
}

.json-editor {
  flex: 1;
  width: 100%;
  min-height: 250px;
  border: 1px solid var(--surface-glass-border);
  border-radius: 8px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  background: var(--surface-input);
  color: var(--text-on-input);
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 0;
}

.character-select {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-label {
  font-size: 14px;
  color: var(--text-on-card);
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

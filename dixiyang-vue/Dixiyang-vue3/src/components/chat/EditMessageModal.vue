<template>
  <el-dialog v-model="dialogVisible" title="编辑回答" width="850px" @close="handleClose" :close-on-click-modal="false">
    <div class="edit-layout">
      <div class="original-section">
        <label class="section-label">原始回答</label>
        <div class="original-content" v-html="renderedOriginal"></div>
      </div>
      <div class="edit-section">
        <label class="section-label">修改内容</label>
        <textarea v-model="editContent" class="edit-textarea" @keydown.enter.exact.prevent="handleSave"></textarea>
      </div>
    </div>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSave" :disabled="!editContent.trim()">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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

const dialogVisible = ref(false)
const editContent = ref('')
const originalContent = ref('')

const renderedOriginal = computed(() => renderMarkdown(originalContent.value))

const open = (content: string) => {
  originalContent.value = content
  editContent.value = content
  dialogVisible.value = true
}

const emit = defineEmits<{
  save: [content: string]
}>()

const handleSave = () => {
  if (editContent.value.trim()) {
    emit('save', editContent.value)
    dialogVisible.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

defineExpose({ open })
</script>

<style scoped>
.edit-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.section-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary, #aaa);
  margin-bottom: 8px;
}
.original-section {
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  max-height: 350px;
  overflow-y: auto;
}
.original-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-secondary, #ccc);
}
.original-content :deep(p) { margin: 0 0 6px; }
.original-content :deep(pre) {
  margin: 6px 0; padding: 8px 12px;
  background: rgba(0,0,0,0.3); border-radius: 8px;
  overflow-x: auto; font-size: 0.8rem;
}
.original-content :deep(code) {
  font-family: monospace; font-size: 0.85em;
  padding: 1px 4px; background: rgba(0,0,0,0.2); border-radius: 4px;
}
.edit-section {
  flex: 1;
}
.edit-textarea {
  width: 100%;
  min-height: 300px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  background: rgba(0,0,0,0.2);
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.7;
  resize: vertical;
  font-family: inherit;
}
.edit-textarea:focus {
  outline: none;
  border-color: var(--neon-cyan, #28c4d4);
  box-shadow: 0 0 0 2px rgba(40,196,212,0.15);
}
</style>

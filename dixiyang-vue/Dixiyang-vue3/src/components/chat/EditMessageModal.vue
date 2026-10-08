<template>
  <el-dialog v-model="dialogVisible" title="编辑消息" width="720px" @close="handleClose" :close-on-click-modal="false">
    <div class="edit-layout">
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
import { ref } from 'vue'

const dialogVisible = ref(false)
const editContent = ref('')

const open = (content: string) => {
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
.edit-section {
  flex: 1;
}
.edit-textarea {
  width: 100%;
  min-height: 380px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  background: rgba(0,0,0,0.2);
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.7;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}
.edit-textarea:focus {
  outline: none;
  border-color: var(--neon-cyan, #28c4d4);
  box-shadow: 0 0 0 2px rgba(40,196,212,0.15);
}
</style>

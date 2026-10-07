<template>
  <el-dialog
    v-model="visible"
    title="云端内容已发生变化"
    width="520px"
    align-center
    :close-on-click-modal="false"
    @close="$emit('cancel')"
  >
    <div class="conflict-body">
      <p class="conflict-tip">
        云端内容已发生变化，当前本地版本可能不是最新版本。请选择处理方式：
      </p>
      <div class="conflict-meta">
        <div class="meta-row">
          <span>云端版本</span>
          <span>v{{ serverVersion }}</span>
        </div>
        <div class="meta-row">
          <span>本地同步版本</span>
          <span>v{{ localVersion }}</span>
        </div>
      </div>
      <div class="conflict-options">
        <button class="option-btn primary" @click="$emit('use-local')">
          <strong>使用本地版本覆盖云端</strong>
          <span>保留当前编辑内容，强制上传</span>
        </button>
        <button class="option-btn" @click="$emit('use-remote')">
          <strong>使用云端版本</strong>
          <span>放弃本地修改，拉取云端内容</span>
        </button>
      </div>
    </div>
    <template #footer>
      <el-button @click="$emit('cancel')">取消</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  serverVersion: number
  localVersion: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  cancel: []
  'use-local': []
  'use-remote': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
</script>

<style scoped>
.conflict-body {
  color: var(--text-secondary);
}
.conflict-tip {
  margin: 0 0 16px;
  font-size: 0.9rem;
  line-height: 1.7;
}
.conflict-meta {
  background: var(--warning-soft);
  border: 1px solid var(--warning-border);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  margin-bottom: 16px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  padding: 3px 0;
}
.conflict-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.option-btn {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
  padding: 12px 14px;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: var(--surface-card);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}
.option-btn:hover {
  border-color: var(--accent-primary);
}
.option-btn.primary {
  border-color: var(--accent-primary);
  background: var(--accent-soft);
}
.option-btn strong {
  font-size: 0.88rem;
}
.option-btn span {
  font-size: 0.76rem;
  color: var(--text-muted);
}
</style>

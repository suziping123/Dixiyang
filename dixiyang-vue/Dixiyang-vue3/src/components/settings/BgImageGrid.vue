<template>
  <div class="bg-image-grid">
    <div
      v-for="img in list"
      :key="img.id"
      class="bg-image-card"
      :class="{ active: activeId === img.id }"
      role="button"
      tabindex="0"
      :aria-pressed="activeId === img.id"
      @click="toggle(img.id)"
      @keydown.enter="toggle(img.id)"
      @keydown.space.prevent="toggle(img.id)"
    >
      <img v-if="loaded[img.id]" :src="loaded[img.id]" :alt="img.label" class="bg-image-thumb" />
      <div v-else class="bg-image-placeholder">加载中</div>
      <span class="bg-image-label">{{ img.label }}</span>
      <button
        v-if="img.isCustom"
        class="bg-delete-btn"
        type="button"
        title="删除该自定义背景"
        aria-label="删除该自定义背景"
        @click.stop="emit('delete', img.id)"
      >
        <Close />
      </button>
    </div>

    <div
      class="bg-image-card no-bg"
      :class="{ active: !activeId }"
      role="button"
      tabindex="0"
      :aria-pressed="!activeId"
      @click="emit('select', undefined)"
      @keydown.enter="emit('select', undefined)"
      @keydown.space.prevent="emit('select', undefined)"
    >
      <Close class="no-bg-icon" />
      <span class="bg-image-label">不使用背景</span>
    </div>

    <div
      class="bg-image-card upload-card"
      role="button"
      tabindex="0"
      @click="emit('upload')"
      @keydown.enter="emit('upload')"
    >
      <Plus class="upload-icon" />
      <span class="bg-image-label">上传背景</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Close, Plus } from '@element-plus/icons-vue'
import type { BgImageItem } from '@/composables/useBackgroundConfig'

interface Props {
  list: BgImageItem[]
  loaded: Record<string, string>
  activeId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [id: string | undefined]
  delete: [id: string]
  upload: []
}>()

/** 再次点击已选中的背景 = 取消选择 */
const toggle = (id: string) => {
  emit('select', props.activeId === id ? undefined : id)
}
</script>

<style scoped>
.bg-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
}

.bg-image-card {
  position: relative;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 16 / 10;
  transition:
    border-color var(--dur-fast) var(--ease-out),
    background var(--dur-fast) var(--ease-out);
  background: var(--surface-input);
}

.bg-image-card:hover {
  border-color: var(--surface-glass-border-hover);
}

.bg-image-card:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 1px;
}

.bg-image-card.active {
  border-color: var(--accent-primary);
}

.bg-image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bg-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.bg-image-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.6875rem;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 无背景 / 上传 */
.bg-image-card.no-bg,
.bg-image-card.upload-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.bg-image-card.upload-card {
  border-style: dashed;
}

.bg-image-card.upload-card:hover {
  border-color: var(--accent-primary);
}

.no-bg-icon {
  width: 22px;
  height: 22px;
  color: var(--text-muted);
  transition: color var(--dur-fast) var(--ease-out);
}

.bg-image-card.no-bg:hover .no-bg-icon {
  color: var(--text-secondary);
}

.upload-icon {
  width: 24px;
  height: 24px;
  color: var(--text-muted);
  transition: color var(--dur-fast) var(--ease-out);
}

.bg-image-card.upload-card:hover .upload-icon {
  color: var(--accent-primary);
}

/* 自定义背景删除 */
.bg-delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.55);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition:
    opacity var(--dur-fast) var(--ease-out),
    background var(--dur-fast) var(--ease-out);
  z-index: 1;
}

.bg-delete-btn svg {
  width: 13px;
  height: 13px;
}

.bg-image-card:hover .bg-delete-btn,
.bg-delete-btn:focus-visible {
  opacity: 1;
}

.bg-delete-btn:hover {
  background: var(--danger);
  color: #fff;
}

.bg-delete-btn:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .bg-image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

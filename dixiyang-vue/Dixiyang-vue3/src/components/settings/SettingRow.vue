<template>
  <div class="setting-row" :class="{ 'is-stacked': stacked }">
    <div class="row-text">
      <span class="row-label">{{ label }}</span>
      <span v-if="desc" class="row-desc">{{ desc }}</span>
    </div>
    <div class="row-control">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string
  desc?: string
  /** 控件占满整行（表单类输入用） */
  stacked?: boolean
}

defineProps<Props>()
</script>

<style scoped>
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.setting-row.is-stacked {
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

.row-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.row-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.row-desc {
  font-size: 0.8125rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.row-control {
  flex-shrink: 0;
}

.is-stacked .row-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* stacked 行内的按钮统一宽度并居中（flex column 默认 stretch 会占满整行） */
.is-stacked .row-control :deep(.btn) {
  width: 100%;
  max-width: 320px;
}

/* 行内控件统一外观（slot 内容继承） */
.row-control :deep(input),
.row-control :deep(select) {
  width: 100%;
  min-width: 220px;
  padding: 10px 14px;
  background: var(--surface-input);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.9375rem;
  font-family: inherit;
  transition: border-color var(--dur-fast) var(--ease-out);
}

.row-control :deep(input:hover),
.row-control :deep(select:hover) {
  border-color: var(--surface-glass-border-hover);
}

.row-control :deep(input:focus),
.row-control :deep(select:focus) {
  outline: none;
  border-color: var(--accent-primary);
}

.row-control :deep(input:focus-visible),
.row-control :deep(select:focus-visible) {
  outline: 2px solid var(--accent-primary);
  outline-offset: 1px;
}

.row-control :deep(input::placeholder) {
  color: var(--text-disabled);
}

.row-control :deep(input:disabled),
.row-control :deep(select:disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

.is-stacked .row-control :deep(input) {
  min-width: 0;
}

@media (max-width: 768px) {
  .setting-row:not(.is-stacked) {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .row-control :deep(input),
  .row-control :deep(select) {
    min-width: 0;
  }
}
</style>

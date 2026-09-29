<template>
  <Transition name="field-err">
    <p v-if="message" class="field-error" role="alert" aria-live="polite">
      <svg class="field-error__ico" viewBox="0 0 12 12" aria-hidden="true">
        <path
          d="M6 1.2 11 10.5H1L6 1.2Z"
          fill="none"
          stroke="currentColor"
          stroke-width="1.2"
          stroke-linejoin="round"
        />
        <path d="M6 4.6v2.6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
        <circle cx="6" cy="8.9" r="0.7" fill="currentColor" />
      </svg>
      <span class="field-error__text">{{ message }}</span>
    </p>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  /** 错误文案；为空/undefined 时不渲染、不占位 */
  message?: string
}

defineProps<Props>()
</script>

<style scoped>
.field-error {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--danger);
  text-align: left;
}

.field-error__ico {
  flex-shrink: 0;
  width: 12px;
  height: 12px;
  margin-top: 3px;
}

/* 滑入 + 淡入，随文案切换重播 */
.field-err-enter-active {
  transition:
    opacity var(--dur-fast) var(--ease-out),
    transform var(--dur-fast) var(--ease-out);
}

.field-err-leave-active {
  transition: opacity var(--dur-fast) var(--ease-out);
}

.field-err-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.field-err-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .field-err-enter-active,
  .field-err-leave-active {
    transition-duration: 0.01ms;
  }
}
</style>

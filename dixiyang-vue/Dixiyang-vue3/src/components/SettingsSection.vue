<template>
  <section class="settings-section">
    <header class="section-header">
      <h2 class="section-title">{{ title }}</h2>
      <p v-if="description" class="section-desc">{{ description }}</p>
    </header>
    <div class="section-body">
      <slot></slot>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title: string
  description?: string
}

defineProps<Props>()
</script>

<style scoped>
/* RAG 助手同款玻璃面板（glass-bg + blur20 + glass-border），叠深色衬底保证可读 */
.settings-section {
  padding: 24px;
  background: var(--surface-panel);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

.section-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: normal;
}

.section-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 6px 0 0;
}

.section-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>

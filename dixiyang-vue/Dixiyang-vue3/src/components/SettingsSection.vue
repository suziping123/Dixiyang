<template>
  <section class="settings-section">
    <div class="section-header">
      <h3 class="section-title">{{ title }}</h3>
      <p v-if="description" class="section-description">{{ description }}</p>
    </div>
    <div class="section-content">
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
.settings-section {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.settings-section:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-description {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>

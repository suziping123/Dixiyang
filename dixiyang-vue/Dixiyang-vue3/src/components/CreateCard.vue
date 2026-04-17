<template>
  <div class="novel-card-wrapper create-card-wrapper">
    <div class="glass-card create-card" @click="handleClick">
      <div class="card-create-content">
        <svg class="create-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        <span>构建新宇宙</span>
        <p class="create-hint">开启你的新故事</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  click: []
}>()

const handleClick = () => emit('click')
</script>

<style scoped>
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 0;
  height: 100%;
  aspect-ratio: 2 / 3;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transform-style: preserve-3d;
  cursor: pointer;
  perspective: 1200px;
  box-sizing: border-box;
}

.create-card {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-card:hover {
  border-color: var(--neon-blue);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.08);
}

.novel-card-wrapper {
  cursor: pointer;
  transition: all 0.4s ease;
}

.novel-card-wrapper:hover { transform: translateY(-8px); }

.card-create-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-secondary);
  text-align: center;
}

.create-icon {
  width: 60px;
  height: 60px;
  color: var(--neon-blue);
  opacity: 0.8;
}

.create-hint {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
}
</style>

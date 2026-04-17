<template>
  <div class="nav-wrapper" @mouseenter="isVisible = true" @mouseleave="isVisible = false">
    <div class="nav-trigger"></div>
    <nav class="floating-nav" :class="{ visible: isVisible }">
      <div
        v-for="(item, idx) in navItems"
        :key="idx"
        class="nav-item"
        :class="{ active: activeNav === idx }"
        @click="handleNavClick(idx)"
        :title="item.tooltip"
      >
        {{ item.iconClass }}
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

interface NavItem {
  iconClass: string
  tooltip: string
  path: string
}

const props = defineProps<{
  modelValue?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

const router = useRouter()
const route = useRoute()

const activeNav = ref(props.modelValue ?? 0)
const isVisible = ref(false)

const navItems = ref<NavItem[]>([
  { iconClass: '🏠', tooltip: '首页', path: '/home' },
  { iconClass: '🧭', tooltip: '发现', path: '/discover' },
  { iconClass: '💾', tooltip: '库', path: '/library' },
  { iconClass: '🤖', tooltip: 'RAG助手', path: '/rag-assistant' },
  { iconClass: '🔔', tooltip: '通知', path: '/notifications' },
  { iconClass: '⚙️', tooltip: '设置', path: '/settings' },
])

const pathToIndex = (path: string) => {
  const idx = navItems.value.findIndex(item => item.path === path)
  return idx >= 0 ? idx : 0
}

watch(() => route.path, (newPath) => {
  activeNav.value = pathToIndex(newPath)
  emit('update:modelValue', activeNav.value)
}, { immediate: true })

const handleNavClick = (idx: number) => {
  activeNav.value = idx
  emit('update:modelValue', idx)
  const item = navItems.value[idx]
  if (item) {
    router.push(item.path).catch(() => {
      console.log(`功能开发中...`)
    })
  }
}
</script>

<style scoped>
.nav-wrapper {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 100px;
  z-index: 100;
}

.nav-trigger {
  position: absolute;
  left: 0;
  top: 0;
  width: 30px;
  height: 100vh;
}

.floating-nav {
  position: absolute;
  left: -100px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 50px;
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  gap: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: left 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.floating-nav.visible {
  left: 20px;
}

.nav-item {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.5rem;
}

.nav-item:hover { color: var(--neon-cyan); transform: scale(1.1); }
.nav-item.active { background: rgba(59, 130, 246, 0.2); color: var(--neon-blue); box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.3), 0 0 20px rgba(59, 130, 246, 0.5); }
</style>

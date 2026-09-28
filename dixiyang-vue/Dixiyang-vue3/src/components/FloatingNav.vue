<template>
  <div class="nav-wrapper" @mouseenter="isVisible = true" @mouseleave="isVisible = false">
    <div class="nav-trigger"></div>
    <nav class="floating-nav" :class="{ visible: isVisible }" aria-label="全局导航">
      <button
        v-for="(item, idx) in navItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: activeNav === idx }"
        type="button"
        :title="item.label"
        :aria-label="item.label"
        :aria-current="activeNav === idx ? 'page' : undefined"
        @click="handleNavClick(idx)"
      >
        <component :is="item.icon" />
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChatDotRound, House, Setting } from '@element-plus/icons-vue'

interface NavItem {
  icon: typeof House
  label: string
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

const activeNav = ref(props.modelValue ?? -1)
const isVisible = ref(false)

// 只列真实存在的路由（/discover /library /notifications 无路由，已移除）
const navItems: NavItem[] = [
  { icon: House, label: '首页', path: '/home' },
  { icon: ChatDotRound, label: 'RAG 助手', path: '/rag-assistant' },
  { icon: Setting, label: '设置', path: '/settings' },
]

const pathToIndex = (path: string) => navItems.findIndex((item) => item.path === path)

watch(
  () => route.path,
  (newPath) => {
    const idx = pathToIndex(newPath)
    activeNav.value = idx
    emit('update:modelValue', idx)
  },
  { immediate: true },
)

const handleNavClick = (idx: number) => {
  activeNav.value = idx
  emit('update:modelValue', idx)
  const item = navItems[idx]
  if (item) {
    router.push(item.path)
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
  background: var(--surface-glass);
  backdrop-filter: blur(20px);
  border: 1px solid var(--surface-glass-border);
  border-radius: 24px;
  padding: 16px 10px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--shadow-card);
  transition: left var(--dur) var(--ease-out);
  transform: translateY(-50%);
}

.floating-nav.visible {
  left: 16px;
}

.nav-item {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  transition:
    background var(--dur-fast) var(--ease-out),
    color var(--dur-fast) var(--ease-out);
}

.nav-item svg {
  width: 20px;
  height: 20px;
}

.nav-item:hover {
  background: var(--accent-soft);
  color: var(--text-primary);
}

.nav-item:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: -2px;
}

.nav-item.active {
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
}

/* ============ 触屏设备：左下角常驻横条（hover 触发在触屏无效） ============ */
@media (hover: none), (pointer: coarse) {
  .nav-wrapper {
    width: auto;
    height: auto;
    top: auto;
    bottom: 14px;
    left: 14px;
  }

  .nav-trigger {
    display: none;
  }

  .floating-nav {
    position: fixed;
    left: 14px;
    top: auto;
    bottom: 14px;
    transform: none;
    flex-direction: row;
    padding: 8px 10px;
    gap: 8px;
    border-radius: 999px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
  }

  /* 不依赖 hover 的 visible 状态 */
  .floating-nav,
  .floating-nav.visible {
    left: 14px;
  }

  .nav-item {
    width: 38px;
    height: 38px;
  }

  .nav-item svg {
    width: 18px;
    height: 18px;
  }
}
</style>

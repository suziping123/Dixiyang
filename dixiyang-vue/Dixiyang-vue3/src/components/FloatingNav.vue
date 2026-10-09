<template>
  <div class="nav-wrapper" @mouseenter="handleEnter" @mouseleave="handleLeave">
    <div v-if="!isFab" class="nav-trigger"></div>

    <!-- FAB 模式：展开时的透明遮罩，点击任意处收起，避免误触页面 -->
    <div v-if="isFab && fabOpen" class="nav-backdrop" @click="fabOpen = false"></div>

    <!-- FAB 模式：常驻悬浮球（右侧垂直居中，向左展开横条，避免遮挡页面右下角元素） -->
    <button
      v-if="isFab"
      class="nav-fab"
      :class="{ open: fabOpen }"
      type="button"
      :aria-label="fabOpen ? '收起导航' : '展开导航'"
      :aria-expanded="fabOpen"
      @click="fabOpen = !fabOpen"
    >
      <!-- 双图标叠放：展开时 Menu 旋出、Close 旋入，替代生硬的整体切换 -->
      <span class="fab-ico" aria-hidden="true">
        <Menu class="ico-menu" />
        <Close class="ico-close" />
      </span>
    </button>

    <nav class="floating-nav" :class="{ visible: navVisible }" aria-label="全局导航">
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
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChatDotRound, House, Setting, Menu, Close, Collection } from '@element-plus/icons-vue'

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

// FAB（悬浮球）模式判定：触屏（hover:none / pointer:coarse）或窄视口（≤1024px，与 RAG 抽屉断点一致）
// 窄视口下桌面模式的 100px hover 热区会盖住页面左侧按钮，故同样改用悬浮球
const touchMedia = window.matchMedia('(hover: none), (pointer: coarse)')
const compactMedia = window.matchMedia('(max-width: 1024px)')
const isFab = ref(touchMedia.matches || compactMedia.matches)

const syncFabMode = () => {
  isFab.value = touchMedia.matches || compactMedia.matches
}

// Esc 收起展开的导航（FAB 模式）
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && fabOpen.value) fabOpen.value = false
}

onMounted(() => {
  touchMedia.addEventListener('change', syncFabMode)
  compactMedia.addEventListener('change', syncFabMode)
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  touchMedia.removeEventListener('change', syncFabMode)
  compactMedia.removeEventListener('change', syncFabMode)
  window.removeEventListener('keydown', onKeydown)
})

const activeNav = ref(props.modelValue ?? -1)
const isVisible = ref(false)
// FAB 模式：悬浮球展开状态
const fabOpen = ref(false)

// FAB 模式看 fabOpen，桌面 hover 看 isVisible
const navVisible = computed(() => (isFab.value ? fabOpen.value : isVisible.value))

const handleEnter = () => {
  if (!isFab.value) isVisible.value = true
}
const handleLeave = () => {
  if (!isFab.value) isVisible.value = false
}

// 只列真实存在的路由（/discover /library /notifications 无路由，已移除）
const navItems: NavItem[] = [
  { icon: House, label: '首页', path: '/home' },
  { icon: ChatDotRound, label: 'RAG 助手', path: '/rag-assistant' },
  { icon: Collection, label: '广场', path: '/ideas' },
  { icon: Setting, label: '设置', path: '/settings' },
]

const pathToIndex = (path: string) => navItems.findIndex((item) => item.path === path)

watch(
  () => route.path,
  (newPath) => {
    const idx = pathToIndex(newPath)
    activeNav.value = idx
    emit('update:modelValue', idx)
    // 路由切换（含浏览器返回）时收起菜单
    fabOpen.value = false
  },
  { immediate: true },
)

const handleNavClick = (idx: number) => {
  activeNav.value = idx
  emit('update:modelValue', idx)
  if (isFab.value) fabOpen.value = false
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

/* ============ FAB 模式：触屏 或 窄视口(≤1024px，避免 100px hover 热区挡按钮) ============ */
@media (hover: none), (pointer: coarse), (max-width: 1024px) {
  .nav-wrapper {
    /* 右侧中间锚点条：球由 flex 垂直居中（不占 transform，hover/active 的 scale 不会互相覆盖） */
    top: 0;
    bottom: 0;
    left: auto;
    right: 0;
    width: 74px; /* 14 边距 + 46 球 + 14 */
    height: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-end;
    padding-right: calc(14px + env(safe-area-inset-right, 0px));
    /* 关键：全高条不能拦截右侧页面内容的点击 */
    pointer-events: none;
    /* 抽屉(120)/抽屉遮罩(110) 之上：RAG 抽屉打开时球仍可导航 */
    z-index: 130;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  .nav-trigger {
    display: none;
  }

  /* 展开时的全屏透明遮罩：盖住页面（z-index 低于球和横条），点击收起 */
  .nav-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1;
    cursor: default;
    pointer-events: auto;
  }

  /* 常驻悬浮球：只占 46×46，不再整条遮挡；pointer-events 恢复可点 */
  .nav-fab {
    position: relative;
    pointer-events: auto;
    z-index: 2;
    width: 46px;
    height: 46px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border: 1px solid var(--surface-glass-border);
    background: var(--surface-glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    color: var(--text-secondary);
    cursor: pointer;
    touch-action: manipulation;
    /* 玻璃质感：分层阴影 + 顶部内高光 */
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 2px 6px rgba(0, 0, 0, 0.35),
      inset 0 1px 0 rgba(255, 255, 255, 0.16);
    transition:
      transform var(--dur-fast) var(--ease-out),
      color var(--dur-fast) var(--ease-out),
      background var(--dur-fast) var(--ease-out),
      border-color var(--dur-fast) var(--ease-out),
      box-shadow var(--dur-fast) var(--ease-out);
    /* 入场引导：呼吸光晕 2 次即停（prefers-reduced-motion 下关闭） */
    animation: fabHint 1.4s ease-out 2;
  }

  /* Menu/Close 双图标叠放交叉过渡 */
  .fab-ico {
    position: relative;
    width: 20px;
    height: 20px;
    display: flex;
  }

  .fab-ico svg {
    position: absolute;
    inset: 0;
    width: 20px;
    height: 20px;
    transition:
      opacity var(--dur-fast) var(--ease-out),
      transform var(--dur) var(--ease-out);
  }

  .ico-menu {
    opacity: 1;
    transform: rotate(0) scale(1);
  }

  .ico-close {
    opacity: 0;
    transform: rotate(-90deg) scale(0.5);
  }

  .nav-fab.open .ico-menu {
    opacity: 0;
    transform: rotate(90deg) scale(0.5);
  }

  .nav-fab.open .ico-close {
    opacity: 1;
    transform: rotate(0) scale(1);
  }

  /* 按压波纹：球内扩散淡出 */
  .nav-fab::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: var(--accent-soft-strong);
    transform: scale(0);
    opacity: 0;
    pointer-events: none;
  }

  .nav-fab:active::after {
    animation: fabRipple 0.4s var(--ease-out);
  }

  .nav-fab:active {
    transform: scale(0.92);
  }

  .nav-fab:focus-visible {
    outline: 2px solid var(--accent-primary);
    outline-offset: 3px;
  }

  .nav-fab.open {
    color: var(--accent-primary);
    background: var(--accent-soft-strong);
    border-color: var(--accent-primary);
    /* 展开态：强调色微光 */
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 0 16px var(--accent-soft-strong),
      inset 0 1px 0 rgba(255, 255, 255, 0.16);
  }

  /* 窄视口桌面（有指针）才有悬停反馈，触屏不受影响 */
  @media (hover: hover) and (pointer: fine) {
    .nav-fab:hover {
      transform: translateY(-1px) scale(1.05);
      color: var(--text-primary);
      border-color: var(--surface-glass-border-hover);
    }

    .nav-fab.open:hover {
      color: var(--accent-primary);
      border-color: var(--accent-primary);
    }
  }

  .floating-nav {
    position: fixed;
    /* 右侧中间：与球同一水平线（球中心在 50%），向左展开 */
    top: 50%;
    right: calc(68px + env(safe-area-inset-right, 0px));
    left: auto;
    /* 防左溢出：条目过多/超窄屏时最多占到左缘 */
    max-width: calc(100vw - 82px - env(safe-area-inset-right, 0px));
    z-index: 2;
    flex-direction: row;
    padding: 8px 10px;
    gap: 8px;
    border-radius: 999px;
    /* 与球同款质感：分层阴影 + 顶部内高光 */
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 2px 6px rgba(0, 0, 0, 0.35),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    /* 收起态：透明 + 向右（球方向）缩回；translateY(-50%) 负责垂直居中并入各状态 */
    opacity: 0;
    transform: translateY(-50%) translateX(8px) scale(0.92);
    pointer-events: none;
    transition:
      opacity var(--dur-fast) var(--ease-out),
      transform var(--dur-fast) var(--ease-out);
  }

  .floating-nav.visible {
    /* 覆盖桌面态 .floating-nav.visible{left:16px}（同特异性靠后置取胜），左移让开悬浮球 */
    right: calc(68px + env(safe-area-inset-right, 0px));
    opacity: 1;
    transform: translateY(-50%) translateX(0) scale(1);
    pointer-events: auto;
  }

  .nav-item {
    /* 44×44：满足 iOS 触控目标下限 */
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    transition:
      background var(--dur-fast) var(--ease-out),
      color var(--dur-fast) var(--ease-out),
      opacity var(--dur-fast) var(--ease-out),
      transform var(--dur) var(--ease-out);
    opacity: 0;
    /* 从球的方向（右）向左依次弹入 */
    transform: translateX(8px) scale(0.85);
  }

  /* 展开：条目依次弹入；收起由外层容器整体淡出（delay 归零不拖沓） */
  .floating-nav.visible .nav-item {
    opacity: 1;
    transform: none;
  }

  .floating-nav.visible .nav-item:nth-child(1) {
    transition-delay: 40ms;
  }

  .floating-nav.visible .nav-item:nth-child(2) {
    transition-delay: 80ms;
  }

  .floating-nav.visible .nav-item:nth-child(3) {
    transition-delay: 120ms;
  }

  .floating-nav.visible .nav-item:nth-child(4) {
    transition-delay: 160ms;
  }

  .nav-item svg {
    width: 20px;
    height: 20px;
  }
}

/* ============ FAB 动效关键帧 ============ */
@keyframes fabHint {
  0% {
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 0 0 0 var(--accent-primary);
  }

  70% {
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 0 0 12px transparent;
  }

  100% {
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 0 0 12px transparent;
  }
}

@keyframes fabRipple {
  from {
    transform: scale(0);
    opacity: 0.65;
  }

  to {
    transform: scale(2.4);
    opacity: 0;
  }
}

/* 无障碍：减弱动效偏好下关闭脉冲/波纹与过渡位移 */
@media (prefers-reduced-motion: reduce) {
  .nav-fab {
    animation: none;
  }

  .nav-fab::after {
    animation: none !important;
  }

  .floating-nav,
  .nav-item,
  .fab-ico svg {
    transition-duration: 0.01ms !important;
  }
}
</style>

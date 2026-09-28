<template>
  <div class="settings-container">
    <FloatingNav />

    <div class="settings-wrapper">
      <!-- 侧边栏分类 -->
      <aside class="settings-sidebar">
        <div class="sidebar-header">
          <h1 class="sidebar-title">
            <Setting class="title-icon" />
            设置
          </h1>
        </div>

        <nav class="settings-menu" aria-label="设置分类">
          <button
            v-for="category in categories"
            :key="category.id"
            class="menu-item"
            :class="{ active: activeCategory === category.id }"
            :aria-current="activeCategory === category.id ? 'page' : undefined"
            type="button"
            @click="switchCategory(category.id)"
          >
            <component :is="category.icon" class="menu-icon" />
            <span class="menu-label">{{ category.label }}</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <button class="back-btn" type="button" @click="goBack">
            <ArrowLeft /> 返回首页
          </button>
        </div>
      </aside>

      <!-- 分类内容 -->
      <main class="settings-content">
        <div class="section-wrapper" :key="activeCategory">
          <AccountSection v-if="activeCategory === 'account'" />
          <AppearanceSection v-else-if="activeCategory === 'appearance'" />
          <DataSection v-else-if="activeCategory === 'data'" />
          <AboutSection v-else />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, DataLine, InfoFilled, Picture, Setting, User } from '@element-plus/icons-vue'
import FloatingNav from '@/components/FloatingNav.vue'
import AccountSection from '@/components/settings/AccountSection.vue'
import AppearanceSection from '@/components/settings/AppearanceSection.vue'
import DataSection from '@/components/settings/DataSection.vue'
import AboutSection from '@/components/settings/AboutSection.vue'

const router = useRouter()

type CategoryId = 'account' | 'appearance' | 'data' | 'about'

const activeCategory = ref<CategoryId>('account')

const categories: { id: CategoryId; label: string; icon: typeof User }[] = [
  { id: 'account', label: '账户', icon: User },
  { id: 'appearance', label: '外观', icon: Picture },
  { id: 'data', label: '数据', icon: DataLine },
  { id: 'about', label: '关于', icon: InfoFilled },
]

/** 切换分类并滚回内容顶部（避免停在上一分类的滚动位置） */
const switchCategory = (id: CategoryId) => {
  activeCategory.value = id
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goBack = () => router.push('/home')
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  /* clip 不创建滚动容器，避免破坏侧边栏 sticky（hidden 会使 sticky 失效） */
  overflow-x: clip;
  position: relative;
  font-family: var(--font-family);
}

/* ============ 主容器 ============ */
.settings-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 100vh;
}

/* ============ 侧边栏 ============ */
.settings-sidebar {
  width: 260px;
  flex-shrink: 0;
  padding: 28px 18px;
  background: var(--surface-panel);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 24px;
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.375rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: normal;
  color: var(--text-primary);
}

.title-icon {
  width: 20px;
  height: 20px;
  color: var(--accent-primary);
}

.settings-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 11px 14px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  text-align: left;
  font-size: 0.9375rem;
  font-weight: 500;
  font-family: inherit;
  transition:
    background var(--dur-fast) var(--ease-out),
    color var(--dur-fast) var(--ease-out);
}

.menu-item:hover {
  background: var(--accent-soft);
  color: var(--text-primary);
}

.menu-item:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: -2px;
}

.menu-item.active {
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
}

.menu-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.menu-label {
  flex: 1;
}

.sidebar-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.sidebar-footer .back-btn {
  width: 100%;
  justify-content: center;
}

/* ============ 主内容区 ============ */
.settings-content {
  flex: 1;
  width: 100%;
  max-width: 1040px;
  margin: 0 auto;
  padding: 40px;
}

.section-wrapper {
  animation: settings-fade var(--dur) var(--ease-out);
}

@keyframes settings-fade {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ============ 响应式 ============ */
@media (max-width: 1024px) {
  .settings-wrapper {
    flex-direction: column;
  }

  /* 分类条吸顶，滚动内容时不消失 */
  .settings-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 10px 14px;
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-areas:
      "head foot"
      "menu menu";
    align-items: center;
    gap: 8px;
    overflow: visible;
  }

  .sidebar-header {
    grid-area: head;
    margin-bottom: 0;
  }

  .sidebar-title {
    font-size: 1.125rem;
    gap: 8px;
  }

  .settings-menu {
    grid-area: menu;
    /* 4 个分类等分，大小一致 */
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }

  .menu-item {
    flex-direction: column;
    gap: 3px;
    padding: 7px 4px;
    font-size: 0.75rem;
    justify-content: center;
    text-align: center;
  }

  .menu-icon {
    width: 16px;
    height: 16px;
  }

  .sidebar-footer {
    grid-area: foot;
    margin-top: 0;
    padding-top: 0;
    border-top: none;
  }

  .sidebar-footer .back-btn {
    width: auto;
    padding: 7px 12px;
    font-size: 0.8125rem;
  }

  .settings-content {
    padding: 24px 18px;
  }
}

@media (max-width: 768px) {
  .settings-content {
    padding: 18px 14px;
  }
}
</style>

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
            @click="activeCategory = category.id"
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

const goBack = () => router.push('/home')
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  overflow: hidden;
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
  padding: 28px 18px;
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border-right: 1px solid var(--border-color);
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
  padding: 40px;
  max-width: 860px;
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

  .settings-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    position: static;
    padding: 16px;
    gap: 14px;
  }

  .sidebar-header {
    margin-bottom: 0;
  }

  .settings-menu {
    flex-direction: row;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .menu-item {
    flex-shrink: 0;
    padding: 9px 14px;
  }

  .sidebar-footer {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
  }

  .sidebar-footer .back-btn {
    width: auto;
  }

  .settings-content {
    padding: 28px 20px;
  }
}

@media (max-width: 768px) {
  .settings-content {
    padding: 20px 16px;
  }

  .menu-item {
    font-size: 0.875rem;
    padding: 8px 12px;
  }
}
</style>

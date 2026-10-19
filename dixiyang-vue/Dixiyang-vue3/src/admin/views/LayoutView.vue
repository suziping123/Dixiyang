<template>
  <div class="console-shell">
    <aside class="console-sidebar">
      <div class="sb-brand">
        <img class="sb-logo" :src="logo" alt="DIXIYANG">
        <div class="sb-name">
          <strong>DIXIYANG</strong>
          <em>管理控制台</em>
        </div>
      </div>

      <nav class="sb-menu" aria-label="控制台导航">
        <button
          v-for="p in pages"
          :key="p.name"
          class="sb-item"
          type="button"
          :class="{ active: activeName === p.name }"
          @click="openPage(p)"
        >
          <el-icon><component :is="p.icon" /></el-icon>
          <span>{{ p.title }}</span>
        </button>
      </nav>

      <div class="sb-foot">
        <div class="sb-who">
          <span class="sb-user" :title="nickname">{{ nickname }}</span>
          <span class="sb-role">管理员</span>
        </div>
        <a class="sb-link" href="./index.html">← 返回用户端</a>
        <button class="sb-logout" type="button" @click="onLogout">退出登录</button>
      </div>
    </aside>

    <div class="console-main">
      <!-- 多页签条：浏览器式（点菜单开签 / 仪表盘固定首签 / 关签跳邻签），会话内保持 -->
      <div class="tabbar" role="tablist" aria-label="已打开的页面">
        <div
          v-for="t in tabs"
          :key="t.name"
          class="tab"
          role="tab"
          :aria-selected="t.name === activeName"
          tabindex="0"
          @click="activate(t)"
          @keydown.enter="activate(t)"
        >
          <el-icon class="tab-ico"><component :is="iconOf(t.name)" /></el-icon>
          <span class="tab-label">{{ titleOf(t.name) }}</span>
          <button
            v-if="t.name !== FIXED_TAB"
            class="tab-close"
            type="button"
            :aria-label="`关闭 ${titleOf(t.name)}`"
            @click.stop="close(t)"
          >
            ×
          </button>
        </div>
      </div>

      <main class="content">
        <RouterView v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <keep-alive :include="keepNames">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </RouterView>
      </main>
    </div>

    <!-- 窄屏 / 触屏：导航交给复用的 FloatingNav（注册项 = 控制台页面表；桌面宽屏由侧栏承担） -->
    <FloatingNav v-if="showFabNav" :items="ADMIN_NAV_ITEMS" nav-label="控制台导航" @select="onNavSelect" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import logo from '@/assets/logoByGpt.png'
import FloatingNav from '@/components/FloatingNav.vue'
import type { FloatingNavItem } from '@/components/FloatingNav.types'
import { ADMIN_NAV_ITEMS, CONSOLE_PAGES, FIXED_TAB, pageByName } from '../menu'
import type { ConsolePage } from '../menu'
import { useAdminTabs } from '../composables/useAdminTabs'
import type { AdminTab } from '../composables/useAdminTabs'
import { clearAdminSession } from '../utils/session'

const route = useRoute()
const router = useRouter()
const { tabs, activeName, syncRoute, closeTab, keepNames } = useAdminTabs()

const pages = CONSOLE_PAGES
const nickname = computed(
  () => localStorage.getItem('admin_nickname') || localStorage.getItem('admin_username') || '管理员',
)

// 路由 → 页签同步（含刷新 / 直达 URL；关签后的导航也走这里回正激活态）
watch(
  () => route.name,
  (name) => syncRoute(name),
  { immediate: true },
)

const openPage = (p: ConsolePage) => router.push(p.path)
const activate = (t: AdminTab) => router.push(t.path)

const close = (t: AdminTab) => {
  const next = closeTab(t.name) // 关当前签时返回相邻签；缓存随之丢弃（keepNames 变更）
  if (next) router.push(next.path)
}

const iconOf = (name: string) => pageByName(name)?.icon
const titleOf = (name: string) => pageByName(name)?.title ?? name

const onLogout = () => {
  clearAdminSession()
  router.replace('/login')
}

// ---------- 窄屏 / 触屏：复用 FloatingNav（FAB 悬浮球），注册控制台页面 ----------
// 挂载判定与组件内 FAB 模式一致（触屏 或 ≤1024px）；桌面宽屏不挂载（侧栏即导航，避免第二套左缘热区）
const fabMedia = window.matchMedia('(hover: none), (pointer: coarse), (max-width: 1024px)')
const showFabNav = ref(fabMedia.matches)
const syncFabNav = () => {
  showFabNav.value = fabMedia.matches
}

onMounted(() => fabMedia.addEventListener('change', syncFabNav))
onBeforeUnmount(() => fabMedia.removeEventListener('change', syncFabNav))

const onNavSelect = (item: FloatingNavItem) => {
  // 「退出登录」条目没有 path/href，由这里接管（其余条目组件内部已完成跳转）
  if (item.key === 'logout') onLogout()
}
</script>

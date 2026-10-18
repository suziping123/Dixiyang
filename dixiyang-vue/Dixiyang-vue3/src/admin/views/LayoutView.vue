<template>
  <div class="console-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">D</span>
        <div class="brand-text">
          <strong>DIXIYANG</strong>
          <em>管理控制台</em>
        </div>
      </div>

      <nav class="menu" aria-label="控制台导航">
        <button
          class="menu-item"
          type="button"
          :class="{ active: route.name === 'admin-dashboard' }"
          @click="go('/')"
        >
          仪表盘
        </button>
        <button
          class="menu-item"
          type="button"
          :class="{ active: route.name === 'admin-users' }"
          @click="go('/users')"
        >
          用户管理
        </button>
      </nav>

      <div class="sidebar-foot">
        <div class="who">
          <span class="who-name">{{ nickname }}</span>
          <span class="who-role">管理员</span>
        </div>
        <a class="foot-link" href="./index.html">← 返回用户端</a>
        <button class="logout" type="button" @click="onLogout">退出登录</button>
      </div>
    </aside>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { clearAdminSession } from '../utils/session'

const route = useRoute()
const router = useRouter()

const nickname = computed(
  () => localStorage.getItem('admin_nickname') || localStorage.getItem('admin_username') || '管理员',
)

const go = (path: string) => router.push(path)

const onLogout = () => {
  clearAdminSession()
  router.replace('/login')
}
</script>

<style scoped>
.console-shell {
  display: flex;
  min-height: 100vh;
}

/* 左侧栏 */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 216px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 20px 14px 16px;
  background: var(--c-panel);
  border-right: 1px solid var(--c-border);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 8px 18px;
  border-bottom: 1px solid var(--c-border);
  margin-bottom: 14px;
}
.brand-mark {
  display: inline-flex;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-weight: 800;
  font-size: 19px;
  color: #0d0d0f;
  background: linear-gradient(135deg, var(--c-cyan), var(--c-accent));
  flex-shrink: 0;
}
.brand-text { display: flex; flex-direction: column; line-height: 1.25; }
.brand-text strong { font-size: 14px; letter-spacing: 1.5px; }
.brand-text em { font-style: normal; font-size: 12px; color: var(--c-text-3); }

.menu { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.menu-item {
  appearance: none;
  border: 1px solid transparent;
  background: transparent;
  color: var(--c-text-2);
  font-size: 14px;
  text-align: left;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 160ms ease, color 160ms ease;
}
.menu-item:hover { background: rgba(255, 255, 255, 0.05); color: var(--c-text); }
.menu-item.active {
  background: rgba(75, 139, 245, 0.14);
  border-color: rgba(75, 139, 245, 0.35);
  color: #cfe0ff;
}

.sidebar-foot { display: flex; flex-direction: column; gap: 10px; padding: 0 8px; }
.who { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.who-name { color: var(--c-text); font-weight: 600; max-width: 108px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.who-role {
  font-size: 11px;
  color: var(--c-warn);
  border: 1px solid rgba(230, 162, 60, 0.45);
  background: rgba(230, 162, 60, 0.14);
  padding: 1px 7px;
  border-radius: 999px;
}
.foot-link { font-size: 13px; color: var(--c-text-3); text-decoration: none; }
.foot-link:hover { color: var(--c-cyan); }
.logout {
  appearance: none;
  border: 1px solid rgba(239, 68, 68, 0.45);
  background: rgba(239, 68, 68, 0.12);
  color: #ff9d9d;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 160ms ease;
}
.logout:hover { background: rgba(239, 68, 68, 0.22); }

/* 内容区 */
.content {
  flex: 1;
  min-width: 0;
  padding: 28px 32px 60px;
}
/* 视图根元素（子组件根会带上父作用域属性，无需 :deep） */
.content > * { max-width: 1140px; margin: 0 auto; }

/* 移动端：侧栏变顶栏 */
@media (max-width: 768px) {
  .console-shell { flex-direction: column; }
  .sidebar {
    position: static;
    height: auto;
    width: 100%;
    flex-direction: row;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-right: none;
    border-bottom: 1px solid var(--c-border);
  }
  .brand { padding: 0 10px 0 0; border-bottom: none; margin-bottom: 0; border-right: 1px solid var(--c-border); }
  .brand-text { display: none; }
  .menu { flex-direction: row; flex: 1; gap: 8px; }
  .menu-item { padding: 8px 12px; }
  .sidebar-foot { flex-direction: row; align-items: center; gap: 12px; padding: 0; }
  .who { display: none; }
  .content { padding: 18px 16px 48px; }
}
</style>

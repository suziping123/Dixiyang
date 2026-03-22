<template>
  <div class="novel-editor-container">
    <div class="bg-gradient-animation"></div>
    
    <nav class="floating-nav">
      <div
        v-for="(item, idx) in navItems"
        :key="idx"
        class="nav-item"
        :class="{ active: activeNav === 2 }"
        @click="handleNavClick(idx)"
        :title="item.tooltip"
      >
        {{ item.iconClass }}
      </div>
    </nav>
    
    <main class="main-stage">
      <header class="stage-header">
        <div class="header-top">
          <div class="logo-wrapper">
            <h1 class="logo-text">DIXIYANG <span class="engine-span">ENGINE</span></h1>
            <div class="glow-line"></div>
          </div>
        </div>
        <p class="subtitle">小说编辑器 - 正在编辑：<span class="user-name">{{ novelTitle || '未知小说' }}</span></p>
      </header>
      
      <div class="editor-section">
        <div class="editor-content">
          <h2 class="section-title">✧ 小说编辑</h2>
          <div class="editor-placeholder">
            <svg viewBox="0 0 24 24" class="editor-icon"><path fill="currentColor" d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>
            <h3>小说编辑器功能开发中</h3>
            <p>该功能正在积极开发中，敬请期待...</p>
            <button class="back-btn" @click="goBack">返回首页</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/UserStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeNav = ref(2)
const novelTitle = ref('')

const navItems = ref([
  { iconClass: '🏠', tooltip: '首页' },
  { iconClass: '🧭', tooltip: '发现' },
  { iconClass: '💾', tooltip: '库' },
  { iconClass: '🔔', tooltip: '通知' },
  { iconClass: '⚙️', tooltip: '设置' },
])

const handleNavClick = (idx: number) => {
  activeNav.value = idx
  const routes = ['/home', '/discover', '/library', '/notifications', '/settings']
  const routePath = routes[idx]
  if (routePath && routePath !== '/home') {
    router.push(routePath).catch(() => console.log(`功能开发中...`))
  }
}

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  const novelId = route.params.id
  console.log('编辑小说ID:', novelId)
  // 这里可以根据novelId获取小说详情
  novelTitle.value = `小说 ${novelId}`
})
</script>

<style scoped>
.novel-editor-container {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* 导航栏样式 */
.floating-nav {
  position: fixed;
  left: 30px;
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
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
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

/* 主舞台 */
.main-stage {
  position: relative;
  z-index: 1;
  padding: 80px 120px;
  margin-left: 100px;
}

.stage-header {
  margin-bottom: 60px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.logo-wrapper {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.logo-text {
  font-size: 3.5rem;
  font-weight: 900;
  letter-spacing: -2px;
  margin: 0;
  background: linear-gradient(135deg, var(--text-primary) 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.engine-span {
  background: linear-gradient(135deg, var(--neon-purple) 0%, var(--neon-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
}

.glow-line {
  position: absolute;
  bottom: -10px;
  left: 0;
  height: 3px;
  width: 150px;
  background: linear-gradient(to right, var(--neon-blue), var(--neon-purple), transparent);
  filter: blur(2px);
}

.subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin: 20px 0 0 0;
}

.subtitle .highlight, .user-name {
  color: var(--neon-cyan);
  font-weight: 600;
  text-shadow: 0 0 10px rgba(6, 182, 212, 0.4);
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 50px 0 30px 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* 编辑器区域 */
.editor-section {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 40px;
  min-height: 600px;
}

.editor-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  padding: 60px 20px;
}

.editor-icon {
  width: 80px;
  height: 80px;
  color: var(--neon-cyan);
  opacity: 0.6;
  margin-bottom: 20px;
}

.editor-placeholder h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.editor-placeholder p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0 0 30px 0;
  max-width: 400px;
}

.back-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(168, 85, 247, 0.1));
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: var(--text-primary);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
}

.back-btn:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(168, 85, 247, 0.3));
  border-color: var(--glass-border-hover);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

/* 背景动画 */
.bg-gradient-animation {
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.12) 0%, transparent 50%),
  radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
  radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
  radial-gradient(circle at center, #1e1b4b 0%, #0a0a0c 70%);
  z-index: 0;
  animation: rotate 30s linear infinite;
  opacity: var(--bg-intensity, 1);
  transition: opacity 0.3s ease;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 1400px) {
  .main-stage {
    padding: 60px 80px;
    margin-left: 80px;
  }
}

@media (max-width: 1024px) {
  .main-stage {
    padding: 60px 60px;
    margin-left: 60px;
  }
  .logo-text { font-size: 2.5rem; }
}

@media (max-width: 768px) {
  .floating-nav {
    left: 10px;
    width: 60px;
    padding: 15px 5px;
    gap: 15px;
  }
  .nav-item {
    width: 40px;
    height: 40px;
  }
  .main-stage {
    padding: 40px 30px;
    margin-left: 80px;
  }
  .logo-text { font-size: 2rem; }
  .editor-section {
    padding: 20px;
  }
}
</style>
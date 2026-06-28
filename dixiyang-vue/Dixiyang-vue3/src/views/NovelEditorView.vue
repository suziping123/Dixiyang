<template>
  <div class="novel-editor-container">
    <div class="bg-gradient-animation"></div>

    <FloatingNav />

    <main class="main-stage">
      <NovelPageHeader page-title="小说编辑器" />

      <div class="editor-section">
        <div class="editor-content">
          <h2 class="section-title">✧ 小说编辑</h2>
          <div class="editor-placeholder">
            <svg viewBox="0 0 24 24" class="editor-icon"><path fill="currentColor" d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>
            <h3>小说编辑器功能开发中</h3>
            <p>该功能正在积极开发中，敬请期待...</p>
            <button class="back-btn" @click="goBack">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
              返回首页
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import FloatingNav from '@/components/FloatingNav.vue'
import NovelPageHeader from '@/components/NovelPageHeader.vue'
import { useNovelStore } from '@/stores/novelStore'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  const novelId = route.params.id
  novelStore.loadNovel(novelId as string)
})
</script>

<style scoped>
.novel-editor-container {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* 主舞台 */
.main-stage {
  position: relative;
  z-index: 1;
  padding: 80px 120px;
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

/* 响应式 */
@media (max-width: 1400px) {
  .main-stage {
    padding: 60px 80px;
  }
}

@media (max-width: 1024px) {
  .main-stage {
    padding: 60px 60px;
  }
  .logo-text { font-size: 2.5rem; }
}

@media (max-width: 768px) {
  .main-stage {
    padding: 40px 30px;
  }
  .logo-text { font-size: 2rem; }
  .editor-section {
    padding: 20px;
  }
}
</style>

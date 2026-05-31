<template>
  <div class="background-control" :class="[`mode-${mode}`]">
    <!-- 紧凑模式 -->
    <div v-if="mode === 'compact'" class="compact-mode">
      <button
        v-for="theme in THEMES"
        :key="theme.id"
        class="theme-btn"
        :class="{ active: bgConfig.themeId.value === theme.id }"
        :title="theme.label"
        @click="bgConfig.setTheme(theme.id)"
      >
        {{ theme.icon }}
      </button>
    </div>

    <!-- 完整模式 -->
    <div v-else class="full-mode">
      <!-- 主题选择 -->
      <div class="settings-section">
        <h3 class="section-title">全局主题</h3>
        <p class="section-desc">主题影响所有页面的配色和风格</p>
        <div class="theme-grid">
          <button
            v-for="theme in THEMES"
            :key="theme.id"
            class="theme-card"
            :class="{ active: bgConfig.themeId.value === theme.id }"
            @click="bgConfig.setTheme(theme.id)"
          >
            <span class="theme-icon">{{ theme.icon }}</span>
            <div class="theme-info">
              <span class="theme-name">{{ theme.label }}</span>
              <span class="theme-desc">{{ theme.description }}</span>
            </div>
          </button>
        </div>
      </div>

      <!-- 背景图选择（仅在暗色主题下显示，亮色主题下背景图不明显） -->
      <div v-if="bgConfig.themeId.value !== 'minimal-light'" class="settings-section">
        <h3 class="section-title">背景图</h3>
        <p class="section-desc">叠加在背景之上的预设图片（QQ 聊天背景风格）</p>
        <div class="bg-image-grid">
          <button
            v-for="img in bgImageList"
            :key="img.id"
            class="bg-image-card"
            :class="{ active: bgConfig.bgImageId.value === img.id }"
            @click="selectBgImage(img.id)"
          >
            <img v-if="loadedImages[img.id]" :src="loadedImages[img.id]" :alt="img.label" class="bg-image-thumb" />
            <div v-else class="bg-image-placeholder">加载中...</div>
            <span class="bg-image-label">{{ img.label }}</span>
          </button>
          <button
            class="bg-image-card no-bg"
            :class="{ active: !bgConfig.bgImageId.value }"
            @click="bgConfig.setBgImage(undefined)"
          >
            <span class="bg-image-empty">✕</span>
            <span class="bg-image-label">无背景图</span>
          </button>
        </div>
      </div>

      <!-- 恢复默认 -->
      <div class="settings-section">
        <button class="btn-reset" @click="handleReset">恢复默认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBackgroundConfig, THEMES, BG_IMAGES } from '@/composables/useBackgroundConfig'

interface Props { mode?: 'compact' | 'full' }
withDefaults(defineProps<Props>(), { mode: 'compact' })

const bgConfig = useBackgroundConfig()

const bgImageList = BG_IMAGES
const loadedImages = ref<Record<string, string>>({})

/** 预加载所有背景图缩略图 */
onMounted(async () => {
  for (const img of BG_IMAGES) {
    try {
      const url = await img.importFn()
      loadedImages.value[img.id] = url
    } catch {
      // 静默跳过
    }
  }
})

const selectBgImage = (id: string) => {
  bgConfig.setBgImage(bgConfig.bgImageId.value === id ? undefined : id)
}

const handleReset = () => {
  if (confirm('确定要恢复默认设置吗？')) {
    bgConfig.resetToDefault()
    bgConfig.applyTheme()
  }
}
</script>

<style scoped>
.background-control { display: flex; align-items: center; gap: 16px; }
.mode-compact { flex-wrap: wrap; gap: 8px; }

.theme-btn {
  width: 36px; height: 36px; border: 1px solid var(--glass-border);
  border-radius: 8px; background: var(--glass-bg); color: var(--text-secondary);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 1rem; transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.theme-btn:hover { background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.5); }
.theme-btn.active { background: rgba(59,130,246,0.25); border-color: var(--neon-primary); color: var(--neon-primary); box-shadow: 0 0 10px rgba(59,130,246,0.3); }

/* 完整模式 */
.full-mode { padding: 20px; background: var(--glass-bg); border-radius: 16px; border: 1px solid var(--glass-border); width: 100%; }
.settings-section { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
.settings-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0 0 4px 0; color: var(--neon-cyan); text-transform: uppercase; letter-spacing: 1px; }
.section-desc { font-size: 0.85rem; color: var(--text-muted); margin: 0 0 14px 0; }

/* 主题卡片 */
.theme-grid { display: flex; flex-direction: column; gap: 10px; }
.theme-card {
  display: flex; align-items: center; gap: 14px; padding: 16px;
  border: 2px solid var(--glass-border); border-radius: 14px;
  background: var(--input-bg); cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.theme-card:hover { border-color: var(--glass-border-hover); background: rgba(59,130,246,0.06); }
.theme-card.active { border-color: var(--neon-primary); background: rgba(59,130,246,0.10); box-shadow: 0 0 16px rgba(59,130,246,0.15); }
.theme-icon { font-size: 2rem; line-height: 1; }
.theme-info { display: flex; flex-direction: column; gap: 2px; }
.theme-name { font-weight: 600; font-size: 1rem; color: var(--text-primary); }
.theme-desc { font-size: 0.85rem; color: var(--text-muted); }

/* 背景图 */
.bg-image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.bg-image-card {
  position: relative; border: 2px solid var(--glass-border); border-radius: 12px;
  overflow: hidden; cursor: pointer; aspect-ratio: 16/10;
  transition: all 0.3s; background: var(--input-bg);
}
.bg-image-card:hover { border-color: var(--neon-primary); }
.bg-image-card.active { border-color: var(--neon-primary); box-shadow: 0 0 12px rgba(59,130,246,0.35); }
.bg-image-thumb { width: 100%; height: 100%; object-fit: cover; }
.bg-image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--text-muted); }
.bg-image-label { position: absolute; bottom: 0; left: 0; right: 0; padding: 3px 6px; background: rgba(0,0,0,0.55); color: white; font-size: 0.7rem; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bg-image-card.no-bg { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.bg-image-empty { font-size: 1.6rem; color: var(--text-muted); }

/* 按钮 */
.btn-reset { width: 100%; padding: 12px; border: 1px solid var(--glass-border); border-radius: 10px; background: var(--input-bg); color: var(--text-secondary); cursor: pointer; font-weight: 600; transition: all 0.3s; }
.btn-reset:hover { background: rgba(168,85,247,0.12); border-color: rgba(168,85,247,0.4); color: var(--neon-purple); }

@media (max-width: 768px) {
  .full-mode { padding: 16px; }
  .theme-card { padding: 14px; }
  .bg-image-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>

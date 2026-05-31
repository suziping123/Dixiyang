<template>
  <div class="background-control" :class="[`mode-${mode}`]">
    <div v-if="mode === 'full'" class="full-mode">
      <div class="settings-section">
        <h3 class="section-title">主题</h3>
        <p class="section-desc">当前：暗色玻璃 · 浅色文字</p>
      </div>

      <div v-if="bgList.length" class="settings-section">
        <h3 class="section-title">背景图</h3>
        <p class="section-desc">独立于主题，可单独选择</p>
        <div class="bg-image-grid">
          <button v-for="img in bgList" :key="img.id" class="bg-image-card"
            :class="{ active: cfg.bgImageId.value === img.id }"
            @click="cfg.setBgImage(cfg.bgImageId.value === img.id ? undefined : img.id)">
            <img v-if="loaded[img.id]" :src="loaded[img.id]" :alt="img.label" class="bg-image-thumb" />
            <div v-else class="bg-image-placeholder">加载中</div>
            <span class="bg-image-label">{{ img.label }}</span>
          </button>
          <button class="bg-image-card no-bg" :class="{ active: !cfg.bgImageId.value }"
            @click="cfg.setBgImage(undefined)">
            <span class="bg-image-empty">✕</span>
            <span class="bg-image-label">无</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBackgroundConfig, BG_IMAGES } from '@/composables/useBackgroundConfig'

interface Props { mode?: 'compact' | 'full' }
withDefaults(defineProps<Props>(), { mode: 'compact' })

const cfg = useBackgroundConfig()
const bgList = BG_IMAGES
const loaded = ref<Record<string, string>>({})

onMounted(async () => {
  for (const img of BG_IMAGES) {
    try { loaded.value[img.id] = await img.importFn() } catch { /* */ }
  }
})
</script>

<style scoped>
.background-control { display: flex; align-items: center; gap: 16px; }
.full-mode { padding: 20px; background: var(--surface-glass); border-radius: 16px; border: 1px solid var(--surface-glass-border); width: 100%; }
.settings-section { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
.settings-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0 0 4px; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 1px; }
.section-desc { font-size: 0.85rem; color: var(--text-muted); margin: 0 0 14px; }

.bg-image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.bg-image-card { position: relative; border: 2px solid var(--surface-glass-border); border-radius: 12px; overflow: hidden; cursor: pointer; aspect-ratio: 16/10; transition: all 0.3s; background: var(--surface-input); }
.bg-image-card:hover { border-color: var(--accent-primary); }
.bg-image-card.active { border-color: var(--accent-primary); box-shadow: 0 0 12px rgba(59,130,246,0.35); }
.bg-image-thumb { width: 100%; height: 100%; object-fit: cover; }
.bg-image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--text-muted); }
.bg-image-label { position: absolute; bottom: 0; left: 0; right: 0; padding: 3px 6px; background: rgba(0,0,0,0.55); color: white; font-size: 0.7rem; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bg-image-card.no-bg { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.bg-image-empty { font-size: 1.6rem; color: var(--text-muted); }

@media (max-width: 768px) { .full-mode { padding: 16px; } .bg-image-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

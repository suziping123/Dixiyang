<template>
  <div class="background-control" :class="[`mode-${mode}`]">
    <div v-if="mode === 'compact'" class="compact-mode">
      <button v-for="t in THEMES" :key="t.id" class="theme-btn"
        :class="{ active: cfg.themeId.value === t.id }"
        :title="t.label" @click="cfg.setTheme(t.id)">{{ t.icon }}</button>
    </div>

    <div v-else class="full-mode">
      <div class="settings-section">
        <h3 class="section-title">主题</h3>
        <p class="section-desc">切换后全局生效</p>
        <div class="theme-grid">
          <button v-for="t in THEMES" :key="t.id" class="theme-card"
            :class="{ active: cfg.themeId.value === t.id }"
            @click="cfg.setTheme(t.id)">
            <span class="theme-icon">{{ t.icon }}</span>
            <div class="theme-info">
              <span class="theme-name">{{ t.label }}</span>
              <span class="theme-desc">{{ t.description }}</span>
            </div>
          </button>
        </div>
      </div>

      <div v-if="bgList.length" class="settings-section">
        <h3 class="section-title">背景图</h3>
        <p class="section-desc">独立于主题，可搭配任意主题</p>
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
import { useBackgroundConfig, THEMES, BG_IMAGES } from '@/composables/useBackgroundConfig'

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
.mode-compact { flex-wrap: wrap; gap: 8px; }
.theme-btn {
  width: 36px; height: 36px; border: 1px solid var(--surface-glass-border);
  border-radius: 8px; background: var(--surface-glass); color: var(--text-secondary);
  cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1rem; transition: all 0.3s;
}
.theme-btn:hover { background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.5); }
.theme-btn.active { background: rgba(59,130,246,0.25); border-color: var(--accent-primary); color: var(--accent-primary); }

.full-mode { padding: 20px; background: var(--surface-glass); border-radius: 16px; border: 1px solid var(--surface-glass-border); width: 100%; }
.settings-section { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
.settings-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0 0 4px; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 1px; }
.section-desc { font-size: 0.85rem; color: var(--text-muted); margin: 0 0 14px; }

.theme-grid { display: flex; flex-direction: column; gap: 10px; }
.theme-card { display: flex; align-items: center; gap: 14px; padding: 16px; border: 2px solid var(--surface-glass-border); border-radius: 14px; background: var(--surface-input); cursor: pointer; transition: all 0.3s; }
.theme-card:hover { border-color: var(--surface-glass-border-hover); background: rgba(59,130,246,0.06); }
.theme-card.active { border-color: var(--accent-primary); background: rgba(59,130,246,0.10); }
.theme-icon { font-size: 2rem; line-height: 1; }
.theme-info { display: flex; flex-direction: column; gap: 2px; }
.theme-name { font-weight: 600; font-size: 1rem; color: var(--text-primary); }
.theme-desc { font-size: 0.85rem; color: var(--text-muted); }

.bg-image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.bg-image-card { position: relative; border: 2px solid var(--surface-glass-border); border-radius: 12px; overflow: hidden; cursor: pointer; aspect-ratio: 16/10; transition: all 0.3s; background: var(--surface-input); }
.bg-image-card:hover { border-color: var(--accent-primary); }
.bg-image-card.active { border-color: var(--accent-primary); box-shadow: 0 0 12px rgba(59,130,246,0.35); }
.bg-image-thumb { width: 100%; height: 100%; object-fit: cover; }
.bg-image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--text-muted); }
.bg-image-label { position: absolute; bottom: 0; left: 0; right: 0; padding: 3px 6px; background: rgba(0,0,0,0.55); color: white; font-size: 0.7rem; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bg-image-card.no-bg { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.bg-image-empty { font-size: 1.6rem; color: var(--text-muted); }

@media (max-width: 768px) { .full-mode { padding: 16px; } .theme-card { padding: 14px; } .bg-image-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

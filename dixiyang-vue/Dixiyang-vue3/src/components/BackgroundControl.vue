<template>
  <div class="background-control" :class="[`mode-${mode}`]">
    <div v-if="mode === 'full'" class="full-mode">
      <div class="settings-section">
        <h3 class="section-title">主题</h3>
        <p class="section-desc">当前：暗色玻璃 · 浅色文字</p>
      </div>

      <div class="settings-section">
        <h3 class="section-title">背景图</h3>
        <p class="section-desc">独立于主题，可单独选择</p>
        <div class="bg-image-grid">
          <button v-for="img in bgList" :key="img.id" class="bg-image-card"
            :class="{ active: cfg.bgImageId.value === img.id }"
            @click="cfg.setBgImage(cfg.bgImageId.value === img.id ? undefined : img.id)">
            <img v-if="loaded[img.id]" :src="loaded[img.id]" :alt="img.label" class="bg-image-thumb" />
            <div v-else class="bg-image-placeholder">加载中</div>
            <span class="bg-image-label">{{ img.label }}</span>
            <button v-if="img.isCustom" class="bg-delete-btn" @click.stop="handleDeleteCustom(img.id)" title="删除">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
          </button>
          <button class="bg-image-card no-bg" :class="{ active: !cfg.bgImageId.value }"
            @click="cfg.setBgImage(undefined)">
            <span class="bg-image-empty">✕</span>
            <span class="bg-image-label">无</span>
          </button>
          <button class="bg-image-card upload-card" @click="triggerBgUpload">
            <input ref="bgFileInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none"
                   @change="onBgFileUpload" />
            <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor" class="upload-icon">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            <span class="bg-image-label">上传背景</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBackgroundConfig, BG_IMAGES, getCustomBgImages, addCustomBg, removeCustomBg } from '@/composables/useBackgroundConfig'
import { uploadBgImage, deleteBgImage } from '@/api/novelApi'
import { useUserStore } from '@/stores/UserStore'
import { confirmDelete } from '@/utils/confirm'
import { ElMessage } from 'element-plus'

interface Props { mode?: 'compact' | 'full' }
withDefaults(defineProps<Props>(), { mode: 'compact' })

const cfg = useBackgroundConfig()
const userStore = useUserStore()
const bgList = ref([...BG_IMAGES, ...getCustomBgImages()])
const loaded = ref<Record<string, string>>({})
const bgFileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const refreshBgList = () => {
  bgList.value = [...BG_IMAGES, ...getCustomBgImages()]
}

onMounted(async () => {
  for (const img of bgList.value) {
    try { loaded.value[img.id] = await img.importFn() } catch { /* */ }
  }
})

const triggerBgUpload = () => bgFileInput.value?.click()

const onBgFileUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (isUploading.value) return
  isUploading.value = true

  try {
    const res = await uploadBgImage(file)
    const url = (res as any).data
    const id = addCustomBg(url, file.name.replace(/\.[^.]+$/, ''))
    loaded.value[id] = url
    refreshBgList()
    ElMessage.success('背景上传成功')
  } catch (err) {
    console.error('背景上传失败:', err)
    ElMessage.error('背景上传失败，请重试')
  } finally {
    isUploading.value = false
    target.value = ''
  }
}

const handleDeleteCustom = async (id: string) => {
  const confirmed = await confirmDelete('确定要删除这个自定义背景吗？')
  if (!confirmed) return

  // 找到对应的 URL 并调用后端删除（物理文件 + 数据库索引）
  const item = bgList.value.find(b => b.id === id)
  if (item?.url && userStore.userId) {
    try { await deleteBgImage(item.url, userStore.userId) } catch { /* 后端删除失败不阻塞前端 */ }
  }

  removeCustomBg(id)
  delete loaded.value[id]
  refreshBgList()
  if (cfg.bgImageId.value === id) {
    cfg.setBgImage(undefined)
  }
  ElMessage.success('已删除')
}
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


.bg-image-empty { font-size: 1.6rem; color: var(--text-muted);transition: color 0.3s, transform 0.3s; }

.bg-image-empty:hover {
  color: var(--accent-cyan);
  transform: scale(1.15) rotate(90deg);
}

.upload-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-style: dashed;
}
.upload-card:hover {
  border-color: var(--accent-cyan);
}
.upload-icon {
  color: var(--text-muted);
  transition: color 0.3s, transform 0.3s;
}
.upload-card:hover .upload-icon {
  color: var(--accent-cyan);
  transform: scale(1.15) rotate(90deg);
}

.bg-delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.5);
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
  transition: opacity 0.2s, background 0.2s, color 0.2s;
  z-index: 1;
}
.bg-image-card:hover .bg-delete-btn { opacity: 1; color: white; }
.bg-delete-btn:hover { background: rgba(239,68,68,0.9); color: white; }

@media (max-width: 768px) { .full-mode { padding: 16px; } .bg-image-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

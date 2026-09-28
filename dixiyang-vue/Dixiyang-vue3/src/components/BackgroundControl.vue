<template>
  <div class="background-control" :class="`mode-${mode}`">
    <!-- full：设置页内直接展开 -->
    <BgImageGrid
      v-if="mode === 'full'"
      :list="bgList"
      :loaded="loaded"
      :active-id="cfg.bgImageId.value"
      @select="cfg.setBgImage"
      @delete="handleDeleteCustom"
      @upload="triggerBgUpload"
    />

    <!-- compact：首页 / 章节页头部，弹层选择 -->
    <el-popover
      v-else
      :width="330"
      trigger="click"
      placement="bottom-end"
      :teleported="false"
      popper-class="bg-compact-popper"
    >
      <template #reference>
        <button class="compact-trigger" type="button" title="更换背景">
          <Picture /> 背景
        </button>
      </template>
      <div class="compact-panel">
        <p class="panel-title">更换背景</p>
        <BgImageGrid
          :list="bgList"
          :loaded="loaded"
          :active-id="cfg.bgImageId.value"
          @select="cfg.setBgImage"
          @delete="handleDeleteCustom"
          @upload="triggerBgUpload"
        />
      </div>
    </el-popover>

    <!-- 隐藏的上传入口（full / compact 共用） -->
    <input
      ref="bgFileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      style="display: none"
      @change="onBgFileUpload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import BgImageGrid from '@/components/settings/BgImageGrid.vue'
import {
  useBackgroundConfig,
  BG_IMAGES,
  getCustomBgImages,
  addCustomBg,
  removeCustomBg,
} from '@/composables/useBackgroundConfig'
import { uploadBgImage, deleteBgImage } from '@/api/novelApi'
import { useUserStore } from '@/stores/UserStore'
import { confirmDelete } from '@/utils/confirm'

interface Props {
  mode?: 'compact' | 'full'
}

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
    try {
      loaded.value[img.id] = await img.importFn()
    } catch {
      /* 单张加载失败不影响其余 */
    }
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
    const url = res.data
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
  const ok = await confirmDelete('确定要删除这个自定义背景吗？')
  if (!ok) return

  // 先请求后端删除物理文件，失败不阻塞本地移除
  const item = bgList.value.find((b) => b.id === id)
  if (item?.url && userStore.userId) {
    try {
      await deleteBgImage(item.url, userStore.userId)
    } catch {
      /* 后端删除失败不阻塞前端 */
    }
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
.background-control {
  display: block;
  width: 100%;
}

/* ============ compact 触发按钮 ============ */
.compact-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--surface-glass);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition:
    border-color var(--dur-fast) var(--ease-out),
    color var(--dur-fast) var(--ease-out);
}

.compact-trigger:hover {
  border-color: var(--surface-glass-border-hover);
  color: var(--text-primary);
}

.compact-trigger:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

.compact-trigger svg {
  width: 16px;
  height: 16px;
}

/* ============ compact 弹层 ============ */
.compact-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}
</style>

<style>
/* 弹层 teleported=false 时内容仍在本组件，但 popper 容器由 EP 生成，需全局样式 */
.bg-compact-popper {
  padding: 14px !important;
  background: var(--surface-page) !important;
  border: 1px solid var(--surface-glass-border) !important;
}
</style>

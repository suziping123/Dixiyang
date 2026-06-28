<template>
  <header class="stage-header">
    <div class="header-top">
      <div class="logo-wrapper">
        <h1 class="logo-text">DIXIYANG <span class="engine-span">ENGINE</span></h1>
        <div class="glow-line"></div>
      </div>
      <div class="header-controls">
        <BackgroundControl mode="compact" />
      </div>
    </div>
    <div class="subtitle-row">
      <img
        class="novel-cover-thumb"
        :src="coverSrc"
        @error="(e: Event) => { (e.target as HTMLImageElement).src = defaultCover }"
      />
      <div class="subtitle-text-group">
        <p class="subtitle">{{ pageTitle }} - <span class="user-name">{{ novelStore.currentNovel?.title || '未知' }}</span></p>
        <div class="cover-actions">
          <button class="cover-change-btn" @click="showCoverDialog = true">更换封面</button>
          <button v-if="hasCover" class="cover-delete-btn" @click="removeCover">删除封面</button>
        </div>
      </div>
    </div>
  </header>

  <el-dialog v-model="showCoverDialog" title="更换封面" width="480px" align-center>
    <el-tabs v-model="coverTab">
      <el-tab-pane label="上传文件" name="upload">
        <div class="cover-upload-area" @click="triggerUpload" @drop.prevent="onDrop" @dragover.prevent>
          <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="onFileChange" />
          <img v-if="coverPreview" :src="coverPreview" class="cover-preview" />
          <div v-else class="upload-placeholder">
            <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor" ><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            <p>点击或拖拽上传封面</p>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="输入URL" name="url">
        <el-input v-model="coverUrlInput" placeholder="https://example.com/cover.jpg" clearable />
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <el-button @click="showCoverDialog = false">取消</el-button>
      <el-button type="primary" @click="saveCover" :loading="isUploading">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import BackgroundControl from '@/components/BackgroundControl.vue'
import { useNovelStore } from '@/stores/novelStore'
import { uploadNovelCover, deleteNovelCover } from '@/api/novelApi'
import { confirmDelete } from '@/utils/confirm'
import { resolveNovelCover } from '@/utils/localImages'
import defaultCoverImg from '@/images/default-cover.png'

defineProps<{ pageTitle: string }>()

const novelStore = useNovelStore()

const showCoverDialog = ref(false)
const coverTab = ref('upload')
const coverUrlInput = ref('')
const coverPreview = ref('')
const isUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const coverSrc = computed(() => resolveNovelCover(novelStore.currentNovel?.cover_url))
const defaultCover = defaultCoverImg
const hasCover = computed(() => !!novelStore.currentNovel?.cover_url)

const triggerUpload = () => fileInputRef.value?.click()
const onFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) coverPreview.value = URL.createObjectURL(file)
}
const onDrop = (e: DragEvent) => {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) coverPreview.value = URL.createObjectURL(file)
}
const saveCover = async () => {
  if (!novelStore.currentNovel?.id) return
  isUploading.value = true
  try {
    let url = ''
    if (coverTab.value === 'upload' && fileInputRef.value?.files?.[0]) {
      const res = await uploadNovelCover(fileInputRef.value.files[0])
      url = (res as any).data
    } else if (coverTab.value === 'url') {
      url = coverUrlInput.value.trim()
    }
    if (url) {
      await novelStore.updateCover(novelStore.currentNovel.id, url)
      showCoverDialog.value = false
      coverPreview.value = ''
      coverUrlInput.value = ''
      ElMessage.success('封面更新成功')
    }
  } catch (e) { console.error(e) }
  finally { isUploading.value = false }
}

const removeCover = async () => {
  const id = Number(novelStore.currentNovel?.id)
  if (!id || isNaN(id) || !novelStore.currentNovel?.cover_url) return
  const confirmed = await confirmDelete('确定要删除封面吗？')
  if (!confirmed) return
  try {
    await deleteNovelCover(novelStore.currentNovel.cover_url, id)
    novelStore.currentNovel = { ...novelStore.currentNovel, cover_url: '' }
    ElMessage.success('封面已删除')
  } catch (e) { console.error(e) }
}
</script>

<style scoped>
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
  margin: 0;
}

.subtitle-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 20px;
}

.subtitle-text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cover-actions {
  display: flex;
  gap: 6px;
}

.cover-change-btn, .cover-delete-btn {
  padding: 3px 10px;
  font-size: 0.75rem;
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  width: fit-content;
}
.cover-change-btn:hover {
  border-color: rgba(255,255,255,0.5);
  color: #fff;
}
.cover-delete-btn {
  border-color: rgba(239,68,68,0.3);
  color: rgba(239,68,68,0.7);
}
.cover-delete-btn:hover {
  border-color: rgba(239,68,68,0.8);
  color: #ef4444;
}

.novel-cover-thumb {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid var(--glass-border);
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}
.novel-cover-thumb:hover {
  border-color: var(--neon-blue);
  box-shadow: 0 0 12px rgba(59,130,246,0.3);
}
.cover-upload-area {
  width: 100%;
  height: 200px; /* 或者你需要的任意高度 */
  border: 2px dashed var(--glass-border);
  border-radius: 8px;
  cursor: pointer;
  
  /* 使用 flex 让内部的占位符区域整体居中 */
  display: flex;
  justify-content: center;
  align-items: center;
  transition: border-color 0.4s ease, box-shadow 0.4s ease;
}
.cover-upload-area:hover {
  border-color: rgba(255,255,255,0.5);
}

/* 2. 让占位符内部的 SVG 和文字垂直居中排列 */
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.45);
  transition: color 0.4s ease;
}

.cover-upload-area:hover .upload-placeholder {
  color: rgba(255,255,255,0.9);
}

.cover-upload-area:hover .upload-placeholder svg {
  transform: rotate(180deg);
  color: #fff;
}

/* 2. 必须为 SVG 本身配置 transition，否则转动会极其生硬 */
.upload-placeholder svg {
  margin-bottom: 8px;     
  display: inline-block;        /* 确保 SVG 作为块级/行内块级元素渲染，否则 transform 可能会失效 */
  transform-origin: center;     /* 显式指定以 SVG 的正中心为旋转轴心 */
  transition: transform 0.5s ease-in-out, color 0.2s; /* 确保写了 transform */
}

.upload-placeholder p {
  margin: 0;              /* 清除 P 标签自带的默认外边距 */
  font-size: 14px;
}
.cover-preview { max-width: 100%; max-height: 240px; object-fit: contain; }

.user-name {
  color: var(--neon-cyan);
  font-weight: 600;
  text-shadow: 0 0 10px rgba(6, 182, 212, 0.4);
}
</style>

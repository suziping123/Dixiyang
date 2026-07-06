<template>
  <div class="novel-card-wrapper create-card-wrapper">
    <div class="glass-card create-card" @click="showModal = true">
      <div class="card-create-content">
        <svg class="create-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        <span>构建新宇宙</span>
        <p class="create-hint">开启你的新故事</p>
      </div>
    </div>
  </div>

  <!-- 创建弹窗 -->
  <teleport to="body">
    <div v-if="showModal" class="modal-backdrop" @click="closeModal">
      <div class="create-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">✧ 构建新宇宙</h3>
          <button class="close-btn" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
            </svg>
          </button>
        </div>

        <form class="novel-form" @submit.prevent="submitForm">
          <!-- 封面上传 -->
          <div class="form-group cover-upload-group">
            <label class="form-label">宇宙封面</label>
            <div class="cover-upload-wrapper">
              <div class="cover-preview" :style="{ backgroundImage: `url(${coverPreview || defaultCover})` }" @click="triggerUpload">
                <input
                  ref="fileInputRef"
                  type="file"
                  class="cover-input"
                  accept="image/*"
                  @change="handleCoverUpload"
                />
                <div class="upload-overlay">
                  <svg class="upload-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
                  </svg>
                  <span class="upload-text">{{ coverPreview ? '更换封面' : '上传封面' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 宇宙名称 -->
          <div class="form-group">
            <label class="form-label" for="create-title">宇宙名称</label>
            <input
              type="text"
              id="create-title"
              v-model="form.title"
              class="form-input"
              placeholder="请输入你的宇宙名称（如：硅基时代）"
              required
            />
          </div>

          <!-- 创作者笔名 -->
          <div class="form-group">
            <label class="form-label" for="create-penName">创作者笔名</label>
            <input
              type="text"
              id="create-penName"
              v-model="form.penName"
              class="form-input"
              placeholder="请输入你的笔名"
              required
            />
          </div>

          <!-- 宇宙简介 -->
          <div class="form-group">
            <label class="form-label" for="create-description">宇宙简介</label>
            <textarea
              id="create-description"
              v-model="form.description"
              class="form-textarea"
              placeholder="请描述你的宇宙世界观、核心设定等..."
              rows="5"
              required
            ></textarea>
          </div>

          <!-- 按钮 -->
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="!isSubmitting">创建宇宙</span>
              <span v-else>创建中...</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createNovel, uploadNovelCover } from '@/api/novelApi'
import defaultCover from '@/images/default-cover.png'

const emit = defineEmits<{
  'create-success': []
}>()

const showModal = ref(false)
const coverPreview = ref('')
const isSubmitting = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

interface NovelDTO {
  title: string
  penName: string
  description: string
  coverUrl?: string
}
const form = ref<NovelDTO>({
  title: '',
  penName: '',
  description: '',
  coverUrl: ''
})

const triggerUpload = (e?: Event) => {
  e?.stopPropagation()
  fileInputRef.value?.click()
}

const handleCoverUpload = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert('封面图片大小不能超过5MB')
    return
  }
  try {
    coverPreview.value = URL.createObjectURL(file)
    const res = await uploadNovelCover(file)
    form.value.coverUrl = res.data
  } catch (error) {
    console.error('封面上传失败:', error)
    alert('封面上传失败，请重试')
    coverPreview.value = ''
  }
}

const submitForm = async () => {
  if (!form.value.title.trim() || !form.value.penName.trim() || !form.value.description.trim()) {
    alert('请填写完整信息')
    return
  }
  try {
    isSubmitting.value = true
    await createNovel(form.value)
    emit('create-success')
    closeModal()
  } catch (error) {
    const err = error as Error
    console.error('创建小说失败:', err.message)
    alert(err.message)
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  form.value = { title: '', penName: '', description: '', coverUrl: '' }
  coverPreview.value = ''
  if (fileInputRef.value) fileInputRef.value.value = ''
}
</script>

<style scoped>
.novel-card-wrapper {
  cursor: pointer;
  transition: all 0.4s ease;
}
.novel-card-wrapper:hover { transform: translateY(-8px); }

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 0;
  height: 100%;
  aspect-ratio: 2 / 3;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  box-sizing: border-box;
}

.create-card {
  border: 2px dashed rgba(255, 255, 255, 0.2);
}
.create-card:hover {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.08);
}

.card-create-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: var(--text-secondary);
}

.create-icon {
  width: 60px;
  height: 60px;
  color: var(--neon-blue);
  opacity: 0.8;
}

.create-hint {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
}

/* ========== 弹窗 ========== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.create-modal {
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  background: rgba(10, 10, 12, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}
.close-btn:hover { color: #06b6d4; transform: rotate(90deg); }
.close-btn svg { width: 24px; height: 24px; }

.form-group { margin-bottom: 24px; }

.form-label {
  display: block;
  margin-bottom: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
  transform: scale(1.02);
}

.cover-upload-group { margin-bottom: 30px; }

.cover-upload-wrapper { display: flex; justify-content: center; }

.cover-preview {
  width: 200px;
  height: 280px;
  border-radius: 16px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}
.cover-preview:hover {
  border-color: #06b6d4;
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}

.cover-input { display: none; }

.upload-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 14px;
}
.cover-preview:hover .upload-overlay { opacity: 1; }

.upload-icon {
  width: 40px;
  height: 40px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.upload-text {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin-top: 30px;
}

.cancel-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.submit-btn {
  padding: 12px 32px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}
</style>

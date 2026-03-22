<!-- src/components/CreateNovelModal.vue -->
<template>
  <!-- 遮罩层 -->
  <teleport to="body">
    <div v-if="visible" class="modal-backdrop" @click="closeModal">
      <!-- 弹窗主体（加入场动效） -->
      <div
        class="create-modal"
        @click.stop
        :style="{
          opacity: visible ? 1 : 0,
          transform: visible ? 'translate(-50%, -50%) scale(0.75)' : 'translate(-50%, -50%) scale(0.8)'
        }"
      >
        <!-- 弹窗头部（关闭按钮+标题） -->
        <div class="modal-header">
          <h3 class="modal-title">✧ 构建新宇宙</h3>
          <button class="close-btn" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
            </svg>
          </button>
        </div>

        <!-- 原来的创建表单（复用你原来的逻辑） -->
        <form class="novel-form" @submit.prevent="submitForm">
          <!-- 封面上传 -->
          <div class="form-group cover-upload-group">
            <label class="form-label">宇宙封面</label>
            <div class="cover-upload-wrapper">
              <div class="cover-preview" :style="{ backgroundImage: `url(${coverPreview || defaultCover})` }">
                <input
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

          <!-- 小说标题 -->
          <div class="form-group">
            <label class="form-label" for="title">宇宙名称</label>
            <input
              type="text"
              id="title"
              v-model="form.title"
              class="form-input"
              placeholder="请输入你的宇宙名称（如：硅基时代）"
              required
            />
          </div>

          <!-- 笔名 -->
          <div class="form-group">
            <label class="form-label" for="penName">创作者笔名</label>
            <input
              type="text"
              id="penName"
              v-model="form.penName"
              class="form-input"
              placeholder="请输入你的笔名"
              required
            />
          </div>

          <!-- 描述 -->
          <div class="form-group">
            <label class="form-label" for="description">宇宙简介</label>
            <textarea
              id="description"
              v-model="form.description"
              class="form-textarea"
              placeholder="请描述你的宇宙世界观、核心设定等..."
              rows="5"
              required
            ></textarea>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="!isSubmitting">创建宇宙</span>
              <span v-if="isSubmitting">创建中...</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue';
import { createNovel, uploadNovelCover } from '@/api/novelApi';
import defaultCover from '@/images/default-cover.png';

// 定义Props：控制弹窗显隐
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// 定义Emits：关闭弹窗、创建成功
const emit = defineEmits(['close', 'create-success']);

// 表单数据
interface NovelDTO {
  title: string;
  penName: string;
  description: string;
  coverUrl?: string;
}
const form = ref<NovelDTO>({
  title: '',
  penName: '',
  description: '',
  coverUrl: ''
});

// 状态管理
const coverPreview = ref('');
const isSubmitting = ref(false);

// 关闭弹窗
const closeModal = () => {
  emit('close');
  // 重置表单
  form.value = { title: '', penName: '', description: '', coverUrl: '' };
  coverPreview.value = '';
};

// 处理封面上传（复用你原来的逻辑）
const handleCoverUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  if (file.size > 5 * 1024 * 1024) {
    alert('封面图片大小不能超过5MB');
    return;
  }

  try {
    coverPreview.value = URL.createObjectURL(file);
    const res = await uploadNovelCover(file);
    form.value.coverUrl = res.data.coverUrl;
  } catch (error) {
    console.error('封面上传失败:', error);
    alert('封面上传失败，请重试');
    coverPreview.value = '';
  }
};

// 提交表单（核心修改：创建成功后关闭弹窗+通知父组件刷新列表）
const submitForm = async () => {
  if (!form.value.title.trim() || !form.value.penName.trim() || !form.value.description.trim()) {
    alert('请填写完整信息');
    return;
  }

  try {
    isSubmitting.value = true;
    const res = await createNovel(form.value);
    alert(res.msg || '宇宙创建成功！');
    emit('create-success'); // 通知父组件刷新列表
    closeModal(); // 关闭弹窗
  } catch (error) {
    const err = error as Error;
    console.error('创建小说失败:', err.message);
    alert(err.message);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* 遮罩层 */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: backdropFadeIn 0.3s ease;
}

@keyframes backdropFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 弹窗主体 */
.create-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.8);
  opacity: 0;
  width: 100%;
  max-width: 600px;
  background: rgba(10, 10, 12, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 1000;
}

/* 弹窗头部 */
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

.close-btn:hover {
  color: #06b6d4;
  transform: rotate(90deg);
}

.close-btn svg {
  width: 24px;
  height: 24px;
}

/* 复用你原来的表单样式（保持视觉统一） */
.form-group {
  margin-bottom: 30px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.form-input, .form-textarea {
  width: 100%;
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
}

.cover-upload-group {
  margin-bottom: 40px;
}

.cover-upload-wrapper {
  display: flex;
  justify-content: center;
}

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

.cover-input {
  display: none;
}

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

.cover-preview:hover .upload-overlay {
  opacity: 1;
}

.upload-icon {
  width: 40px;
  height: 40px;
  color: #ffffff;
  margin-bottom: 10px;
}

.upload-text {
  color: #ffffff;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin-top: 40px;
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
  color: #ffffff;
}

.submit-btn {
  padding: 12px 32px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
  border: none;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}
.form-input {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.form-input:focus {
  transform: scale(1.02);
  border-color: #06b6d4;
  box-shadow: 0 0 25px rgba(6, 182, 212, 0.3);
}
</style>

<template>
  <div class="background-control" :class="[`mode-${mode}`]">
    <!-- 紧凑模式：工具栏 -->
    <div v-if="mode === 'compact'" class="compact-mode">
      <div class="preset-buttons">
        <button
          v-for="preset in presets"
          :key="preset.value"
          class="preset-btn"
          :class="{ active: bgConfig.preset.value === preset.value }"
          :title="preset.label"
          @click="bgConfig.setPreset(preset.value)"
        >
          {{ preset.icon }}
        </button>
      </div>

      <div class="control-buttons">
        <button
          class="control-btn anim-btn"
          :class="{ active: bgConfig.animEnabled.value }"
          @click="bgConfig.toggleAnimation"
          title="动画开关"
        >
          {{ bgConfig.animEnabled.value ? '▶' : '⏸' }}
        </button>
      </div>

      <div class="intensity-group">
        <input
          type="range"
          min="0"
          max="100"
          :value="bgConfig.intensity.value"
          @input="(e) => bgConfig.setIntensity(Number((e.target as HTMLInputElement).value))"
          class="intensity-slider"
          title="背景强度"
        />
        <span class="intensity-value">{{ bgConfig.intensity.value }}%</span>
      </div>

      <div class="theme-buttons">
        <button
          v-for="theme in themes"
          :key="theme.value"
          class="color-btn"
          :class="{ active: bgConfig.colorTheme.value === theme.value }"
          :style="{ '--theme-color': theme.color }"
          @click="bgConfig.setColorTheme(theme.value)"
          :title="theme.label"
        >
          ●
        </button>
      </div>
    </div>

    <!-- 完整模式：详细设置面板 -->
    <div v-else class="full-mode">
      <!-- 背景预设网格 -->
      <div class="settings-section">
        <h3 class="section-title">背景预设</h3>
        <div class="presets-grid">
          <button
            v-for="preset in presets"
            :key="preset.value"
            class="preset-card"
            :class="{ active: bgConfig.preset.value === preset.value }"
            @click="bgConfig.setPreset(preset.value)"
          >
            <span class="preset-icon">{{ preset.icon }}</span>
            <span class="preset-name">{{ preset.label }}</span>
            <span class="preset-desc">{{ preset.description }}</span>
          </button>
        </div>
      </div>

      <!-- 自定义图片上传 -->
      <div v-if="bgConfig.preset.value === 'custom'" class="settings-section custom-upload">
        <h3 class="section-title">📸 上传自定义背景</h3>
        <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
          <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <p class="upload-text">拖拽图片或点击上传</p>
          <p class="upload-hint">支持 JPG、PNG、WebP 格式</p>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          style="display: none"
          @change="handleFileSelect"
        />
        <div v-if="bgConfig.customImageUrl.value" class="upload-preview">
          <img :src="bgConfig.customImageUrl.value" alt="预览" class="preview-img" />
          <button class="btn-remove" @click="removeCustomImage">✕ 移除图片</button>
        </div>
      </div>

      <!-- 动画设置 -->
      <div class="settings-section">
        <h3 class="section-title">动画设置</h3>
        <div class="toggle-wrapper">
          <label class="toggle-label">
            <button
              class="toggle-btn"
              :class="{ active: bgConfig.animEnabled.value }"
              @click="bgConfig.toggleAnimation"
            >
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ bgConfig.animEnabled.value ? '启用' : '禁用' }}</span>
            </button>
            <span class="label-text">动画效果</span>
          </label>
        </div>
      </div>

      <!-- 强度调节 -->
      <div class="settings-section">
        <h3 class="section-title">强度调节</h3>
        <div class="intensity-wrapper">
          <input
            type="range"
            min="0"
            max="100"
            :value="bgConfig.intensity.value"
            @input="(e) => bgConfig.setIntensity(Number((e.target as HTMLInputElement).value))"
            class="intensity-slider-full"
          />
          <div class="intensity-display">
            <span class="intensity-percent">{{ bgConfig.intensity.value }}%</span>
            <span class="intensity-bar">
              <span class="intensity-fill" :style="{ width: `${bgConfig.intensity.value}%` }"></span>
            </span>
          </div>
        </div>
      </div>

      <!-- 主题色 -->
      <div class="settings-section">
        <h3 class="section-title">主题色</h3>
        <div class="theme-grid">
          <button
            v-for="theme in themes"
            :key="theme.value"
            class="theme-btn"
            :class="{ active: bgConfig.colorTheme.value === theme.value }"
            @click="bgConfig.setColorTheme(theme.value)"
          >
            <span class="theme-color" :style="{ backgroundColor: theme.color }"></span>
            <span class="theme-name">{{ theme.label }}</span>
          </button>
        </div>
      </div>

      <!-- 文字对比度设置 -->
      <div class="settings-section contrast-section">
        <h3 class="section-title">📝 文字对比度</h3>
        <div class="contrast-info">
          <p v-if="themeSystem.sampledBrightness.value !== null" class="brightness-value">
            背景亮度: <code>{{ (themeSystem.sampledBrightness.value * 100).toFixed(0) }}%</code>
          </p>
          <p class="text-mode">
            文字模式:
            <span class="mode-badge" :class="themeSystem.textColorMode.value">
              {{ themeSystem.textColorMode.value === 'light' ? '浅色文字' : '深色文字' }}
            </span>
          </p>
        </div>
        <div class="contrast-toggle">
          <label class="toggle-label">
            <button
              class="toggle-btn"
              :class="{ active: themeSystem.autoAdjustTextColor.value }"
              @click="themeSystem.setAutoAdjustTextColor(!themeSystem.autoAdjustTextColor.value)"
            >
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ themeSystem.autoAdjustTextColor.value ? '启' : '关' }}</span>
            </button>
            <span class="label-text">自动调整文字颜色</span>
          </label>
          <p class="contrast-desc">根据背景亮度自动选择文字颜色，保证可读性</p>
        </div>

        <!-- 手动文字颜色选择 -->
        <div v-if="!themeSystem.autoAdjustTextColor.value" class="manual-text-color">
          <p class="color-label">手动选择文字颜色:</p>
          <div class="text-color-buttons">
            <button
              class="text-color-btn light"
              :class="{ active: themeSystem.textColorMode.value === 'light' }"
              @click="themeSystem.setTextColorMode('light')"
              title="浅色文字 - 适合深色背景"
            >
              <span class="btn-label">浅色 (白)</span>
              <span class="btn-preview"></span>
            </button>
            <button
              class="text-color-btn dark"
              :class="{ active: themeSystem.textColorMode.value === 'dark' }"
              @click="themeSystem.setTextColorMode('dark')"
              title="深色文字 - 适合浅色背景"
            >
              <span class="btn-label">深色 (黑)</span>
              <span class="btn-preview"></span>
            </button>
          </div>
        </div>
      </div>

      <!-- 恢复默认 -->
      <div class="settings-section">
        <button class="btn-reset" @click="handleReset">
          🔄 恢复默认
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useBackgroundConfig, type BackgroundPreset, type ColorTheme } from '@/composables/useBackgroundConfig'
import { useThemeSystem } from '@/composables/useThemeSystem'
import { compressImage } from '@/utils/colorUtils'

interface Props {
  mode?: 'compact' | 'full'
}

withDefaults(defineProps<Props>(), {
  mode: 'compact',
})

const bgConfig = useBackgroundConfig()
const themeSystem = useThemeSystem()
const fileInput = ref<HTMLInputElement>()

interface PresetItem {
  value: BackgroundPreset
  icon: string
  label: string
  description: string
}

interface ThemeItem {
  value: ColorTheme
  color: string
  label: string
}

const presets: PresetItem[] = [
  { value: 'dynamic', icon: '✨', label: '动态', description: '动感渐变流动' },
  { value: 'static', icon: '🎨', label: '静态', description: '固定渐变' },
  { value: 'gradient', icon: '🌈', label: '渐变', description: '彩虹色系' },
  { value: 'grid', icon: '📊', label: '网格', description: '几何网格' },
  { value: 'minimal', icon: '◆', label: '极简', description: '高端黑' },
  { value: 'custom', icon: '🖼️', label: '自定义', description: '上传图片' },
]

const themes: ThemeItem[] = [
  { value: 'purple', color: '#a855f7', label: '紫色' },
  { value: 'blue', color: '#3b82f6', label: '蓝色' },
  { value: 'cyan', color: '#06b6d4', label: '青色' },
]

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  const file = event.dataTransfer?.files?.[0]
  if (file?.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = async (file: File) => {
  try {
    // 压缩图片：最大宽度 1920px，质量 0.7
    const compressedUrl = await compressImage(file, 1920, 1080, 0.7)
    bgConfig.saveCustomImage(compressedUrl)
    bgConfig.setPreset('custom')
  } catch (error) {
    console.error('图片压缩失败:', error)
    // 降级方案：直接使用原始图片
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target?.result as string
      bgConfig.saveCustomImage(imageUrl)
      bgConfig.setPreset('custom')
    }
    reader.readAsDataURL(file)
  }
}

const removeCustomImage = () => {
  bgConfig.customImageUrl.value = undefined
  bgConfig.setPreset('dynamic')
}

const handleReset = () => {
  if (confirm('确定要恢复默认设置吗？')) {
    bgConfig.resetToDefault()
    themeSystem.resetThemeToDefault()
  }
}
</script>

<style scoped>
.background-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* ========== 紧凑模式 ========== */
.mode-compact {
  flex-wrap: wrap;
  gap: 12px;
}

.compact-mode {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.preset-buttons,
.control-buttons,
.theme-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.preset-btn,
.control-btn,
.color-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.preset-btn:hover,
.control-btn:hover,
.color-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  color: #3b82f6;
}

.preset-btn.active,
.control-btn.active,
.color-btn.active {
  background: rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
  color: #3b82f6;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
}

.color-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.color-btn.active {
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.4), inset 0 0 8px rgba(255, 255, 255, 0.2);
}

.intensity-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.intensity-slider {
  width: 100px;
  height: 6px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.intensity-value {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  min-width: 40px;
  text-align: right;
}

/* ========== 完整模式 ========== */
.full-mode {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
}

.settings-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.settings-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ========== 预设网格 ========== */
.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 12px;
}

.preset-card {
  padding: 16px 12px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.preset-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.preset-card.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3b82f6;
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.3);
  color: #fff;
}

.preset-icon {
  font-size: 1.8rem;
}

.preset-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.preset-desc {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* ========== 图片上传 ========== */
.custom-upload {
  background: rgba(6, 182, 212, 0.05) !important;
  border-color: rgba(6, 182, 212, 0.2) !important;
}

.upload-area {
  border: 2px dashed rgba(6, 182, 212, 0.5);
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(6, 182, 212, 0.02);
}

.upload-area:hover {
  border-color: rgba(6, 182, 212, 0.8);
  background: rgba(6, 182, 212, 0.05);
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: #06b6d4;
  margin-bottom: 12px;
  opacity: 0.7;
}

.upload-text {
  font-weight: 600;
  color: white;
  margin: 0 0 4px 0;
}

.upload-hint {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.upload-preview {
  margin-top: 16px;
  position: relative;
}

.preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.btn-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.8);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-remove:hover {
  background: rgba(239, 68, 68, 1);
}

/* ========== 切换开关 ========== */
.toggle-wrapper {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle-btn {
  position: relative;
  width: 50px;
  height: 28px;
  border: none;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn.active {
  background: #3b82f6;
}

.toggle-switch {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  transition: left 0.3s ease;
}

.toggle-btn.active .toggle-switch {
  left: 25px;
}

.toggle-text {
  position: absolute;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.label-text {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* ========== 强度控制 ========== */
.intensity-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intensity-slider-full {
  width: 100%;
  height: 6px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.intensity-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.intensity-percent {
  min-width: 45px;
  font-weight: 600;
  color: #3b82f6;
}

.intensity-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.intensity-fill {
  height: 100%;
  background: linear-gradient(to right, #3b82f6, #a855f7);
  transition: width 0.2s ease;
}

/* ========== 主题网格 ========== */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 12px;
}

.theme-btn {
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.theme-btn:hover {
  border-color: rgba(255, 255, 255, 0.3);
}

.theme-btn.active {
  border-color: #3b82f6;
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.3);
}

.theme-color {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.theme-name {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* ========== 对比度设置 ========== */
.contrast-section {
  background: rgba(6, 182, 212, 0.05) !important;
  border-color: rgba(6, 182, 212, 0.2) !important;
  border-radius: 12px;
  padding: 16px;
}

.contrast-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(6, 182, 212, 0.05);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 8px;
}

.brightness-value {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.brightness-value code {
  background: rgba(6, 182, 212, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  color: #06b6d4;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.text-mode {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.mode-badge.light {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.mode-badge.dark {
  background: rgba(26, 26, 26, 0.3);
  color: rgba(255, 255, 255, 0.8);
}

.contrast-toggle {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contrast-desc {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* ========== 手动文字颜色选择 ========== */
.manual-text-color {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(6, 182, 212, 0.3);
}

.manual-text-color .color-label {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.text-color-buttons {
  display: flex;
  gap: 12px;
}

.text-color-btn {
  flex: 1;
  padding: 10px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  color: rgba(255, 255, 255, 0.8);
}

.text-color-btn:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: rgba(6, 182, 212, 0.4);
}

.text-color-btn.active {
  background: rgba(6, 182, 212, 0.15);
  border-color: #06b6d4;
  color: #06b6d4;
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.3);
}

.btn-label {
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.text-color-btn.light .btn-preview {
  background: #ffffff;
}

.text-color-btn.dark .btn-preview {
  background: #1a1a1a;
  border-color: rgba(0, 0, 0, 0.5);
}

/* ========== 按钮 ========== */
.btn-reset {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-reset:hover {
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.5);
  color: #a855f7;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .background-control {
    gap: 8px;
  }

  .preset-btn,
  .control-btn,
  .color-btn {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }

  .intensity-slider {
    width: 80px;
  }

  .full-mode {
    padding: 16px;
  }

  .presets-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .theme-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

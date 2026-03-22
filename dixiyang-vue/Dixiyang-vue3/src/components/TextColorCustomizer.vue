<template>
  <div class="text-color-customizer">
    <!-- 标题和描述 -->
    <div class="section-header">
      <h3 class="section-title">🎨 自定义文字颜色</h3>
      <p class="section-desc">为不同的文本类型选择合适的颜色</p>
    </div>

    <!-- 颜色选择卡片容器 -->
    <div class="color-cards-grid">
      <!-- 主要文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">主要文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.textPrimary.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.textPrimary.value)"
            @input="(e) => textColorCustomizer.setTextPrimary(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.textPrimary.value"
            @input="(e) => textColorCustomizer.setTextPrimary(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example">预览文本</p>
      </div>

      <!-- 次要文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">次要文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.textSecondary.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.textSecondary.value)"
            @input="(e) => textColorCustomizer.setTextSecondary(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.textSecondary.value"
            @input="(e) => textColorCustomizer.setTextSecondary(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-secondary">预览文本</p>
      </div>

      <!-- 弱化文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">弱化文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.textMuted.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.textMuted.value)"
            @input="(e) => textColorCustomizer.setTextMuted(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.textMuted.value"
            @input="(e) => textColorCustomizer.setTextMuted(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-muted">预览文本</p>
      </div>

      <!-- 禁用文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">禁用文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.textDisabled.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.textDisabled.value)"
            @input="(e) => textColorCustomizer.setTextDisabled(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.textDisabled.value"
            @input="(e) => textColorCustomizer.setTextDisabled(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-disabled">预览文本</p>
      </div>

      <!-- 描述文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">描述文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.descriptionColor.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.descriptionColor.value)"
            @input="(e) => textColorCustomizer.setDescriptionColor(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.descriptionColor.value"
            @input="(e) => textColorCustomizer.setDescriptionColor(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-description">小说描述与摘要文本</p>
      </div>

      <!-- 链接文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">链接文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.linkColor.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.linkColor.value)"
            @input="(e) => textColorCustomizer.setLinkColor(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.linkColor.value"
            @input="(e) => textColorCustomizer.setLinkColor(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-link">可点击的链接</p>
      </div>

      <!-- 强调文本颜色 -->
      <div class="color-card">
        <div class="color-card-header">
          <span class="color-label">强调文本</span>
          <span class="color-preview" :style="{ backgroundColor: textColorCustomizer.accentColor.value }"></span>
        </div>
        <div class="color-input-group">
          <input
            type="color"
            class="color-picker"
            :value="hexToColorInput(textColorCustomizer.accentColor.value)"
            @input="(e) => textColorCustomizer.setAccentColor(hexFromInput(getInputValue(e)))"
          />
          <input
            type="text"
            class="color-text-input"
            :value="textColorCustomizer.accentColor.value"
            @input="(e) => textColorCustomizer.setAccentColor(getInputValue(e))"
            placeholder="#ffffff 或 rgba(...)"
          />
        </div>
        <p class="color-example-accent">重要强调内容</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button
        class="btn btn-reset"
        @click="handleReset"
        :disabled="textColorCustomizer.isDefaultConfig()"
      >
        ↻ 重置为默认
      </button>

      <button
        class="btn btn-sync"
        @click="handleSync"
        :disabled="textColorCustomizer.isSyncing.value || textColorCustomizer.isDefaultConfig()"
      >
        {{ textColorCustomizer.isSyncing.value ? '同步中...' : '☁️ 同步到云端' }}
      </button>
    </div>

    <!-- 同步状态提示 -->
    <div v-if="textColorCustomizer.syncMessage.value" class="sync-message" :class="{ success: textColorCustomizer.syncMessage.value.includes('✅') }">
      {{ textColorCustomizer.syncMessage.value }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

const textColorCustomizer = useTextColorCustomizer()

/**
 * 将 hex 或 rgba 颜色转换为 HTML5 color input 可接受的格式
 */
const hexToColorInput = (color: string): string => {
  // 如果是 hex 格式，直接返回
  if (color.startsWith('#')) {
    return color.length === 7 ? color : '#ffffff'
  }

  // 如果是 rgba 格式，尝试提取颜色信息
  // 对于 rgba 格式，我们无法完全转换，所以返回白色作为默认
  if (color.includes('rgba') || color.includes('rgb')) {
    return '#ffffff'
  }

  return '#ffffff'
}

/**
 * 将 HTML5 color input 的值转换回标准格式
 */
const hexFromInput = (hexValue: string): string => {
  return hexValue // color input 返回的就是 #RRGGBB 格式
}

/**
 * 处理重置操作
 */
const handleReset = () => {
  if (confirm('确认重置所有文字颜色为默认值？')) {
    textColorCustomizer.resetToDefault()
  }
}

/**
 * 处理同步操作
 */
const handleSync = async () => {
  await textColorCustomizer.saveToBackend()
}

/**
 * 安全的事件处理 - 获取输入值
 */
const getInputValue = (e: Event): string => {
  return (e.target as HTMLInputElement).value
}
</script>

<style scoped>
.text-color-customizer {
  width: 100%;
  padding: 0;
}

/* 标题部分 */
.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.section-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

/* 颜色卡片网格 */
.color-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

/* 单个颜色卡片 */
.color-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.color-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 卡片标题 */
.color-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.color-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.color-preview {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-preview:hover {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.1);
}

/* 颜色输入组 */
.color-input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-picker:hover {
  border-color: rgba(255, 255, 255, 0.3);
}

.color-text-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 12px;
  font-family: 'Monaco', 'Courier New', monospace;
  transition: all 0.2s ease;
}

.color-text-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.color-text-input::placeholder {
  color: var(--text-muted);
}

/* 预览文本 */
.color-example {
  font-size: 14px;
  color: var(--text-primary);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
}

.color-example-secondary {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
}

.color-example-muted {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
}

.color-example-disabled {
  font-size: 14px;
  color: var(--text-disabled);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
}

.color-example-description {
  font-size: 14px;
  color: var(--description-color);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
}

.color-example-link {
  font-size: 14px;
  color: var(--link-color);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
  text-decoration: underline;
}

.color-example-accent {
  font-size: 14px;
  color: var(--accent-color);
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-align: center;
  font-weight: 600;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-reset {
  border-color: rgba(168, 85, 247, 0.3);
  background: rgba(168, 85, 247, 0.05);
}

.btn-reset:hover:not(:disabled) {
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.5);
}

.btn-sync {
  border-color: rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.05);
}

.btn-sync:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
}

/* 同步状态提示 */
.sync-message {
  padding: 12px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 14px;
  text-align: center;
  animation: slideIn 0.3s ease;
}

.sync-message.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #86efac;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .color-cards-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>







<template>
  <div class="font-control" :class="{ compact: mode === 'compact', full: mode === 'full' }">
    <!-- ========== COMPACT 模式 ========== -->
    <template v-if="mode === 'compact'">
      <div class="compact-toolbar">
        <!-- 字体族选择（下拉框）-->
        <div class="compact-group">
          <label class="compact-label">字体</label>
          <select v-model="fontConfig.family" class="compact-select">
            <option value="inter">Inter</option>
            <option value="serif">Serif</option>
            <option value="monospace">Monospace</option>
            <option value="system">System</option>
          </select>
        </div>

        <!-- 字体大小滑块 -->
        <div class="compact-group">
          <label class="compact-label">大小</label>
          <input
            type="range"
            :value="fontConfig.size"
            min="12"
            max="24"
            @input="(e) => fontConfig.setFontSize(Number((e.target as HTMLInputElement).value))"
            class="compact-range"
          />
        </div>
      </div>
    </template>

    <!-- ========== FULL 模式 ========== -->
    <template v-else>
      <!-- 字体族选择 -->
      <div class="font-family-section">
        <h4 class="section-title">字体族</h4>
        <p class="section-desc">选择适合你的字体样式</p>
        <div class="font-family-grid">
          <div
            v-for="font in fontOptions"
            :key="font.value"
            class="font-card"
            :class="{ active: fontConfig.family.value === font.value }"
            @click="fontConfig.setFontFamily(font.value as any)"
          >
            <div class="font-preview" :style="{ fontFamily: getFontFamilyCSS(font.value) }">
              {{ font.preview }}
            </div>
            <div class="font-label">{{ font.label }}</div>
            <div class="font-desc">{{ font.desc }}</div>
          </div>
        </div>
      </div>

      <!-- 字体大小调整 -->
      <div class="font-size-section">
        <h4 class="section-title">基础字体大小</h4>
        <div class="size-controls">
          <input
            type="range"
            :value="fontConfig.size"
            min="12"
            max="24"
            step="1"
            @input="(e) => fontConfig.setFontSize(Number((e.target as HTMLInputElement).value))"
            class="size-slider"
          />
          <div class="size-display">
            <input
              type="number"
              :value="fontConfig.size"
              min="12"
              max="24"
              @change="(e) => fontConfig.setFontSize(Number((e.target as HTMLInputElement).value))"
              class="size-input"
            />
            <span class="size-unit">px</span>
          </div>
        </div>
        <div class="size-preview">
          <span class="preview-label">预览</span>
          <p class="preview-text">这是你的基础文字显示效果</p>
        </div>
      </div>

      <!-- 全局缩放因子 -->
      <div class="font-scale-section">
        <h4 class="section-title">全局字体缩放</h4>
        <p class="section-desc">同时缩放标题和正文大小（{{ (fontConfig.scale * 100).toFixed(0) }}%）</p>
        <div class="scale-controls">
          <button
            class="scale-btn"
            v-for="scaleValue in [0.85, 0.9, 1.0, 1.1, 1.2]"
            :key="scaleValue"
            :class="{ active: fontConfig.scale === scaleValue }"
            @click="fontConfig.setFontScale(scaleValue)"
          >
            {{ (scaleValue * 100).toFixed(0) }}%
          </button>
        </div>

        <!-- 自定义滑块 -->
        <div class="scale-slider-wrap">
          <input
            type="range"
            :value="fontConfig.scale"
            min="0.5"
            max="1.5"
            step="0.05"
            @input="fontConfig.setFontScale(Number($event.target.value))"
            class="scale-slider"
          />
          <div class="scale-value">{{ (fontConfig.scale * 100).toFixed(0) }}%</div>
        </div>

        <!-- 缩放预览 -->
        <div class="scale-preview">
          <div class="preview-title">标题示例</div>
          <div class="preview-paragraph">这是缩放后的文字。你可以在此看到不同缩放比例下的效果。</div>
        </div>
      </div>

      <!-- 高级选项 -->
      <div class="advanced-section">
        <h4 class="section-title">高级选项</h4>
        <div class="advanced-options">
          <label class="advanced-item">
            <input
              type="checkbox"
              v-model="showAdvancedInfo"
              class="advanced-checkbox"
            />
            <span class="advanced-label">显示字体信息</span>
          </label>
        </div>

        <!-- 当前字体信息 -->
        <div v-if="showAdvancedInfo" class="font-info">
          <div class="info-item">
            <span class="info-label">当前字体族：</span>
            <code class="info-value">{{ fontConfig.family }}</code>
          </div>
          <div class="info-item">
            <span class="info-label">基础大小：</span>
            <code class="info-value">{{ fontConfig.size }}px</code>
          </div>
          <div class="info-item">
            <span class="info-label">缩放因子：</span>
            <code class="info-value">{{ fontConfig.scale }}</code>
          </div>
          <div class="info-item">
            <span class="info-label">有效大小：</span>
            <code class="info-value">{{ fontConfig.getEffectiveFontSize().toFixed(1) }}px</code>
          </div>
        </div>
      </div>

      <!-- 重置按钮 -->
      <div class="reset-section">
        <button class="btn-reset-all" @click="handleResetAll">
          ↻ 重置所有字体设置
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFontConfig } from '@/composables/useFontConfig'

interface Props {
  mode?: 'compact' | 'full'
}

withDefaults(defineProps<Props>(), {
  mode: 'full',
})

const fontConfig = useFontConfig()
const showAdvancedInfo = ref(false)

// 字体选项
const fontOptions = ref([
  {
    value: 'inter',
    label: 'Inter',
    desc: '现代无衬线',
    preview: 'Aa',
  },
  {
    value: 'serif',
    label: 'Serif',
    desc: '经典衬线',
    preview: 'Aa',
  },
  {
    value: 'monospace',
    label: 'Monospace',
    desc: '编程字体',
    preview: 'Aa',
  },
  {
    value: 'system',
    label: 'System',
    desc: '系统字体',
    preview: 'Aa',
  },
])

/**
 * 根据字体族返回CSS字体族字符串
 */
const getFontFamilyCSS = (family: string): string => {
  const families: Record<string, string> = {
    inter: "'Inter', -apple-system, 'Segoe UI', sans-serif",
    serif: "'Georgia', 'Garamond', serif",
    monospace: "'Courier New', 'Monaco', monospace",
    system: "system-ui, -apple-system, 'Segoe UI', sans-serif",
  }
  return families[family] || (families['inter'] ?? "'Inter'")
}

/**
 * 处理重置（compact模式）
 */
const handleReset = () => {
  if (confirm('确认重置字体设置为默认值？')) {
    fontConfig.resetToDefault()
  }
}

/**
 * 处理重置全部（full模式）
 */
const handleResetAll = () => {
  if (confirm('确认重置所有字体设置为默认值？')) {
    fontConfig.resetToDefault()
    showAdvancedInfo.value = false
  }
}
</script>

<style scoped>
/* 全局样式变量 */
:root {
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.15);
  --glass-border-hover: rgba(255, 255, 255, 0.3);
  --neon-primary: #3b82f6;
  --neon-cyan: #06b6d4;
  --text-primary: #ffffff;
  --text-muted: rgba(255, 255, 255, 0.5);
}

.font-control {
  width: 100%;
}

/* ============= COMPACT 模式 ============= */
.font-control.compact .compact-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.compact-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.compact-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.compact-select {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
}

.compact-select:hover {
  border-color: var(--neon-primary);
  background: rgba(59, 130, 246, 0.05);
}

.compact-select:focus {
  outline: none;
  border-color: var(--neon-primary);
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.2);
}

.compact-slider {
  width: 80px;
  height: 6px;
  cursor: pointer;
  accent-color: var(--neon-primary);
}

.size-value {
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 35px;
}

.compact-reset-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
  font-weight: 600;
}

.compact-reset-btn:hover:not(:disabled) {
  color: var(--neon-cyan);
  border-color: var(--neon-cyan);
  background: rgba(6, 182, 212, 0.05);
}

.compact-reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============= FULL 模式 ============= */
.font-control.full {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--neon-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 12px 0;
}

/* 字体族网格 */
.font-family-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.font-card {
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.font-card:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: var(--glass-border-hover);
}

.font-card.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: var(--neon-primary);
  box-shadow: inset 0 0 8px rgba(59, 130, 246, 0.1);
}

.font-preview {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--neon-primary);
}

.font-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: white;
}

.font-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* 字体大小控制 */
.size-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.size-slider {
  flex: 1;
  height: 6px;
  cursor: pointer;
  accent-color: var(--neon-primary);
}

.size-display {
  display: flex;
  align-items: center;
  gap: 4px;
}

.size-input {
  width: 50px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: white;
  text-align: center;
  font-size: 0.85rem;
}

.size-input:focus {
  outline: none;
  border-color: var(--neon-primary);
}

.size-unit {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.size-preview {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  font-size: var(--font-size-base, 16px);
}

.preview-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 8px;
}

.preview-text {
  color: white;
  margin: 0;
  line-height: 1.6;
}

/* 全局缩放 */
.scale-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.scale-btn {
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
  font-weight: 600;
}

.scale-btn:hover {
  border-color: var(--neon-primary);
  background: rgba(59, 130, 246, 0.05);
  color: var(--neon-primary);
}

.scale-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: var(--neon-primary);
  color: var(--neon-primary);
}

.scale-slider-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.scale-slider {
  flex: 1;
  height: 6px;
  cursor: pointer;
  accent-color: var(--neon-primary);
}

.scale-value {
  min-width: 50px;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.scale-preview {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.preview-title {
  font-size: calc(var(--font-size-base, 16px) * var(--font-scale, 1) * 1.5);
  font-weight: 700;
  margin-bottom: 8px;
  color: white;
}

.preview-paragraph {
  font-size: calc(var(--font-size-base, 16px) * var(--font-scale, 1));
  line-height: 1.6;
  color: var(--text-muted);
  margin: 0;
}

/* 高级选项 */
.advanced-section {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
}

.advanced-options {
  margin-bottom: 16px;
}

.advanced-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s;
}

.advanced-item:hover {
  background: rgba(59, 130, 246, 0.05);
}

.advanced-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--neon-primary);
}

.advanced-label {
  font-size: 0.9rem;
  color: white;
  font-weight: 500;
}

.font-info {
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
}

.info-label {
  color: var(--text-muted);
  min-width: 100px;
}

.info-value {
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--neon-cyan);
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

/* 重置按钮 */
.reset-section {
  display: flex;
  justify-content: center;
}

.btn-reset-all {
  padding: 12px 24px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.5);
  border-radius: 10px;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-reset-all:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
}

/* 响应式 */
@media (max-width: 768px) {
  .font-control.full {
    gap: 16px;
  }

  .font-family-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .scale-controls {
    gap: 6px;
  }

  .scale-btn {
    padding: 6px 10px;
    font-size: 0.75rem;
  }
}
</style>

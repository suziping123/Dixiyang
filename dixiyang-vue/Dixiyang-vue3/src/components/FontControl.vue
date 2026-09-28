<template>
  <div class="font-control">
    <!-- 字体族 -->
    <div class="control-block">
      <h4 class="control-title">字体族</h4>
      <p class="control-desc">影响全站正文与标题的字体</p>
      <div class="font-family-grid">
        <div
          v-for="font in fontOptions"
          :key="font.value"
          class="font-card"
          :class="{ active: fontConfig.family.value === font.value }"
          role="radio"
          :tabindex="fontConfig.family.value === font.value ? 0 : -1"
          :aria-checked="fontConfig.family.value === font.value"
          @click="fontConfig.setFontFamily(font.value)"
          @keydown.enter="fontConfig.setFontFamily(font.value)"
          @keydown.space.prevent="fontConfig.setFontFamily(font.value)"
        >
          <div class="font-preview" :style="{ fontFamily: getFontFamilyCSS(font.value) }">
            {{ font.preview }}
          </div>
          <div class="font-label">{{ font.label }}</div>
          <div class="font-desc">{{ font.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 正文字号 -->
    <div class="control-block">
      <h4 class="control-title">正文字号</h4>
      <p class="control-desc">当前 {{ fontConfig.size }}px，段落与列表按此显示</p>
      <div class="slider-row">
        <input
          type="range"
          :value="fontConfig.size"
          min="12"
          max="24"
          step="1"
          aria-label="正文字号"
          class="range"
          @input="(e) => fontConfig.setFontSize(Number((e.target as HTMLInputElement).value))"
        />
        <div class="number-wrap">
          <input
            type="number"
            :value="fontConfig.size"
            min="12"
            max="24"
            aria-label="正文字号（像素）"
            class="number-input"
            @change="(e) => fontConfig.setFontSize(Number((e.target as HTMLInputElement).value))"
          />
          <span class="number-unit">px</span>
        </div>
      </div>
      <div class="preview-box">
        <p class="preview-text">清晨的港口还浸在雾里，第一班渡轮拉响了汽笛。</p>
      </div>
    </div>

    <!-- 全局缩放 -->
    <div class="control-block">
      <h4 class="control-title">全局缩放</h4>
      <p class="control-desc">标题、导航等大号文字的整体缩放，当前 {{ scalePercent }}%</p>
      <div class="scale-presets">
        <button
          v-for="scaleValue in SCALE_PRESETS"
          :key="scaleValue"
          type="button"
          class="preset-btn"
          :class="{ active: isScaleActive(scaleValue) }"
          :aria-pressed="isScaleActive(scaleValue)"
          @click="fontConfig.setFontScale(scaleValue)"
        >
          {{ Math.round(scaleValue * 100) }}%
        </button>
      </div>
    </div>

    <!-- 重置 -->
    <div class="reset-row">
      <button class="btn btn-danger" type="button" @click="handleResetAll">
        <RefreshLeft /> 重置字体设置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RefreshLeft } from '@element-plus/icons-vue'
import { useFontConfig, type FontFamily } from '@/composables/useFontConfig'
import { confirmDelete } from '@/utils/confirm'

const fontConfig = useFontConfig()

/** 缩放预设档位 */
const SCALE_PRESETS = [0.85, 0.9, 1.0, 1.1, 1.2]

const scalePercent = computed(() => Math.round(fontConfig.scale.value * 100))
const isScaleActive = (value: number) => Math.abs(fontConfig.scale.value - value) < 0.001

const fontOptions: { value: FontFamily; label: string; desc: string; preview: string }[] = [
  { value: 'inter', label: 'Inter', desc: '现代无衬线', preview: 'Aa' },
  { value: 'serif', label: 'Serif', desc: '经典衬线', preview: 'Aa' },
  { value: 'monospace', label: 'Mono', desc: '等宽字体', preview: 'Aa' },
  { value: 'system', label: 'System', desc: '跟随系统', preview: 'Aa' },
]

/** 字体族 → CSS 字体栈 */
const getFontFamilyCSS = (family: FontFamily): string => {
  const families: Record<FontFamily, string> = {
    inter: "'Inter', -apple-system, 'Segoe UI', sans-serif",
    serif: "'Georgia', 'Garamond', serif",
    monospace: "'Courier New', 'Monaco', monospace",
    system: "system-ui, -apple-system, 'Segoe UI', sans-serif",
  }
  return families[family]
}

const handleResetAll = async () => {
  const ok = await confirmDelete('重置字体族、字号与缩放为默认值？')
  if (!ok) return
  fontConfig.resetToDefault()
}
</script>

<style scoped>
.font-control {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.control-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.control-desc {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin: 0;
}

/* 字体族卡片 */
.font-family-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 10px;
}

.font-card {
  padding: 14px 10px;
  background: var(--surface-input);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    border-color var(--dur-fast) var(--ease-out),
    background var(--dur-fast) var(--ease-out);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.font-card:hover {
  border-color: var(--surface-glass-border-hover);
  background: var(--accent-soft);
}

.font-card:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 1px;
}

.font-card.active {
  border-color: var(--accent-primary);
  background: var(--accent-soft-strong);
}

.font-preview {
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--text-primary);
}

.font-card.active .font-preview {
  color: var(--accent-primary);
}

.font-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.font-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* 滑块 */
.slider-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.range {
  flex: 1;
  accent-color: var(--accent-primary);
  cursor: pointer;
  min-width: 0;
}

.range:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 4px;
}

.number-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.number-input {
  width: 64px;
  padding: 8px 10px;
  background: var(--surface-input);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  text-align: center;
  font-size: 0.875rem;
  font-family: inherit;
  transition: border-color var(--dur-fast) var(--ease-out);
}

.number-input:hover {
  border-color: var(--surface-glass-border-hover);
}

.number-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.number-input:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 1px;
}

.number-unit {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.preview-box {
  padding: 14px 16px;
  background: var(--surface-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.preview-text {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* 缩放预设 */
.scale-presets {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 8px 16px;
  background: var(--surface-input);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: inherit;
  transition:
    border-color var(--dur-fast) var(--ease-out),
    background var(--dur-fast) var(--ease-out),
    color var(--dur-fast) var(--ease-out);
}

.preset-btn:hover {
  border-color: var(--surface-glass-border-hover);
  color: var(--text-primary);
}

.preset-btn:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

.preset-btn.active {
  background: var(--accent-soft-strong);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 重置 */
.reset-row {
  display: flex;
  justify-content: flex-start;
  padding-top: 4px;
}

@media (max-width: 768px) {
  .font-family-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .slider-row {
    flex-wrap: wrap;
  }

  .range {
    flex-basis: 100%;
  }
}
</style>

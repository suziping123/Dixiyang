<script setup lang="ts">
/**
 * 章节索引（左缘竖排 tablist）：点击切换面板；滚轮/方向键由 useLandingMotion 驱动
 */
export interface LandingPanelMeta {
  id: string
  label: string
  en: string
}

defineProps<{
  panels: LandingPanelMeta[]
  active: number
}>()

const emit = defineEmits<{ select: [index: number] }>()
</script>

<template>
  <nav class="ld-index" aria-label="页面章节">
    <div class="ld-index__list" role="tablist" aria-orientation="vertical">
      <button
        v-for="(p, i) in panels"
        :id="`tab-${p.id}`"
        :key="p.id"
        class="ld-index__btn"
        type="button"
        role="tab"
        :aria-selected="active === i"
        :aria-controls="`panel-${p.id}`"
        :tabindex="active === i ? 0 : -1"
        @click="emit('select', i)"
      >
        <span class="ld-index__num">{{ String(i).padStart(2, '0') }}</span>
        <span class="ld-index__label">
          {{ p.label }}
          <span class="en">{{ p.en }}</span>
        </span>
      </button>
    </div>
    <p class="ld-index__hint">Wheel / ↑↓ 切换</p>
  </nav>
</template>

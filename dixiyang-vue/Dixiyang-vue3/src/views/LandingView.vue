<script setup lang="ts">
/**
 * 落地页（对外介绍页，路由 /）—— 单屏 instrument
 * 结构：顶栏 + 左缘章节索引（tablist）+ 舞台 6 面板；切换即签名动效
 * 移动端降级：索引退场，面板纵向流（见 landing-base.css @media）
 */
import { ref } from 'vue'
import LandingNav from '@/components/landing/LandingNav.vue'
import LandingIndex, { type LandingPanelMeta } from '@/components/landing/LandingIndex.vue'
import HeroPanel from '@/components/landing/HeroPanel.vue'
import ProblemPanel from '@/components/landing/ProblemPanel.vue'
import CapabilitiesPanel from '@/components/landing/CapabilitiesPanel.vue'
import AssistantPanel from '@/components/landing/AssistantPanel.vue'
import ProcessPanel from '@/components/landing/ProcessPanel.vue'
import StartPanel from '@/components/landing/StartPanel.vue'
import { useLandingMotion } from '@/composables/useLandingMotion'

const panels: LandingPanelMeta[] = [
  { id: 'hero', label: '首页', en: 'Cover' },
  { id: 'problem', label: '问题', en: 'Problem' },
  { id: 'capabilities', label: '能力', en: 'Features' },
  { id: 'assistant', label: '助手', en: 'Assistant' },
  { id: 'process', label: '流程', en: 'Process' },
  { id: 'start', label: '开始', en: 'Start' },
]

const root = ref<HTMLElement | null>(null)
const active = ref(0)
useLandingMotion(root, active, panels.length)
</script>

<template>
  <div ref="root" class="ld-page">
    <a class="vh" href="#main">跳到主要内容</a>
    <LandingNav />
    <LandingIndex :panels="panels" :active="active" @select="active = $event" />

    <main id="main" class="ld-stage">
      <HeroPanel :class="{ 'is-active': active === 0 }" />
      <ProblemPanel :class="{ 'is-active': active === 1 }" />
      <CapabilitiesPanel :class="{ 'is-active': active === 2 }" />
      <AssistantPanel :class="{ 'is-active': active === 3 }" :is-active="active === 3" />
      <ProcessPanel :class="{ 'is-active': active === 4 }" />
      <StartPanel :class="{ 'is-active': active === 5 }" />
    </main>
  </div>
</template>

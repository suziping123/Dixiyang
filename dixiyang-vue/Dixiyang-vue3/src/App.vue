<template>
  <RouterView />
  <!-- 全局导航（悬浮球/左缘呼出）：仅带 meta.showNav 的主页渲染（5 个主页），其余页面一律隐藏 -->
  <FloatingNav v-if="showNav" />
  <!-- 全局便签悬浮层：便签钉在哪个路由就只在哪个路由显示 -->
  <StickyNoteLayer />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import FloatingNav from '@/components/FloatingNav.vue'
import StickyNoteLayer from '@/components/sticky/StickyNoteLayer.vue'
import { useFontConfig } from '@/composables/useFontConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

const route = useRoute()
// 导航白名单：仅路由声明 showNav: true 时渲染（登录/落地/404/编辑器等一律无导航）
const showNav = computed(() => route.meta.showNav === true)

useFontConfig()

const tc = useTextColorCustomizer()
tc.loadFromStorage()
tc.applyCSSVariables()
</script>

<template>
  <RouterView />
  <!-- 全局导航（右侧 FAB 悬浮球） -->
  <FloatingNav />
  <!-- 全局便签悬浮层：便签钉在哪个路由就只在哪个路由显示 -->
  <StickyNoteLayer />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import FloatingNav from '@/components/FloatingNav.vue'
import StickyNoteLayer from '@/components/sticky/StickyNoteLayer.vue'
import { useFontConfig } from '@/composables/useFontConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

useFontConfig()

const tc = useTextColorCustomizer()
tc.loadFromStorage()
tc.applyCSSVariables()
</script>

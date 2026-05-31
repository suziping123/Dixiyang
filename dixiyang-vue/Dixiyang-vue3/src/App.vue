<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import { useFontConfig } from '@/composables/useFontConfig'

// 应用启动时初始化全局配置
const textColorCustomizer = useTextColorCustomizer()
const bgConfig = useBackgroundConfig()
const fontConfig = useFontConfig()

onMounted(() => {
  // 从 localStorage 加载并应用背景配置
  bgConfig.loadFromStorage()
  bgConfig.applyColorTheme()
  bgConfig.applyBackgroundPreset()

  // 从 localStorage 加载并应用字体配置
  fontConfig.loadFromStorage()
  fontConfig.applyFontSettings()

  // 从 localStorage 加载并应用文字颜色配置
  textColorCustomizer.loadFromStorage()
  textColorCustomizer.applyCSSVariables()
})
</script>

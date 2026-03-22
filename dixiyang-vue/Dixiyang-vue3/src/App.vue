<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

// 应用启动时初始化全局文字颜色系统
const textColorCustomizer = useTextColorCustomizer()

onMounted(async () => {
  // 从后端加载用户的颜色配置
  await textColorCustomizer.loadFromBackend()
  // 应用颜色到 CSS 变量
  textColorCustomizer.applyCSSVariables()
})
</script>

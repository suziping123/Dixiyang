<template>
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import { useFontConfig } from '@/composables/useFontConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

useBackgroundConfig()
useFontConfig()

const textColorCustomizer = useTextColorCustomizer()
textColorCustomizer.loadFromStorage()
textColorCustomizer.applyCSSVariables()
</script>

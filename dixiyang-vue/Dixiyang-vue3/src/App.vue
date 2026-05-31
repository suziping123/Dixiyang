<template>
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useFontConfig } from '@/composables/useFontConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'

useFontConfig()

const tc = useTextColorCustomizer()
tc.loadFromStorage()
tc.applyCSSVariables()
</script>

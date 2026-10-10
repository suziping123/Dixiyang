<template>
  <div ref="el" class="echart-box" :style="{ height }"></div>
</template>

<script setup lang="ts">
/** ECharts 暗色封装：主题注册一次、自动 resize、卸载 dispose。数据变由父组件 watch 后 setOption */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsCoreOption } from 'echarts/core'

echarts.use([BarChart, LineChart, PieChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

/** 项目暗色风格：青主色 + 紫辅色，轴线/文字适配 --surface-card 深底 */
const DARK_THEME = {
  color: ['#4dd0e1', '#b388ff', '#81c784', '#ffb74d', '#f06292', '#64b5f6', '#e57373'],
  backgroundColor: 'transparent',
  textStyle: { color: '#aab2c8' },
  legend: { textStyle: { color: '#c3cbdd' }, top: 0 },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#3a4157' } },
    axisLabel: { color: '#8b94ab' },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisLabel: { color: '#8b94ab' },
    splitLine: { lineStyle: { color: '#262c3d' } },
  },
}
echarts.registerTheme('dixi-dark', DARK_THEME)

const props = withDefaults(defineProps<{ option: EChartsCoreOption; height?: string }>(), { height: '260px' })

const el = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const render = () => {
  if (!chart) return
  chart.setOption(props.option, true)
  chart.resize()
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value, 'dixi-dark')
  render()
  window.addEventListener('resize', onResize)
})

const onResize = () => chart?.resize()

watch(() => props.option, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.echart-box { width: 100%; }
</style>

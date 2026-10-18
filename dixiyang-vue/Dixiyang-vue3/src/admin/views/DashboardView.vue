<template>
  <div class="dash-page">
    <header class="page-head">
      <div>
        <h1 class="page-title">仪表盘</h1>
        <p class="page-sub">站点总览 · 用户 / 内容 / 会话与发帖趋势</p>
      </div>
    </header>

    <section class="stat-grid" v-loading="statsLoading">
      <div
        v-for="(c, i) in statCards"
        :key="c.label"
        class="c-card stat-card rise-in"
        :style="{ '--i': i }"
      >
        <span class="stat-num tnum">{{ c.value }}</span>
        <span class="stat-label">{{ c.label }}</span>
      </div>
    </section>

    <div class="section-rule rise-in" :style="{ '--i': 4 }">
      <strong>内容概况</strong>
      <span class="sr-line"></span>
      <i v-if="stats" class="sr-count">分区 {{ stats.postCategories.length }}</i>
    </div>

    <section class="cat-row rise-in" :style="{ '--i': 5 }" v-if="stats">
      <span class="cat-chip" v-for="c in stats.postCategories" :key="c.category">
        {{ catLabel(c.category) }}<b class="tnum">{{ c.count }}</b>
      </span>
    </section>

    <section class="charts-row" v-if="stats">
      <div class="c-card chart-card rise-in" :style="{ '--i': 6 }">
        <h3>近 7 天发帖趋势</h3>
        <EChart :option="trendOption" height="240px" />
      </div>
      <div class="c-card chart-card rise-in" :style="{ '--i': 7 }">
        <h3>帖子分区占比</h3>
        <EChart :option="catOption" height="240px" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import EChart from '@/components/EChart.vue'
import { getAdminStats } from '../api/admin'
import type { AdminStats } from '../api/admin'
import { unwrap } from '../api/util'

defineOptions({ name: 'AdminDashboard' })

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const stats = ref<AdminStats | null>(null)
const statsLoading = ref(false)

// 大数字锚点：数据到达后短促计数动画（reduced-motion 直接落终值）
const shown = ref<[number, number, number, number]>([0, 0, 0, 0])
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

function animateNumbers(target: [number, number, number, number], duration = 700) {
  if (prefersReduced) {
    shown.value = [...target]
    return
  }
  const from = shown.value.slice() as [number, number, number, number]
  const start = performance.now()
  const tick = (now: number) => {
    const t = Math.min(1, (now - start) / duration)
    const eased = 1 - Math.pow(1 - t, 3)
    shown.value = target.map((v, i) => Math.round((from[i] ?? 0) + (v - (from[i] ?? 0)) * eased)) as [
      number, number, number, number,
    ]
    if (t < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

watch(
  () => stats.value,
  (s) => {
    if (!s) return
    animateNumbers([s.totals.users, s.totals.novels, s.totals.posts, s.totals.sessions])
  },
)

const statCards = computed(() => {
  const s = stats.value
  return [
    { label: '用户', value: s ? shown.value[0] : '-' },
    { label: '小说', value: s ? shown.value[1] : '-' },
    { label: '广场帖子', value: s ? shown.value[2] : '-' },
    { label: '对话会话', value: s ? shown.value[3] : '-' },
  ]
})

// 图表 option：近7天发帖趋势（柱）+ 分区占比（环形）
const trendOption = computed(() => {
  const list = stats.value?.postTrend ?? []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 16, top: 24, bottom: 28 },
    xAxis: { type: 'category', data: list.map((d) => d.date.slice(5)) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: list.map((d) => d.count), barWidth: '46%', itemStyle: { borderRadius: [4, 4, 0, 0] } }],
  }
})
const catOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['42%', '68%'],
    center: ['50%', '44%'],
    label: { color: '#c3cbdd' },
    data: (stats.value?.postCategories ?? []).map((c) => ({ name: catLabel(c.category), value: c.count })),
  }],
}))

const loadStats = async () => {
  statsLoading.value = true
  try {
    stats.value = unwrap<AdminStats>(await getAdminStats())
  } finally {
    statsLoading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.stat-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 22px 18px;
}
.stat-num {
  /* 大数字为全页锚点（与 /home 的表格数字同语言） */
  font-size: clamp(1.9rem, 3.4vw, 2.6rem);
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text-primary);
  line-height: 1.05;
}
.stat-label { font-size: 0.72rem; letter-spacing: 3px; color: var(--text-muted); }

.cat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.cat-chip {
  background: var(--glass-bg-strong);
  border: 1px solid var(--surface-glass-border);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}
.cat-chip b { margin-left: 6px; color: var(--accent-cyan); font-weight: 700; }

.charts-row { display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; }
.chart-card { padding: 16px 18px; }
.chart-card h3 {
  margin: 0 0 6px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .stat-num { font-size: 1.9rem; }
  .charts-row { grid-template-columns: 1fr; }
}
</style>

<template>
  <div class="dash-page">
    <header class="page-head">
      <h1>仪表盘</h1>
      <span class="head-sub">站点总览 · 发帖趋势与分区占比</span>
    </header>

    <section class="stat-cards" v-loading="statsLoading">
      <div v-for="c in statCards" :key="c.label" class="stat-card">
        <span class="stat-num">{{ c.value }}</span>
        <span class="stat-label">{{ c.label }}</span>
      </div>
    </section>

    <section class="cat-row" v-if="stats">
      <span class="cat-chip" v-for="c in stats.postCategories" :key="c.category">
        {{ catLabel(c.category) }}<i>{{ c.count }}</i>
      </span>
    </section>

    <section class="charts-row" v-if="stats">
      <div class="chart-card">
        <h3>近 7 天发帖趋势</h3>
        <EChart :option="trendOption" height="240px" />
      </div>
      <div class="chart-card">
        <h3>帖子分区占比</h3>
        <EChart :option="catOption" height="240px" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import EChart from '@/components/EChart.vue'
import { getAdminStats } from '../api/admin'
import type { AdminStats } from '../api/admin'
import { unwrap } from '../api/util'

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const stats = ref<AdminStats | null>(null)
const statsLoading = ref(false)

const statCards = computed(() => [
  { label: '用户', value: stats.value?.totals.users ?? '-' },
  { label: '小说', value: stats.value?.totals.novels ?? '-' },
  { label: '广场帖子', value: stats.value?.totals.posts ?? '-' },
  { label: '对话会话', value: stats.value?.totals.sessions ?? '-' },
])

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
.page-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 22px;
}
.page-head h1 { font-size: 24px; color: var(--c-text); margin: 0; }
.head-sub { font-size: 13px; color: var(--c-text-3); }

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}
.stat-card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stat-num { font-size: 30px; font-weight: 700; color: var(--c-cyan); }
.stat-label { font-size: 13px; color: var(--c-text-2); }

.cat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 22px; }
.cat-chip {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--c-text-2);
}
.cat-chip i { font-style: normal; margin-left: 6px; color: var(--c-accent); font-weight: 600; }

.charts-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 14px;
}
.chart-card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: 16px 18px;
}
.chart-card h3 { margin: 0 0 6px; font-size: 14px; font-weight: 600; color: var(--c-text-2); }

@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
}
</style>

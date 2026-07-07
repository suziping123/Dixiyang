<template>
  <div class="rag-page">
    <div class="bg-gradient-animation"></div>
    <FloatingNav />
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">RAG 知识库</h1>
        <p class="page-subtitle">查看和管理向量数据库中的知识文档</p>
      </div>
    </header>

    <div class="kb-container">
      <section class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon doc-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13zM6 20V4h5v7h7v9H6z"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_documents ?? '—' }}</span>
            <span class="stat-label">文档总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon db-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3C7.58 3 4 4.79 4 7v10c0 2.21 3.58 4 8 4s8-1.79 8-4V7c0-2.21-3.58-4-8-4zm0 2c3.87 0 6 1.5 6 2s-2.13 2-6 2-6-1.5-6-2 2.13-2 6-2zM6 17v-2.42c1.23.81 3.3 1.42 6 1.42s4.77-.61 6-1.42V17c0 .5-2.13 2-6 2s-6-1.5-6-2zm0-5v-2.42c1.23.81 3.3 1.42 6 1.42s4.77-.61 6-1.42V12c0 .5-2.13 2-6 2s-6-1.5-6-2z"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ sourceKeys.length }}</span>
            <span class="stat-label">来源类型</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon model-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM9 8h2v8H9zm4 0h2v8h-2z"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.embedding_model?.split('/').pop() || '—' }}</span>
            <span class="stat-label">嵌入模型</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon dim-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12zM10 9h8v2h-8zm0 3h4v2h-4zm0-6h8v2h-8z"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.embedding_dimension ?? '—' }}</span>
            <span class="stat-label">向量维度</span>
          </div>
        </div>
      </section>

      <div class="charts-row" v-if="hasCharts">
        <section class="chart-card" v-if="sourceKeys.length">
          <h3 class="chart-title">按来源分布</h3>
          <div class="bar-chart">
            <div v-for="k in sourceKeys" :key="k" class="bar-row">
              <span class="bar-label" :title="k">{{ k }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: barWidth(k, sourceDist) }"></div>
              </div>
              <span class="bar-count">{{ sourceDist[k] }}</span>
            </div>
          </div>
        </section>
        <section class="chart-card" v-if="catKeys.length">
          <h3 class="chart-title">按分类分布</h3>
          <div class="bar-chart">
            <div v-for="k in catKeys" :key="k" class="bar-row">
              <span class="bar-label" :title="k">{{ k }}</span>
              <div class="bar-track">
                <div class="bar-fill cat-fill" :style="{ width: barWidth(k, catDist) }"></div>
              </div>
              <span class="bar-count">{{ catDist[k] }}</span>
            </div>
          </div>
        </section>
        <section class="chart-card" v-if="bookKeys.length">
          <h3 class="chart-title">按书籍/来源分布 (Top 20)</h3>
          <div class="bar-chart">
            <div v-for="k in bookKeys" :key="k" class="bar-row">
              <span class="bar-label" :title="k">{{ k }}</span>
              <div class="bar-track">
                <div class="bar-fill book-fill" :style="{ width: barWidth(k, bookDist) }"></div>
              </div>
              <span class="bar-count">{{ bookDist[k] }}</span>
            </div>
          </div>
        </section>
      </div>

      <section class="search-section">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <input v-model="searchQuery" placeholder="搜索知识库内容..." @keyup.enter="handleSearch" />
          <select v-model="searchSourceFilter" class="filter-select">
            <option value="">全部来源</option>
            <option v-for="s in sourceKeys" :key="s" :value="s">{{ s }}</option>
          </select>
          <button class="search-btn" @click="handleSearch">搜索</button>
        </div>
        <div class="search-meta" v-if="searchResult">
          <span>查询：{{ searchResult.query }}</span>
          <span>找到 {{ (searchResult.total ?? searchResult.results?.length) || 0 }} 条结果</span>
        </div>
      </section>

      <section class="docs-section">
        <div class="section-tabs">
          <button :class="{ active: activeTab === 'docs' }" @click="switchTab('docs')">文档列表</button>
          <button :class="{ active: activeTab === 'search' }" @click="switchTab('search')" v-if="searchResult">搜索结果</button>
        </div>

        <div v-if="activeTab === 'docs'">
          <div class="doc-filter-bar">
            <select v-model="docSourceFilter" class="filter-select" @change="loadDocuments(1)">
              <option value="">全部来源</option>
              <option v-for="s in sourceKeys" :key="s" :value="s">{{ s }}</option>
            </select>
            <span class="doc-count" v-if="totalDocs > 0">共 {{ totalDocs }} 条</span>
          </div>
          <div class="docs-list">
            <div v-for="(doc, i) in docs" :key="doc.id || i" class="doc-card">
              <div class="doc-header">
                <span class="doc-id">#{{ (docPage - 1) * pageSize + i + 1 }}</span>
                <span class="doc-source-tag" v-if="doc.metadata?.source" :class="'src-' + doc.metadata.source">{{ doc.metadata.source }}</span>
                <span class="doc-category-tag" v-if="doc.metadata?.category">{{ doc.metadata.category }}</span>
                <span class="doc-chunk" v-if="doc.metadata?.chunk_index">Chunk {{ doc.metadata.chunk_index }}</span>
              </div>
              <p class="doc-content">{{ doc.content }}</p>
            </div>
            <div v-if="docs.length === 0" class="empty-state">
              <p>暂无文档数据</p>
            </div>
            <div class="pagination" v-if="totalDocs > pageSize">
              <button :disabled="docPage <= 1" @click="changePage(docPage - 1)">上一页</button>
              <span>第 {{ docPage }} / {{ totalPages }} 页</span>
              <button :disabled="docPage >= totalPages" @click="changePage(docPage + 1)">下一页</button>
            </div>
          </div>
        </div>

        <div v-else class="search-results">
          <div v-for="(item, i) in searchResult?.results" :key="item.id || i" class="doc-card result-card">
            <div class="doc-header">
              <span class="score-badge">{{ ((item.score ?? 0) * 100).toFixed(1) }}%</span>
              <span class="doc-source-tag" v-if="item.metadata?.source" :class="'src-' + item.metadata.source">{{ item.metadata.source }}</span>
              <span class="doc-category-tag" v-if="item.metadata?.category">{{ item.metadata.category }}</span>
              <span class="doc-book-title" v-if="item.metadata?.book_title">{{ item.metadata.book_title }}</span>
            </div>
            <p class="doc-content">{{ item.content }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import FloatingNav from '@/components/FloatingNav.vue'
import { getRagStats, getRagDocuments, searchRag } from '@/api/ragApi'
import type { RagStats, RagDocPage, RagSearchResult } from '@/api/ragApi'

const stats = ref<RagStats>({
  total_collections: 0,
  embedding_model: '',
  embedding_dimension: 0,
  collection_details: [],
  connected: false,
})

const docs = ref<{ id: string; content: string; metadata: Record<string, unknown> | null }[]>([])
const docPage = ref(1)
const pageSize = ref(20)
const totalDocs = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(totalDocs.value / pageSize.value)))

const searchQuery = ref('')
const searchResult = ref<RagSearchResult | null>(null)
const activeTab = ref<'docs' | 'search'>('docs')
const docSourceFilter = ref('')
const searchSourceFilter = ref('')

const sourceDist = computed(() => stats.value.source_distribution ?? {})
const catDist = computed(() => stats.value.category_distribution ?? {})
const bookDist = computed(() => stats.value.book_distribution ?? {})
const sourceKeys = computed(() => Object.keys(sourceDist.value))
const catKeys = computed(() => Object.keys(catDist.value))
const bookKeys = computed(() => Object.keys(bookDist.value).slice(0, 20))
const hasCharts = computed(() => sourceKeys.value.length > 0 || catKeys.value.length > 0 || bookKeys.value.length > 0)

function barWidth(key: string, dist: Record<string, number>) {
  const vals = Object.values(dist)
  const max = Math.max(...vals, 1)
  return Math.max(((dist[key] ?? 0) / max) * 100, 2) + '%'
}

function switchTab(tab: 'docs' | 'search') {
  activeTab.value = tab
}

async function loadStats() {
  try {
    const res = await getRagStats()
    stats.value = res.data
  } catch (e) {
    console.error('加载 RAG 统计失败', e)
  }
}

async function loadDocuments(page: number) {
  try {
    const res = await getRagDocuments(page, pageSize.value, docSourceFilter.value || undefined)
    const data = res.data as RagDocPage
    docs.value = (data.ids || []).map((id: string, i: number) => ({
      id,
      content: data.documents?.[i] || '',
      metadata: data.metadatas?.[i] || null,
    }))
    totalDocs.value = data.total ?? stats.value.total_documents ?? 0
    docPage.value = page
  } catch (e) {
    console.error('加载文档失败', e)
  }
}

function changePage(page: number) {
  if (page < 1) return
  loadDocuments(page)
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  try {
    const res = await searchRag(
      searchQuery.value,
      10,
      searchSourceFilter.value || undefined
    )
    searchResult.value = res.data
    activeTab.value = 'search'
  } catch (e) {
    console.error('搜索失败', e)
  }
}

onMounted(() => {
  loadStats()
  loadDocuments(1)
})
</script>

<style scoped>
.rag-page {
  min-height: 100vh;
  position: relative;
  padding-bottom: 40px;
}
.bg-gradient-animation {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--surface-page, #0a0a1a);
  z-index: -1;
}
.page-header {
  padding: 40px 48px 20px;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-on-page, #e0e0e0);
  margin: 0 0 8px;
}
.page-subtitle {
  color: var(--text-secondary, #8892b0);
  margin: 0;
  font-size: 0.95rem;
}
.kb-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.stat-card {
  background: var(--surface-card, rgba(20, 25, 45, 0.85));
  backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  padding: 10px; flex-shrink: 0;
}
.stat-icon svg { width: 28px; height: 28px; }
.doc-icon { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.db-icon { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.model-icon { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.dim-icon { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 1.35rem; font-weight: 700; color: var(--text-on-card, #e0e0e0); }
.stat-label { font-size: 0.8rem; color: var(--text-secondary, #8892b0); }

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.chart-card {
  background: var(--surface-card, rgba(20, 25, 45, 0.85));
  backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  padding: 20px;
}
.chart-title {
  color: #a78bfa;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 12px;
}
.bar-chart { display: flex; flex-direction: column; gap: 4px; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
}
.bar-label {
  width: 120px;
  text-align: right;
  color: var(--text-secondary, #8892b0);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}
.bar-track {
  flex: 1;
  height: 18px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6c5ce7, #a78bfa);
  border-radius: 4px;
  min-width: 2px;
  transition: width 0.3s;
}
.cat-fill {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}
.book-fill {
  background: linear-gradient(90deg, #10b981, #34d399);
}
.bar-count {
  width: 50px;
  color: var(--text-muted, #5a6a8a);
  flex-shrink: 0;
  text-align: right;
}

.search-section {
  background: var(--surface-card, rgba(20, 25, 45, 0.85));
  backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  padding: 20px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface-input, rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 4px 4px 4px 16px;
}
.search-icon {
  width: 20px; height: 20px;
  color: var(--text-muted, #5a6a8a);
  flex-shrink: 0;
}
.search-box input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-on-input, #e0e0e0);
  font-size: 0.95rem;
  padding: 10px 0;
}
.search-box input::placeholder { color: var(--text-muted, #5a6a8a); }
.filter-select {
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-on-card, #e0e0e0);
  font-size: 0.82rem;
  cursor: pointer;
  outline: none;
}
.filter-select option { background: #1a1b2e; }
.search-btn {
  padding: 8px 24px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: opacity 0.2s;
}
.search-btn:hover { opacity: 0.85; }
.search-meta {
  margin-top: 12px;
  display: flex;
  gap: 24px;
  font-size: 0.85rem;
  color: var(--text-secondary, #8892b0);
}

.docs-section {
  background: var(--surface-card, rgba(20, 25, 45, 0.85));
  backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  padding: 20px;
}
.section-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 12px;
}
.section-tabs button {
  background: transparent;
  border: none;
  color: var(--text-muted, #5a6a8a);
  padding: 6px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.section-tabs button.active {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}
.section-tabs button:hover:not(.active) {
  color: var(--text-secondary, #8892b0);
  background: rgba(255, 255, 255, 0.05);
}

.doc-filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.doc-count {
  font-size: 0.82rem;
  color: var(--text-muted, #5a6a8a);
}

.docs-list, .search-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.doc-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 16px;
  transition: border-color 0.2s;
}
.doc-card:hover { border-color: rgba(59, 130, 246, 0.3); }
.result-card { border-left: 3px solid rgba(59, 130, 246, 0.5); }
.doc-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 0.78rem;
  flex-wrap: wrap;
}
.doc-id {
  color: var(--text-muted, #5a6a8a);
  font-family: monospace;
}
.doc-source-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.src-book { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.src-law { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.src-qa { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.src-cars { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.src-company { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
.src-text { background: rgba(255, 255, 255, 0.08); color: #ccc; }
.doc-category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary, #8892b0);
}
.doc-book-title {
  color: var(--text-muted, #5a6a8a);
  font-style: italic;
}
.doc-chunk {
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}
.score-badge {
  color: white;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  padding: 2px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.82rem;
}
.doc-content {
  color: var(--text-secondary, #8892b0);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.empty-state { padding: 40px; text-align: center; color: var(--text-muted, #5a6a8a); }
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.pagination button {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text-on-card, #e0e0e0);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.pagination button:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { color: var(--text-secondary, #8892b0); font-size: 0.85rem; }

@media (max-width: 768px) {
  .page-header { padding: 20px; }
  .kb-container { padding: 0 12px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
}
</style>

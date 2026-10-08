<template>
  <div class="engine-container">
    <FloatingNav />

    <main class="main-stage" :class="{ 'blur-bg': showRag }">
      <div class="topbar" :class="{ stuck: topbarStuck }">
        <div class="brand">
          <img src="../assets/logoByGpt.png" alt="Dixiyang Logo" class="brand-logo">
          <h1 class="brand-name">DIXIYANG <span class="brand-engine">ENGINE</span></h1>
        </div>
        <BackgroundControl mode="compact" />
      </div>

      <header class="stage-header">
        <div class="hero">
          <div class="hero-left">
            <p class="eyebrow">创作台 WORKSPACE</p>
            <h2 class="hero-title">我的创作宇宙</h2>
            <p class="subtitle">欢迎回来，<span class="user-name">{{ userStore.nickname || '创作者' }}</span>。当前有 <span class="highlight">{{ total }}</span> 个宇宙正在运行。</p>
          </div>
          <div class="hero-stats">
            <div class="stat-hero">
              <b class="stat-hero-num">{{ total }}</b>
              <span class="stat-hero-label">宇宙</span>
            </div>
            <div class="stat-hero">
              <b class="stat-hero-num">{{ charTotal }}</b>
              <span class="stat-hero-label">角色</span>
            </div>
            <div class="stat-hero">
              <b class="stat-hero-num">{{ nodeTotal }}</b>
              <span class="stat-hero-label">节点</span>
            </div>
          </div>
        </div>
      </header>

      <div class="galaxy-section">
        <div class="section-head">
          <h2 class="section-title">全部作品</h2>
          <span class="section-rule"></span>
          <span class="section-count">{{ total }}</span>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载你的创作宇宙...</p>
        </div>

        <template v-else>
          <div v-if="novels.length === 0" class="empty-hint">
            <svg viewBox="0 0 100 100" class="empty-icon"><circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="2" opacity="0.5"/><path d="M50 30 L60 50 L50 70 L40 50 Z" fill="currentColor" opacity="0.5"/></svg>
            <p>暂无创作宇宙，开始构建你的第一个宇宙吧</p>
          </div>

          <div class="galaxy-grid" :class="{ 'single-card': novels.length === 0 }">
            <div v-for="novel in novels" :key="novel.id" class="novel-card-wrapper" @mouseenter="hoveredCard = novel.id" @mouseleave="hoveredCard = null">
              <div class="glass-card novel-card" :class="{ flipped: flippedCards.has(novel.id) }" @click="handleCardClick(novel, $event)" title="点击查看宇宙概览，快速双击翻转">

                <!-- 封面层 -->
                <div class="novel-cover-wrapper">
                  <button class="novel-cover">
                    <img :src="resolveNovelCover(novel.cover_url)"
                      alt="封面"
                      @error="(e: Event) => { (e.target as HTMLImageElement).src = defaultCover }"
                    >
                  </button>
                </div>

                <!-- 内容层 -->
                <div class="card-content">
                  <div class="card-header">
                    <span class="pen-name">{{ novel.pen_name || '匿名作者' }}</span>
                    <span class="novel-id">#{{ novel.id }}</span>
                  </div>
                  <h2 class="novel-title">{{ novel.title }}</h2>
                  <p class="description">{{ novel.description || '暂无描述' }}</p>
                  <div class="card-stats" :class="{ expanded: hoveredCard === novel.id }">
                    <div class="stat">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                      <span>角色</span>
                      <b class="stat-value">{{ novel.char_count || 0 }}</b>
                    </div>
                    <div class="stat">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M4 6h16V4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16v-2H4V6z"/></svg>
                      <span>节点</span>
                      <b class="stat-value">{{ novel.node_count || 0 }}</b>
                    </div>
                    <div class="stat" v-if="hoveredCard === novel.id">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-2.16-2.66c-.44-.53-1.25-.53-1.69 0-.44.54-.44 1.39 0 1.93l3 3.68c.44.53 1.25.53 1.69 0L21.27 9c.44-.54.44-1.39 0-1.93-.44-.54-1.25-.54-1.69 0l-6.62 8.22z"/></svg>
                      <span>关联</span>
                      <b class="stat-value">{{ novel.relation_count || 0 }}</b>
                    </div>
                  </div>
                  <div class="card-actions-row">
                    <button class="action-btn-sm character-btn" @click.stop="openCharacterManager(novel)" title="角色管理">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                    </button>
                    <button class="action-btn-sm timeline-btn" @click.stop="openTimeline(novel)" title="时间线管理">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
                    </button>
                    <button class="action-btn-sm delete-btn" @click.stop="deleteNovel(novel)" title="删除小说">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    </button>
                  </div>
                  <button class="enter-btn" @click.stop="openNovel(novel)" title="进入创作">
                    <span class="btn-text">进入创作</span>
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M5 13l4 4L19 7"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <CreateCard @create-success="() => fetchNovels()" />
          </div>

          <!-- 分页：还有未加载的宇宙时提供「加载更多」+ 触底自动加载哨兵 -->
          <div v-if="hasMore" class="load-more-row">
            <button
              class="load-more-btn"
              :class="{ 'is-error': loadError }"
              type="button"
              :disabled="loadingMore"
              @click="loadMore"
            >
              {{ loadMoreLabel }}
            </button>
            <span ref="sentinel" class="load-sentinel" aria-hidden="true"></span>
          </div>
        </template>


      </div>
    </main>

    <div class="rag-drawer" :class="{ open: showRag }">
      <div class="drawer-header">
        <h3>宇宙概览</h3>
        <button class="close-btn" @click="showRag = false"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/></svg></button>
      </div>
      <div class="drawer-content">
        <div v-if="ragLoading" class="rag-loading">
          <div class="rag-spinner"></div>
          <p>加载相关内容中...</p>
        </div>
        <div v-else-if="selectedNovel" class="rag-info">
          <h4>{{ selectedNovel.title }}</h4>
          <div class="info-section">
            <strong>📍 相关角色：</strong>
            <p>{{ selectedNovel.char_count || 0 }} 个角色已录入</p>
          </div>
          <div class="info-section">
            <strong>⏳ 历史线索：</strong>
            <p>{{ selectedNovel.node_count || 0 }} 个节点已记录</p>
          </div>
          <div class="info-section">
            <strong>🔗 关联世界：</strong>
            <p>{{ selectedNovel.relation_count || 0 }} 个相关宇宙</p>
          </div>

          <button class="enter-btn rag-enter-btn" @click="goToRagAssistant">
            <span class="btn-text">进入 RAG 智能助手</span>
            <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M5 13l4 4L19 7"/></svg>
          </button>
        </div>
        <div v-else class="empty-state-drawer">
          <svg viewBox="0 0 24 24" class="empty-icon-drawer"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <p>选择一个宇宙开始分析</p>
        </div>
      </div>
    </div>

    <div class="knowledge-sphere" :class="{ active: hoveredCard }" @click="showKnowledgeGraph">
      <svg class="sphere-visual" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" opacity="0.1"/>
        <circle cx="50" cy="50" r="35" fill="none" stroke="currentColor" opacity="0.15"/>
        <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" opacity="0.2"/>
        <circle cx="50" cy="50" r="8" fill="currentColor" opacity="0.6"/>
      </svg>
      <div class="sphere-label">知识图谱</div>
    </div>

    <div class="backdrop-overlay" v-if="showRag" @click="showRag = false"></div>
  </div>
</template>

<script setup lang="ts">
// 核心导入（统一放在顶部）
import { computed, onMounted, onBeforeUnmount, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
// 组件导入
import BackgroundControl from '@/components/BackgroundControl.vue'
import CreateCard from '@/components/CreateCard.vue'
import FloatingNav from '@/components/FloatingNav.vue'
// 工具/状态导入
import { useUserStore } from '@/stores/UserStore'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'
import http, { assertApiResponse } from '@/utils/http'
import { confirmDelete } from '@/utils/confirm'
// 资源导入
import defaultCover from '@/images/default-cover.png'
import { resolveNovelCover } from '@/utils/localImages'


// 路由/状态初始化
const router = useRouter()
const userStore = useUserStore()
const textColorCustomizer = useTextColorCustomizer()

// TS类型定义（与后端 NovelVO @JsonProperty 对齐，后端返回 snake_case）
interface Novel {
  id: string | number
  title: string
  cover_url?: string
  description?: string
  pen_name?: string
  char_count?: number
  node_count?: number
  relation_count?: number
  createTime?: string
  updateTime?: string
  [key: string]: unknown
}


const hoveredCard = ref<string | number | null>(null)
const showRag = ref(false)
const selectedNovel = ref<Novel | null>(null)
const isLoading = ref(true)
const ragLoading = ref(false)
const novels = ref<Novel[]>([])
// 分页：后端 /novel/listall 返回 { records, total, ... }，参数为蛇形 page_size
const PAGE_SIZE = 10
const page = ref(1)
const total = ref(0)
const loadingMore = ref(false)
const hasMore = computed(() => novels.value.length < total.value)
// 追加加载连续失败态（按钮显示「加载失败，点击重试」）
const loadError = ref(false)
// 触底自动加载哨兵（IntersectionObserver 目标）
const sentinel = ref<HTMLElement | null>(null)
// 列表操作互斥锁：触底自动加载与删除后对齐重拉不可并发写 novels
let listLocked = false
const withListLock = async (fn: () => Promise<void>) => {
  let wait = 0
  while (listLocked && wait < 40) {
    await new Promise((r) => setTimeout(r, 50))
    wait++
  }
  listLocked = true
  try {
    await fn()
  } finally {
    listLocked = false
  }
}
// 按钮文案（加载中 / 失败重试 / 常规进度）
const loadMoreLabel = computed(() => {
  if (loadingMore.value) return '加载中…'
  if (loadError.value) return '加载失败，点击重试'
  return `加载更多（${novels.value.length} / ${total.value}）`
})
const flippedCards = ref<Set<string | number>>(new Set())
const clickTimers = new Map<string | number, ReturnType<typeof setTimeout>>()

// 顶栏吸顶态（滚动后出现玻璃底）
const topbarStuck = ref(false)
const onScroll = () => { topbarStuck.value = window.scrollY > 12 }

// Hero 大数字统计：仅汇总接口真实字段，不引入杜撰指标
const charTotal = computed(() => novels.value.reduce((s, n) => s + (n.char_count || 0), 0))
const nodeTotal = computed(() => novels.value.reduce((s, n) => s + (n.node_count || 0), 0))



// 事件处理：卡片翻转
const toggleCardFlip = (novelId: string | number, event: Event) => {
  event.stopPropagation()
  flippedCards.value.has(novelId)
    ? flippedCards.value.delete(novelId)
    : flippedCards.value.add(novelId)
}

// 事件处理：卡片点击（单击/双击区分）
const handleCardClick = (novel: Novel, event: Event) => {
  event.stopPropagation()
  const novelId = novel.id

  // 清除之前的计时器
  if (clickTimers.has(novelId)) {
    clearTimeout(clickTimers.get(novelId)!)
    clickTimers.delete(novelId)
    // 双击 - 翻转卡片
    toggleCardFlip(novel.id, event)
  } else {
    // 单击 - 打开RAG抽屉
    const timer = setTimeout(() => {
      selectNovel(novel)
      clickTimers.delete(novelId)
    }, 250)
    clickTimers.set(novelId, timer)
  }
}

// 事件处理：选择小说（打开RAG）
const selectNovel = (novel: Novel) => {
  selectedNovel.value = novel
  showRag.value = true
  ragLoading.value = true
  setTimeout(() => { ragLoading.value = false }, 800)
}

// 事件处理：进入小说编辑
const openNovel = (novel: Novel) => {
  router.push({ name: 'novel-editor', params: { id: novel.id } })
}

// 事件处理：进入角色管理
const openCharacterManager = (novel: Novel) => {
  router.push({ name: 'character-manager', params: { novelId: novel.id } })
}
const openTimeline = (novel: Novel) => {
  router.push({ name: 'timeline', params: { novelId: novel.id } })
}
async function deleteNovel(novel: Novel) {
  try {
    const confirm = await confirmDelete(`确认删除小说 "${novel.title}" 吗？此操作并未设置逻辑删除，无法撤销，是否继续？`)
    if (!confirm) {
      return
    }

    await http.post(`/novel/delete/${novel.id}`)
    novels.value = novels.value.filter(n => n.id !== novel.id)

    if (selectedNovel.value?.id === novel.id) {
      showRag.value = false
      selectedNovel.value = null
    }
    // 删除使服务端数据前移，客户端页码/total 失去一致性 → 对齐重拉当前窗口
    await realignList()
  } catch {
    // 取消确认或请求失败（失败时列表未动，保持原状）
  }
}

// 事件处理：跳转到RAG助手页面
const showKnowledgeGraph = () => {
  // TODO: 实现知识图谱窗口
}

// 从概览抽屉进入RAG助手
const goToRagAssistant = () => {
  router.push('/rag-assistant')
}

// 存储之前的小说数量，用于判断是否是新卡片
const prevNovelCount = ref(0)

// 数据请求：获取小说列表；返回本次写入条数（loadMore 据此判断空页兜底）
// append=true 为「加载更多」追加下一页；失败回退 page 并置 loadError，避免跳页
const fetchNovels = async (append = false): Promise<number> => {
  if (append) loadingMore.value = true
  else isLoading.value = true
  let ok = false
  let written = 0
  try {
    const res = await http.get('/novel/listall', {
      params: { page: append ? page.value : 1, page_size: PAGE_SIZE },
    })
    // 401 已由拦截器统一跳登录；其它业务失败直接返回，避免读空 data
    const apiRes = assertApiResponse<{ records?: Novel[]; total?: number } | Novel[] | null>(res)
    if (apiRes.code !== 200 || !apiRes.data) return 0
    const data = apiRes.data
    const records = Array.isArray(data) ? data : (data.records || [])
    if (!Array.isArray(data) && typeof data.total === 'number') total.value = data.total
    novels.value = append ? [...novels.value, ...records] : records
    written = records.length
    ok = true

    if (append) {
      // 追加页不重播全列表入场动画，仅重启悬浮（纳入新卡片）
      nextTick(() => startFloatAnimation())
      return written
    }

    // 判断是否有新卡片增加
    const hasNewCards = novels.value.length > prevNovelCount.value
    prevNovelCount.value = novels.value.length

    nextTick(() => {
      // 入场动画：所有卡片同一起点同时滑入（无stagger）
      if (hasNewCards || floatAnimation.length === 0) {
        gsap.from(".novel-card, .create-card", {
          y: 40,
          opacity: 0,
          duration: 0.5,
          ease: "power2.out",
          onComplete: () => {
            startFloatAnimation()
          }
        });
      } else {
        startFloatAnimation()
      }
    });
    return written
  } catch {
    // 获取小说列表失败（401 已由拦截器跳转登录）
    return written
  } finally {
    if (append) {
      loadingMore.value = false
      if (!ok) {
        page.value -= 1 // 追加失败回退页码，下次点击不跳页
        loadError.value = true
      }
    } else {
      isLoading.value = false
    }
  }
}

// 对齐重拉（不加锁内核，供锁外与锁内复用）：
// 按已加载条数重拉服务端前 pages 页并覆盖本地 → 本地 = 服务端前 N 页，页码/total 归位
const realignImpl = async () => {
  loadingMore.value = true
  try {
    const loaded = novels.value.length
    const pages = Math.max(1, Math.ceil(loaded / PAGE_SIZE))
    const results = await Promise.all(
      Array.from({ length: pages }, (_, i) =>
        http.get('/novel/listall', { params: { page: i + 1, page_size: PAGE_SIZE } })
      )
    )
    const records: Novel[] = []
    let lastTotal: number | null = null
    for (const res of results) {
      const apiRes = assertApiResponse<{ records?: Novel[]; total?: number } | Novel[] | null>(res)
      if (apiRes.code !== 200 || !apiRes.data) throw new Error('realign failed')
      const d = apiRes.data
      if (Array.isArray(d)) records.push(...d)
      else {
        records.push(...(d.records || []))
        if (typeof d.total === 'number') lastTotal = d.total
      }
    }
    novels.value = records
    page.value = pages
    total.value = lastTotal ?? records.length
    loadError.value = false
    nextTick(() => startFloatAnimation())
  } catch {
    loadError.value = true
  } finally {
    loadingMore.value = false
  }
}

// 对齐入口（带列表锁）：删除后调用
const realignList = () => withListLock(realignImpl)

// 「加载更多」：翻页并追加；空页但仍有未加载 → 数据不一致，自动对齐兜底
const loadMore = () => {
  if (loadingMore.value || !hasMore.value) return
  void withListLock(async () => {
    if (!hasMore.value) return // 排队等待期间状态可能已变化
    loadError.value = false
    page.value += 1
    const added = await fetchNovels(true)
    if (added === 0 && hasMore.value) await realignImpl()
  })
}

// 触底自动加载：哨兵进入视口（提前 200px 预载）自动 loadMore，与按钮共用守卫
let io: IntersectionObserver | null = null
const setupSentinelObserver = () => {
  io?.disconnect()
  io = null
  if (!hasMore.value || !sentinel.value) return
  io = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) loadMore()
    },
    { rootMargin: '200px 0px' }
  )
  io.observe(sentinel.value)
}
// hasMore 变化驱动挂/卸（哨兵是 v-if="hasMore" 渲染，需等 DOM 更新）
watch(hasMore, () => nextTick(setupSentinelObserver))

// 保存悬浮动画实例
let floatAnimation: gsap.core.Tween[] = []

// 启动卡片悬浮动画（每张卡片独立随机幅度和节奏）
const startFloatAnimation = () => {
  // 先清除之前的动画
  if (floatAnimation.length) {
    floatAnimation.forEach(tw => tw.kill())
    floatAnimation = []
  }

  const cards = document.querySelectorAll('.novel-card, .create-card')
  cards.forEach((card) => {
    const randomY = 5 + Math.random() * 15 // 5~20px 随机幅度
    const randomDuration = 3 + Math.random() * 2 // 3~5秒 随机周期
    const randomDelay = Math.random() * 2 // 0~2秒 随机延迟

    const tw = gsap.to(card, {
      y: randomY,
      duration: randomDuration,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: randomDelay,
    })
    floatAnimation.push(tw)
  })
}

// 生命周期：挂载
onMounted(async () => {
  window.addEventListener('scroll', onScroll, { passive: true })
  await fetchNovels()

  textColorCustomizer.loadFromStorage()
  textColorCustomizer.applyCSSVariables()
})

// 生命周期：卸载（清理定时器和动画）
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  io?.disconnect()
  io = null
  clickTimers.forEach(timer => clearTimeout(timer))
  clickTimers.clear()
  // 清理悬浮动画
  if (floatAnimation.length) {
    floatAnimation.forEach(tw => tw.kill())
    floatAnimation = []
  }
})
</script>

<style scoped>
/* ============ 主容器 ============ */
.engine-container {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  /* clip 而非 hidden：拦住横向溢出，但不破坏内部 position:sticky 吸顶 */
  overflow-x: clip;
  position: relative;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  transition: filter 0.3s ease;
}

.engine-container.blur-bg { filter: blur(3px); }

/* ============ 背景 ============ */
.bg-gradient-animation {
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: transparent;
  z-index: 0;
  opacity: var(--bg-intensity, 1);
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.bg-gradient-animation.paused { animation-play-state: paused; }

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ============ 主舞台 ============ */
.main-stage {
  position: relative;
  z-index: 1;
  /* 边距提为变量：顶栏负 margin 出血复用同一值 */
  --stage-py: clamp(28px, 5vh, 64px);
  --stage-px: clamp(20px, 5vw, 64px);
  padding: var(--stage-py) var(--stage-px);
}

.stage-header { margin-bottom: 32px; }

/* 吸顶栏：负 margin 满幅出血，滚动后浮出玻璃底 + 发丝线 */
.topbar {
  position: sticky;
  top: 0;
  z-index: 90;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin: 0 calc(-1 * var(--stage-px));
  padding: 14px var(--stage-px);
  background: transparent;
  transition: background-color 0.25s ease;
}

.topbar.stuck {
  background: rgba(13, 13, 15, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.brand-logo {
  height: 40px;
  width: auto;
  display: block;
}

.brand-name {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--text-primary);
  white-space: nowrap;
}

.brand-engine {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.28em;
  color: var(--accent-primary);
}

/* ============ Hero：左编辑部标题区 + 右大数字统计 ============ */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 28px 56px;
  align-items: end;
}

.eyebrow {
  margin: 0 0 14px;
  font-size: 0.75rem;
  letter-spacing: 0.3em;
  color: var(--accent-primary);
}

/* 发丝线眉标：结构线，非装饰光效 */
.eyebrow::before {
  content: '';
  display: inline-block;
  width: 28px;
  height: 1px;
  background: var(--accent-primary);
  vertical-align: middle;
  margin-right: 10px;
}

.hero-title {
  margin: 0;
  font-size: clamp(2rem, 3.6vw, 3.25rem);
  font-weight: 900;
  line-height: 1.25;
  letter-spacing: 0.02em;
  color: var(--text-primary);
}

.hero-stats {
  display: flex;
  gap: clamp(24px, 4vw, 48px);
}

.stat-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* 全页尺度锚点：大数字对 0.9rem 正文 ≈ 5 倍对比 */
.stat-hero-num {
  font-size: clamp(2.75rem, 5vw, 4.5rem);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}

.stat-hero-label {
  margin-top: 10px;
  font-size: 0.72rem;
  letter-spacing: 0.24em;
  color: var(--text-muted);
}

.subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 14px 0 0;
}

.subtitle .highlight, .user-name {
  color: var(--neon-cyan);
  font-weight: 600;
}

/* ============ 分节横规：标题 + 细线 + 计数徽章 ============ */
.section-head {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-title {
  font-size: clamp(1.5rem, 2.4vw, 2rem);
  font-weight: 800;
  margin: 0;
  letter-spacing: 0.08em;
  line-height: 1.35;
  white-space: nowrap;
}

.section-rule {
  flex: 1;
  height: 1px;
  background: var(--glass-border);
}

.section-count {
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums;
  color: var(--text-muted);
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  padding: 3px 12px;
}

/* ============ 加载状态 ============ */
.loading-state, .rag-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.spinner, .rag-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(75, 139, 245, 0.22);
  border-top-color: var(--neon-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ============ 网格布局 ============ */
.galaxy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 35px;
  margin-top: 18px;
}
.galaxy-grid.single-card {
  grid-template-columns: 1fr;
  max-width: 320px;
  margin-left: auto;
  margin-right: auto;
}

/* 分页「加载更多」 */
.load-more-row {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
.load-more-btn {
  padding: 10px 26px;
  border-radius: 999px;
  border: 1px solid var(--surface-glass-border, rgba(255, 255, 255, 0.12));
  background: var(--surface-glass, rgba(255, 255, 255, 0.05));
  color: var(--text-secondary, #9aa3b5);
  font-size: 0.85rem;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition:
    border-color var(--dur, 240ms) var(--ease-out, ease-out),
    color var(--dur, 240ms) var(--ease-out, ease-out);
}
.load-more-btn:hover:not(:disabled) {
  border-color: rgba(75, 139, 245, 0.5);
  color: var(--text-on-glass, #e8ecf5);
}
.load-more-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
/* 连续失败态：按钮变警示色，点击重试 */
.load-more-btn.is-error {
  border-color: rgba(229, 84, 75, 0.55);
  color: var(--danger, #e5544b);
}
/* 触底自动加载哨兵：1px 不占视觉空间，仅作 IntersectionObserver 目标 */
.load-sentinel {
  display: block;
  width: 100%;
  height: 1px;
}

/* 移动端：加大触摸目标、收紧间距，375 宽不溢出 */
@media (max-width: 768px) {
  .load-more-row {
    margin-top: 24px;
  }
  .load-more-btn {
    min-height: 44px;
    padding: 12px 28px;
    font-size: 0.9rem;
  }
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 50px 20px 0;
}
.empty-hint p {
  margin: 16px 0 0;
  font-size: 1rem;
}

.novel-card-wrapper {
  cursor: pointer;
  transition: all 0.4s ease;
}

.novel-card-wrapper:hover { transform: translateY(-8px); }

/* ============ 玻璃卡片 ============ */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 0;
  height: 100%;
  aspect-ratio: 2 / 3;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transform-style: preserve-3d;
  cursor: pointer;
  perspective: 1200px;
  box-sizing: border-box;
}

.novel-card {
  border: 1px solid rgba(75, 139, 245, 0.22);
}

.novel-card:hover {
  border-color: rgba(75, 139, 245, 0.5);
  box-shadow: var(--card-shadow);
  background: rgba(255, 255, 255, 0.08);
}

/* 封面层 - 真实卡牌翻转动画 */
.novel-cover-wrapper {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: transform 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  opacity 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  opacity: 1;
  transform: rotateY(0deg) rotateX(0deg) scale(1);
  transform-origin: center center;
  transform-style: preserve-3d;
  backface-visibility: hidden;
  border-radius: 24px;
}

/* 悬停时轻微旋转预览 */
.novel-card-wrapper:hover .novel-card:not(.flipped) .novel-cover-wrapper {
  transform: rotateY(-12deg) rotateX(2deg) scale(0.98);
  opacity: 0.8;
}

/* 翻转后的状态 - 180度水平翻转 + 逐渐消失 */
.novel-card.flipped .novel-cover-wrapper {
  z-index: 0;
  pointer-events: none;
  backface-visibility: hidden;
  transform: rotateY(180deg) rotateX(0deg) scale(0.95);
  opacity: 0;
}

.novel-cover {
  width: 100%;
  height: 100%;
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
  border-radius: 20px;
  overflow: hidden;
}

.novel-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 24px;
  display: block;
  transition: transform 0.5s ease;
}

/* hover 语义 = 「进入这个世界」：封面轻微推近 */
.novel-card-wrapper:hover .novel-cover img {
  transform: scale(1.04);
}

.card-content {
  position: absolute;
  inset: 0;
  padding: 28px;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: transform 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  opacity 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  visibility 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  transform: rotateY(-180deg) translateY(40px);
  opacity: 0;
  visibility: hidden;
  backface-visibility: hidden;
  pointer-events: none;
}

.novel-card.flipped .card-content {
  transform: rotateY(0deg) translateY(0);
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pen-name {
  font-size: 0.85rem;
  color: var(--neon-cyan);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.novel-id {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  font-family: 'Courier New', monospace;
}

.novel-title {
  font-size: 1.6rem;
  font-weight: 900;
  margin: 0 0 12px 0;
  color: var(--text-primary);
  line-height: 1.3;
}

.description {
  font-size: 0.9rem;
  color: var(--description-color);
  margin: 0 0 15px 0;
  flex: 1;
  line-height: 1.5;
  overflow-y: auto;
  max-height: 120px;
  padding-right: 8px;
  transition: color 0.3s ease;
}

.card-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 15px 0 20px 0;
  max-height: 60px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card-stats.expanded {
  grid-template-columns: repeat(3, 1fr);
  max-height: 180px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s;
}

.card-stats.expanded .stat {
  background: rgba(75, 139, 245, 0.1);
  border-color: rgba(75, 139, 245, 0.3);
}

.stat-icon, .btn-icon {
  width: 1.2rem;
  height: 1.2rem;
}

.stat span {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.stat-value {
  font-size: 1.3rem;
  color: var(--neon-blue);
}

.enter-btn {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--accent-primary);
  border: 1px solid transparent;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
}

.card-actions-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 10px;
}

.action-btn-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn-sm .btn-icon {
  width: 1.1rem;
  height: 1.1rem;
  opacity: 0.7;
  transition: all 0.3s;
  transform: none;
}

.action-btn-sm:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.action-btn-sm:hover .btn-icon {
  opacity: 1;
}

/* 语义 hover 收敛为青（角色）/ 蓝（时间线）/ 红（删除），呼应蓝+青+中性色板 */
.action-btn-sm.character-btn:hover,
.action-btn-sm.character-btn:hover .btn-icon {
  background: rgba(6, 182, 212, 0.12);
  border-color: rgba(6, 182, 212, 0.35);
  color: var(--neon-cyan);
  opacity: 1;
}

.action-btn-sm.timeline-btn:hover,
.action-btn-sm.timeline-btn:hover .btn-icon {
  background: rgba(75, 139, 245, 0.12);
  border-color: rgba(75, 139, 245, 0.35);
  color: var(--accent-primary);
  opacity: 1;
}

.action-btn-sm.delete-btn:hover,
.action-btn-sm.delete-btn:hover .btn-icon {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.35);
  color: #ef4444;
  opacity: 1;
}

.enter-btn .btn-icon {
  width: 1.2rem;
  height: 1.2rem;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s;
}

.enter-btn:hover {
  filter: brightness(1.12);
  transform: translateY(-2px);
}

.enter-btn:hover .btn-icon {
  opacity: 1;
  transform: translateX(0);
}

/* ============ 创建卡片 ============ */
.create-card {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  min-height: 320px;
}

.create-card:hover {
  border-color: var(--neon-cyan);
}

.card-create-content {
  gap: 12px;
}

.create-icon {
  width: 3rem;
  height: 3rem;
  color: rgba(6, 182, 212, 0.6);
}

.card-create-content span {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.create-hint {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

/* ============ 空状态 ============ */

.empty-state-drawer {
  height: 300px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-icon-drawer {
  width: 60px;
  height: 60px;
  margin-bottom: 20px;
  opacity: 0.5;
}

/* ============ RAG 抽屉 ============ */
.rag-drawer {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  background: rgba(10, 10, 12, 0.95);
  backdrop-filter: blur(20px);
  border-left: 1px solid var(--glass-border);
  box-shadow: -20px 0 40px rgba(0, 0, 0, 0.5);
  z-index: 200;
  transform: translateX(100%);
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow-y: auto;
}

.rag-drawer.open { transform: translateX(0); }

.drawer-header {
  padding: 24px;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: rgba(10, 10, 12, 0.8);
  backdrop-filter: blur(10px);
}

.drawer-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--neon-cyan);
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-btn svg {
  width: 24px;
  height: 24px;
}

.close-btn:hover {
  color: var(--neon-blue);
  transform: rotate(90deg);
}

.drawer-content { padding: 24px; }

.rag-info h4 {
  color: var(--neon-blue);
  margin-bottom: 20px;
  font-size: 1.1rem;
}

.info-section {
  margin-bottom: 20px;
}

.info-section strong {
  color: var(--neon-cyan);
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 10px;
}

.info-section p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid var(--neon-blue);
  border-radius: 4px;
}

.rag-enter-btn {
  margin-top: 20px !important;
}

/* ============ 知识球体 ============ */
.knowledge-sphere {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 120px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 80;
  cursor: pointer;
  transition: all 0.4s ease;
}

.sphere-visual {
  width: 100%;
  height: 100%;
  color: var(--neon-cyan);
  transition: all 0.3s;
}

.knowledge-sphere:hover .sphere-visual {
  transform: scale(1.1);
}

.sphere-label {
  position: absolute;
  bottom: -30px;
  font-size: 0.85rem;
  color: rgba(6, 182, 212, 0.8);
  letter-spacing: 1px;
  text-transform: uppercase;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s;
}

.knowledge-sphere:hover .sphere-label { opacity: 1; }

/* ============ 遮罩 ============ */
.backdrop-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 150;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ============ 响应式 ============ */
@media (max-width: 1400px) {
  .galaxy-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 25px;
  }
  .galaxy-grid.single-card {
    grid-template-columns: 1fr;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }
}

@media (max-width: 1024px) {
  .galaxy-grid { grid-template-columns: repeat(2, 1fr); }
  .galaxy-grid.single-card {
    grid-template-columns: 1fr;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }
  .rag-drawer { width: 350px; }
}

@media (max-width: 768px) {
  /* 顶栏：品牌字号与 logo 收窄，防止右侧控制被挤出屏 */
  .brand-logo { height: 32px; }
  .brand-name { font-size: 1rem; letter-spacing: 0.08em; }
  .brand-engine { font-size: 0.6rem; letter-spacing: 0.2em; }
  .subtitle { font-size: 0.85rem; }
  /* Hero 纵向堆叠：标题区在上，统计行横排在下 */
  .hero { grid-template-columns: 1fr; gap: 22px; }
  .hero-stats { gap: 22px; flex-wrap: wrap; }
  .stat-hero-num { font-size: clamp(2.25rem, 10vw, 3rem); }
  .section-title { font-size: 1.25rem; }

  /* 手机上双列小卡，避免单列封面占满整屏 */
  .galaxy-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }
  .galaxy-grid.single-card {
    grid-template-columns: 1fr;
    max-width: 240px;
    margin-left: auto;
    margin-right: auto;
  }

  /* 双列卡片内容区：28px 内边距 + 桌面字号在 ~160px 宽卡片里会溢出、挤掉底部按钮 */
  .card-content { padding: 14px; }
  .card-header { margin-bottom: 8px; }
  .pen-name { font-size: 0.7rem; }
  .novel-id { display: none; }
  .novel-title { font-size: 1.1rem; margin-bottom: 6px; line-height: 1.25; }
  .description { font-size: 0.8rem; margin-bottom: 8px; line-height: 1.4; max-height: 54px; }
  .card-stats { gap: 6px; margin: 8px 0 10px; max-height: 48px; }
  .stat { padding: 6px; border-radius: 8px; }
  .stat span { font-size: 0.6rem; margin-top: 2px; letter-spacing: 0.3px; }
  .stat-icon, .btn-icon { width: 1rem; height: 1rem; }
  .card-actions { gap: 6px; margin-bottom: 6px; }
  .action-btn-sm { padding: 5px; border-radius: 8px; }
  .empty-hint p { font-size: 0.9rem; }

  .rag-drawer { width: 100%; }
  .knowledge-sphere {
    width: 80px;
    height: 80px;
    bottom: 20px;
    right: 20px;
  }
}

/* 进入按钮图标：入场滑入 */
@keyframes enterIconReveal {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* 触屏设备 / 移动端：图标常驻，只播一次动画后固定 */
@media (hover: none), (max-width: 768px) {
  .enter-btn .btn-icon,
  .enter-btn:hover .btn-icon,
  .enter-btn:active .btn-icon {
    opacity: 1;
    transform: translateX(0);
    /* both = 延迟期保持 from（隐藏），结束后保持 to（固定显示） */
    animation: enterIconReveal 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s both;
  }
}
</style>

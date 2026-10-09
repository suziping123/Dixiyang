<template>
  <div class="idea-page">
    <FloatingNav />
    <header class="page-head">
      <div class="head-title">
        <h1>点子库</h1>
        <span class="head-sub">私有草稿写灵感，发布后进入创意社区</span>
      </div>
      <div class="head-actions">
        <el-input
          v-model="search"
          class="search-box"
          placeholder="搜索标题 / 摘要"
          clearable
          :prefix-icon="Search"
          @keyup.enter="enterSubmit(onSearch, $event)"
          @clear="onSearch"
        />
        <el-button type="primary" :icon="EditPen" @click="openEditor(null)">写点子</el-button>
      </div>
    </header>

    <nav class="tab-bar" role="tablist">
      <button
        v-for="t in tabs"
        :key="t.key"
        type="button"
        class="tab-btn"
        :class="{ active: tab === t.key }"
        role="tab"
        :aria-selected="tab === t.key"
        @click="switchTab(t.key)"
      >
        {{ t.label }}
      </button>
    </nav>

    <!-- ========== 广场 ========== -->
    <section v-if="tab === 'feed'" class="tab-section">
      <div class="filter-row">
        <div class="chip-group" role="group" aria-label="分区筛选">
          <button
            v-for="c in categories"
            :key="c.key"
            type="button"
            class="chip"
            :class="{ on: category === c.key }"
            @click="category = c.key; page = 1; loadFeed()"
          >
            {{ c.label }}
          </button>
        </div>
        <div class="sort-group">
          <button
            v-for="s in sorts"
            :key="s.key"
            type="button"
            class="chip"
            :class="{ on: sort === s.key }"
            @click="sort = s.key; page = 1; loadFeed()"
          >
            {{ s.label }}
          </button>
        </div>
      </div>

      <div v-if="hotTags.length" class="tag-row">
        <span class="tag-row-label">热门标签</span>
        <button
          v-for="t in hotTags"
          :key="t.tag"
          type="button"
          class="tag-chip"
          :class="{ on: activeTag === t.tag }"
          @click="toggleTag(t.tag)"
        >
          #{{ t.tag }}<i>{{ t.count }}</i>
        </button>
      </div>

      <div v-loading="loading" class="post-grid feed-waterfall">
        <article
          v-for="p in posts"
          :key="p.id"
          class="post-card xhs-card"
          tabindex="0"
          @click="openPost(p.id)"
          @keyup.enter="openPost(p.id)"
        >
          <div v-if="p.coverUrl" class="card-cover">
            <img :src="p.coverUrl" alt="" loading="lazy" />
            <span class="cat-tag" :class="`cat-${p.category}`">{{ catLabel(p.category) }}</span>
            <span v-if="p.attach" class="attach-flag" title="含附件"><IdeaIcon name="clip" :size="15" /></span>
          </div>
          <div class="card-top" v-else>
            <span class="cat-tag" :class="`cat-${p.category}`">{{ catLabel(p.category) }}</span>
            <span v-if="p.attach" class="attach-flag" title="含附件"><IdeaIcon name="clip" :size="15" /></span>
          </div>
          <div class="card-body">
            <h3 class="card-title">{{ p.title }}</h3>
            <p v-if="!p.coverUrl && p.summary" class="card-summary">{{ p.summary }}</p>
            <div v-if="p.tags?.length" class="card-tags">
              <span v-for="tg in p.tags.slice(0, 3)" :key="tg" class="mini-tag">#{{ tg }}</span>
            </div>
            <footer class="card-foot">
              <span class="avatar">{{ (p.authorName || '?').slice(0, 1) }}</span>
              <span class="author">{{ p.authorName }}</span>
              <button
                type="button"
                class="stat-btn"
                :class="{ on: p.likedByMe, bump: animKey === `like-${p.id}` }"
                :aria-label="p.likedByMe ? '取消点赞' : '点赞'"
                @click.stop="onCardLike(p)"
              >
                <IdeaIcon name="heart" :size="15" :filled="p.likedByMe" />
                <span :key="p.likeCount" class="stat-num">{{ p.likeCount }}</span>
              </button>
              <span class="stat-btn static" title="评论数"><IdeaIcon name="bubble" :size="15" /><span>{{ p.commentCount }}</span></span>
              <button
                type="button"
                class="stat-btn star"
                :class="{ on: p.collectedByMe, bump: animKey === `collect-${p.id}` }"
                :aria-label="p.collectedByMe ? '取消收藏' : '收藏'"
                @click.stop="onCardCollect(p)"
              >
                <IdeaIcon name="star" :size="15" :filled="p.collectedByMe" />
                <span :key="p.collectCount" class="stat-num">{{ p.collectCount }}</span>
              </button>
            </footer>
          </div>
        </article>
        <el-empty v-if="!loading && !posts.length" description="这里还很安静，发第一篇吧" />
      </div>

      <el-pagination
        v-if="feedTotal > pageSize"
        v-model:current-page="page"
        class="pager"
        layout="prev, pager, next"
        :total="feedTotal"
        :page-size="pageSize"
        @current-change="loadFeed()"
      />
    </section>

    <!-- ========== 草稿箱 ========== -->
    <section v-else-if="tab === 'drafts'" class="tab-section">
      <div v-loading="loading" class="draft-list">
        <div v-for="d in drafts" :key="d.id" class="draft-row">
          <div class="draft-main">
            <span class="cat-tag" :class="`cat-${d.category}`">{{ catLabel(d.category) }}</span>
            <b class="draft-title">{{ d.title }}</b>
            <span class="draft-time">{{ d.updateTime }}</span>
          </div>
          <div class="draft-ops">
            <el-button size="small" @click="openEditor(d.id)">编辑</el-button>
            <el-button size="small" type="primary" plain @click="quickPublish(d.id)">发布</el-button>
            <el-button size="small" type="danger" plain @click="onDeleteDraft(d.id)">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!loading && !drafts.length" description="草稿箱是空的" />
      </div>
      <el-pagination
        v-if="draftTotal > pageSize"
        v-model:current-page="page"
        class="pager"
        layout="prev, pager, next"
        :total="draftTotal"
        :page-size="pageSize"
        @current-change="loadDrafts()"
      />
    </section>

    <!-- ========== 我发布的 ========== -->
    <section v-else-if="tab === 'mine'" class="tab-section">
      <div v-loading="loading" class="post-grid">
        <article v-for="p in posts" :key="p.id" class="post-card" tabindex="0" @click="openPost(p.id)">
          <div class="card-top">
            <span class="cat-tag" :class="`cat-${p.category}`">{{ catLabel(p.category) }}</span>
            <span v-if="p.status === 'removed'" class="removed-flag">已下架</span>
          </div>
          <h3 class="card-title">{{ p.title }}</h3>
          <p class="card-summary">{{ p.summary }}</p>
          <footer class="card-foot">
            <span class="stat"><IdeaIcon name="eye" :size="14" />{{ p.viewCount }}</span>
            <span class="stat"><IdeaIcon name="heart" :size="14" />{{ p.likeCount }}</span>
            <span class="stat"><IdeaIcon name="bubble" :size="14" />{{ p.commentCount }}</span>
            <span class="stat"><IdeaIcon name="star" :size="14" />{{ p.collectCount }}</span>
            <button
              v-if="p.status === 'removed'"
              type="button"
              class="edit-entry"
              title="下架后可修改，改完重新上架"
              @click.stop="openPostEdit(p.id)"
            >
              <IdeaIcon name="edit" :size="14" />编辑
            </button>
          </footer>
        </article>
        <el-empty v-if="!loading && !posts.length" description="还没有发布过点子" />
      </div>
      <el-pagination
        v-if="feedTotal > pageSize"
        v-model:current-page="page"
        class="pager"
        layout="prev, pager, next"
        :total="feedTotal"
        :page-size="pageSize"
        @current-change="loadMine()"
      />
    </section>

    <!-- ========== 我的收藏 ========== -->
    <section v-else class="tab-section">
      <div v-loading="loading" class="post-grid">
        <article v-for="p in posts" :key="p.id" class="post-card" tabindex="0" @click="openPost(p.id)">
          <div class="card-top">
            <span class="cat-tag" :class="`cat-${p.category}`">{{ catLabel(p.category) }}</span>
          </div>
          <h3 class="card-title">{{ p.title }}</h3>
          <p class="card-summary">{{ p.summary }}</p>
          <footer class="card-foot">
            <span class="author">{{ p.authorName }}</span>
            <span class="stat"><IdeaIcon name="heart" :size="14" />{{ p.likeCount }}</span>
            <span class="stat"><IdeaIcon name="bubble" :size="14" />{{ p.commentCount }}</span>
            <button
              type="button"
              class="stat-btn star on"
              :class="{ bump: animKey === `collect-${p.id}` }"
              aria-label="取消收藏"
              @click.stop="onCardCollect(p)"
            >
              <IdeaIcon name="star" :size="15" filled />
              <span :key="p.collectCount" class="stat-num">{{ p.collectCount }}</span>
            </button>
          </footer>
        </article>
        <el-empty v-if="!loading && !posts.length" description="收藏夹是空的" />
      </div>
      <el-pagination
        v-if="feedTotal > pageSize"
        v-model:current-page="page"
        class="pager"
        layout="prev, pager, next"
        :total="feedTotal"
        :page-size="pageSize"
        @current-change="loadCollects()"
      />
    </section>

    <DraftEditorDialog
      v-model="editorVisible"
      :draft-id="editingDraftId"
      @saved="onDraftSaved"
      @published="onPublished"
    />
    <PostDetailDialog v-model="detailVisible" :post-id="detailPostId" @change="reload" />
    <PostEditDialog v-model="editVisible" :post-id="editPostId" @saved="reload" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, EditPen } from '@element-plus/icons-vue'
import {
  listPosts, listDrafts, deleteDraft, publishDraft,
  listMinePosts, listMineCollects, listTags, toggleLike, toggleCollect,
  type IdeaPostItem, type IdeaDraftItem, type IdeaCategory, type IdeaSort,
} from '@/api/ideaApi'
import DraftEditorDialog from '@/components/idea/DraftEditorDialog.vue'
import PostDetailDialog from '@/components/idea/PostDetailDialog.vue'
import PostEditDialog from '@/components/idea/PostEditDialog.vue'
import IdeaIcon from '@/components/idea/IdeaIcon.vue'
import FloatingNav from '@/components/FloatingNav.vue'
import { confirmDelete } from '@/utils/confirm'
import { enterSubmit } from '@/utils/enterSubmit'

type TabKey = 'feed' | 'drafts' | 'mine' | 'collects'

const tabs: { key: TabKey; label: string }[] = [
  { key: 'feed', label: '广场' },
  { key: 'drafts', label: '草稿箱' },
  { key: 'mine', label: '我发布的' },
  { key: 'collects', label: '我的收藏' },
]

const categories: { key: string; label: string }[] = [
  { key: '', label: '全部' },
  { key: 'idea', label: '点子' },
  { key: 'character', label: '角色' },
  { key: 'setting', label: '设定' },
  { key: 'timeline', label: '时间线' },
  { key: 'tech', label: '技术' },
]

const sorts: { key: IdeaSort; label: string }[] = [
  { key: 'new', label: '最新' },
  { key: 'hot', label: '热门' },
  { key: 'like', label: '最多赞' },
]

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const tab = ref<TabKey>('feed')
const loading = ref(false)
const search = ref('')
const category = ref('')
const sort = ref<IdeaSort>('new')
const activeTag = ref('')
const page = ref(1)
const pageSize = 12

const posts = ref<IdeaPostItem[]>([])
const feedTotal = ref(0)
const drafts = ref<IdeaDraftItem[]>([])
const draftTotal = ref(0)
const hotTags = ref<{ tag: string; count: number }[]>([])

const editorVisible = ref(false)
const editingDraftId = ref<number | null>(null)
const detailVisible = ref(false)
const detailPostId = ref(0)
const editVisible = ref(false)
const editPostId = ref(0)
/** 互动弹跳动画键：`like-12` / `collect-12`，300ms 后清除 */
const animKey = ref('')

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

// ---------- 数据加载 ----------

const loadFeed = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: IdeaPostItem[] }>(
      await listPosts({
        category: category.value || undefined,
        sort: sort.value,
        q: search.value || undefined,
        tags: activeTag.value || undefined,
        page: page.value,
        pageSize,
      }),
    )
    if (data) {
      posts.value = data.list
      feedTotal.value = data.total
    }
  } finally {
    loading.value = false
  }
}

const loadDrafts = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: IdeaDraftItem[] }>(
      await listDrafts({ category: category.value || undefined, q: search.value || undefined, page: page.value, pageSize }),
    )
    if (data) {
      drafts.value = data.list
      draftTotal.value = data.total
    }
  } finally {
    loading.value = false
  }
}

const loadMine = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: IdeaPostItem[] }>(await listMinePosts({ page: page.value, pageSize }))
    if (data) {
      posts.value = data.list
      feedTotal.value = data.total
    }
  } finally {
    loading.value = false
  }
}

const loadCollects = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: IdeaPostItem[] }>(await listMineCollects({ page: page.value, pageSize }))
    if (data) {
      posts.value = data.list
      feedTotal.value = data.total
    }
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  const data = unwrap<{ tag: string; count: number }[]>(await listTags(20))
  if (data) hotTags.value = data
}

const reload = () => {
  if (tab.value === 'feed') loadFeed()
  else if (tab.value === 'drafts') loadDrafts()
  else if (tab.value === 'mine') loadMine()
  else loadCollects()
}

// ---------- 交互 ----------

const switchTab = (key: TabKey) => {
  tab.value = key
  page.value = 1
  reload()
}

const onSearch = () => {
  page.value = 1
  reload()
}

const toggleTag = (tag: string) => {
  activeTag.value = activeTag.value === tag ? '' : tag
  page.value = 1
  loadFeed()
}

const openEditor = (draftId: number | null) => {
  editingDraftId.value = draftId
  editorVisible.value = true
}

const quickPublish = (draftId: number) => {
  editingDraftId.value = draftId
  editorVisible.value = true
}

const onDraftSaved = () => reload()

const onPublished = () => {
  editorVisible.value = false
  tab.value = 'feed'
  page.value = 1
  activeTag.value = ''
  loadFeed()
  loadTags()
}

const onDeleteDraft = async (id: number) => {
  const ok = await confirmDelete('确定删除这篇草稿吗？删除后无法恢复。', '警告')
  if (!ok) return
  const res = (await deleteDraft(id)) as { code?: number; msg?: string }
  if (res.code === 200) {
    ElMessage.success('已删除')
    loadDrafts()
  } else {
    ElMessage.warning(res.msg || '删除失败')
  }
}

const openPost = (id: number) => {
  detailPostId.value = id
  detailVisible.value = true
}

const openPostEdit = (id: number) => {
  editPostId.value = id
  editVisible.value = true
}

// ---------- 卡片快捷互动（乐观更新，失败回滚） ----------

const playBump = (key: string) => {
  animKey.value = key
  window.setTimeout(() => {
    if (animKey.value === key) animKey.value = ''
  }, 320)
}

const onCardLike = async (p: IdeaPostItem) => {
  const prevLiked = p.likedByMe
  const prevCount = p.likeCount
  p.likedByMe = !prevLiked
  p.likeCount = prevCount + (prevLiked ? -1 : 1)
  playBump(`like-${p.id}`)
  try {
    const r = (await toggleLike(p.id)) as { code?: number; data?: { liked: boolean; likeCount: number } }
    if (r.code === 200 && r.data) {
      p.likedByMe = r.data.liked
      p.likeCount = r.data.likeCount
    } else {
      p.likedByMe = prevLiked
      p.likeCount = prevCount
      ElMessage.warning((r as { msg?: string }).msg || '点赞失败')
    }
  } catch {
    p.likedByMe = prevLiked
    p.likeCount = prevCount
    ElMessage.warning('网络异常，已还原')
  }
}

const onCardCollect = async (p: IdeaPostItem) => {
  const prev = p.collectedByMe
  const prevCount = p.collectCount
  p.collectedByMe = !prev
  p.collectCount = prevCount + (prev ? -1 : 1)
  playBump(`collect-${p.id}`)
  try {
    const r = (await toggleCollect(p.id)) as { code?: number; data?: { collected: boolean; collectCount: number } }
    if (r.code === 200 && r.data) {
      p.collectedByMe = r.data.collected
      p.collectCount = r.data.collectCount
      ElMessage.success(r.data.collected ? '已收藏' : '已取消收藏')
    } else {
      p.collectedByMe = prev
      p.collectCount = prevCount
      ElMessage.warning((r as { msg?: string }).msg || '收藏失败')
    }
  } catch {
    p.collectedByMe = prev
    p.collectCount = prevCount
    ElMessage.warning('网络异常，已还原')
  }
}

onMounted(() => {
  loadFeed()
  loadTags()
})
</script>

<style scoped>
.idea-page {
  /* ⚠️ 警告后续 agent：新增页面根容器必须 position:relative，否则有背景图时整页被 #theme-bg 压住（看不见但可点）。
     先例：docs/404页被背景图覆盖修复.md、docs/小说编辑页背景图层叠与视觉AI修复.md */
  position: relative;
  min-height: 100vh;
  padding: 32px 32px 64px;
  color: var(--text-on-page);
  max-width: 1280px;
  margin: 0 auto;
  /* 卡片实底化：全局 --surface-card 是 4% 半透明，叠在背景图上会"融为一体"（用户反馈⑤），此处作用域覆盖为深色实底 */
  --surface-card: #171a24;
}

/* 窄屏（FAB 悬浮球占右侧 74px）时避让，防止遮住卡片操作 */
@media (max-width: 1024px) {
  .idea-page {
    padding-right: 88px;
  }
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.head-title h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.head-sub {
  font-size: 13px;
  color: var(--text-secondary);
}

.head-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-box {
  width: 240px;
}

/* ---------- Tab ---------- */

.tab-bar {
  display: flex;
  gap: 6px;
  border-bottom: 1px solid var(--surface-glass-border);
  margin-bottom: 18px;
}

.tab-btn {
  padding: 10px 18px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: 15px;
  cursor: pointer;
  transition: color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out);
}

.tab-btn:hover {
  color: var(--text-on-page);
}

.tab-btn.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
  font-weight: 600;
}

/* ---------- 筛选 ---------- */

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.chip-group,
.sort-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.chip:hover {
  color: var(--text-on-page);
  border-color: var(--accent-primary);
}

.chip.on {
  background: var(--accent-soft-strong);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  font-weight: 600;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag-row-label {
  font-size: 12px;
  color: var(--text-muted);
}

.tag-chip {
  border: none;
  background: var(--accent-soft);
  color: var(--text-secondary);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.tag-chip i {
  font-style: normal;
  margin-left: 4px;
  opacity: 0.6;
}

.tag-chip.on {
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
  font-weight: 600;
}

/* ---------- 卡片 ---------- */

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  min-height: 200px;
}

/* 广场小红书瀑布流：CSS multi-column，卡片 break-inside 避免截断，高度自然参差 */
.feed-waterfall {
  display: block;
  column-width: 220px;
  column-gap: 14px;
}

.feed-waterfall .xhs-card {
  display: inline-block;
  width: 100%;
  box-sizing: border-box;
  margin: 0 0 14px;
  padding: 0;
  gap: 0;
  overflow: hidden;
  break-inside: avoid;
  vertical-align: top;
}

.feed-waterfall .xhs-card:hover,
.feed-waterfall .xhs-card:focus-visible {
  transform: translateY(-3px);
}

.card-cover {
  position: relative;
  aspect-ratio: 3 / 4;
  background: var(--surface-input);
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-cover .cat-tag {
  position: absolute;
  left: 8px;
  top: 8px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
}

.card-cover .attach-flag {
  position: absolute;
  right: 8px;
  top: 8px;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 999px;
  padding: 2px 7px;
  font-size: 12px;
}

.xhs-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px 14px;
}

.xhs-card .card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.45;
  color: var(--text-on-card, var(--text-primary));
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.xhs-card .card-summary {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.xhs-card .card-foot {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.xhs-card .avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.xhs-card .author {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-card {
  background: var(--surface-card);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: var(--radius-md);
  padding: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 常驻微投影：卡片从背景图上"浮起来"，不再融为一体 */
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.28);
  transition: transform var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out),
    box-shadow var(--dur-fast) var(--ease-out);
}

.post-card:hover,
.post-card:focus-visible {
  transform: translateY(-3px);
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-card);
  outline: none;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cat-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-cyan);
}

.cat-character { color: var(--accent-purple); }
.cat-setting { color: #f0c674; }
.cat-timeline { color: #8be98b; }
.cat-tech { color: var(--accent-primary); }

.attach-flag {
  display: inline-flex;
  align-items: center;
  opacity: 0.85;
}

.removed-flag {
  font-size: 11px;
  color: var(--danger);
  background: var(--danger-soft);
  padding: 2px 8px;
  border-radius: 999px;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.card-summary {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.mini-tag {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface-input);
  border-radius: 4px;
  padding: 2px 6px;
}

.card-foot {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--surface-glass-border);
  padding-top: 8px;
}

.author {
  color: var(--text-secondary);
  font-weight: 600;
  margin-right: auto;
}

.stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

/* ---------- 卡片快捷互动（图标按钮 + 弹跳反馈） ---------- */

.stat-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  padding: 3px 6px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  transition: color var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out);
}

.stat-btn.static {
  cursor: default;
}

.stat-btn:hover:not(.static) {
  color: var(--text-on-page);
  background: rgba(255, 255, 255, 0.06);
}

.stat-btn:active:not(.static) {
  transform: scale(0.9);
}

.stat-btn.on {
  color: var(--danger, #f56c6c);
}

.stat-btn.star.on {
  color: #f0c674;
}

.stat-btn.bump .idea-icon,
.stat-btn.bump .stat-num {
  animation: stat-bump 0.32s var(--ease-out);
}

.stat-num {
  display: inline-block;
  min-width: 1em;
}

@keyframes stat-bump {
  0% { transform: scale(1); }
  35% { transform: scale(1.42); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

/* 我发布的：下架帖编辑入口（下架为修改服务） */
.edit-entry {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--danger, #f56c6c);
  background: var(--danger-soft, rgba(245, 108, 108, 0.12));
  color: var(--danger, #f56c6c);
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
}

.edit-entry:hover {
  background: rgba(245, 108, 108, 0.22);
}

.edit-entry:active {
  transform: scale(0.94);
}

/* ---------- 草稿列表 ---------- */

.draft-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 160px;
}

.draft-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  flex-wrap: wrap;
}

.draft-main {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.draft-title {
  font-size: 15px;
}

.draft-time {
  font-size: 12px;
  color: var(--text-muted);
}

.draft-ops {
  display: flex;
  gap: 6px;
}

.pager {
  margin-top: 20px;
  justify-content: center;
}

/* ---------- 移动端（用户反馈④） ---------- */

@media (max-width: 768px) {
  .idea-page {
    /* 右侧 88px 避让 FAB 悬浮球（球常驻右侧居中，否则会盖住卡片内容） */
    padding: 14px 88px 72px 14px;
    max-width: 100%;
  }

  .page-head {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .head-title h1 {
    font-size: 22px;
  }

  .head-actions {
    flex-wrap: wrap;
  }

  .search-box {
    width: auto;
    flex: 1;
    min-width: 140px;
  }

  /* Tab：可横滑，不换行 */
  .tab-bar {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .tab-bar::-webkit-scrollbar { display: none; }

  .tab-btn {
    padding: 9px 13px;
    font-size: 14px;
    white-space: nowrap;
  }

  /* 筛选 chips：整行横向滑动（chips 不压缩不换行，overflow 收在 .filter-row 块级容器内，
     避免 flex-shrink:0 的 group 直接撑破文档宽度——第三轮移动端实测溢出根因） */
  .filter-row {
    flex-wrap: nowrap;
    gap: 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .filter-row::-webkit-scrollbar { display: none; }

  .chip-group,
  .sort-group {
    flex-wrap: nowrap;
    flex-shrink: 0;
  }

  .chip {
    white-space: nowrap;
    padding: 5px 12px;
  }

  .tag-row {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .tag-row::-webkit-scrollbar { display: none; }

  .tag-row-label {
    white-space: nowrap;
    flex-shrink: 0;
  }

  .tag-chip {
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* 卡片：双列/单列自适应 */
  .post-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }

  .feed-waterfall {
    column-width: 150px;
    column-gap: 10px;
  }

  .feed-waterfall .xhs-card {
    margin-bottom: 10px;
  }

  .post-card {
    padding: 12px;
  }

  .xhs-card .card-body {
    padding: 10px 11px 11px;
  }

  .xhs-card .card-title {
    font-size: 14px;
  }

  .card-foot {
    gap: 6px;
    font-size: 11px;
  }

  .stat-btn {
    padding: 4px;
  }

  .draft-row {
    padding: 10px 12px;
  }

  .draft-ops {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

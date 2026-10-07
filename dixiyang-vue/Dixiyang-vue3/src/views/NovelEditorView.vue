<template>
  <div class="editor-layout">
    <!-- 顶栏 -->
    <header class="topbar">
      <div class="topbar-left">
        <button class="nav-btn" title="返回首页" @click="goHome">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
        </button>
        <span class="book-name">{{ novelStore.currentNovel?.title || '小说编辑器' }}</span>
      </div>
      <div class="topbar-center">
        <span v-if="currentChapter" class="chapter-breadcrumb">{{ currentChapter.title }}</span>
      </div>
      <div class="topbar-right">
        <span class="sync-badge" :data-state="syncState">{{ syncLabelShort }}</span>
        <button class="nav-btn" title="切换章节树" @click="toggleTree">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2Z"/></svg>
        </button>
        <button class="nav-btn" title="切换侧栏" @click="toggleSidebar">
          <svg viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M3 4h18v16H3V4zM5 6v12h14V6H5zM15 6h4v12h-4z"/></svg>
        </button>
      </div>
    </header>

    <!-- 移动端抽屉遮罩：点任意处收起目录/侧栏 -->
    <div v-if="drawerVisible" class="drawer-backdrop" @click="closeDrawers" />

    <!-- 三栏主体 -->
    <div class="workspace">
      <div class="col col-tree" :class="{ collapsed: treeCollapsed }">
        <ChapterTree
          :volumes="volumes"
          :chapters="chapterList"
          :active-id="currentChapter?.id ?? null"
          @select="openChapter"
          @create-volume="handleCreateVolume"
          @create-chapter="handleCreateChapter"
          @delete-volume="handleDeleteVolume"
          @delete-chapter="handleDeleteChapter"
        />
      </div>

      <main class="col col-main">
        <ChapterEditor
          v-if="currentChapter"
          ref="editorRef"
          v-model="content"
          :title="title"
          :ghost-text="ghostText"
          :save-hint="saveHint"
          @update:title="onTitleChange"
          @doc-change="onDocChange"
          @accept-ghost="onAcceptGhost"
          @reject-ghost="rejectAI()"
          @ai-trigger="triggerAI"
        />
        <div v-else class="empty-editor">
          <h2>✧ 开始创作</h2>
          <p>从左侧选择章节，或新建一章开始写作。</p>
          <button class="primary-btn" @click="handleCreateChapter">新建章节</button>
        </div>
      </main>

      <div class="col col-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <ChapterSidebar
          :chapter="currentChapter"
          :sync-state="syncState"
          :server-version="serverVersion"
          :is-dirty="isDirty"
          :word-count="content.replace(/\s/g, '').length"
          :ai-state="aiState"
          @save-cloud="saveToCloud"
          @ai-trigger="triggerAI"
        >
          <template #ai-context>
            <AIContextPanel
              ref="ctxPanelRef"
              :novel-id="novelId"
              :characters="characters"
              :timelines="timelines"
              :nodes="storyNodes"
            />
          </template>
        </ChapterSidebar>
      </div>
    </div>

    <ConflictDialog
      v-model="conflictVisible"
      :server-version="conflictInfo.serverVersion"
      :local-version="serverVersion"
      @use-local="resolveConflict('local')"
      @use-remote="resolveConflict('remote')"
      @cancel="conflictVisible = false"
    />

    <DialogHost ref="dialogs" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ChapterTree from '@/components/novel-editor/ChapterTree.vue'
import ChapterEditor from '@/components/novel-editor/ChapterEditor.vue'
import ChapterSidebar, { type SyncState } from '@/components/novel-editor/ChapterSidebar.vue'
import AIContextPanel from '@/components/novel-editor/AIContextPanel.vue'
import ConflictDialog from '@/components/novel-editor/ConflictDialog.vue'
import DialogHost from '@/components/novel-editor/DialogHost.vue'
import { useNovelStore } from '@/stores/novelStore'
import { useChapterDraft } from '@/composables/useChapterDraft'
import { useAICompletion } from '@/composables/useAICompletion'
import {
  listVolumes,
  createVolume,
  deleteVolume,
  listChapters,
  createChapter,
  deleteChapter,
  updateChapter,
  getChapterContent,
  saveChapterContent,
} from '@/api/chapterApi'
import { getAllCharacters } from '@/api/characterApi'
import { getAllTimelines, getAllStoryNodes } from '@/api/timelineApi'
import type { Character, Chapter, Timeline, TimelineNode, Volume } from '@/api/types'
import { getDraft } from '@/utils/draftDB'

const router = useRouter()
const dialogs = ref<InstanceType<typeof DialogHost> | null>(null)
const novelStore = useNovelStore()
const draft = useChapterDraft()
const {
  aiState,
  ghostText,
  bind: bindAI,
  request: requestAI,
  onDocChange: onAIDocChange,
  accept: acceptAI,
  reject: rejectAI,
} = useAICompletion()

const routeId = router.currentRoute.value.params.id as string
const novelId = Number(routeId)

// ---------- 目录数据 ----------
const volumes = ref<Volume[]>([])
const chapters = ref<Chapter[]>([])
const dirtyIds = ref<Set<number>>(new Set())

const chapterList = computed(() =>
  chapters.value.map((c) => ({ ...c, isDirty: dirtyIds.value.has(c.id) })),
)

// ---------- 当前章节 ----------
const currentChapter = ref<Chapter | null>(null)
const content = ref('')
const title = ref('')
const editorRef = ref<InstanceType<typeof ChapterEditor> | null>(null)

// ---------- AI 设定上下文（角色/时间线/事件，供勾选面板） ----------
const characters = ref<Character[]>([])
const timelines = ref<Timeline[]>([])
const storyNodes = ref<TimelineNode[]>([])
const ctxPanelRef = ref<InstanceType<typeof AIContextPanel> | null>(null)

/** 拉取设定数据（失败不阻塞编辑） */
async function loadContextData() {
  try {
    const [charRes, tlRes, nodeRes] = await Promise.all([
      getAllCharacters(novelId),
      getAllTimelines(novelId),
      getAllStoryNodes(novelId),
    ])
    characters.value = charRes.data || []
    timelines.value = tlRes.data || []
    storyNodes.value = nodeRes.data || []
  } catch {
    /* 无网络或无数据时面板显示空态 */
  }
}

const isDirty = ref(false)
const serverVersion = ref(1)
const serverHash = ref('')
const saveCloudState = ref<'idle' | 'uploading' | 'uploaded' | 'conflict' | 'failed'>('idle')

const syncState = computed<SyncState>(() => {
  if (saveCloudState.value === 'uploading') return 'uploading'
  if (saveCloudState.value === 'conflict') return 'conflict'
  if (saveCloudState.value === 'failed') return 'upload-failed'
  if (saveCloudState.value === 'uploaded' && !isDirty.value) return 'uploaded'
  return isDirty.value ? 'local-dirty' : 'local-clean'
})

const syncLabelShort = computed(() => {
  const map: Record<SyncState, string> = {
    'local-clean': '与云端一致',
    'local-dirty': '本地有修改',
    uploading: '正在上传…',
    uploaded: '已保存到云端',
    conflict: '版本冲突',
    'upload-failed': '上传失败',
  }
  return map[syncState.value]
})

const saveHint = computed(() => {
  if (draft.saveState.value === 'saving') return '正在保存到本地…'
  if (draft.saveState.value === 'saved') return '已保存到本地'
  if (draft.saveState.value === 'error') return '本地保存失败'
  return ''
})

// ---------- 目录加载 ----------
async function loadTree() {
  const [volRes, chRes] = await Promise.all([listVolumes(novelId), listChapters(novelId)])
  if (volRes.code === 200) volumes.value = volRes.data || []
  if (chRes.code === 200) chapters.value = chRes.data || []
  // 恢复本地脏标记
  for (const c of chapters.value) {
    const local = await getDraft(c.id)
    if (local?.isDirty) dirtyIds.value.add(c.id)
  }
}

// ---------- 打开章节（本地优先恢复） ----------
async function openChapter(ch: Chapter) {
  if (currentChapter.value?.id === ch.id) return
  await draft.flushSave()

  currentChapter.value = ch
  title.value = ch.title
  serverVersion.value = ch.version
  serverHash.value = ch.content_hash || ''
  isDirty.value = dirtyIds.value.has(ch.id)

  // 取云端正文（失败不阻塞，本地草稿仍可恢复）
  let cloudContent = ''
  try {
    const res = await getChapterContent(ch.id)
    if (res.code === 200 && res.data) cloudContent = res.data.content || ''
  } catch {
    /* 离线时用本地草稿 */
  }

  const loaded = await draft.loadDraft(novelId, ch.id, cloudContent, serverVersion.value, serverHash.value)
  content.value = loaded.content
  isDirty.value = loaded.isDirty
  if (loaded.fromLocal && loaded.isDirty) dirtyIds.value.add(ch.id)
}

// ---------- 本地自动保存 ----------
function onDocChange() {
  if (!currentChapter.value) return
  isDirty.value = true
  dirtyIds.value.add(currentChapter.value.id)
  saveCloudState.value = 'idle'
  draft.scheduleSave({
    chapterId: currentChapter.value.id,
    novelId,
    title: title.value,
    content: content.value,
  })
  onAIDocChange()
}

/** 接受 AI 补全：把幽灵文本插入光标处 */
function onAcceptGhost() {
  const text = acceptAI()
  if (text !== null && editorRef.value) {
    editorRef.value.insertAtCursor(text)
  }
}

/** 手动触发补全：空文档给可见提示，避免"点了没反应"的死代码感 */
function triggerAI() {
  const doc = editorRef.value?.getDoc() ?? ''
  if (!doc.trim()) {
    ElMessage.info('先写几句正文，AI 才能接着帮你续写')
    return
  }
  void requestAI(true)
}

function onTitleChange(t: string) {
  title.value = t
  if (!currentChapter.value) return
  isDirty.value = true
  draft.scheduleSave({
    chapterId: currentChapter.value.id,
    novelId,
    title: t,
    content: content.value,
  })
}

// ---------- 云端保存 ----------
async function saveToCloud(force = false) {
  const ch = currentChapter.value
  if (!ch || saveCloudState.value === 'uploading') return

  saveCloudState.value = 'uploading'
  try {
    await draft.flushSave()

    // 1) 标题变更同步到元数据
    if (title.value !== ch.title) {
      const r = await updateChapter(ch.id, { title: title.value })
      if (r.code === 200) currentChapter.value = { ...ch, title: title.value }
    }

    // 2) 上传正文（后端先做冲突检测）
    const res = await saveChapterContent(ch.id, {
      title: title.value,
      content: content.value,
      clientVersion: serverVersion.value,
      clientHash: serverHash.value,
      force,
    })

    if (res.code === 200 && res.data) {
      if (res.data.hasConflict) {
        saveCloudState.value = 'conflict'
        conflictInfo.value = {
          serverVersion: res.data.serverVersion || 0,
          serverHash: res.data.serverHash || '',
        }
        conflictVisible.value = true
        return
      }
      serverVersion.value = res.data.version
      serverHash.value = res.data.contentHash
      await draft.markSynced(ch.id, res.data.version, res.data.contentHash)
      isDirty.value = false
      dirtyIds.value.delete(ch.id)
      saveCloudState.value = 'uploaded'
      // 同步章节元数据
      currentChapter.value = { ...ch, version: res.data.version, content_hash: res.data.contentHash }
      const idx = chapters.value.findIndex((c) => c.id === ch.id)
      if (idx >= 0) chapters.value[idx] = { ...ch, version: res.data.version, content_hash: res.data.contentHash }
      ElMessage.success('已保存到云端')
    } else {
      saveCloudState.value = 'failed'
      ElMessage.error(res.msg || '保存到云端失败')
    }
  } catch {
    saveCloudState.value = 'failed'
    ElMessage.error('保存到云端失败，请稍后重试')
  }
}

// ---------- 冲突处理 ----------
const conflictVisible = ref(false)
const conflictInfo = ref({ serverVersion: 0, serverHash: '' })

async function resolveConflict(choice: 'local' | 'remote') {
  conflictVisible.value = false
  const ch = currentChapter.value
  if (!ch) return

  if (choice === 'local') {
    // 本地覆盖云端
    await saveToCloud(true)
    return
  }
  // 用云端版本
  try {
    const res = await getChapterContent(ch.id)
    if (res.code === 200 && res.data) {
      content.value = res.data.content || ''
      serverVersion.value = res.data.version
      serverHash.value = res.data.contentHash || ''
      await draft.loadDraft(novelId, ch.id, res.data.content || '', res.data.version, res.data.contentHash || '')
      await draft.markSynced(ch.id, res.data.version, res.data.contentHash || '')
      isDirty.value = false
      dirtyIds.value.delete(ch.id)
      saveCloudState.value = 'idle'
      ElMessage.success('已恢复到云端版本')
    }
  } catch {
    ElMessage.error('获取云端内容失败')
  }
}

// ---------- CRUD ----------
async function handleCreateVolume() {
  const value = await dialogs.value?.prompt({ title: '新建卷', message: '卷名称', defaultValue: '第一卷' })
  if (!value?.trim()) return
  const res = await createVolume(novelId, { title: value.trim() })
  if (res.code === 200 && res.data) volumes.value.push(res.data)
}

async function handleCreateChapter() {
  const value = await dialogs.value?.prompt({
    title: '新建章节',
    message: '章节标题',
    defaultValue: `第${chapters.value.length + 1}章`,
  })
  if (!value?.trim()) return
  const res = await createChapter(novelId, { title: value.trim() })
  if (res.code === 200 && res.data) {
    chapters.value.push(res.data)
    await openChapter(res.data)
  }
}

async function handleDeleteVolume(v: Volume) {
  const ok = await dialogs.value?.confirm({
    title: '删除确认',
    message: `删除卷「${v.title}」？其下章节不会被删除。`,
    danger: true,
  })
  if (!ok) return
  const res = await deleteVolume(v.id)
  if (res.code === 200) {
    volumes.value = volumes.value.filter((x) => x.id !== v.id)
    chapters.value = chapters.value.map((c) =>
      c.volume_id === v.id ? { ...c, volume_id: null } : c,
    )
  }
}

async function handleDeleteChapter(c: Chapter) {
  const ok = await dialogs.value?.confirm({
    title: '删除确认',
    message: `删除章节「${c.title}」？本地与云端正文将一并删除。`,
    danger: true,
  })
  if (!ok) return
  const res = await deleteChapter(c.id)
  if (res.code === 200) {
    chapters.value = chapters.value.filter((x) => x.id !== c.id)
    dirtyIds.value.delete(c.id)
    if (currentChapter.value?.id === c.id) {
      currentChapter.value = null
      content.value = ''
      title.value = ''
    }
  }
}

// ---------- 离开提醒 ----------
function hasUnsavedRemote(): boolean {
  return isDirty.value && syncState.value !== 'uploading'
}

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', onBeforeUnload)
  window.removeEventListener('resize', onWindowResize)
  draft.dispose()
})

function onBeforeUnload(e: BeforeUnloadEvent) {
  void draft.flushSave()
  if (hasUnsavedRemote()) {
    e.preventDefault()
    e.returnValue = '当前章节存在未上传到云端的修改。'
  }
}

onBeforeRouteLeave(async () => {
  await draft.flushSave()
  if (!hasUnsavedRemote()) return true
  const choice = (await dialogs.value?.confirmLeave('当前章节存在未上传到云端的修改。离开前要保存到云端吗？')) ?? 'cancel'
  if (choice === 'save') {
    await saveToCloud()
    return true
  }
  return choice === 'leave'
})

function goHome() {
  router.push('/home')
}

// ---------- 响应式默认值（跨断点才更新，同档位内不覆盖用户手动切换） ----------
type Breakpoint = 'mobile' | 'mid' | 'wide'
let lastBreakpoint: Breakpoint | null = null

function breakpointOf(w: number): Breakpoint {
  return w < 1024 ? 'mobile' : w < 1440 ? 'mid' : 'wide'
}

function applyResponsiveDefaults(force = false) {
  const bp = breakpointOf(window.innerWidth)
  if (!force && bp === lastBreakpoint) return
  lastBreakpoint = bp
  sidebarCollapsed.value = bp !== 'wide'
  treeCollapsed.value = bp !== 'wide'
  isMobile.value = bp === 'mobile'
}

const treeCollapsed = ref(false)
const sidebarCollapsed = ref(false)
const isMobile = ref(false)

/** 移动端：任一抽屉展开即显示遮罩 */
const drawerVisible = computed(() => isMobile.value && (!treeCollapsed.value || !sidebarCollapsed.value))

/** 移动端互斥打开（同一时刻只展示一个抽屉） */
function toggleTree() {
  if (isMobile.value) sidebarCollapsed.value = true
  treeCollapsed.value = !treeCollapsed.value
}
function toggleSidebar() {
  if (isMobile.value) treeCollapsed.value = true
  sidebarCollapsed.value = !sidebarCollapsed.value
}
function closeDrawers() {
  treeCollapsed.value = true
  sidebarCollapsed.value = true
}

function onWindowResize() {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 1024
  if (wasMobile && !isMobile.value) closeDrawers() // 桌面不留残余遮罩
  applyResponsiveDefaults() // 仅跨断点时回默认折叠
}

onMounted(async () => {
  applyResponsiveDefaults(true)
  window.addEventListener('beforeunload', onBeforeUnload)
  window.addEventListener('resize', onWindowResize)
  await novelStore.loadNovel(novelId)
  await Promise.all([loadTree(), loadContextData()])
  bindAI({
    get chapterId() {
      return currentChapter.value?.id ?? 0
    },
    get chapterTitle() {
      return title.value
    },
    getTextBefore: (max) => editorRef.value?.getTextBefore(max) ?? '',
    getTextAfter: (max) => editorRef.value?.getTextAfter(max) ?? '',
    getCursorPos: () => editorRef.value?.getCursorPos() ?? 0,
    getDoc: () => editorRef.value?.getDoc() ?? '',
    getContext: () =>
      ctxPanelRef.value?.getSelection() ?? {
        novelId,
        characterIds: [],
        storyNodeIds: [],
        timelineIds: [],
      },
  })
  const first = chapters.value[0]
  if (first) {
    await openChapter(first)
  }
})
</script>

<style scoped>
.editor-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  /* 半透明 scrim：有背景图时朦胧透出（不干扰创作），无背景图时叠在 body #0d0d0f 上视觉不变。
     必须有 position！否则有背景图时被 #theme-bg（fixed;z-index:0;pointer-events:none，
     body 首子）整层压住 → 看不见但能点。同 404 页历史问题，见 docs/404页被背景图覆盖修复.md */
  background: rgba(13, 13, 15, 0.72);
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
}

/* 顶栏：玻璃条，与两侧栏和稿纸区分 */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 14px;
  border-bottom: 1px solid var(--surface-glass-border);
  background: rgba(10, 10, 12, 0.55);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  flex-shrink: 0;
  z-index: 10;
}
.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.topbar-center {
  flex: 1;
  text-align: center;
  overflow: hidden;
}
.book-name {
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 1px;
}
.chapter-breadcrumb {
  font-size: 0.82rem;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}
.nav-btn:hover {
  background: var(--surface-glass);
  color: var(--text-primary);
}
.nav-btn svg {
  width: 16px;
  height: 16px;
}

.sync-badge {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--surface-glass-border);
  color: var(--text-muted);
}
.sync-badge[data-state='local-dirty'] {
  border-color: var(--warning-border);
  color: var(--warning);
  background: var(--warning-soft);
}
.sync-badge[data-state='uploaded'] {
  border-color: rgba(40, 196, 212, 0.45);
  color: var(--accent-cyan);
}
.sync-badge[data-state='conflict'],
.sync-badge[data-state='upload-failed'] {
  border-color: var(--danger-border);
  color: var(--danger);
  background: var(--danger-soft);
}
.sync-badge[data-state='uploading'] {
  border-color: var(--accent-primary);
  color: var(--accent-secondary);
}

/* 三栏 */
.workspace {
  display: flex;
  flex: 1;
  min-height: 0;
}
.col {
  min-width: 0;
  min-height: 0;
}
.col-tree {
  width: 260px;
  flex-shrink: 0;
  transition: width var(--dur) var(--ease-out), opacity var(--dur) var(--ease-out);
}
.col-tree.collapsed {
  width: 0;
  opacity: 0;
  overflow: hidden;
}
.col-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  /* 编辑区 = 浮起的"稿纸"：比两侧亮一档 + 圆角 + 阴影，制造焦点与区分度 */
  background: rgba(26, 26, 31, 0.4);
  margin: 10px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 0 14px 44px rgba(0, 0, 0, 0.42);
  overflow: hidden;
}
.col-sidebar {
  width: 280px;
  flex-shrink: 0;
  transition: width var(--dur) var(--ease-out), opacity var(--dur) var(--ease-out);
}
.col-sidebar.collapsed {
  width: 0;
  opacity: 0;
  overflow: hidden;
}

.empty-editor {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
}
.empty-editor h2 {
  font-size: 1.4rem;
  letter-spacing: 3px;
  color: var(--text-secondary);
  margin: 0;
}
.empty-editor p {
  color: var(--text-muted);
  font-size: 0.9rem;
}
.primary-btn {
  padding: 9px 22px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent-primary);
  color: #fff;
  font-size: 0.88rem;
  cursor: pointer;
  transition: opacity var(--dur-fast) var(--ease-out);
}
.primary-btn:hover {
  opacity: 0.85;
}

/* 响应式：1366~1440 自动收窄侧栏（默认值由 JS 设置，这里做补充） */
@media (max-width: 1280px) {
  .col-tree {
    width: 220px;
  }
  .col-sidebar {
    width: 250px;
  }
}

/* ========== 移动端（≤1024px）：树/侧栏改为覆盖式抽屉 ==========
   宽度不再是并排挤压，而是 fixed 覆盖在编辑区之上；折叠态滑出视口。
   遮罩 .drawer-backdrop 点击任意处收起。 */
@media (max-width: 1024px) {
  .col-tree,
  .col-sidebar {
    position: fixed;
    top: 48px; /* 顶栏下方 */
    bottom: 0;
    width: min(82vw, 300px);
    z-index: 40;
    opacity: 1; /* 覆盖默认折叠的 opacity:0，显隐交给 transform */
    overflow: visible;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    transition: transform var(--dur) var(--ease-out);
  }
  .col-tree {
    left: 0;
    border-right: 1px solid var(--border-color);
  }
  .col-sidebar {
    right: 0;
    border-left: 1px solid var(--border-color);
  }
  /* 折叠 = 滑出视口（覆盖桌面版 .collapsed 的 width:0/opacity:0） */
  .col-tree.collapsed {
    width: min(82vw, 300px);
    transform: translateX(-105%);
  }
  .col-sidebar.collapsed {
    width: min(82vw, 300px);
    transform: translateX(105%);
  }

  .drawer-backdrop {
    position: fixed;
    inset: 48px 0 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 35;
    -webkit-tap-highlight-color: transparent;
  }

  /* 顶栏窄屏：隐藏面包屑与状态胶囊（右侧抽栏内有完整状态），书名截断 */
  .topbar-center,
  .topbar .sync-badge {
    display: none;
  }
  .book-name {
    max-width: 46vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>

<template>
  <div class="engine-container">
    <FloatingNav />

    <main class="main-stage">
      <NovelPageHeader page-title="时间线管理" />

      <div class="timeline-toolbar">
        <div class="toolbar-left">
          <select class="timeline-select glass-sm" v-model="selectedTimelineId" @change="onTimelineChange">
            <option v-for="tl in timelines" :key="tl.id" :value="tl.id">{{ tl.name }}</option>
          </select>
          <button class="btn-icon" @click="showCreateTimeline = true" title="新建时间线">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
          </button>
          <button class="btn-icon btn-danger" @click="confirmDeleteTimeline" v-if="selectedTimelineId" title="删除时间线">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
          </button>
        </div>
        <div class="toolbar-right">
          <div class="mode-switcher">
            <button v-for="mode in modes" :key="mode.value" class="mode-btn" :class="{ active: currentMode === mode.value }" @click="currentMode = mode.value">
              {{ mode.label }}
            </button>
          </div>
          <button class="back-btn" @click="router.back()">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
            返回
          </button>
        </div>
      </div>

      <div class="filter-bar glass-sm">
        <div class="type-tags">
          <button v-for="type in eventTypes" :key="type.value" class="type-tag" :class="{ active: selectedTypes.includes(type.value) }" :style="{ '--tag-color': type.color }" @click="toggleType(type.value)">
            <span>{{ type.icon }}</span> {{ type.label }}
          </button>
        </div>
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <input type="text" placeholder="搜索事件..." v-model="searchQuery" />
        </div>
      </div>

      <div v-if="allCharacters.length > 0" class="character-bar glass-sm">
        <span class="bar-label">角色筛选</span>
        <div class="char-tags">
          <button v-for="char in allCharacters" :key="char" class="char-tag" :class="{ active: selectedCharacters.includes(char) }" @click="toggleCharacter(char)">{{ char }}</button>
        </div>
      </div>

      <div class="timeline-content">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载时间线...</p>
        </div>

        <div v-else-if="!selectedTimelineId" class="empty-state">
          <p>请先选择或创建一个时间线</p>
          <button class="btn-primary" @click="showCreateTimeline = true">创建第一个时间线</button>
        </div>

        <div v-else-if="filteredNodes.length === 0 && !creatingNode" class="empty-state">
          <p>暂无事件节点</p>
          <button class="btn-primary" @click="startCreateNode">添加第一个事件</button>
        </div>

        <div v-else class="track-wrapper">
          <div class="track-line"></div>

          <div v-for="(node, index) in filteredNodes" :key="node.id" class="timeline-node" :style="{ animationDelay: `${index * 0.05}s` }">
            <div class="node-dot" :class="node.eventType || 'default'"></div>
            <div class="node-card glass-card">
              <div class="node-header">
                <span v-if="editingNodeId !== node.id" class="node-date editable" @click.stop="startEditField(node, 'date')">{{ node.eventDate || '未知时间' }}</span>
                <input v-else-if="editingField === 'date'" class="inline-input date-input" v-model="editValue" @blur="saveField(node)" @keyup.enter="saveField(node)" @keyup.escape="cancelEdit" ref="dateInputRef" />
                <div class="node-badges">
                  <select v-if="editingNodeId === node.id && editingField === 'type'" class="inline-select" v-model="editValue" @change="saveField(node)">
                    <option value="birth">出生</option>
                    <option value="war">战争</option>
                    <option value="politics">政治</option>
                    <option value="major">转折</option>
                  </select>
                  <span v-else class="event-type-tag" :class="node.eventType" @click.stop="startEditField(node, 'type')" :title="'点击修改类型'">{{ eventTypeLabel(node.eventType) }}</span>
                  <select v-if="editingNodeId === node.id && editingField === 'importance'" class="inline-select imp-select" v-model.number="editValue" @change="saveField(node)">
                    <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
                  </select>
                  <span v-else class="importance-badge" :class="`lv-${node.importance || 3}`" @click.stop="startEditField(node, 'importance')" :title="'点击修改重要性'">{{ importanceLabel(node.importance) }}</span>
                </div>
              </div>

              <h3 v-if="editingNodeId !== node.id" class="node-title editable" @click.stop="startEditField(node, 'title')">{{ node.title }}</h3>
              <input v-else-if="editingField === 'title'" class="inline-input title-input" v-model="editValue" @blur="saveField(node)" @keyup.enter="saveField(node)" @keyup.escape="cancelEdit" ref="titleInputRef" />

              <p v-if="editingNodeId !== node.id" class="node-summary editable" @click.stop="startEditField(node, 'content')">{{ truncateText(node.content, 80) }}</p>
              <textarea v-else-if="editingField === 'content'" class="inline-textarea" v-model="editValue" @blur="saveField(node)" @keyup.escape="cancelEdit" rows="3" ref="contentInputRef"></textarea>

              <div class="node-actions">
                <button class="btn-sm btn-expand" @click.stop="toggleExpand(node.id)">{{ expandedId === node.id ? '收起' : '展开' }}</button>
                <button class="btn-sm btn-delete" @click.stop="confirmDeleteNode(node)">删除</button>
              </div>

              <Transition name="expand">
                <div v-if="expandedId === node.id" class="node-detail">
                  <div v-if="node.characterNames?.length" class="detail-chars">
                    <span v-for="c in node.characterNames" :key="c" class="detail-char">{{ c }}</span>
                  </div>
                  <div v-if="node.tags?.length" class="detail-tags">
                    <span v-for="t in node.tags" :key="t" class="detail-tag">{{ t }}</span>
                  </div>
                </div>
              </Transition>
            </div>
          </div>

          <div v-if="creatingNode" class="timeline-node">
            <div class="node-dot default"></div>
            <div class="node-card glass-card creating-card">
              <div class="node-header">
                <input class="inline-input date-input" v-model="newNode.eventDate" placeholder="时间，如：木叶1年" ref="newDateRef" />
                <select class="inline-select" v-model="newNode.eventType">
                  <option value="birth">出生</option>
                  <option value="war">战争</option>
                  <option value="politics">政治</option>
                  <option value="major">转折</option>
                </select>
              </div>
              <input class="inline-input title-input" v-model="newNode.title" placeholder="事件标题" />
              <textarea class="inline-textarea" v-model="newNode.content" placeholder="事件描述（可选）" rows="2"></textarea>
              <div class="new-node-meta">
                <input class="inline-input sm" v-model="newNode.characterNames" placeholder="角色名，逗号分隔" />
                <input class="inline-input sm" v-model="newNode.tags" placeholder="标签，逗号分隔" />
                <select class="inline-select imp-select" v-model.number="newNode.importance">
                  <option v-for="n in 5" :key="n" :value="n">重要性 {{ n }}</option>
                </select>
              </div>
              <div class="node-actions">
                <button class="btn-sm btn-save" @click="saveNewNode" :disabled="!newNode.title">保存</button>
                <button class="btn-sm btn-cancel" @click="cancelCreateNode">取消</button>
              </div>
            </div>
          </div>

          <div v-if="selectedTimelineId && !creatingNode" class="add-node-btn" @click="startCreateNode">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            添加新事件
          </div>
        </div>
      </div>

      <div class="legend-fixed glass-sm">
        <span class="legend-dot birth"></span> 出生
        <span class="legend-dot war"></span> 战争
        <span class="legend-dot politics"></span> 政治
        <span class="legend-dot major"></span> 转折
      </div>
    </main>

    <el-dialog v-model="showCreateTimeline" title="新建时间线" width="420px">
      <el-form label-position="top">
        <el-form-item label="时间线名称" required>
          <el-input v-model="newTimelineName" placeholder="如：木叶纪年" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newTimelineDesc" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTimeline = false">取消</el-button>
        <el-button type="primary" @click="createNewTimeline" :disabled="!newTimelineName.trim()">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDeleteNodeDialog" title="确认删除" width="400px">
      <p>确定要删除事件「{{ deleteTarget?.title }}」吗？此操作不可恢复。</p>
      <template #footer>
        <el-button @click="showDeleteNodeDialog = false">取消</el-button>
        <el-button type="danger" @click="doDeleteNode" :loading="isDeleting">确认删除</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDeleteTimelineDialog" title="确认删除时间线" width="400px">
      <p>确定要删除该时间线吗？时间线下的所有事件也会被删除。</p>
      <template #footer>
        <el-button @click="showDeleteTimelineDialog = false">取消</el-button>
        <el-button type="danger" @click="doDeleteTimeline" :loading="isDeleting">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import FloatingNav from '@/components/FloatingNav.vue'
import NovelPageHeader from '@/components/NovelPageHeader.vue'
import { useNovelStore } from '@/stores/novelStore'
import {
  getAllTimelines, getStoryNodesByTimeline,
  createTimeline, updateTimeline, deleteTimeline as deleteTimelineApi,
  createStoryNode, updateStoryNode, deleteStoryNode
} from '@/api/timelineApi'
import type { Timeline, TimelineNode } from '@/api/types'
import { EVENT_TYPES, eventTypeLabel } from '@/utils/storyMappings'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

const isLoading = ref(true)
const timelines = ref<Timeline[]>([])
const selectedTimelineId = ref<number | null>(null)
const nodes = ref<TimelineNode[]>([])
const currentMode = ref<'story' | 'full' | 'character'>('story')
const selectedTypes = ref<string[]>([])
const selectedCharacters = ref<string[]>([])
const expandedId = ref<number | null>(null)
const searchQuery = ref('')

const editingNodeId = ref<number | null>(null)
const editingField = ref<string>('')
const editValue = ref<any>('')
const titleInputRef = ref<HTMLInputElement | null>(null)
const dateInputRef = ref<HTMLInputElement | null>(null)
const contentInputRef = ref<HTMLTextAreaElement | null>(null)

const creatingNode = ref(false)
const newNode = ref({ title: '', content: '', eventDate: '', eventType: 'major', importance: 3, characterNames: '', tags: '' })
const newDateRef = ref<HTMLInputElement | null>(null)

const showCreateTimeline = ref(false)
const newTimelineName = ref('')
const newTimelineDesc = ref('')

const showDeleteNodeDialog = ref(false)
const deleteTarget = ref<TimelineNode | null>(null)
const showDeleteTimelineDialog = ref(false)
const isDeleting = ref(false)

const modes = [
  { value: 'story' as const, label: '故事模式' },
  { value: 'full' as const, label: '全量模式' },
  { value: 'character' as const, label: '角色模式' }
]

const eventTypes = EVENT_TYPES

const parseJsonField = (v: any): string[] => {
  if (Array.isArray(v)) return v
  if (typeof v === 'string' && v) { try { const p = JSON.parse(v); return Array.isArray(p) ? p : [] } catch { return [] } }
  return []
}

const allCharacters = computed(() => {
  const s = new Set<string>()
  nodes.value.forEach(n => { const arr = parseJsonField(n.characterNames); arr.forEach((c: string) => s.add(c)) })
  return Array.from(s)
})

const filteredNodes = computed(() => {
  let r = [...nodes.value]
  if (currentMode.value === 'story') r = r.filter(n => (n.importance || 3) >= 3)
  if (selectedTypes.value.length) r = r.filter(n => n.eventType && selectedTypes.value.includes(n.eventType))
  if (selectedCharacters.value.length) {
    r = r.filter(n => { const arr = parseJsonField(n.characterNames); return arr.some((c: string) => selectedCharacters.value.includes(c)) })
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter(n => n.title?.toLowerCase().includes(q) || n.content?.toLowerCase().includes(q) || n.eventDate?.toLowerCase().includes(q))
  }
  r.sort((a, b) => (a.eventDate?.match(/\d+/)?.[0] || '0').localeCompare(b.eventDate?.match(/\d+/)?.[0] || '0', undefined, { numeric: true }))
  return r
})

const toggleType = (t: string) => { const i = selectedTypes.value.indexOf(t); i === -1 ? selectedTypes.value.push(t) : selectedTypes.value.splice(i, 1) }
const toggleCharacter = (c: string) => { const i = selectedCharacters.value.indexOf(c); i === -1 ? selectedCharacters.value.push(c) : selectedCharacters.value.splice(i, 1) }
const toggleExpand = (id: number) => { expandedId.value = expandedId.value === id ? null : id }
const truncateText = (t: string, max: number) => t && t.length > max ? t.substring(0, max) + '...' : t || ''
const importanceLabel = (v?: number) => ({ 1: '次要', 2: '一般', 3: '重要', 4: '关键', 5: '核心' })[v || 3] || '重要'

const refreshNodes = async () => {
  if (!selectedTimelineId.value) { nodes.value = []; return }
  try {
    const res = await getStoryNodesByTimeline(selectedTimelineId.value)
    const raw = (res as any).data
    nodes.value = (Array.isArray(raw) ? raw : []).map((n: any) => ({
      ...n,
      characterNames: n.characterNames,
      tags: n.tags,
      importance: n.importance || 3
    }))
  } catch (e) { console.error(e) }
}

const onTimelineChange = () => { expandedId.value = null; editingNodeId.value = null; creatingNode.value = false; refreshNodes() }

const startEditField = (node: TimelineNode, field: string) => {
  editingNodeId.value = node.id
  editingField.value = field
  if (field === 'title') editValue.value = node.title || ''
  else if (field === 'date') editValue.value = node.eventDate || ''
  else if (field === 'content') editValue.value = node.content || ''
  else if (field === 'type') editValue.value = node.eventType || 'major'
  else if (field === 'importance') editValue.value = node.importance || 3
  nextTick(() => {
    if (field === 'title') titleInputRef.value?.focus()
    else if (field === 'date') dateInputRef.value?.focus()
    else if (field === 'content') contentInputRef.value?.focus()
  })
}

const cancelEdit = () => { editingNodeId.value = null; editingField.value = '' }

const saveField = async (node: TimelineNode) => {
  const dto: any = {}
  if (editingField.value === 'title') dto.title = editValue.value
  else if (editingField.value === 'date') dto.eventDate = editValue.value
  else if (editingField.value === 'content') dto.content = editValue.value
  else if (editingField.value === 'type') dto.eventType = editValue.value
  else if (editingField.value === 'importance') dto.importance = editValue.value
  try {
    await updateStoryNode(node.id, dto)
    Object.assign(node, dto)
  } catch (e) { console.error(e) }
  cancelEdit()
}

const startCreateNode = () => {
  creatingNode.value = true
  newNode.value = { title: '', content: '', eventDate: '', eventType: 'major', importance: 3, characterNames: '', tags: '' }
  nextTick(() => newDateRef.value?.focus())
}

const cancelCreateNode = () => { creatingNode.value = false }

const saveNewNode = async () => {
  if (!newNode.value.title || !selectedTimelineId.value) return
  const novelId = Number(route.params.novelId)
  const payload = {
    novelId, timelineId: selectedTimelineId.value,
    title: newNode.value.title, content: newNode.value.content,
    eventDate: newNode.value.eventDate, eventType: newNode.value.eventType,
    importance: newNode.value.importance,
    characterNames: newNode.value.characterNames ? JSON.stringify(newNode.value.characterNames.split(/[,，]/).map(s => s.trim()).filter(Boolean)) : '[]',
    tags: newNode.value.tags ? JSON.stringify(newNode.value.tags.split(/[,，]/).map(s => s.trim()).filter(Boolean)) : '[]'
  }
  try {
    await createStoryNode(payload)
    creatingNode.value = false
    await refreshNodes()
    ElMessage.success('创建成功')
  } catch (e) { console.error(e) }
}

const confirmDeleteNode = (node: TimelineNode) => { deleteTarget.value = node; showDeleteNodeDialog.value = true }
const doDeleteNode = async () => {
  if (!deleteTarget.value) return
  isDeleting.value = true
  try {
    await deleteStoryNode(deleteTarget.value.id)
    showDeleteNodeDialog.value = false
    await refreshNodes()
    ElMessage.success('删除成功')
  } catch (e) { console.error(e) }
  finally { isDeleting.value = false }
}

const createNewTimeline = async () => {
  if (!newTimelineName.value.trim()) return
  const novelId = Number(route.params.novelId)
  try {
    const res = await createTimeline({ novelId, name: newTimelineName.value.trim(), description: newTimelineDesc.value.trim() || undefined })
    const created = (res as any).data
    timelines.value.push(created)
    selectedTimelineId.value = created.id
    showCreateTimeline.value = false
    newTimelineName.value = ''
    newTimelineDesc.value = ''
    await onTimelineChange()
    ElMessage.success('时间线创建成功')
  } catch (e) { console.error(e) }
}

const confirmDeleteTimeline = () => { showDeleteTimelineDialog.value = true }
const doDeleteTimeline = async () => {
  if (!selectedTimelineId.value) return
  isDeleting.value = true
  try {
    await deleteTimelineApi(selectedTimelineId.value)
    timelines.value = timelines.value.filter(t => t.id !== selectedTimelineId.value)
    selectedTimelineId.value = timelines.value.length ? timelines.value[0].id : null
    showDeleteTimelineDialog.value = false
    await onTimelineChange()
    ElMessage.success('删除成功')
  } catch (e) { console.error(e) }
  finally { isDeleting.value = false }
}

onMounted(async () => {
  const novelId = Number(route.params.novelId)
  if (!novelId) return
  novelStore.loadNovel(novelId)
  try {
    isLoading.value = true
    const tlRes = await getAllTimelines(novelId)
    timelines.value = (tlRes as any).data || []
    if (timelines.value.length) {
      selectedTimelineId.value = timelines.value[0].id
      await refreshNodes()
    }
  } catch (e) { console.error(e) }
  finally { isLoading.value = false }
})
</script>

<style scoped>
.engine-container { min-height: 100vh; background: transparent; color: var(--text-primary); position: relative; font-family: 'Inter', system-ui, -apple-system, sans-serif; }
.main-stage { position: relative; z-index: 1; padding: 80px 60px 120px; max-width: 1100px; margin: 0 auto; }

.timeline-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.toolbar-left { display: flex; align-items: center; gap: 8px; }
.toolbar-right { display: flex; align-items: center; gap: 12px; }
.timeline-select { padding: 8px 14px; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; color: var(--text-primary); font-size: 0.9rem; outline: none; min-width: 160px; cursor: pointer; }
.timeline-select:focus { border-color: var(--neon-blue); }
.btn-icon { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: all 0.3s; }
.btn-icon:hover { border-color: var(--neon-blue); color: var(--neon-blue); }
.btn-icon.btn-danger:hover { border-color: #ef4444; color: #ef4444; }

.mode-switcher { display: flex; gap: 4px; }
.mode-btn { padding: 6px 14px; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer; transition: all 0.3s; }
.mode-btn:hover { border-color: var(--neon-blue); color: var(--text-primary); }
.mode-btn.active { background: linear-gradient(135deg, var(--neon-blue), var(--neon-cyan)); color: white; border-color: transparent; }

.filter-bar { display: flex; gap: 16px; align-items: center; padding: 12px 20px; margin-bottom: 16px; flex-wrap: wrap; }
.type-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.type-tag { display: flex; align-items: center; gap: 4px; padding: 5px 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--glass-border); border-radius: 20px; color: var(--text-secondary); font-size: 0.85rem; transition: all 0.3s; cursor: pointer; }
.type-tag:hover { border-color: var(--tag-color); color: var(--tag-color); }
.type-tag.active { background: var(--tag-color); border-color: var(--tag-color); color: white; }
.search-box { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 180px; }
.search-box svg { color: var(--text-muted); flex-shrink: 0; }
.search-box input { flex: 1; padding: 8px 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--glass-border); border-radius: 8px; color: var(--text-primary); font-size: 0.9rem; outline: none; transition: all 0.3s; }
.search-box input:focus { border-color: var(--neon-blue); }
.search-box input::placeholder { color: var(--text-muted); }

.character-bar { display: flex; align-items: center; gap: 12px; padding: 10px 20px; margin-bottom: 20px; flex-wrap: wrap; }
.bar-label { font-size: 0.85rem; color: var(--text-muted); flex-shrink: 0; }
.char-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.char-tag { padding: 4px 10px; background: rgba(255,255,255,0.04); border: 1px solid var(--glass-border); border-radius: 16px; color: var(--text-secondary); font-size: 0.8rem; cursor: pointer; transition: all 0.3s; }
.char-tag:hover { border-color: var(--neon-cyan); color: var(--neon-cyan); }
.char-tag.active { background: var(--neon-cyan); border-color: var(--neon-cyan); color: white; }

.loading-state { display: flex; flex-direction: column; align-items: center; padding: 100px 20px; color: var(--text-muted); }
.spinner { width: 40px; height: 40px; border: 3px solid var(--glass-border); border-top-color: var(--neon-blue); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: 80px 20px; color: var(--text-muted); }
.btn-primary { margin-top: 16px; padding: 10px 24px; background: linear-gradient(135deg, var(--neon-blue), var(--neon-cyan)); color: white; border: none; border-radius: 8px; font-size: 0.95rem; cursor: pointer; transition: all 0.3s; }
.btn-primary:hover { box-shadow: 0 4px 20px rgba(59,130,246,0.3); }

.track-wrapper { position: relative; padding-left: 40px; }
.track-line { position: absolute; left: 11px; top: 0; bottom: 0; width: 2px; background: linear-gradient(180deg, var(--neon-blue), var(--neon-cyan), var(--neon-purple)); opacity: 0.3; }
.timeline-node { position: relative; margin-bottom: 16px; animation: fadeInUp 0.4s ease forwards; opacity: 0; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.node-dot { position: absolute; left: -33px; top: 18px; width: 14px; height: 14px; border-radius: 50%; z-index: 2; border: 2px solid var(--surface-page); }
.node-dot.birth { background: #3b82f6; box-shadow: 0 0 10px rgba(59,130,246,0.5); }
.node-dot.war { background: #ef4444; box-shadow: 0 0 10px rgba(239,68,68,0.5); }
.node-dot.politics { background: #a855f7; box-shadow: 0 0 10px rgba(168,85,247,0.5); }
.node-dot.major { background: #10b981; box-shadow: 0 0 10px rgba(16,185,129,0.5); }
.node-dot.default { background: #6b7280; }

.node-card { padding: 16px 20px; transition: all 0.3s; }
.node-card:hover { border-color: var(--neon-blue); box-shadow: 0 4px 20px rgba(59,130,246,0.15); }
.node-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px; }
.node-date { font-size: 0.85rem; color: var(--neon-cyan); font-weight: 600; }
.node-badges { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.importance-badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 8px; cursor: pointer; }
.importance-badge:hover { opacity: 0.8; }
.importance-badge.lv-1 { background: rgba(107,114,128,0.15); color: #9ca3af; }
.importance-badge.lv-2 { background: rgba(59,130,246,0.15); color: #60a5fa; }
.importance-badge.lv-3 { background: rgba(16,185,129,0.15); color: #34d399; }
.importance-badge.lv-4 { background: rgba(245,158,11,0.15); color: #fbbf24; }
.importance-badge.lv-5 { background: rgba(239,68,68,0.15); color: #f87171; }
.event-type-tag { font-size: 0.75rem; padding: 2px 8px; border-radius: 8px; cursor: pointer; }
.event-type-tag:hover { opacity: 0.8; }
.event-type-tag.birth { background: rgba(59,130,246,0.15); color: #60a5fa; }
.event-type-tag.war { background: rgba(239,68,68,0.15); color: #f87171; }
.event-type-tag.politics { background: rgba(168,85,247,0.15); color: #c084fc; }
.event-type-tag.major { background: rgba(16,185,129,0.15); color: #34d399; }

.node-title { font-size: 1rem; font-weight: 600; color: var(--text-primary); margin: 0 0 4px 0; }
.node-summary { font-size: 0.85rem; color: var(--text-muted); margin: 0; line-height: 1.5; }
.editable { cursor: pointer; border-radius: 4px; padding: 2px 4px; margin: -2px -4px; transition: background 0.2s; }
.editable:hover { background: rgba(59,130,246,0.08); }

.inline-input { width: 100%; padding: 6px 10px; background: rgba(255,255,255,0.06); border: 1px solid var(--neon-blue); border-radius: 6px; color: var(--text-primary); font-size: 0.9rem; outline: none; font-family: inherit; }
.inline-input.title-input { font-size: 1rem; font-weight: 600; }
.inline-input.date-input { width: auto; min-width: 120px; font-size: 0.85rem; }
.inline-input.sm { font-size: 0.8rem; padding: 4px 8px; }
.inline-textarea { width: 100%; padding: 8px 10px; background: rgba(255,255,255,0.06); border: 1px solid var(--neon-blue); border-radius: 6px; color: var(--text-primary); font-size: 0.85rem; outline: none; resize: vertical; font-family: inherit; line-height: 1.5; }
.inline-select { padding: 4px 8px; background: rgba(255,255,255,0.06); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-primary); font-size: 0.8rem; outline: none; cursor: pointer; }
.inline-select.imp-select { width: auto; }

.node-actions { display: flex; gap: 8px; margin-top: 10px; }
.btn-sm { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; border: 1px solid var(--glass-border); background: transparent; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; }
.btn-expand:hover { border-color: var(--neon-blue); color: var(--neon-blue); }
.btn-delete:hover { border-color: #ef4444; color: #ef4444; }
.btn-save { background: var(--neon-blue); border-color: var(--neon-blue); color: white; }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-cancel:hover { border-color: var(--text-muted); color: var(--text-muted); }

.creating-card { border-color: var(--neon-cyan); }
.new-node-meta { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }

.add-node-btn { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 16px; padding: 14px; border: 2px dashed var(--glass-border); border-radius: 12px; color: var(--text-muted); font-size: 0.9rem; cursor: pointer; transition: all 0.3s; }
.add-node-btn:hover { border-color: var(--neon-blue); color: var(--neon-blue); }

.node-detail { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--glass-border); }
.detail-chars { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.detail-char { font-size: 0.75rem; padding: 2px 8px; background: rgba(6,182,212,0.12); border: 1px solid rgba(6,182,212,0.25); border-radius: 10px; color: var(--neon-cyan); }
.detail-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.detail-tag { font-size: 0.7rem; padding: 2px 8px; background: rgba(168,85,247,0.12); border: 1px solid rgba(168,85,247,0.25); border-radius: 10px; color: var(--neon-purple); }

.expand-enter-active, .expand-leave-active { transition: all 0.25s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; margin-top: 0; padding-top: 0; overflow: hidden; }
.expand-enter-to, .expand-leave-from { max-height: 500px; }

.legend-fixed { position: fixed; bottom: 24px; right: 24px; padding: 10px 16px; display: flex; gap: 12px; align-items: center; font-size: 0.8rem; color: var(--text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-dot.birth { background: #3b82f6; }
.legend-dot.war { background: #ef4444; }
.legend-dot.politics { background: #a855f7; }
.legend-dot.major { background: #10b981; }

@media (max-width: 1024px) { .main-stage { padding: 60px 30px 100px; } }
@media (max-width: 768px) {
  .main-stage { padding: 40px 16px 80px; }
  .track-wrapper { padding-left: 24px; }
  .node-dot { left: -21px; width: 10px; height: 10px; }
  .track-line { left: 5px; }
  .timeline-toolbar { flex-direction: column; align-items: stretch; }
  .toolbar-left, .toolbar-right { justify-content: center; }
}
</style>

<template>
  <aside class="chapter-tree">
    <div class="tree-header">
      <span class="tree-title">目录</span>
      <div class="tree-actions">
        <button class="icon-btn" title="新建卷" @click="$emit('create-volume')">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M13 19C13 19.34 13.04 19.67 13.09 20H4C2.9 20 2 19.11 2 18V6C2 4.89 2.89 4 4 4H10L12 6H20C21.1 6 22 6.89 22 8V13.81C21.39 13.46 20.72 13.22 20 13.09V8H4V18H13.09C13.04 18.33 13 18.66 13 19M20 18V15H18V18H15V20H18V23H20V20H23V18H20Z"/></svg>
        </button>
        <button class="icon-btn" title="新建章节" @click="$emit('create-chapter')">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m-1 15h-2v-2h2v2m0-4h-2V9h2v4m-4 4h-2v-2h2v2m0-4h-2V9h2v4m8 4h-2v-2h2v2m0-4h-2V9h2v4Z"/></svg>
        </button>
      </div>
    </div>

    <div class="tree-search">
      <input v-model="keyword" placeholder="搜索章节…" />
    </div>

    <div class="tree-body" @contextmenu.prevent>
      <div v-if="!filteredTree.length" class="tree-empty">暂无章节</div>

      <template v-for="group in filteredTree" :key="group.volume?.id ?? 0">
        <div v-if="group.volume" class="volume-row">
          <span class="volume-title">{{ group.volume.title }}</span>
          <span class="volume-count">{{ group.chapters.length }}</span>
          <button class="mini-btn" title="删除卷" @click.stop="$emit('delete-volume', group.volume)">
            <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12Z"/></svg>
          </button>
        </div>

        <div
          v-for="ch in group.chapters"
          :key="ch.id"
          class="chapter-row"
          :class="{ active: ch.id === activeId }"
          @click="$emit('select', ch)"
        >
          <span class="chapter-title">{{ ch.title }}</span>
          <span v-if="ch.isDirty" class="dirty-dot" title="有未上传的修改"></span>
          <button class="mini-btn danger" title="删除章节" @click.stop="$emit('delete-chapter', ch)">
            <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12Z"/></svg>
          </button>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Chapter, Volume } from '@/api/types'

const props = defineProps<{
  volumes: Volume[]
  chapters: (Chapter & { isDirty?: boolean })[]
  activeId: number | null
}>()

defineEmits<{
  select: [chapter: Chapter]
  'create-volume': []
  'create-chapter': []
  'delete-volume': [volume: Volume]
  'delete-chapter': [chapter: Chapter]
}>()

const keyword = ref('')

interface TreeGroup {
  volume: Volume | null
  chapters: (Chapter & { isDirty?: boolean })[]
}

const filteredTree = computed<TreeGroup[]>(() => {
  const kw = keyword.value.trim().toLowerCase()
  const match = (c: Chapter) => !kw || c.title.toLowerCase().includes(kw)

  const groups: TreeGroup[] = []
  const loose = props.chapters.filter((c) => !c.volume_id && match(c))
  if (loose.length) groups.push({ volume: null, chapters: loose })

  for (const v of [...props.volumes].sort((a, b) => a.sort_order - b.sort_order)) {
    const list = props.chapters.filter((c) => c.volume_id === v.id && match(c))
    if (!kw || list.length) groups.push({ volume: v, chapters: list })
  }
  return groups
})
</script>

<style scoped>
.chapter-tree {
  display: flex;
  flex-direction: column;
  height: 100%;
  /* 玻璃面板：背景图透出但被 blur 糊掉，可读且与"稿纸"编辑区区分 */
  background: rgba(12, 14, 19, 0.45);
  backdrop-filter: blur(18px) saturate(1.15);
  -webkit-backdrop-filter: blur(18px) saturate(1.15);
  border-right: 1px solid var(--surface-glass-border);
  min-width: 0;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 8px;
}
.tree-title {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-secondary);
}
.tree-actions {
  display: flex;
  gap: 4px;
}

.icon-btn,
.mini-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all var(--dur-fast) var(--ease-out);
}
.icon-btn {
  width: 26px;
  height: 26px;
}
.icon-btn svg {
  width: 15px;
  height: 15px;
}
.icon-btn:hover {
  background: var(--accent-soft);
  color: var(--accent-primary);
}
.mini-btn {
  width: 22px;
  height: 22px;
  opacity: 0;
}
.mini-btn svg {
  width: 13px;
  height: 13px;
}
.chapter-row:hover .mini-btn,
.volume-row:hover .mini-btn {
  opacity: 1;
}
/* 键盘可达：焦点落在按钮/所在行内时必须可见（原来 focus 也隐藏，看不见却能点） */
.chapter-row:focus-within .mini-btn,
.volume-row:focus-within .mini-btn,
.mini-btn:focus-visible {
  opacity: 1;
}
/* 触屏无 hover：常显半透明，避免"看不见但能点/点一下才出现" */
@media (hover: none) {
  .mini-btn {
    opacity: 0.6;
  }
}
.mini-btn.danger:hover {
  background: var(--danger-soft);
  color: var(--danger);
}
.mini-btn:hover {
  background: var(--surface-glass);
  color: var(--text-primary);
}

.tree-search {
  padding: 0 12px 10px;
}
.tree-search input {
  width: 100%;
  padding: 6px 10px;
  font-size: 0.8rem;
  background: var(--surface-input);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  color: var(--text-on-input, var(--text-primary));
  outline: none;
}
.tree-search input:focus {
  border-color: var(--accent-primary);
}
.tree-search input::placeholder {
  color: var(--text-disabled);
}

.tree-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 16px;
}

.tree-empty {
  text-align: center;
  color: var(--text-disabled);
  font-size: 0.82rem;
  padding: 32px 0;
}

.volume-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 8px 4px;
  margin-top: 6px;
  border-top: 1px dashed var(--border-color);
}
.volume-row:first-child {
  border-top: none;
  margin-top: 0;
}
.volume-title {
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 1px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.volume-count {
  font-size: 0.7rem;
  color: var(--text-disabled);
}

.chapter-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--dur-fast) var(--ease-out);
}
.chapter-row:hover {
  background: var(--surface-glass);
}
.chapter-row.active {
  background: var(--accent-soft-strong);
}
.chapter-title {
  flex: 1;
  font-size: 0.86rem;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chapter-row.active .chapter-title {
  color: var(--text-primary);
  font-weight: 600;
}

.dirty-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--warning);
  flex-shrink: 0;
}
</style>

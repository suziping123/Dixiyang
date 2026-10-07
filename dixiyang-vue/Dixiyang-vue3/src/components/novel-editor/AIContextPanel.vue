<template>
  <section class="panel ctx-panel">
    <div class="ctx-head">
      <h3 class="panel-title">设定上下文</h3>
      <button
        class="ctx-toggle"
        :class="{ on: enabled }"
        role="switch"
        :aria-checked="enabled"
        :title="enabled ? '已启用 · 点击停用' : '未启用 · 点击启用'"
        :aria-label="enabled ? '已启用' : '未启用'"
        @click="enabled = !enabled"
      >
        <span class="ctx-dot"></span>
      </button>
    </div>
    <p v-if="!enabled" class="ctx-note">开启后，补全时会带上勾选的角色/时间线/事件设定。</p>
    <template v-else>
      <div class="ctx-group" v-if="characters.length">
        <div class="ctx-group-head">
          <span class="ctx-group-name">角色 · {{ selected.characters.size }}/{{ characters.length }}</span>
          <span class="ctx-group-ops">
            <a @click="selectAll('characters', characters)">全选</a>
            <a @click="clearGroup('characters')">清空</a>
          </span>
        </div>
        <div class="ctx-chips">
          <button
            v-for="c in characters"
            :key="c.id"
            class="ctx-chip"
            :class="{ active: selected.characters.has(c.id) }"
            :title="c.background || c.personality || ''"
            @click="toggle('characters', c.id)"
          >{{ c.name }}</button>
        </div>
      </div>
      <div class="ctx-group" v-if="timelines.length">
        <div class="ctx-group-head">
          <span class="ctx-group-name">时间线 · {{ selected.timelines.size }}/{{ timelines.length }}</span>
          <span class="ctx-group-ops">
            <a @click="selectAll('timelines', timelines)">全选</a>
            <a @click="clearGroup('timelines')">清空</a>
          </span>
        </div>
        <div class="ctx-chips">
          <button
            v-for="t in timelines"
            :key="t.id"
            class="ctx-chip"
            :class="{ active: selected.timelines.has(t.id!) }"
            :title="t.description || ''"
            @click="toggle('timelines', t.id!)"
          >{{ t.name }}</button>
        </div>
      </div>
      <div class="ctx-group" v-if="nodes.length">
        <div class="ctx-group-head">
          <span class="ctx-group-name">事件 · {{ selected.nodes.size }}/{{ nodes.length }}</span>
          <span class="ctx-group-ops">
            <a @click="selectAll('nodes', nodes)">全选</a>
            <a @click="clearGroup('nodes')">清空</a>
          </span>
        </div>
        <div class="ctx-chips">
          <button
            v-for="n in sortedNodes"
            :key="n.id"
            class="ctx-chip"
            :class="{ active: selected.nodes.has(n.id) }"
            :title="`${n.eventDate || ''} ${n.eventType || ''} ${n.content || ''}`.trim()"
            @click="toggle('nodes', n.id)"
          >{{ n.eventDate ? `${n.eventDate} ` : '' }}{{ n.title }}</button>
        </div>
      </div>
      <p v-if="!characters.length && !timelines.length && !nodes.length" class="ctx-note">
        本小说暂无角色/时间线/事件。
      </p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Character, Timeline, TimelineNode } from '@/api/types'
import type { CompletionContextIds } from '@/composables/useAICompletion'

const props = defineProps<{
  novelId: number
  characters: Character[]
  timelines: Timeline[]
  nodes: TimelineNode[]
}>()

const enabled = ref(false)
const selected = ref({
  characters: new Set<number>(),
  timelines: new Set<number>(),
  nodes: new Set<number>(),
})

type GroupKey = 'characters' | 'timelines' | 'nodes'
const STORE_KEY = (novelId: number) => `aiCtxSel_${novelId}`
const ENABLED_KEY = (novelId: number) => `aiCtxEnabled_${novelId}`

/** 事件按时间升序（"当时的时间线"更直观） */
const sortedNodes = computed(() =>
  [...props.nodes].sort((a, b) => (a.eventDate || '').localeCompare(b.eventDate || '')),
)

function toggle(group: GroupKey, id: number): void {
  const set = selected.value[group]
  if (set.has(id)) set.delete(id)
  else set.add(id)
  persist()
}
function selectAll(group: GroupKey, items: Array<{ id?: number }>): void {
  for (const it of items) if (it.id != null) selected.value[group].add(it.id)
  persist()
}
function clearGroup(group: GroupKey): void {
  selected.value[group].clear()
  persist()
}

function persist(): void {
  const s = selected.value
  localStorage.setItem(
    STORE_KEY(props.novelId),
    JSON.stringify({
      characters: [...s.characters],
      timelines: [...s.timelines],
      nodes: [...s.nodes],
    }),
  )
}

/** 供 useAICompletion 在请求时同步读取；未启用=不带任何设定 */
function getSelection(): CompletionContextIds {
  if (!enabled.value) {
    return { novelId: props.novelId, characterIds: [], storyNodeIds: [], timelineIds: [] }
  }
  const s = selected.value
  return {
    novelId: props.novelId,
    characterIds: [...s.characters],
    storyNodeIds: [...s.nodes],
    timelineIds: [...s.timelines],
  }
}

// 恢复该小说的记忆
try {
  enabled.value = localStorage.getItem(ENABLED_KEY(props.novelId)) === '1'
  const raw = localStorage.getItem(STORE_KEY(props.novelId))
  if (raw) {
    const saved = JSON.parse(raw) as { characters?: number[]; timelines?: number[]; nodes?: number[] }
    selected.value = {
      characters: new Set(saved.characters ?? []),
      timelines: new Set(saved.timelines ?? []),
      nodes: new Set(saved.nodes ?? []),
    }
  }
} catch {
  /* 记忆损坏则用默认值 */
}

watch(enabled, (v) => localStorage.setItem(ENABLED_KEY(props.novelId), v ? '1' : '0'))

defineExpose({ getSelection })
</script>

<style scoped>
.ctx-panel {
  /* 融入外层「AI 补全」面板：不再套卡片底（原卡中卡与周围平铺 section 不一致） */
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 12px 0 0;
  margin-top: 12px;
  border-top: 1px dashed var(--border-color);
}
.ctx-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.ctx-head .panel-title {
  margin: 0;
  /* 对齐 ChapterSidebar 的 .panel-title：全局 h3 是 1.875rem，不覆盖会大 4 倍 */
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-secondary);
}
/* 纯色状态钮：状态只靠颜色区分，文字说明仅在 hover title 中显示 */
.ctx-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: var(--glass-bg);
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}
.ctx-toggle:hover {
  border-color: var(--surface-glass-border-hover);
}
.ctx-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-disabled);
  transition: all var(--dur-fast) var(--ease-out);
}
.ctx-toggle.on {
  border-color: var(--accent-primary);
  background: var(--accent-soft-strong);
}
.ctx-toggle.on .ctx-dot {
  background: var(--accent-primary);
  box-shadow: 0 0 6px var(--accent-primary);
}
.ctx-note {
  margin: 0;
  font-size: 0.72rem;
  line-height: 1.6;
  color: var(--text-disabled);
}
.ctx-group + .ctx-group {
  margin-top: 10px;
}
.ctx-group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.ctx-group-name {
  font-size: 0.74rem;
  color: var(--text-secondary);
}
.ctx-group-ops {
  display: flex;
  gap: 8px;
}
.ctx-group-ops a {
  font-size: 0.72rem;
  color: var(--text-muted);
  cursor: pointer;
}
.ctx-group-ops a:hover {
  color: var(--accent-primary);
}
.ctx-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 132px;
  overflow-y: auto;
}
.ctx-chip {
  max-width: 100%;
  padding: 3px 9px;
  border: 1px solid var(--surface-glass-border);
  border-radius: 999px;
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 0.72rem;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all var(--dur-fast) var(--ease-out);
}
.ctx-chip:hover {
  border-color: var(--accent-primary);
}
.ctx-chip.active {
  border-color: var(--accent-primary);
  background: var(--accent-soft-strong);
  color: #fff;
}
</style>

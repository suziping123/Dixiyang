import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { createNote, deleteNote, listNotes, updateNote } from '@/api/stickyApi';
import type { NoteUpdateBody, StickyColor, StickyNoteItem } from '@/api/stickyApi';

/**
 * 便签全局状态：一次拉全量，悬浮层按当前路由过滤渲染。
 * 便签两种状态：浮动（pinnedRoute=null，全站可见可拖）/ 钉住（只在 pinnedRoute 路由显示且锁定）。
 */
export const useStickyStore = defineStore('sticky', () => {
  const notes = ref<StickyNoteItem[]>([]);
  const loaded = ref(false);
  /** 灵感墙搜索词（非匹配便签降透明度，不隐藏——避免"钉住的便签不见了"困惑） */
  const query = ref('');
  /** 顶部 zIndex 递增（点选置顶用，仅内存，落库时机随拖动/更新） */
  let topZ = 0;

  /** 池内灵感（AI 补全素材池） */
  const pool = computed(() => notes.value.filter((n) => n.inPool));

  /** 当前路由可见的便签：浮动全见 + 钉在本路由的 */
  function visibleOn(routePath: string): StickyNoteItem[] {
    return notes.value.filter((n) => !n.pinnedRoute || n.pinnedRoute === routePath);
  }

  async function fetch() {
    if (loaded.value) return;
    try {
      const res = await listNotes();
      const data = (res as { data?: StickyNoteItem[] }).data;
      notes.value = Array.isArray(data) ? data : [];
      topZ = notes.value.reduce((m, n) => Math.max(m, n.zIndex), 0);
      loaded.value = true;
    } catch {
      /* 拉取失败：悬浮层按空渲染，不阻塞页面 */
    }
  }

  async function create(body: { content: string; color: StickyColor; x: number; y: number; images?: string[] }) {
    const res = await createNote(body);
    const note = (res as { data?: StickyNoteItem }).data;
    if (note) notes.value.unshift(note);
    return note ?? null;
  }

  /** 局部字段更新（乐观写入，失败静默回滚到服务端值由下次 fetch 纠正） */
  async function patch(id: number, body: NoteUpdateBody) {
    const idx = notes.value.findIndex((n) => n.id === id);
    if (idx < 0) return;
    const prev = { ...notes.value[idx]! };
    const optimistic: Partial<StickyNoteItem> = {};
    if (body.content !== undefined) optimistic.content = body.content;
    if (body.color !== undefined) optimistic.color = body.color;
    if (body.x !== undefined) optimistic.x = body.x;
    if (body.y !== undefined) optimistic.y = body.y;
    if (body.images !== undefined) optimistic.images = body.images;
    if (body.inPool !== undefined) optimistic.inPool = body.inPool;
    if (body.zIndex !== undefined) optimistic.zIndex = body.zIndex;
    if (body.pinned === true) optimistic.pinnedRoute = body.routePath ?? prev.pinnedRoute;
    if (body.pinned === false) optimistic.pinnedRoute = null;
    notes.value[idx] = { ...prev, ...optimistic };
    try {
      const res = await updateNote(id, body);
      const data = (res as { data?: StickyNoteItem }).data;
      if (data) {
        const i2 = notes.value.findIndex((n) => n.id === id);
        if (i2 >= 0) notes.value[i2] = data;
      }
    } catch {
      /* 保存失败：保留乐观值，用户下次操作覆盖（便签不做强一致） */
    }
  }

  /** 点选置顶：内存递增 + 随下次保存落库 */
  function bringToFront(id: number): number {
    topZ += 1;
    const idx = notes.value.findIndex((n) => n.id === id);
    if (idx >= 0) notes.value[idx]!.zIndex = topZ;
    return topZ;
  }

  async function remove(id: number) {
    const idx = notes.value.findIndex((n) => n.id === id);
    if (idx < 0) return;
    notes.value.splice(idx, 1);
    try {
      await deleteNote(id);
    } catch {
      /* 删除失败静默（下次 fetch 恢复） */
    }
  }

  function reset() {
    notes.value = [];
    loaded.value = false;
    topZ = 0;
    query.value = '';
  }

  return { notes, loaded, query, pool, visibleOn, fetch, create, patch, bringToFront, remove, reset };
});

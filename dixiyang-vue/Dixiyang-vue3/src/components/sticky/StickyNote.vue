<template>
  <div
    ref="el"
    class="sticky"
    :class="[
      note.color,
      { pinned, dragging, editing, 'in-pool': note.inPool, dim, done: note.done, toolbarVisible },
    ]"
    :style="wrapStyle"
    @pointerdown="onPointerDown"
    @dblclick="startEdit"
    @mouseenter="onStickyEnter"
    @mouseleave="onStickyLeave"
  >
    <!-- 悬浮工具栏：hover/按下显现，含投喂/编辑/钉住/删除 -->
    <div class="toolbar" ref="toolbar" @pointerdown.stop>
      <button
        class="tool-btn"
        type="button"
        :class="{ active: note.inPool }"
        :title="note.inPool ? '已投喂 AI 素材池 · 点击取消投喂' : '投喂到 AI 素材池'"
        :aria-label="note.inPool ? '取消投喂' : '投喂到 AI 素材池'"
        @click.stop="toggleFeed"
      >
        <svg v-if="!note.inPool" class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
        <svg v-else class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </button>
      <button
        class="tool-btn"
        type="button"
        :title="editing ? '正在编辑' : '编辑内容'"
        :aria-label="editing ? '正在编辑' : '编辑内容'"
        :disabled="editing"
        @click.stop="startEdit"
      >
        <Edit class="tool-icon" />
      </button>
      <button
        class="tool-btn"
        type="button"
        :class="{ active: pinned }"
        :title="pinned ? '已钉在此页 · 点击解锁' : '钉在当前页面（钉住后仅本页可见）'"
        :aria-label="pinned ? '解锁便签' : '钉住便签'"
        @click.stop="togglePin"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17v5"/><path d="M9 10a3 3 0 0 1 6 0"/><path d="M6 10a7 7 0 0 1 12 0"/></svg>
      </button>
      <button
        class="tool-btn danger"
        type="button"
        title="删除便签"
        aria-label="删除便签"
        @click.stop="removeNote"
      >
        <Delete class="tool-icon" />
      </button>
    </div>

    <!-- 纸面：双击进入编辑 -->
    <div class="paper" @click="bringFront">
      <template v-if="editing">
        <textarea
          ref="ta"
          v-model="draft"
          class="edit-ta"
          maxlength="5000"
          placeholder="写下灵感…（Ctrl+Enter 保存，Esc 取消）"
          @pointerdown.stop
          @keydown.esc.prevent="cancelEdit"
          @keydown.ctrl.enter.prevent="saveEdit"
          @keydown.meta.enter.prevent="saveEdit"
        ></textarea>
        <div class="edit-bar" @pointerdown.stop>
          <button class="eb" type="button" title="添加图片" @click="pickImage">
            <Picture class="eb-icon" />
          </button>
          <span v-for="(img, i) in draftImages" :key="img" class="edit-thumb">
            <img :src="img" alt="" />
            <i class="rm" title="移除图片" @click="draftImages.splice(i, 1)">×</i>
          </span>
          <span class="eb-gap"></span>
          <button class="eb ok" type="button" @click="saveEdit">
            <Check class="eb-icon" /> 保存
          </button>
          <button class="eb" type="button" @click="cancelEdit">
            <Close class="eb-icon" /> 取消
          </button>
        </div>
      </template>
      <template v-else>
        <!-- 完成勾选：灰空心圈 → 黑底白勾（由灰变黑）；替代旧的"点正文=划掉" -->
        <button
          class="done-mark"
          type="button"
          :class="{ on: note.done }"
          :title="note.done ? '标记为未完成' : '标记为完成'"
          :aria-label="note.done ? '标记为未完成' : '标记为完成'"
          :aria-pressed="note.done"
          @click.stop="toggleDone"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </button>
        <div class="content" :class="{ empty: !note.content, done: note.done }">
          {{ note.content || '（空便签，双击编辑）' }}
        </div>
        <div v-if="note.images.length" class="imgs">
          <img v-for="img in note.images.slice(0, 3)" :key="img" :src="img" alt="" loading="lazy" />
        </div>
      </template>
    </div>
    <input ref="file" type="file" accept="image/*" hidden @change="onFile" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { uploadNoteImage } from '@/api/stickyApi';
import type { StickyNoteItem } from '@/api/stickyApi';
import { useStickyStore } from '@/stores/stickyStore';
import { confirmDelete } from '@/utils/confirm';
import { Edit, Delete, Picture, Check, Close } from '@element-plus/icons-vue';

const props = defineProps<{
  note: StickyNoteItem;
  vw: number;
  vh: number;
  /** 便签边长（与 Layer 同步：桌面 220 / 移动 160） */
  size: number;
}>();

/** 投喂落点：拖动结束命中池窗口 → 进素材池 */
const emit = defineEmits<{ fed: [id: number] }>();

const store = useStickyStore();
const route = useRoute();
const el = ref<HTMLElement | null>(null);
const toolbar = ref<HTMLElement | null>(null);
const ta = ref<HTMLTextAreaElement | null>(null);
const file = ref<HTMLInputElement | null>(null);

const editing = ref(false);
const dragging = ref(false);
const draft = ref('');
const draftImages = ref<string[]>([]);

/** 钉/解锁瞬间给纸面受压/上弹动画（520ms 后摘除类） */
watch(
  () => props.note.pinnedRoute,
  (nv, ov) => {
    if (nv === ov || !el.value) return;
    const cls = nv ? 'just-pinned' : 'just-unpinned';
    el.value.classList.add(cls);
    setTimeout(() => el.value?.classList.remove(cls), 520);
  },
);

const pinned = computed(() => !!props.note.pinnedRoute);

/** 灵感墙搜索：非匹配便签降透明度（不隐藏，钉住语义不被破坏） */
const dim = computed(() => {
  const q = store.query.trim();
  return !!q && !props.note.content.includes(q) && !props.note.images.some((i) => i.includes(q));
});

/** FAB 悬浮球在右侧（74px 条），坐标夹紧时让开 */
const rightGap = () => (props.vw <= 1024 ? 74 : 0);

/** 归一化坐标 → 像素，并夹紧在视口内（防 resize 后跑出屏幕） */
const pos = computed(() => {
  const maxL = Math.max(0, props.vw - props.size - rightGap());
  const maxT = Math.max(0, props.vh - props.size - 8);
  return {
    left: Math.min(Math.max(props.note.x * props.vw, 0), maxL),
    top: Math.min(Math.max(props.note.y * props.vh, 0), maxT),
  };
});

const wrapStyle = computed(() => ({
  left: `${pos.value.left}px`,
  top: `${pos.value.top}px`,
  width: `${props.size}px`,
  height: `${props.size}px`,
  zIndex: props.note.zIndex,
  '--rot': `${props.note.rotation}deg`,
}));

/** 悬浮工具栏显隐：hover/长按触发 */
const toolbarVisible = ref(false);
let toolbarHideTimer: ReturnType<typeof setTimeout> | null = null;

function showToolbar() {
  if (toolbarHideTimer) {
    clearTimeout(toolbarHideTimer);
    toolbarHideTimer = null;
  }
  toolbarVisible.value = true;
}

function hideToolbar(delay = 300) {
  if (toolbarHideTimer) clearTimeout(toolbarHideTimer);
  toolbarHideTimer = setTimeout(() => {
    toolbarVisible.value = false;
  }, delay);
}

/** 投喂按钮：切换素材池状态（与拖放投喂等效，二选一均可） */
function toggleFeed() {
  const next = !props.note.inPool;
  store.patch(props.note.id, { inPool: next });
  if (next) {
    ElMessage.success('灵感已投喂 AI 素材池');
  } else {
    ElMessage.info('已取消投喂');
  }
}

/** 通用 pointerdown：显示工具栏 + 可拖动（未钉住时） */
function onPointerDown(e: PointerEvent) {
  if (e.button !== 0) return;
  if (pinned.value || editing.value) return;
  if ((e.target as HTMLElement).closest('button, textarea, input, a, .edit-bar')) return;
  showToolbar();
  moved = false; // 每次按下重置：否则拖过一次后单击也会走拖拽保存逻辑（误 PUT + 可能误投喂）
  const rect = el.value!.getBoundingClientRect();
  offX = e.clientX - rect.left;
  offY = e.clientY - rect.top;
  dragging.value = true;
  store.dragging = true; // 供素材池高亮"可投喂"（替代旧 body class 轮询）
  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('pointerup', onPointerUp, { once: true });
  window.addEventListener('pointercancel', onPointerUp, { once: true });
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value) return;
  moved = true;
  const maxL = Math.max(0, props.vw - props.size - rightGap());
  const maxT = Math.max(0, props.vh - props.size - 8);
  const left = Math.min(Math.max(e.clientX - offX, 0), maxL);
  const top = Math.min(Math.max(e.clientY - offY, 0), maxT);
  const st = el.value!.style;
  st.left = `${left}px`;
  st.top = `${top}px`;
}

let offX = 0;
let offY = 0;
let moved = false;
/** 拖拽刚结束：抑制浏览器补发的 click（下一次 click 消费后复位） */
let suppressClick = false;

function onPointerUp() {
  window.removeEventListener('pointermove', onPointerMove);
  dragging.value = false;
  store.dragging = false;
  hideToolbar();
  if (!moved) return;
  // 拖拽结束后浏览器仍会补发 click（down/up 都落在便签上）→ 必须抑制，
  // 否则松手瞬间会误触发 toggleDone 划掉内容 / bringFront 置顶
  suppressClick = true;
  // 兜底：若补发的 click 落在别处（如按钮 @click.stop 吞掉）则本标记无处消费，
  // 0ms 后自动复位，避免吞掉下一次合法点击（click 在当前任务派发，timeout 后跑）
  setTimeout(() => {
    suppressClick = false;
  }, 0);
  const node = el.value!;
  const rect = node.getBoundingClientRect();
  // 关键：拖拽中的便签自己悬浮在光标下（pointer-events:auto），
  // 不临时屏蔽的话 elementFromPoint 永远命中便签自己 → 拖放投喂永不生效
  const prevPe = node.style.pointerEvents;
  node.style.pointerEvents = 'none';
  const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
  node.style.pointerEvents = prevPe;
  const target = hit?.closest('[data-pool-drop]');
  if (target) {
    emit('fed', props.note.id);
    return;
  }
  const maxL = Math.max(1, props.vw - props.size - rightGap());
  const maxT = Math.max(1, props.vh - props.size - 8);
  const x = Math.min(Math.max(rect.left, 0), maxL) / props.vw;
  const y = Math.min(Math.max(rect.top, 0), maxT) / props.vh;
  store.patch(props.note.id, { x, y, zIndex: store.bringToFront(props.note.id) });
}

/** 图钉：钉住当前页 / 解锁回浮动 */
function togglePin() {
  if (pinned.value) {
    store.patch(props.note.id, { pinned: false });
    ElMessage.success('已解锁，可以拖去其他页面了');
  } else {
    store.patch(props.note.id, { pinned: true, routePath: route.path });
    ElMessage.success(`已钉在 ${route.path}`);
  }
}

/** 切换完成态（右上角勾选圆钮：灰空心圈 → 黑底白勾） */
function toggleDone() {
  if (suppressClick) {
    suppressClick = false;
    return;
  }
  if (editing.value) return;
  if (!props.note.content.trim()) {
    ElMessage.info('空便签，先写点内容再标记完成');
    return;
  }
  store.patch(props.note.id, { done: !props.note.done });
}

function bringFront() {
  if (suppressClick) {
    suppressClick = false;
    return;
  }
  if (dragging.value || editing.value) return;
  store.bringToFront(props.note.id);
}

function startEdit() {
  if (editing.value) return;
  draft.value = props.note.content;
  draftImages.value = [...props.note.images];
  editing.value = true;
  store.bringToFront(props.note.id);
  nextTick(() => ta.value?.focus());
}

function cancelEdit() {
  editing.value = false;
}

async function saveEdit() {
  editing.value = false;
  if (draft.value === props.note.content && draftImages.value.join(' ') === props.note.images.join(' ')) return;
  await store.patch(props.note.id, { content: draft.value, images: draftImages.value });
}

function pickImage() {
  file.value?.click();
}

async function onFile(e: Event) {
  const input = e.target as HTMLInputElement;
  const f = input.files?.[0];
  input.value = '';
  if (!f) return;
  try {
    const res = await uploadNoteImage(f);
    if (res.code === 200 && typeof res.data === 'string') {
      if (draftImages.value.length >= 6) {
        ElMessage.warning('每张便签最多 6 张图');
        return;
      }
      draftImages.value.push(res.data);
    } else {
      ElMessage.error(res.msg || '上传失败');
    }
  } catch (err) {
    ElMessage.error((err as Error).message || '上传失败');
  }
}

async function removeNote() {
  const ok = await confirmDelete('确定删除这张便签吗？内容不可恢复。', '删除便签');
  if (ok) store.remove(props.note.id);
}

// 便签 hover 显示工具栏
function onStickyEnter() {
  showToolbar();
}
function onStickyLeave() {
  hideToolbar();
}

// 卸载兜底（拖拽中断时复位拖拽态，防素材池高亮卡住）
onBeforeUnmount(() => {
  window.removeEventListener('pointermove', onPointerMove);
  window.removeEventListener('pointerup', onPointerUp);
  window.removeEventListener('pointercancel', onPointerUp);
  if (dragging.value) store.dragging = false;
  if (toolbarHideTimer) clearTimeout(toolbarHideTimer);
});
</script>

<style scoped>
/* ============ 拟物便利贴 ============ */
.sticky {
  position: fixed;
  display: flex;
  flex-direction: column;
  transform: rotate(var(--rot, 0deg));
  transition:
    transform var(--dur) var(--ease-out),
    filter var(--dur) var(--ease-out),
    opacity var(--dur) var(--ease-out),
    box-shadow var(--dur) var(--ease-out);
  touch-action: none;
  user-select: none;
  pointer-events: auto;
  /* 默认玻璃底板，配合纸面层叠 */
  border-radius: var(--radius-md);
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border);
  box-shadow: var(--shadow-card);
  /* 只提升合成有效的属性（left/top 不是可提升项，写了无效） */
  will-change: transform, opacity, filter;
}

.sticky.in-pool {
  transform: rotate(var(--rot, 0deg)) scale(0.96) translateY(3px);
  opacity: 0.92;
  filter: saturate(0.6) contrast(0.94) brightness(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.sticky.dim {
  opacity: 0.22;
  filter: saturate(0.4);
}

.sticky.dragging {
  transform: rotate(0deg) scale(1.15);
  filter: drop-shadow(0 28px 56px rgba(0, 0, 0, 0.7));
  cursor: grabbing;
  transition: none;
  /* 盖过池窗口（200000），拖拽时便签须悬浮在池口之上；不写 20 亿这种魔数 */
  z-index: 210000;
  will-change: transform;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  pointer-events: auto;
}

/* 纸面：纸纹（横格）+ 顶光 + 投影 + 右下卷角 */
.paper {
  position: relative;
  flex: 1;
  margin: 44px 8px 8px; /* 顶部留出工具栏位 */
  border-radius: var(--radius-sm);
  padding: 8px 9px;
  overflow: hidden;
  cursor: grab;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.45), transparent 36%),
    repeating-linear-gradient(0deg, transparent 0 21px, rgba(0, 0, 0, 0.05) 21px 22px),
    var(--paper);
  box-shadow:
    0 3px 6px rgba(0, 0, 0, 0.28),
    0 10px 20px rgba(0, 0, 0, 0.18),
    inset 0 0 0 1px rgba(0, 0, 0, 0.06);
  min-height: 0; /* 允许 flex 压缩 */
}

.sticky.dragging .paper {
  cursor: grabbing;
}

.paper::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  background: linear-gradient(315deg, rgba(0, 0, 0, 0.22) 0 50%, rgba(255, 255, 255, 0.55) 50% 100%);
  clip-path: polygon(100% 0, 100% 100%, 0 100%);
  pointer-events: none;
}

/* 五色纸：CSS 变量驱动 */
.sticky.yellow { --paper: #ffe97a; }
.sticky.pink { --paper: #ff9fc4; }
.sticky.blue { --paper: #8ed4ff; }
.sticky.green { --paper: #a9e8a0; }
.sticky.purple { --paper: #cbb2f5; }

/* 完成态：划线 + 降低饱和度 */
.content {
  flex: 1;
  font-size: 0.82rem;
  line-height: 22px;
  color: #3a3126;
  white-space: pre-wrap;
  word-break: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 7;
  -webkit-box-orient: vertical;
  user-select: text;
  cursor: text; /* 正文只用于阅读/选中；完成切换走右上角勾选钮 */
  padding-right: 26px; /* 给勾选圆钮让位，避免首行文字被盖 */
  transition: color var(--dur-fast) var(--ease-out), text-decoration var(--dur-fast) var(--ease-out);
}

/* 完成勾选圆钮：未完成=灰空心圈（hover 浅显勾）→ 完成=黑底白勾（由灰变黑） */
.done-mark {
  position: absolute;
  top: 6px;
  right: 6px;
  z-index: 2;
  width: 22px;
  height: 22px;
  padding: 0;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 2px solid rgba(58, 49, 38, 0.35);
  background: rgba(255, 255, 255, 0.4);
  color: rgba(58, 49, 38, 0.75);
  cursor: pointer;
  transition:
    background var(--dur-fast) var(--ease-out),
    border-color var(--dur-fast) var(--ease-out),
    transform var(--dur-fast) var(--ease-out);
}

.done-mark svg {
  width: 13px;
  height: 13px;
  opacity: 0;
  transform: scale(0.6);
  transition: opacity var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
}

.done-mark:hover {
  border-color: rgba(58, 49, 38, 0.8);
}

.done-mark:hover svg {
  opacity: 0.35; /* 未完成 hover：浅灰勾提示可点 */
  transform: scale(1);
}

.done-mark.on {
  background: #17171c;
  border-color: #17171c;
  color: #fff;
}

.done-mark.on svg {
  opacity: 1;
  transform: scale(1);
}

.done-mark:active {
  transform: scale(0.88);
}

.content.done {
  color: rgba(58, 49, 38, 0.55);
  text-decoration: line-through;
  text-decoration-thickness: 2px;
  text-decoration-color: rgba(58, 49, 38, 0.45);
}

.content.empty {
  color: rgba(58, 49, 38, 0.45);
  font-style: italic;
}

.imgs {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.imgs img {
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  background: #fff;
}

/* ============ 悬浮工具栏 ============ */
.toolbar {
  position: absolute;
  top: 4px;
  left: 50%;
  transform: translateX(-50%) translateY(-8px) scale(0.9);
  display: flex;
  gap: 4px;
  padding: 4px 6px;
  border-radius: 999px;
  background: var(--surface-panel-strong);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--surface-glass-border);
  box-shadow: var(--shadow-card);
  opacity: 0;
  pointer-events: none;
  transition:
    opacity var(--dur-fast) var(--ease-out),
    transform var(--dur) cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 10;
}

.sticky:hover .toolbar,
.toolbarVisible .toolbar {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0) scale(1);
}

.tool-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--dur-fast) var(--ease-out);
}

.tool-btn:hover {
  background: var(--accent-soft);
  color: var(--accent-primary);
}

.tool-btn:active {
  transform: scale(0.92);
}

.tool-btn.danger:hover {
  background: var(--danger-soft);
  color: var(--danger);
}

.tool-btn.active {
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
}

.tool-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* ============ 编辑态 ============ */
/* 不再强制 z-index:1000 !important —— startEdit 已调 bringToFront() 置顶，
   内联 zIndex（topZ 递增）才是真置顶；旧写法会把置顶结果压回 1000 导致被盖 */
.sticky.editing {
  transform: rotate(0deg) scale(1.14);
}

.edit-ta {
  flex: 1;
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  color: #3a3126;
  font-size: 0.82rem;
  line-height: 22px;
  font-family: inherit;
  user-select: text;
}

.edit-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-top: 5px;
  padding-top: 5px;
  border-top: 1px dashed rgba(0, 0, 0, 0.25);
}

.eb {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(0, 0, 0, 0.38);
  background: rgba(255, 255, 255, 0.92);
  color: #3a3126; /* 必须显式深色字：否则继承暗色主题浅色字 → 白底白字看不清 */
  border-radius: var(--radius-sm);
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 7px;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
  transition: all var(--dur-fast) var(--ease-out);
}

.eb:hover {
  background: #fff;
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.eb.ok {
  background: var(--accent-primary);
  color: #fff;
  border-color: var(--accent-primary);
}

.eb.ok:hover {
  filter: brightness(1.1);
  color: #fff;
}

.eb-icon {
  width: 14px;
  height: 14px;
}

.eb-gap {
  flex: 1;
}

.edit-thumb {
  position: relative;
  display: inline-block;
}

.edit-thumb img {
  width: 26px;
  height: 26px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.edit-thumb .rm {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--danger);
  color: #fff;
  font-size: 10px;
  font-style: normal;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* ============ 钉入/拔钉动画 ============ */
.sticky.just-pinned {
  animation: nailPress 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.sticky.just-unpinned {
  animation: nailLift 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes nailPress {
  0% { transform: rotate(var(--rot, 0deg)) translateY(-6px) scaleY(1.03); }
  45% { transform: rotate(var(--rot, 0deg)) translateY(3px) scaleY(0.95); }
  100% { transform: rotate(var(--rot, 0deg)) translateY(0) scaleY(1); }
}

@keyframes nailLift {
  0% { transform: rotate(var(--rot, 0deg)) translateY(3px) scaleY(0.96); }
  55% { transform: rotate(calc(var(--rot, 0deg) + 2deg)) translateY(-5px) scaleY(1.02); }
  100% { transform: rotate(var(--rot, 0deg)) translateY(0) scaleY(1); }
}

@media (prefers-reduced-motion: reduce) {
  .sticky,
  .toolbar {
    transition-duration: 0.01ms !important;
  }
  .sticky.just-pinned,
  .sticky.just-unpinned {
    animation: none;
  }
}

/* ============ 移动端适配（≤768） ============ */
@media (max-width: 768px) {
  .toolbar {
    opacity: 1;
    pointer-events: auto;
    transform: translateX(-50%) translateY(0) scale(1);
  }

  .tool-btn {
    width: 36px;
    height: 36px; /* 44px 触控目标 */
  }

  .paper {
    margin-top: 48px;
  }
}
</style>
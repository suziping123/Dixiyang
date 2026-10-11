<template>
  <aside
    class="pool"
    :class="{ open, 'drag-over': dragging }"
    data-pool-drop
    aria-label="AI 素材池"
  >
    <header class="pool-head" @click="toggleOpen">
      <span class="pool-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      </span>
      <span class="pool-title">AI 素材池</span>
      <span class="pool-count">{{ items.length }}</span>
      <span class="pool-fold" :title="open ? '收起' : '展开'">{{ open ? '▲' : '▼' }}</span>
    </header>

    <transition name="pool-body" @before-enter="onBeforeEnter" @after-leave="onAfterLeave">
      <div v-show="open" class="pool-body" ref="poolBody">
        <!-- 堆叠区：鼠标未 hover 时堆成一摞 -->
        <div class="stack-zone" @mouseenter="hoverStack = true" @mouseleave="hoverStack = false">
          <div class="stack" ref="stack">
            <div
              v-for="(n, idx) in displayItems"
              :key="n.id"
              class="stack-card"
              :class="n.color"
              :style="stackCardStyle(idx, n.id)"
              @click.stop="expandId = expandId === n.id ? null : n.id"
              @mouseenter="hoverIdx = idx"
              @mouseleave="hoverIdx = -1"
            >
              <span class="sc-text">{{ n.content || '（空便签）' }}</span>
              <span class="sc-dot"></span>
            </div>
          </div>
          <p v-if="items.length" class="stack-hint">悬停展开 · 点击查看 / 删除</p>
        </div>

        <!-- 展开列表：hover 时逐个弹出 -->
        <transition-group name="fan" tag="div" class="fan-list" v-if="hoverStack && items.length">
          <div
            v-for="(n, idx) in items"
            :key="n.id"
            class="fan-card"
            :class="n.color"
            :style="fanCardStyle(idx)"
            @click.stop="expandId = expandId === n.id ? null : n.id"
          >
            <p class="fc-text">{{ n.content }}</p>
            <div v-if="n.images.length" class="fc-imgs">
              <img v-for="img in n.images" :key="img" :src="img" alt="" loading="lazy" />
            </div>
            <div class="fc-ops">
              <button type="button" @click.stop="takeBack(n.id)">
                <ArrowLeft class="op-icon" /> 取回
              </button>
              <button type="button" class="danger" @click.stop="removeNote(n.id)">
                <Delete class="op-icon" /> 删除
              </button>
            </div>
          </div>
        </transition-group>

        <p v-if="!items.length" class="pool-empty">池子还空着，拖一张便签进来吧</p>
      </div>
    </transition>
  </aside>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, computed, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { useStickyStore } from '@/stores/stickyStore';
import { confirmDelete } from '@/utils/confirm';
import { ArrowLeft, Delete } from '@element-plus/icons-vue';

/** 池窗口开合（父组件 v-model） */
const open = defineModel<boolean>('open', { default: true });

const store = useStickyStore();
const expandId = ref<number | null>(null);
const hoverStack = ref(false);
const hoverIdx = ref(-1);
const poolBody = ref<HTMLElement | null>(null);
const stack = ref<HTMLElement | null>(null);

/** 拖动便签时 body 加类 → 池口高亮提示可投喂 */
const dragging = ref(false);

// 池列表来自全局 store
const items = store.pool;

/** 显示在堆叠里的卡片：最多 5 张，其余隐藏计数 */
const displayItems = computed(() => items.slice(-5).reverse()); // 栈顶在上

function toggleOpen() {
  open.value = !open.value;
}

/** 堆叠卡片样式：错位旋转模拟手写堆叠感 */
function stackCardStyle(idx: number, id: number) {
  const isExpanded = expandId.value === id;
  const baseRotate = (Math.random() - 0.5) * 6; // -3~3°
  const baseX = (Math.random() - 0.5) * 8;
  const baseY = idx * 4;
  return {
    zIndex: 100 - idx,
    transform: isExpanded
      ? 'scale(1.08) rotate(0deg) translate(0,0)'
      : `rotate(${baseRotate}deg) translate(${baseX}px, ${baseY}px)`,
    transition: isExpanded ? 'transform 0.2s cubic-bezier(0.16,1,0.3,1)' : 'transform 0.3s cubic-bezier(0.16,1,0.3,1)',
    boxShadow: isExpanded ? '0 12px 28px rgba(0,0,0,0.4)' : '0 4px 12px rgba(0,0,0,0.3)',
  };
}

/** 扇形展开样式：依次弹出 */
function fanCardStyle(idx: number) {
  const stagger = idx * 40; // ms
  return {
    transitionDelay: `${stagger}ms`,
    '--stagger': `${stagger}ms`,
  };
}

function takeBack(id: number) {
  expandId.value = null;
  hoverStack.value = false;
  store.patch(id, { inPool: false });
  ElMessage.success('已取回墙上（现在是浮动便签）');
}

async function removeNote(id: number) {
  const ok = await confirmDelete('确定删除这张便签吗？内容不可恢复。', '删除便签');
  if (ok) {
    expandId.value = null;
    hoverStack.value = false;
    store.remove(id);
  }
}

// 拖动状态跟随
let timer: ReturnType<typeof setInterval> | null = null;
function syncDrag() {
  dragging.value = document.body.classList.contains('sticky-dragging');
}
onMounted(() => {
  timer = setInterval(syncDrag, 120);
});
onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
  document.body.classList.remove('sticky-dragging');
});

// 打开时滚动到顶部
function onBeforeEnter() {
  nextTick(() => {
    if (poolBody.value) poolBody.value.scrollTop = 0;
  });
}
function onAfterLeave() {
  hoverStack.value = false;
  expandId.value = null;
}
</script>

<style scoped>
/* ============ 暗色玻璃信箱（对齐项目 dark 主题） ============ */
.pool {
  position: fixed;
  right: 16px;
  bottom: 16px;
  width: 300px; /* 加宽便于堆叠展示 */
  z-index: 126;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: var(--surface-panel-strong);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--surface-glass-border);
  box-shadow:
    0 12px 32px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  overflow: hidden;
  transition:
    box-shadow var(--dur) var(--ease-out),
    transform var(--dur) var(--ease-out),
    opacity var(--dur) var(--ease-out),
    max-height var(--dur) var(--ease-out);
}

/* 关闭态：只露头部 */
.pool:not(.open) {
  max-height: 56px;
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.pool.drag-over {
  box-shadow:
    0 12px 32px rgba(0, 0, 0, 0.55),
    0 0 0 3px var(--accent-primary),
    0 0 28px rgba(75, 139, 245, 0.5);
  animation: poolPulse 0.9s ease-in-out infinite;
}

@keyframes poolPulse {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.pool-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--surface-glass-border);
  user-select: none;
  transition: background var(--dur-fast) var(--ease-out);
}

.pool-head:hover {
  background: var(--accent-soft);
}

.pool-icon {
  display: flex;
  width: 18px;
  height: 18px;
  color: var(--accent-primary);
  flex-shrink: 0;
}

.pool-title {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 1px;
  flex: 1;
  color: var(--text-primary);
}

.pool-count {
  min-width: 22px;
  text-align: center;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-primary);
  font-size: 0.7rem;
  font-weight: 700;
}

.pool-fold {
  font-size: 1rem;
  color: var(--text-muted);
  transition: transform var(--dur) var(--ease-out);
}

.pool.open .pool-fold {
  transform: rotate(180deg);
}

.pool-body {
  max-height: min(50vh, 420px);
  overflow: hidden; /* 由 transition-group 控制 */
  padding: 8px 10px 10px;
}

/* ============ 堆叠区 ============ */
.stack-zone {
  position: relative;
  min-height: 120px; /* 保证堆叠有空间 */
}

.stack {
  position: relative;
  width: 100%;
  min-height: 100px;
}

.stack-card {
  position: absolute;
  left: 50%;
  top: 0;
  width: calc(100% - 16px);
  max-width: 260px;
  transform-origin: center top;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border);
  cursor: pointer;
  will-change: transform, box-shadow;
}

.stack-card:hover {
  z-index: 200 !important;
}

.sc-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--text-secondary);
}

.sc-dot {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-primary);
  opacity: 0.6;
}

.stack-hint {
  margin: 8px 0 0;
  text-align: center;
  font-size: 0.65rem;
  color: var(--text-muted);
}

/* ============ 扇形展开列表 ============ */
.fan-list {
  display: flex;
  flex-direction: column-reverse; /* 栈顶在上，动画从下往上弹 */
  gap: 6px;
  padding-top: 4px;
}

.fan-card {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--surface-glass-border);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
  transform-origin: center bottom;
  opacity: 0;
  transform: scale(0.9) translateY(20px);
  animation: fanIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fanIn {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.fc-text {
  margin: 0 0 6px;
  font-size: 0.8rem;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 100px;
  overflow-y: auto;
  color: var(--text-primary);
}

.fc-imgs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.fc-imgs img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--surface-glass-border);
}

.fc-ops {
  display: flex;
  gap: 6px;
}

.fc-ops button {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 0;
  font-size: 0.7rem;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: var(--surface-glass);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.fc-ops button:hover {
  background: var(--surface-card);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.fc-ops button.danger {
  color: var(--danger);
  border-color: var(--danger-border);
}

.fc-ops button.danger:hover {
  background: var(--danger-soft);
  color: var(--danger);
}

.op-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* ============ 空状态 ============ */
.pool-empty {
  margin: 20px 0;
  padding: 20px 10px;
  text-align: center;
  font-size: 0.74rem;
  color: var(--text-muted);
  border: 1.5px dashed var(--surface-glass-border);
  border-radius: var(--radius-sm);
}

/* ============ 移动端：贴底抽屉 ============ */
@media (max-width: 768px) {
  .pool {
    right: 8px;
    left: 8px;
    bottom: 8px;
    width: auto;
    margin-right: 64px;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
  }

  .pool:not(.open) {
    max-height: 56px;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
  }

  .pool.open {
    max-height: 65vh;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
  }

  .stack-card {
    max-width: calc(100% - 24px);
  }
}

/* ============ 过渡动画 ============ */
.pool-body-enter-active,
.pool-body-leave-active {
  transition: max-height var(--dur) var(--ease-out), opacity var(--dur-fast) var(--ease-out);
}

.pool-body-enter-from,
.pool-body-leave-to {
  max-height: 0;
  opacity: 0;
}

.fan-enter-active,
.fan-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fan-enter-from,
.fan-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(16px);
}

.fan-move {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>
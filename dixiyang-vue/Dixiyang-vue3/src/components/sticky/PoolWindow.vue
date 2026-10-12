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
      <span class="pool-fold" :title="open ? '收起' : '展开'">▼</span>
    </header>

    <transition name="pool-body" @before-enter="onBeforeEnter" @after-leave="onAfterLeave">
      <div v-show="open" class="pool-body" ref="poolBody">
        <!-- 堆叠区：固定高度（hover 不改布局 → 物理上不可能抖动循环） -->
        <div
          class="stack-area"
          :style="{ height: `${areaHeight}px` }"
          @mouseenter="hoverStack = true"
          @mouseleave="hoverStack = false"
        >
          <div class="stack" ref="stack">
            <div
              v-for="(n, idx) in displayItems"
              :key="n.id"
              class="stack-card"
              :class="n.color"
              :style="stackCardStyle(idx, n.id)"
            >
              <!-- 纸质感小卡 -->
              <div class="sc-paper">
                <span class="sc-text">{{ n.content || '（空便签）' }}</span>
                <div v-if="n.images?.length" class="sc-imgs">
                  <img v-for="img in n.images.slice(0, 2)" :key="img" :src="img" alt="" loading="lazy" />
                </div>
                <!-- 卡上操作：hover 该卡时浮现（取回 / 删除） -->
                <div class="sc-ops">
                  <button type="button" title="取回到墙上" @click.stop="takeBack(n.id)">
                    <ArrowLeft class="op-icon" />
                  </button>
                  <button type="button" class="danger" title="删除便签" @click.stop="removeNote(n.id)">
                    <Delete class="op-icon" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p v-if="items.length" class="stack-hint">悬停拉开 · 卡片上可取回 / 删除</p>

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
const hoverStack = ref(false);
const poolBody = ref<HTMLElement | null>(null);
const stack = ref<HTMLElement | null>(null);

/** 拖动便签时 body 加类 → 池口高亮提示可投喂 */
const dragging = ref(false);

/**
 * 池列表必须用 computed 包一层！
 * store.pool 是 computed，每次变化生成新数组；直接 `const items = store.pool`
 * 只在挂载时取一次值 → 之后投喂/取回/删除全部不生效，必须刷新。
 */
const items = computed(() => store.pool);

/** 显示在堆叠里的卡片：最多 5 张，栈顶（最新投喂）在上 */
const displayItems = computed(() => items.value.slice(-5).reverse());

/** 堆叠区固定高度：按张数算，hover 不改变 → 布局稳定不闪烁 */
const areaHeight = computed(() => {
  const n = Math.min(items.value.length, 5);
  if (!n) return 90; // 空态
  // 底部留白 14 + (n-1) 张的拉开间距 24 + 单卡高度约 120
  return Math.max(150, 14 + (n - 1) * 24 + 120);
});

function toggleOpen() {
  open.value = !open.value;
}

/**
 * 每张便签的固定随机偏移（按 id 缓存）。
 * 关键：绝不能在渲染函数里直接调 Math.random() ——
 * hover / 点击触发重渲染时会重新随机，卡片每帧都在变换 = 残影抖动。
 */
const jitterMap = new Map<number, { rot: number; x: number }>();
function jitter(id: number) {
  let j = jitterMap.get(id);
  if (!j) {
    j = { rot: (Math.random() - 0.5) * 10, x: (Math.random() - 0.5) * 8 };
    jitterMap.set(id, j);
  }
  return j;
}

/** 堆叠卡片样式：底部基准堆一摞；hover 拉开间距露出每张上沿（供操作按钮浮现） */
function stackCardStyle(idx: number, id: number) {
  const { rot, x } = jitter(id);
  const gap = hoverStack.value ? 24 : 7; // hover 拉开 24px，露出每张卡的顶部
  const baseY = -idx * gap;
  return {
    zIndex: 5000 - idx, // 最新投喂的在最上
    transform: `translateX(-50%) rotate(${rot}deg) translate(${x}px, ${baseY}px)`,
    transition: `transform 0.28s cubic-bezier(0.25, 0.8, 0.25, 1) ${idx * 25}ms`, // 依次错开入场
  };
}



function takeBack(id: number) {
  store.patch(id, { inPool: false });
  ElMessage.success('已取回墙上（现在是浮动便签）');
}

async function removeNote(id: number) {
  const ok = await confirmDelete('确定删除这张便签吗？内容不可恢复。', '删除便签');
  if (ok) {
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
}
</script>

<style scoped>
/* ============ 暗色玻璃信箱（对齐项目 dark 主题） ============ */
.pool {
  position: fixed;
  right: 16px;
  bottom: 16px;
  width: 300px; /* 加宽便于堆叠展示 */
  z-index: 200000;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: var(--surface-panel-strong);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--surface-glass-border);
  box-shadow:
    0 12px 32px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  overflow: visible;
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
  position: relative;
  z-index: 25;
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



.pool-fold {
  font-size: 0.9rem;
  color: var(--text-muted);
  transition: transform var(--dur) var(--ease-out);
  transform-origin: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.pool.open .pool-fold {
  transform: rotate(-180deg);
}

.pool-body {
  max-height: min(50vh, 420px);
  overflow: visible; /* 允许堆叠卡片在边缘外露/飞入，避免被裁剪导致跑到背后 */
  padding: 8px 10px 10px;
  position: relative; /* 建立层叠上下文 */
  z-index: 12;
  transform: translateZ(0); /* 提升合成层，减少动画被裁剪的概率 */
}

/* ============ 堆叠区 ============ */
/* 固定高度（内联绑定），hover 不改变布局 → 无抖动循环 */
.stack-area {
  position: relative;
}

/* 池底托盘阴影：强化"纸摞在池底" */
.stack-area::after {
  content: '';
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 4px;
  height: 5px;
  border-radius: 999px;
  background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.45) 0%, rgba(0, 0, 0, 0.25) 70%, transparent 100%);
  filter: blur(2px);
  opacity: 0.5;
  pointer-events: none;
  z-index: -1;
}

/* 铺满固定高度的堆叠容器：卡片 bottom 锚点始终在区域底部 */
.stack {
  position: absolute;
  inset: 0;
  z-index: 70;
  isolation: isolate;
}

.stack-card {
  position: absolute;
  left: 50%;
  bottom: 14px; /* 摞在池子底部，往上堆叠 */
  top: auto;
  width: calc(100% - 16px);
  max-width: 260px;
  transform-origin: center bottom; /* 绕底边旋转，像一叠纸 */
  padding: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  will-change: transform; /* 只提升 transform，避免 box-shadow/z-index 抖动 */
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  isolation: isolate;
}

.stack-card:hover {
  z-index: 6000 !important;
}

/* ============ 纸质感小卡（便签纸面） ============ */
.sc-paper {
  position: relative;
  min-height: 96px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 9px 10px 12px;
  border-radius: var(--radius-sm);
  /* 顶部高光 + 横格纸纹 + 纸色 */
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.5), transparent 40%),
    repeating-linear-gradient(0deg, transparent 0 18px, rgba(0, 0, 0, 0.05) 18px 19px),
    var(--paper, #ffe97a);
  box-shadow:
    0 3px 8px rgba(0, 0, 0, 0.38),
    0 14px 32px rgba(0, 0, 0, 0.2),
    inset 0 0 0 1px rgba(0, 0, 0, 0.08);
}

/* 五色纸（与墙上便签同色） */
.stack-card.yellow .sc-paper { --paper: #ffe97a; }
.stack-card.pink .sc-paper { --paper: #ff9fc4; }
.stack-card.blue .sc-paper { --paper: #8ed4ff; }
.stack-card.green .sc-paper { --paper: #a9e8a0; }
.stack-card.purple .sc-paper { --paper: #cbb2f5; }

/* 右下卷角：纸的标志细节 */
.sc-paper::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  width: 14px;
  height: 14px;
  background: linear-gradient(315deg, rgba(0, 0, 0, 0.24) 0 50%, rgba(255, 255, 255, 0.62) 50% 100%);
  clip-path: polygon(100% 0, 100% 100%, 0 100%);
  pointer-events: none;
}

.sc-text {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 0.76rem;
  line-height: 18px;
  color: #3a3126; /* 深墨色，压在纸色上才像写字 */
  white-space: pre-wrap;
  word-break: break-word;
  user-select: none;
}

.sc-imgs {
  display: flex;
  gap: 4px;
  margin-top: auto;
}

.sc-imgs img {
  width: 34px;
  height: 34px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.stack-hint {
  margin: 8px 0 0;
  text-align: center;
  font-size: 0.65rem;
  color: var(--text-muted);
}

/* ============ 卡上操作条（hover 浮现） ============ */
.sc-ops {
  position: absolute;
  top: 3px;
  right: 3px;
  display: flex;
  gap: 4px;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--dur-fast) var(--ease-out);
}

.stack-card:hover .sc-ops {
  opacity: 1;
  pointer-events: auto;
}

.sc-ops button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.92);
  color: #444;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transition: all var(--dur-fast) var(--ease-out);
}

.sc-ops button:hover {
  background: #fff;
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.sc-ops button.danger {
  color: var(--danger);
  border-color: var(--danger-border);
}

.sc-ops button.danger:hover {
  background: var(--danger-soft);
  color: var(--danger);
}

.op-icon {
  width: 13px;
  height: 13px;
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
    bottom: 12px;
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
</style>
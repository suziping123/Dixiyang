<template>
  <!-- 灵感墙：暗色玻璃拟态基调，直接透出全局 #theme-bg -->
  <div class="wall">
    <!-- 玻璃工具条 -->
    <header class="toolbar">
      <div class="tb-brand">
        <span class="tb-pin" aria-hidden="true">
          <svg class="tb-pin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17v5"/><path d="M9 10a3 3 0 0 1 6 0"/><path d="M6 10a7 7 0 0 1 12 0"/></svg>
        </span>
        <h1>灵感墙</h1>
      </div>

      <div class="tb-colors" role="radiogroup" aria-label="新便签颜色">
        <button
          v-for="c in COLORS"
          :key="c"
          class="tb-color"
          :class="[c, { on: newColor === c }]"
          type="button"
          :title="`新便签颜色：${c}`"
          :aria-label="c"
          :aria-checked="newColor === c"
          role="radio"
          @click="newColor = c"
        ></button>
      </div>

      <button class="tb-new" type="button" @click="addNote">
        <Plus class="tb-new-icon" /> 新建便签
      </button>

      <input
        v-model="store.query"
        class="tb-search"
        type="search"
        placeholder="搜索便签…"
        aria-label="搜索便签"
        enterkeyhint="search"
      />

      <button class="tb-pool" type="button" title="AI 素材池" @click="poolOpen = !poolOpen">
        <svg class="tb-pool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
        <span>素材池</span>
        <b>{{ store.pool.length }}</b>
      </button>
    </header>

    <!-- 首次引导（可关闭） -->
    <div v-if="showGuide" class="guide">
      <p><b>①</b> 拖动便签排布灵感，点工具栏 <b><svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17v5"/><path d="M9 10a3 3 0 0 1 6 0"/><path d="M6 10a7 7 0 0 1 12 0"/></svg></b> 钉在当前页（钉住后仅本页可见、不可移动，再点解锁）</p>
      <p><b>②</b> 双击纸面编辑文字 / 传图，工具栏 <b><Delete class="inline-icon" /></b> 删除</p>
      <p><b>③</b> 写小说时把便签拖进右下 <b><svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></b> 素材池 → 编辑器「AI 补全」勾选即带上</p>
      <button class="guide-x" type="button" aria-label="关闭引导" @click="closeGuide">
        <Close class="guide-x-icon" />
      </button>
    </div>

    <!-- 空墙提示（一张便签都没有时） -->
    <div v-if="store.loaded && !store.notes.length" class="empty-wall">
      <p>墙上还空着</p>
      <button type="button" @click="addNote">
        <Plus class="empty-btn-icon" /> 贴第一张灵感
      </button>
    </div>

    <PoolWindow v-model:open="poolOpen" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import PoolWindow from '@/components/sticky/PoolWindow.vue';
import type { StickyColor } from '@/api/stickyApi';
import { useStickyStore } from '@/stores/stickyStore';
import { Plus, Message, Close, Delete } from '@element-plus/icons-vue';

const store = useStickyStore();

const COLORS: StickyColor[] = ['yellow', 'pink', 'blue', 'green', 'purple'];
const newColor = ref<StickyColor>('yellow');
const poolOpen = ref(window.innerWidth > 768);

/** 首次引导：看过即关（localStorage 记忆） */
const showGuide = ref(localStorage.getItem('stickyGuideDone') !== '1');
function closeGuide() {
  showGuide.value = false;
  localStorage.setItem('stickyGuideDone', '1');
}

/** 新建便签：视口中部随机落点（浮动状态，可拖可钉） */
function addNote() {
  const x = 0.18 + Math.random() * 0.45;
  const y = 0.16 + Math.random() * 0.4;
  void store.create({ content: '', color: newColor.value, x, y });
}

onMounted(() => {
  void store.fetch();
});
</script>

<style scoped>
/* ============ 灵感墙容器：透出全局 #theme-bg ============ */
.wall {
  position: relative; /* 形成堆叠上下文，但不设背景，让全局 #theme-bg (z-index:0) 透出 */
  min-height: 100vh;
  padding: 84px 20px 40px;
  overflow: hidden;
}

/* 无需自定义背景层——全局 #theme-bg (fixed, z-index:0) 已覆盖全视口 */

/* ============ 玻璃工具条 ============ */
.toolbar {
  position: fixed;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 124;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  max-width: calc(100vw - 32px);
  padding: 10px 18px;
  border-radius: var(--radius-md);
  background: var(--surface-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--surface-glass-border);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.tb-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tb-pin {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--accent-soft);
  color: var(--accent-primary);
  transform: rotate(-12deg);
}

.tb-pin-icon {
  width: 16px;
  height: 16px;
}

.tb-brand h1 {
  margin: 0;
  font-size: 1rem;
  letter-spacing: 2px;
  color: var(--text-primary);
  font-weight: 700;
}

.tb-colors {
  display: flex;
  gap: 6px;
}

.tb-color {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.15);
  cursor: pointer;
  padding: 0;
  transition: transform var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out);
}

.tb-color.yellow { background: #ffe97a; }
.tb-color.pink { background: #ff9fc4; }
.tb-color.blue { background: #8ed4ff; }
.tb-color.green { background: #a9e8a0; }
.tb-color.purple { background: #cbb2f5; }

.tb-color.on {
  transform: scale(1.25);
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px var(--accent-soft);
}

.tb-new {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--accent-primary);
  background: var(--accent-primary);
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(75, 139, 245, 0.35);
  transition: all var(--dur-fast) var(--ease-out);
}

.tb-new:hover {
  filter: brightness(1.08);
  box-shadow: 0 6px 18px rgba(75, 139, 245, 0.45);
}

.tb-new:active {
  transform: translateY(1px);
}

.tb-new-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.tb-search {
  width: 180px;
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-input);
  color: var(--text-primary);
  font-size: 0.85rem;
  backdrop-filter: blur(10px);
  transition: all var(--dur-fast) var(--ease-out);
}

.tb-search:focus {
  outline: none;
  border-color: var(--surface-glass-border-hover);
  box-shadow: 0 0 15px rgba(75, 139, 245, 0.25);
  background: var(--surface-glass);
}

.tb-search::placeholder {
  color: var(--text-muted);
}

.tb-pool {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.tb-pool:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: var(--accent-soft);
}

.tb-pool-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.tb-pool b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-primary);
  font-size: 0.7rem;
  font-weight: 700;
}

/* ============ 引导卡（玻璃卡片） ============ */
.guide {
  position: relative;
  max-width: 560px;
  margin: 0 auto 26px;
  padding: 16px 40px 16px 18px;
  border-radius: var(--radius-md);
  background: var(--surface-panel-strong);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--surface-glass-border);
  color: var(--text-primary);
  font-size: 0.84rem;
  line-height: 1.7;
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 20px 40px rgba(0, 0, 0, 0.25);
  transform: rotate(-0.5deg);
}

.guide p {
  margin: 4px 0;
  color: var(--text-secondary);
}

.guide b {
  color: var(--accent-cyan);
}

.inline-icon {
  display: inline-flex;
  width: 1em;
  height: 1em;
  vertical-align: -0.15em;
  margin: 0 2px;
}

.guide-x {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: var(--surface-glass);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--dur-fast) var(--ease-out);
}

.guide-x:hover {
  background: var(--accent-soft);
  color: var(--accent-primary);
}

.guide-x-icon {
  width: 14px;
  height: 14px;
}

/* ============ 空墙 ============ */
.empty-wall {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-muted);
  pointer-events: none;
}

.empty-wall p {
  font-size: 1.2rem;
  letter-spacing: 3px;
  font-weight: 600;
}

.empty-wall button {
  pointer-events: auto;
  margin-top: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--surface-glass-border);
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.empty-wall button:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: var(--accent-soft);
}

.empty-btn-icon {
  width: 16px;
  height: 16px;
}

/* ============ 移动端（768 断点） ============ */
@media (max-width: 768px) {
  .wall {
    padding: 132px 12px 32px;
  }

  .toolbar {
    top: 8px;
    gap: 8px;
    padding: 8px 12px;
    width: calc(100vw - 72px);
    left: 8px;
    transform: none;
    justify-content: flex-start;
  }

  .tb-brand h1 {
    font-size: 0.9rem;
    letter-spacing: 1px;
  }

  .tb-search {
    order: 5;
    width: 100%;
    font-size: 16px;
  }

  .tb-new {
    padding: 6px 10px;
    font-size: 0.78rem;
  }

  .tb-new span {
    display: none;
  }

  .guide {
    font-size: 0.78rem;
    margin-bottom: 18px;
  }
}
</style>
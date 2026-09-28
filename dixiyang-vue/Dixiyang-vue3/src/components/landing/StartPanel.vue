<script setup lang="ts">
/**
 * 05 · 开始：大字 CTA + 真实数字带（docs/介绍.md 有出处）+ footer 单行
 * count-up 由 GSAP 落在终值；reduced-motion 直接显示终值
 */
import { computed } from 'vue'
import { isTokenValid } from '@/utils/auth'

const loggedIn = computed(() => isTokenValid(localStorage.getItem('token')))
const ctaHref = computed(() => (loggedIn.value ? '/home' : '/login'))
const ctaLabel = computed(() => (loggedIn.value ? '进入我的宇宙' : '开始创作'))
const year = new Date().getFullYear()

const stats = [
  { value: 111509, text: '111,509', unit: '条', label: '知识库向量', en: 'VECTORS' },
  { value: 26, text: '26', unit: '本', label: '已入库语料', en: 'BOOKS' },
  { value: 70000, text: '70,000', unit: '+', label: '文本块', en: 'CHUNKS', plus: true },
  { value: 5, text: '5', unit: '种', label: '对话模式', en: 'MODES' },
]
</script>

<template>
  <section
    id="panel-start"
    class="ld-panel ld-p-start"
    role="tabpanel"
    aria-labelledby="tab-start"
  >
    <div class="ld-p-start__grid">
      <div>
        <p class="ld-eyebrow" data-ld-in>START <span class="zh">· 开源可自部署</span></p>
        <h2 data-ld-in>第一章，<br />从<span class="accent">这里</span>开始。</h2>
        <div class="ld-p-start__cta" data-ld-in>
          <RouterLink class="ld-btn" :to="ctaHref">{{ ctaLabel }}</RouterLink>
          <a
            class="ld-btn ld-btn--ghost"
            href="https://github.com/suziping123/Dixiyang"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub 开源仓库
            <svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">
              <path
                d="M4.5 1.5h6v6M10.5 1.5 5 7M9 8.5v2h-7.5V3h2"
                stroke="currentColor"
                fill="none"
                stroke-width="1.2"
              />
            </svg>
          </a>
          <p class="ld-p-start__hint">数据留在你自己的机器上</p>
        </div>
      </div>

      <div data-ld-in>
        <p class="ld-eyebrow" style="margin-bottom: 0.75rem">
          KNOWLEDGE BASE <span class="zh">· 私有知识库当前规模</span>
        </p>
        <ul class="ld-stats">
          <li v-for="s in stats" :key="s.label" class="ld-stat">
            <p class="ld-stat__value">
              <span class="num" :data-counter="s.value">{{ s.text }}</span>
              <span class="unit">{{ s.plus ? '+' : '' }}{{ s.unit }}</span>
            </p>
            <p class="ld-stat__label">{{ s.label }} <span class="en">{{ s.en }}</span></p>
          </li>
        </ul>
        <p class="ld-p-start__note">
          数据来源：本项目 RAG 检索流水线的当前部署状态（docs/介绍.md）。
        </p>
      </div>
    </div>

    <footer class="ld-footer-line" data-ld-in>
      <span>© {{ year }} Dixiyang · 沉浸式内容创作 · 智能分发引擎</span>
      <span>
        <a href="https://github.com/suziping123/Dixiyang" target="_blank" rel="noopener noreferrer"
          >GitHub</a
        >
        · <RouterLink to="/login">登录</RouterLink>
      </span>
    </footer>
  </section>
</template>

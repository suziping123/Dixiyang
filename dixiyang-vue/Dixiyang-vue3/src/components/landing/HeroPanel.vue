<script setup lang="ts">
/**
 * 00 · 首屏：h1 巨字 + 一句话 + CTA；右侧章节阶梯呼应标题
 * CTA 依登录态切换目的地（登录后直达工作台）
 */
import { computed } from 'vue'
import { isTokenValid } from '@/utils/auth'

const loggedIn = computed(() => isTokenValid(localStorage.getItem('token')))
const ctaHref = computed(() => (loggedIn.value ? '/home' : '/login'))
const ctaLabel = computed(() => (loggedIn.value ? '进入我的宇宙' : '开始创作'))

/** 章节阶梯：001 ↔ 100 呼应 h1，两处红为关键帧 */
const chapters = [
  { n: '001', name: '开篇', key: true },
  { n: '012', name: '相遇', key: false },
  { n: '027', name: '转折', key: false },
  { n: '045', name: '低谷', key: false },
  { n: '063', name: '重逢', key: false },
  { n: '088', name: '决战', key: false },
  { n: '100', name: '终章', key: true },
]
</script>

<template>
  <section
    id="panel-hero"
    class="ld-panel ld-p-hero"
    role="tabpanel"
    aria-labelledby="tab-hero"
  >
    <div class="ld-p-hero__grid">
      <div>
        <p class="ld-eyebrow ld-p-hero__eyebrow" data-ld-in>
          DIXIYANG <span class="zh">· AI 小说创作平台</span>
        </p>
        <h1 data-ld-in>
          <span class="row">写到第一百章，</span>
          <span class="row">它还记得<span class="accent">第一章</span>。</span>
        </h1>
        <p class="ld-p-hero__lead" data-ld-in>
          角色卡、时间线、故事节点与你的私有知识库，同在一条故事线上——AI
          先检索你的设定，再和你写下去。
        </p>
        <div class="ld-p-hero__cta" data-ld-in>
          <RouterLink class="ld-btn" :to="ctaHref">{{ ctaLabel }}</RouterLink>
          <a
            class="ld-btn ld-btn--quiet"
            href="https://github.com/suziping123/Dixiyang"
            target="_blank"
            rel="noopener noreferrer"
          >
            查看源码
            <svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">
              <path
                d="M4.5 1.5h6v6M10.5 1.5 5 7M9 8.5v2h-7.5V3h2"
                stroke="currentColor"
                fill="none"
                stroke-width="1.2"
              />
            </svg>
          </a>
        </div>
        <p class="ld-p-hero__slogan" data-ld-in>
          沉浸式内容创作 · 智能分发引擎
        </p>
      </div>

      <ul class="ld-chapters" aria-label="章节示意" data-ld-in>
        <li
          v-for="c in chapters"
          :key="c.n"
          class="ld-chapters__item"
          :class="{ 'is-key': c.key }"
        >
          <span>CH.{{ c.n }}</span>
          <span class="name">{{ c.name }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

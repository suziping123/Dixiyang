<script setup lang="ts">
/**
 * 01 · 问题：三条真实痛点，错落缩进的 editorial 单列（docs/介绍.md 原文）
 */
const items = [
  {
    n: '01',
    title: '角色写着写着就忘了',
    desc: '第十五章的他，性格停在第三章——人设靠回忆维持，越写越飘。',
  },
  {
    n: '02',
    title: '前后情节互相矛盾',
    desc: '伏笔埋了没收，时间线对不上，改一处要翻半本书去核对。',
  },
  {
    n: '03',
    title: '资料翻不到，AI 也接不住',
    desc: '设定散落在本地文档里，对话全靠现编——它不知道你写过什么。',
  },
]
</script>

<template>
  <section
    id="panel-problem"
    class="ld-panel ld-p-problem"
    role="tabpanel"
    aria-labelledby="tab-problem"
  >
    <div class="ld-panel__head">
      <p class="ld-eyebrow" data-ld-in>
        PROBLEM <span class="zh">· 写长篇的人输给同一件事</span>
      </p>
      <h2 class="ld-h2" data-ld-in>记忆，是长篇写作最先垮掉的地方。</h2>
    </div>
    <ol class="ld-p-problem__list">
      <li v-for="it in items" :key="it.n" class="ld-p-problem__item" data-ld-in>
        <span class="ld-p-problem__num" aria-hidden="true">{{ it.n }}</span>
        <div>
          <h3>{{ it.title }}</h3>
          <p>{{ it.desc }}</p>
        </div>
      </li>
    </ol>
  </section>
</template>

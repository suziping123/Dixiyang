<script setup lang="ts">
/**
 * 04 · 流程：横向 5 步 + 连线（真实使用路径：建小说 → 角色卡 → 时间线 → 节点 → 共写）
 */
const steps = [
  { n: '01', t: '建一部小说', d: '起个名字，传张封面——这是你宇宙的起点。' },
  { n: '02', t: '铺开角色卡', d: '手动录入，或让 AI 从对话里把设定提出来。' },
  { n: '03', t: '拉起时间线', d: '主线在下，支线在上，层级关系一眼可读。' },
  { n: '04', t: '落下故事节点', d: '给节点标上类型与重要性，剧情有了骨架。' },
  { n: '05', t: '与 AI 共写', d: '带着全部设定开始对话，它检索着回答。' },
]
</script>

<template>
  <section
    id="panel-process"
    class="ld-panel ld-p-process"
    role="tabpanel"
    aria-labelledby="tab-process"
  >
    <div class="ld-panel__head">
      <p class="ld-eyebrow" data-ld-in>
        PROCESS <span class="zh">· 从空白到长篇</span>
      </p>
      <h2 class="ld-h2" data-ld-in>五步，把灵感铺成一条线。</h2>
    </div>

    <div class="ld-steps-wrap" data-ld-in>
      <ol class="ld-steps">
        <li v-for="s in steps" :key="s.n" class="ld-step" data-ld-step>
          <span class="ld-step__dot" aria-hidden="true"></span>
          <span class="ld-step__num">{{ s.n }}</span>
          <h3>{{ s.t }}</h3>
          <p>{{ s.d }}</p>
        </li>
      </ol>
    </div>
  </section>
</template>

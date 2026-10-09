<template>
  <!-- 线性图标集：统一 viewBox=24 / stroke=currentColor / 1.6px，对齐项目线稿风格 -->
  <svg
    class="idea-icon"
    :viewBox="viewBox"
    :width="size"
    :height="size"
    :fill="filled ? 'currentColor' : 'none'"
    stroke="currentColor"
    :stroke-width="filled ? 0 : sw"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- 浏览：眼睛 -->
    <template v-if="name === 'eye'">
      <path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12z" />
      <circle cx="12" cy="12" r="2.6" />
    </template>
    <!-- 点赞：心形 -->
    <template v-else-if="name === 'heart'">
      <path d="M12 20s-7.5-4.7-9.3-9.3C1.3 7 3.6 4 6.9 4c2 0 3.6 1.1 5.1 3 1.5-1.9 3.1-3 5.1-3 3.3 0 5.6 3 4.2 6.7C19.5 15.3 12 20 12 20z" />
    </template>
    <!-- 评论：气泡 -->
    <template v-else-if="name === 'bubble'">
      <path d="M21 12a8 8 0 0 1-8 8H4.5l2-3.2A8 8 0 1 1 21 12z" />
    </template>
    <!-- 收藏：五角星 -->
    <template v-else-if="name === 'star'">
      <path d="M12 3.6l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.5 9.8l5.9-.9z" />
    </template>
    <!-- 附件：回形针 -->
    <template v-else-if="name === 'clip'">
      <path d="M16.5 7.5v8.2a4.7 4.7 0 0 1-9.4 0V6.8a3.1 3.1 0 0 1 6.2 0v8.6a1.6 1.6 0 0 1-3.2 0V7.5" />
    </template>
    <!-- 编辑：铅笔 -->
    <template v-else-if="name === 'edit'">
      <path d="M4 20h4L19.5 8.5a2.1 2.1 0 0 0-3-3L5 17v3z" />
      <path d="M14.5 6.5l3 3" />
    </template>
    <!-- 分享/导出：箭头出框 -->
    <template v-else-if="name === 'share'">
      <path d="M12 3v11M8 6.5L12 3l4 3.5" />
      <path d="M5 13v6.5h14V13" />
    </template>
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  name: 'eye' | 'heart' | 'bubble' | 'star' | 'clip' | 'edit' | 'share';
  size?: number | string;
  filled?: boolean;
  /** stroke 宽度（filled=false 时生效），默认 1.6 */
  sw?: number | string;
}>();
const viewBox = '0 0 24 24';
</script>

<style scoped>
.idea-icon {
  display: inline-block;
  vertical-align: -0.18em;
  flex-shrink: 0;
}
</style>

<template>
  <!-- 全局便签悬浮层：容器不吃指针，便签自身可交互 -->
  <div v-if="active" class="sticky-layer" aria-label="灵感便签层">
    <StickyNote
      v-for="n in visibleNotes"
      :key="n.id"
      :note="n"
      :vw="vw"
      :vh="vh"
      :size="noteSize"
      @fed="feed"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import StickyNote from '@/components/sticky/StickyNote.vue';
import { useStickyStore } from '@/stores/stickyStore';
import { isTokenValid } from '@/utils/auth';

const store = useStickyStore();
const route = useRoute();

const vw = ref(window.innerWidth);
const vh = ref(window.innerHeight);

const onResize = () => {
  vw.value = window.innerWidth;
  vh.value = window.innerHeight;
};

/** 仅登录后激活（未登录/登录页不渲染） */
const active = computed(() => {
  if (route.meta.public || route.name === 'login' || route.name === 'not-found') return false;
  return isTokenValid(localStorage.getItem('token'));
});

/** 当前路由可见：全部浮动便签 + 钉在此路由的便签 */
const visibleNotes = computed(() => (active.value ? store.visibleOn(route.path) : []));

/** 便签边长：桌面 220 / 移动 160（按需求放大） */
const noteSize = computed(() => (vw.value <= 768 ? 160 : 220));

/** 投喂素材池：便签拖入池窗口 */
function feed(id: number) {
  store.patch(id, { inPool: true });
  ElMessage.success('灵感已投喂 AI 素材池');
}

onMounted(() => {
  window.addEventListener('resize', onResize, { passive: true });
  if (active.value) void store.fetch();
});

onBeforeUnmount(() => window.removeEventListener('resize', onResize));
</script>

<style scoped>
.sticky-layer {
  position: fixed;
  inset: 0;
  pointer-events: none; /* 层不吃点击，便签自身 auto */
  z-index: 125; /* < FAB 悬浮球(130) < 弹窗(2000+)，> 页面内容与 RAG 抽屉(120) */
}
</style>

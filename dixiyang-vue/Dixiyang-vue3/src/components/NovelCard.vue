<template>
  <div class="novel-card-wrapper" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div class="glass-card novel-card" :class="{ flipped: isFlipped }" @click="handleClick">
      <div class="card-glow" :style="{ opacity: isHovered ? 1 : 0 }"></div>

      <!-- 封面层 -->
      <div class="novel-cover-wrapper">
        <button class="novel-cover">
          <img
            :src="coverUrl || defaultCover"
            :alt="novel.title"
            @error="(e: Event) => { (e.target as HTMLImageElement).src = defaultCover }"
          >
        </button>
      </div>

      <!-- 内容层 -->
      <div class="card-content">
        <div class="card-header">
          <span class="pen-name">{{ novel.pen_name || '匿名作者' }}</span>
          <span class="novel-id">#{{ novel.id }}</span>
        </div>
        <h2 class="novel-title">{{ novel.title }}</h2>
        <p class="description">{{ novel.description || '暂无描述' }}</p>
        <div class="card-stats" :class="{ expanded: isHovered }">
          <div class="stat">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            <span>角色</span>
            <b class="stat-value">{{ novel.char_count || 0 }}</b>
          </div>
          <div class="stat">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M4 6h16V4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16v-2H4V6z"/></svg>
            <span>节点</span>
            <b class="stat-value">{{ novel.node_count || 0 }}</b>
          </div>
          <div class="stat" v-if="isHovered">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-2.16-2.66c-.44-.53-1.25-.53-1.69 0-.44.54-.44 1.39 0 1.93l3 3.68c.44.53 1.25.53 1.69 0L21.27 9c.44-.54.44-1.39 0-1.93-.44-.54-1.25-.54-1.69 0l-6.62 8.22z"/></svg>
            <span>关联</span>
            <b class="stat-value">{{ novel.relation_count || 0 }}</b>
          </div>
        </div>
        <button class="enter-btn character-btn" @click.stop="handleCharacterManager">
          <span class="btn-text">角色管理</span>
          <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
        </button>
        <button class="enter-btn delete-btn" @click.stop="handleDelete">
          <span class="btn-text">删除小说</span>
          <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
        </button>
        <button class="enter-btn" @click.stop="handleOpenNovel">
          <span class="btn-text">进入创作</span>
          <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M5 13l4 4L19 7"/></svg>
        </button>
      </div>
      <div class="card-border-gradient"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { resolveCoverUrl } from '@/utils/localImages'
import defaultCover from '@/images/default-cover.png'

interface Novel {
  id: string | number
  title: string
  cover_url?: string
  description?: string
  pen_name?: string
  char_count?: number
  node_count?: number
  relation_count?: number
  [key: string]: unknown
}

const props = defineProps<{
  novel: Novel
  isFlipped: boolean
  isHovered?: boolean
}>()

const emit = defineEmits<{
  mouseenter: []
  mouseleave: []
  click: []
  'character-manager': []
  delete: []
  'open-novel': []
}>()

const isHovered = computed(() => props.isHovered || false)

const coverUrl = computed(() => {
  return resolveCoverUrl(props.novel.cover_url)
})

const handleMouseEnter = () => emit('mouseenter')
const handleMouseLeave = () => emit('mouseleave')
const handleClick = () => emit('click')
const handleCharacterManager = () => emit('character-manager')
const handleDelete = () => emit('delete')
const handleOpenNovel = () => emit('open-novel')
</script>

<style scoped>
/* 封面层 - 真实卡牌翻转动画 */
.novel-cover-wrapper {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: transform 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  opacity 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  opacity: 1;
  transform: rotateY(0deg) rotateX(0deg) scale(1);
  transform-origin: center center;
  transform-style: preserve-3d;
  backface-visibility: hidden;
  border-radius: 24px;
}

/* 悬停时轻微旋转预览 */
.novel-card-wrapper:hover .novel-card:not(.flipped) .novel-cover-wrapper {
  transform: rotateY(-12deg) rotateX(2deg) scale(0.98);
  opacity: 0.8;
}

/* 翻转后的状态 - 180度水平翻转 + 逐渐消失 */
.novel-card.flipped .novel-cover-wrapper {
  z-index: 0;
  pointer-events: none;
  backface-visibility: hidden;
  transform: rotateY(180deg) rotateX(0deg) scale(0.95);
  opacity: 0;
}

.novel-cover {
  width: 100%;
  height: 100%;
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
  border-radius: 20px;
  overflow: hidden;
}

.novel-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 24px;
  display: block;
}

.card-content {
  position: absolute;
  inset: 0;
  padding: 28px;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: transform 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  opacity 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55),
  visibility 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  transform: rotateY(-180deg) translateY(40px);
  opacity: 0;
  visibility: hidden;
  backface-visibility: hidden;
  pointer-events: none;
}

/* 其余样式与HomeView保持一致 */
.novel-card-wrapper {
  cursor: pointer;
  transition: all 0.4s ease;
}

.novel-card-wrapper:hover { transform: translateY(-8px); }

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 0;
  height: 100%;
  aspect-ratio: 2 / 3;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transform-style: preserve-3d;
  cursor: pointer;
  perspective: 1200px;
  box-sizing: border-box;
}

.novel-card {
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.novel-card:hover {
  border-color: var(--glass-border-hover);
  box-shadow: var(--card-shadow), var(--glow-shadow);
  background: rgba(255, 255, 255, 0.08);
}

.card-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

/* 内容层内部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pen-name {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.novel-id {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-family: 'Courier New', monospace;
}

.novel-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--text-primary);
  line-height: 1.3;
}

.description {
  flex: 1;
  font-size: 0.95rem;
  color: var(--description-color);
  line-height: 1.6;
  margin: 0 0 20px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.card-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  transition: all 0.3s ease;
}

.card-stats.expanded {
  gap: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  align-items: center;
  min-width: 60px;
}

.stat-icon {
  width: 20px;
  height: 20px;
  color: var(--neon-blue);
}

.stat-value {
  color: var(--neon-cyan);
  font-weight: 700;
  font-size: 1.1rem;
}

.enter-btn {
  width: 100%;
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(59, 130, 246, 0.15);
  color: var(--text-primary);
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
}

.enter-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: var(--neon-blue);
  transform: translateY(-2px);
}

.enter-btn.character-btn {
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.3);
}

.enter-btn.character-btn:hover {
  background: rgba(168, 85, 247, 0.3);
  border-color: var(--neon-purple);
}

.enter-btn.delete-btn {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.enter-btn.delete-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.card-border-gradient {
  position: absolute;
  inset: -2px;
  border-radius: 26px;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue), var(--neon-cyan));
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s;
}

.novel-card:hover .card-border-gradient {
  opacity: 0.3;
}

/* 内容层翻转显示 */
.novel-card.flipped .card-content {
  transform: rotateY(0deg) translateY(0);
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
</style>

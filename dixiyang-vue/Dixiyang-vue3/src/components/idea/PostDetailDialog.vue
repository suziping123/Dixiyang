<template>
  <el-dialog
    :model-value="modelValue"
    title="帖子详情"
    width="760px"
    :close-on-click-modal="false"
    @update:model-value="close"
    @open="load"
  >
    <div v-loading="loading" class="detail-body">
      <template v-if="post">
        <div class="d-head">
          <span class="cat-tag" :class="`cat-${post.category}`">{{ catLabel(post.category) }}</span>
          <span v-if="post.status === 'removed'" class="removed-flag">已下架</span>
          <span class="d-time">{{ post.createTime }}</span>
        </div>
        <h2 class="d-title">{{ post.title }}</h2>
        <div class="d-meta">
          <b>{{ post.authorName }}</b>
          <span><IdeaIcon name="eye" :size="14" />{{ post.viewCount }}</span>
          <span><IdeaIcon name="bubble" :size="14" />{{ post.commentCount }}</span>
          <span><IdeaIcon name="star" :size="14" />{{ post.collectCount }}</span>
        </div>

        <div v-if="post.tags?.length" class="d-tags">
          <span v-for="t in post.tags" :key="t" class="mini-tag">#{{ t }}</span>
        </div>

        <!-- 配图画廊（置顶展示：封面点进详情第一眼可见，用户反馈⑦；点击放大） -->
        <div v-if="post.images?.length" class="d-gallery">
          <el-image
            v-for="(u, i) in post.images"
            :key="u"
            class="d-gallery-img"
            :src="u"
            :preview-src-list="post.images"
            :initial-index="i"
            fit="cover"
            hide-on-click-modal
          />
        </div>

        <div class="d-content">{{ post.content }}</div>

        <!-- 附件区 -->
        <div v-if="post.attach" class="attach-box" v-loading="attLoading">
          <div class="attach-head">
            <span class="attach-title"><IdeaIcon name="clip" :size="14" />{{ post.attach.type === 'character_card' ? '角色卡附件' : '对话快照附件' }}</span>
            <el-button
              v-if="post.attach.type === 'character_card' && attachData?.characters?.length"
              size="small"
              type="primary"
              :loading="importing"
              @click="showImport = true"
            >
              一键导入到我的小说
            </el-button>
          </div>

          <template v-if="post.attach.type === 'character_card' && attachData?.characters?.length">
            <div v-for="c in attachData!.characters" :key="c.characterId" class="char-card">
              <div class="char-name">
                <b>{{ c.name }}</b>
                <span v-if="c.gender || c.age">{{ [c.gender, c.age != null ? `${c.age}岁` : ''].filter(Boolean).join(' · ') }}</span>
              </div>
              <p v-if="c.personality"><label>性格</label>{{ c.personality }}</p>
              <p v-if="c.background"><label>背景</label>{{ c.background }}</p>
              <p v-if="c.appearance"><label>外貌</label>{{ c.appearance }}</p>
            </div>
          </template>

          <template v-else-if="post.attach.type === 'chat_snapshot'">
            <div class="snap-box">
              <p class="snap-count">共 {{ snapshotCount }} 条消息的只读快照</p>
              <div v-for="(m, i) in snapshotPreview" :key="i" class="snap-msg">
                <b>{{ m.role === 'assistant' ? 'AI' : '我' }}：</b>{{ m.content }}
              </div>
              <p v-if="snapshotCount > snapshotPreview.length" class="snap-more">
                …… 仅显示前 {{ snapshotPreview.length }} 条
              </p>
            </div>
          </template>
        </div>

        <!-- 操作栏：图标化 + 点击弹跳反馈 -->
        <div class="d-actions">
          <button
            type="button"
            class="act-btn"
            :class="{ on: post.likedByMe, bump: bumpKey === 'like' }"
            :disabled="acting"
            @click="onLike"
          >
            <IdeaIcon name="heart" :size="17" :filled="post.likedByMe" />
            <span :key="post.likeCount" class="act-num">点赞 {{ post.likeCount }}</span>
          </button>
          <button
            type="button"
            class="act-btn star"
            :class="{ on: post.collectedByMe, bump: bumpKey === 'collect' }"
            :disabled="acting"
            @click="onCollect"
          >
            <IdeaIcon name="star" :size="17" :filled="post.collectedByMe" />
            <span :key="post.collectCount" class="act-num">收藏 {{ post.collectCount }}</span>
          </button>
          <span class="spacer" />
          <template v-if="isAuthor">
            <template v-if="post.status === 'published'">
              <el-button type="danger" plain @click="onRemove">下架</el-button>
            </template>
            <template v-else>
              <el-button type="primary" plain @click="openEdit">
                <IdeaIcon name="edit" :size="14" />&nbsp;编辑帖子
              </el-button>
              <el-button type="success" plain @click="onRestore">重新上架</el-button>
            </template>
          </template>
        </div>

        <!-- 评论 -->
        <div class="comment-box">
          <h4>评论（{{ commentTotal }}）</h4>
          <div class="comment-input">
            <el-input
              v-model="commentText"
              type="textarea"
              :rows="2"
              maxlength="1000"
              show-word-limit
              placeholder="友善评论，最多 1000 字（回车换行，点发送提交）"
            />
            <el-button type="primary" :loading="commenting" @click="onComment">发送</el-button>
          </div>
          <div v-if="comments.length" class="comment-list">
            <div v-for="c in comments" :key="c.id" class="comment-row">
              <div class="comment-who">
                <b>{{ c.authorName }}</b>
                <span>{{ c.createTime }}</span>
                <button v-if="c.authorId === myAuthorId" type="button" class="comment-del" @click="onDeleteComment(c.id)">
                  删除
                </button>
              </div>
              <p class="comment-text">{{ c.content }}</p>
            </div>
          </div>
          <p v-else class="comment-empty">还没有评论，来抢沙发</p>
          <el-pagination
            v-if="commentTotal > 10"
            v-model:current-page="commentPage"
            layout="prev, pager, next"
            small
            :total="commentTotal"
            :page-size="10"
            @current-change="loadComments()"
          />
        </div>
      </template>
    </div>

    <!-- 导入目标选择 -->
    <el-dialog v-model="showImport" title="导入到哪本小说？" width="420px" append-to-body>
      <el-select v-model="importNovelId" placeholder="选择小说" filterable style="width: 100%">
        <el-option v-for="n in myNovels" :key="n.id" :label="n.title" :value="n.id" />
      </el-select>
      <template #footer>
        <el-button @click="showImport = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="onImport">确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 下架帖编辑（下架为修改服务，用户反馈⑧） -->
    <PostEditDialog v-model="editVisible" :post-id="props.postId" @saved="onEdited" append-to-body />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getPost, getAttachment, importAttachment,
  toggleLike, toggleCollect,
  listComments, addComment, deleteComment,
  removePost, restorePost, getNovelOptions,
  type IdeaPostItem, type IdeaComment, type CharacterCard,
} from '@/api/ideaApi'
import IdeaIcon from '@/components/idea/IdeaIcon.vue'
import PostEditDialog from '@/components/idea/PostEditDialog.vue'
import { confirmDelete } from '@/utils/confirm'

const props = defineProps<{
  modelValue: boolean
  postId: number
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  change: []
}>()

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const loading = ref(false)
const post = ref<IdeaPostItem | null>(null)
const attLoading = ref(false)
const attachData = ref<{ characters?: CharacterCard[]; messages?: { role: string; content: string }[] } | null>(null)
const acting = ref(false)
/** 点赞/收藏按钮弹跳动画键，320ms 后清除 */
const bumpKey = ref('')
const editVisible = ref(false)

const comments = ref<IdeaComment[]>([])
const commentTotal = ref(0)
const commentPage = ref(1)
const commentText = ref('')
const commenting = ref(false)

const showImport = ref(false)
const importNovelId = ref<number | ''>('')
const myNovels = ref<{ id: number; title: string }[]>([])
const importing = ref(false)

// 自己的 authorId（用于评论删除按钮显示）
const myAuthorId = ref(-1)

const isAuthor = computed(() => !!post.value && post.value.authorId === myAuthorId.value)

const snapshotCount = computed(() => attachData.value?.messages?.length ?? 0)
const snapshotPreview = computed(() => (attachData.value?.messages ?? []).slice(0, 6))

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

const loadMyId = () => {
  // 与 UserStore 存储对齐：优先独立 userId key，兜底 userInfo JSON
  const direct = Number(localStorage.getItem('userId'))
  if (direct) {
    myAuthorId.value = direct
    return
  }
  try {
    const raw = localStorage.getItem('userInfo')
    if (raw) myAuthorId.value = (JSON.parse(raw) as { id?: number }).id ?? -1
  } catch {
    /* 忽略解析失败 */
  }
}

const load = async () => {
  loading.value = true
  loadMyId()
  commentPage.value = 1
  commentText.value = ''
  attachData.value = null
  try {
    const data = unwrap<IdeaPostItem>(await getPost(props.postId))
    if (data) {
      post.value = data
      if (data.attach) loadAttachment()
    }
    loadComments()
    getNovelOptions().then((res) => {
      myNovels.value = unwrap<{ records: { id: number; title: string }[] }>(res)?.records ?? []
    })
  } finally {
    loading.value = false
  }
}

const loadAttachment = async () => {
  attLoading.value = true
  try {
    const data = unwrap<{ type: string; data: unknown }>(await getAttachment(props.postId))
    if (data) attachData.value = data.data as typeof attachData.value
  } finally {
    attLoading.value = false
  }
}

const loadComments = async () => {
  const data = unwrap<{ total: number; list: IdeaComment[] }>(
    await listComments(props.postId, { page: commentPage.value, pageSize: 10 }),
  )
  if (data) {
    comments.value = data.list
    commentTotal.value = data.total
  }
}

// ---------- 互动 ----------

const playBump = (key: string) => {
  bumpKey.value = key
  window.setTimeout(() => {
    if (bumpKey.value === key) bumpKey.value = ''
  }, 320)
}

const onLike = async () => {
  if (!post.value || acting.value) return
  const p = post.value
  const prevLiked = p.likedByMe
  const prevCount = p.likeCount
  p.likedByMe = !prevLiked
  p.likeCount = prevCount + (prevLiked ? -1 : 1)
  playBump('like')
  acting.value = true
  try {
    const res = (await toggleLike(p.id)) as { code?: number; msg?: string; data?: { liked: boolean; likeCount: number } }
    if (res.code === 200 && res.data) {
      p.likedByMe = res.data.liked
      p.likeCount = res.data.likeCount
      emit('change')
    } else {
      p.likedByMe = prevLiked
      p.likeCount = prevCount
      ElMessage.warning(res.msg || '点赞失败')
    }
  } catch {
    p.likedByMe = prevLiked
    p.likeCount = prevCount
    ElMessage.warning('网络异常，已还原')
  } finally {
    acting.value = false
  }
}

const onCollect = async () => {
  if (!post.value || acting.value) return
  const p = post.value
  const prev = p.collectedByMe
  const prevCount = p.collectCount
  p.collectedByMe = !prev
  p.collectCount = prevCount + (prev ? -1 : 1)
  playBump('collect')
  acting.value = true
  try {
    const res = (await toggleCollect(p.id)) as { code?: number; msg?: string; data?: { collected: boolean; collectCount: number } }
    if (res.code === 200 && res.data) {
      p.collectedByMe = res.data.collected
      p.collectCount = res.data.collectCount
      emit('change')
    } else {
      p.collectedByMe = prev
      p.collectCount = prevCount
      ElMessage.warning(res.msg || '收藏失败')
    }
  } catch {
    p.collectedByMe = prev
    p.collectCount = prevCount
    ElMessage.warning('网络异常，已还原')
  } finally {
    acting.value = false
  }
}

// ---------- 下架帖编辑（用户反馈⑧：下架为修改服务） ----------

const openEdit = () => {
  editVisible.value = true
}

const onEdited = () => {
  load()
  emit('change')
}

const onRemove = async () => {
  const ok = await confirmDelete('确定下架这篇帖子吗？下架后广场不再展示，你仍可重新上架。', '警告')
  if (!ok) return
  const res = (await removePost(props.postId)) as { code?: number; msg?: string }
  if (res.code === 200) {
    ElMessage.success('已下架')
    if (post.value) post.value.status = 'removed'
    emit('change')
  } else {
    ElMessage.warning(res.msg || '操作失败')
  }
}

const onRestore = async () => {
  const res = (await restorePost(props.postId)) as { code?: number; msg?: string }
  if (res.code === 200) {
    ElMessage.success('已重新上架')
    if (post.value) post.value.status = 'published'
    emit('change')
  } else {
    ElMessage.warning(res.msg || '操作失败')
  }
}

// ---------- 导入 ----------

const onImport = async () => {
  if (!importNovelId.value) {
    ElMessage.warning('请选择小说')
    return
  }
  importing.value = true
  try {
    const data = unwrap<{ characters: { characterId: number; name: string }[] }>(
      await importAttachment(props.postId, importNovelId.value),
    )
    if (data) {
      ElMessage.success(`已导入角色：${data.characters.map((c) => c.name).join('、')}`)
      showImport.value = false
    }
  } finally {
    importing.value = false
  }
}

// ---------- 评论 ----------

const onComment = async () => {
  const text = commentText.value.trim()
  if (!text) return
  commenting.value = true
  try {
    const res = (await addComment(props.postId, text)) as { code?: number; msg?: string }
    if (res.code === 200) {
      commentText.value = ''
      commentPage.value = 1
      loadComments()
      if (post.value) post.value.commentCount += 1
      emit('change')
    } else {
      ElMessage.warning(res.msg || '评论失败')
    }
  } finally {
    commenting.value = false
  }
}

const onDeleteComment = async (id: number) => {
  const ok = await confirmDelete('确定删除这条评论吗？', '警告')
  if (!ok) return
  const res = (await deleteComment(id)) as { code?: number; msg?: string }
  if (res.code === 200) {
    ElMessage.success('已删除')
    loadComments()
    if (post.value) post.value.commentCount = Math.max(0, post.value.commentCount - 1)
    emit('change')
  } else {
    ElMessage.warning(res.msg || '删除失败')
  }
}

const close = () => emit('update:modelValue', false)
</script>

<style scoped>
.detail-body {
  max-height: 64vh;
  overflow-y: auto;
  padding-right: 4px;
  /* 弹窗内容区卡片实底化（teleport 到 body 后脱离 .idea-page 作用域，此处单独覆盖 4% 半透明全局值） */
  --surface-card: #171a24;
}

.d-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.d-time {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

.cat-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-cyan);
}

.cat-character { color: var(--accent-purple); }
.cat-setting { color: #f0c674; }
.cat-timeline { color: #8be98b; }
.cat-tech { color: var(--accent-primary); }

.removed-flag {
  font-size: 11px;
  color: var(--danger);
  background: var(--danger-soft);
  padding: 2px 8px;
  border-radius: 999px;
}

.d-title {
  margin: 0 0 8px;
  font-size: 22px;
  line-height: 1.4;
}

.d-meta {
  display: flex;
  gap: 14px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.d-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.d-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.mini-tag {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface-input);
  border-radius: 4px;
  padding: 2px 6px;
}

.d-content {
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 14px;
}

/* 配图画廊 */
.d-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.d-gallery-img {
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--surface-glass-border);
  cursor: zoom-in;
  background: var(--surface-input);
}

.d-gallery-img :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--dur-fast) var(--ease-out);
}

.d-gallery-img:hover :deep(.el-image__inner) {
  transform: scale(1.05);
}

.attach-box {
  border: 1px dashed var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  margin-bottom: 14px;
  background: var(--accent-soft);
}

.attach-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.attach-title {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-primary);
}

.char-card {
  background: var(--surface-card);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  margin-bottom: 8px;
}

.char-name {
  display: flex;
  gap: 10px;
  align-items: baseline;
  margin-bottom: 4px;
}

.char-name span {
  font-size: 12px;
  color: var(--text-secondary);
}

.char-card p {
  margin: 4px 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.char-card label {
  font-size: 11px;
  color: var(--text-muted);
  margin-right: 6px;
  background: var(--surface-input);
  border-radius: 4px;
  padding: 1px 5px;
}

.snap-box {
  background: var(--surface-card);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
}

.snap-count {
  font-size: 12px;
  color: var(--accent-cyan);
  margin: 0 0 6px;
}

.snap-msg {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.snap-more {
  font-size: 12px;
  color: var(--text-muted);
  margin: 6px 0 0;
}

.d-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.spacer {
  flex: 1;
}

/* ---------- 操作按钮：图标化 + 点击弹跳（用户反馈①②） ---------- */

.act-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-glass);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 7px 16px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition: color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out),
    background var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
}

.act-btn:hover:not(:disabled) {
  color: var(--text-on-page);
  border-color: var(--accent-primary);
}

.act-btn:active:not(:disabled) {
  transform: scale(0.93);
}

.act-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.act-btn.on {
  color: var(--danger, #f56c6c);
  border-color: var(--danger, #f56c6c);
  background: var(--danger-soft, rgba(245, 108, 108, 0.12));
}

.act-btn.star.on {
  color: #f0c674;
  border-color: #f0c674;
  background: rgba(240, 198, 116, 0.12);
}

.act-btn.bump .idea-icon,
.act-btn.bump .act-num {
  animation: act-bump 0.32s var(--ease-out);
}

.act-num {
  display: inline-block;
}

@keyframes act-bump {
  0% { transform: scale(1); }
  35% { transform: scale(1.3); }
  70% { transform: scale(0.92); }
  100% { transform: scale(1); }
}

.comment-box h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.comment-input {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.comment-input .el-textarea {
  flex: 1;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-row {
  background: var(--surface-card);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
}

.comment-who {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}

.comment-who b {
  color: var(--text-on-card);
  font-size: 13px;
}

.comment-del {
  margin-left: auto;
  border: none;
  background: none;
  color: var(--danger);
  font-size: 12px;
  cursor: pointer;
}

.comment-text {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.comment-empty {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 12px 0;
}

/* 移动端：操作栏换行，内容区紧凑 */
@media (max-width: 768px) {
  .detail-body {
    max-height: 74vh;
  }

  .d-title {
    font-size: 18px;
  }

  .d-meta {
    gap: 10px;
    flex-wrap: wrap;
  }

  .d-actions .spacer {
    display: none;
  }

  .d-actions .el-button {
    margin-left: 0;
  }

  .d-gallery {
    grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
  }

  .comment-input {
    flex-direction: column;
  }

  .comment-input .el-button {
    align-self: flex-end;
  }
}
</style>

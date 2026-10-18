<template>
  <div class="posts-page">
    <header class="page-head">
      <div>
        <h1 class="page-title">广场管理</h1>
        <p class="page-sub">帖子下架 / 恢复 / 删除 · 评论治理（平台下架后作者不可自行恢复）</p>
      </div>
    </header>

    <div class="cf-row">
      <el-select v-model="status" placeholder="全部状态" @change="search">
        <el-option label="全部状态" value="" />
        <el-option label="已发布" value="published" />
        <el-option label="已下架" value="removed" />
      </el-select>
      <el-select v-model="category" placeholder="全部分区" @change="search">
        <el-option label="全部分区" value="" />
        <el-option v-for="(label, key) in CATEGORY_LABEL" :key="key" :label="label" :value="key" />
      </el-select>
      <el-input
        v-model="keyword"
        class="cf-grow"
        style="max-width: 260px"
        placeholder="搜索标题 / 摘要"
        clearable
        :prefix-icon="Search"
        @keyup.enter="search"
        @clear="search"
      />
      <el-button @click="resetFilters">重置</el-button>
    </div>

    <div class="section-rule">
      <strong>帖子列表</strong>
      <span class="sr-line"></span>
      <i class="sr-count">共 {{ total }} 条</i>
    </div>

    <section class="c-card table-card rise-in">
      <el-table :data="list" v-loading="loading" size="large">
        <el-table-column prop="id" label="ID" width="66" />
        <el-table-column label="标题" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="post-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="authorName" label="作者" width="120" show-overflow-tooltip />
        <el-table-column label="分区" width="86">
          <template #default="{ row }">{{ catLabel(row.category) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="104">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'published'" type="success" effect="plain">已发布</el-tag>
            <el-tag v-else-if="row.adminRemoved" type="danger" effect="plain">平台下架</el-tag>
            <el-tag v-else type="info" effect="plain">已下架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="互动" width="128">
          <template #default="{ row }">
            <span class="tnum counts">赞 {{ row.likeCount }} · 评 {{ row.commentCount }} · 藏 {{ row.collectCount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="150">
          <template #default="{ row }">{{ (row.createTime || '').slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="224" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
            <el-button
              size="small"
              :type="row.status === 'published' ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'published' ? '下架' : '恢复' }}
            </el-button>
            <el-button size="small" type="danger" @click="removePost(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager-row">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </section>

    <!-- 详情：正文 / 配图 / 附件 / 评论治理 -->
    <el-dialog v-model="detailVisible" title="帖子详情" width="780px" destroy-on-close>
      <div v-loading="detailLoading" class="dt">
        <template v-if="detail">
          <div class="dt-head">
            <div class="dt-tags">
              <el-tag v-if="detail.status === 'published'" type="success" effect="plain">已发布</el-tag>
              <el-tag v-else-if="detail.adminRemoved" type="danger" effect="plain">平台下架</el-tag>
              <el-tag v-else type="info" effect="plain">已下架</el-tag>
              <el-tag v-for="t in detail.tags" :key="t" effect="plain" type="warning">{{ t }}</el-tag>
            </div>
            <h3 class="dt-title">{{ detail.title }}</h3>
            <p class="dt-meta tnum">
              {{ detail.authorName }} · {{ catLabel(detail.category) }} · {{ detail.createTime }}
              · 浏览 {{ detail.viewCount }} · 赞 {{ detail.likeCount }} · 评 {{ detail.commentCount }} · 藏 {{ detail.collectCount }}
            </p>
          </div>

          <p class="dt-content">{{ detail.content || '（无正文）' }}</p>

          <div v-if="detail.images.length" class="dt-imgs">
            <el-image
              v-for="u in detail.images"
              :key="u"
              :src="u"
              :preview-src-list="detail.images"
              fit="cover"
              class="dt-img"
              preview-teleported
            />
          </div>

          <p v-if="detail.attachment" class="dt-attach">
            附件：{{ attachLabel(detail.attachment.type) }}（只读快照）{{ detail.attachment.meta ? ' · ' + detail.attachment.meta : '' }}
          </p>

          <div class="section-rule">
            <strong>评论</strong>
            <span class="sr-line"></span>
            <i class="sr-count">共 {{ commentTotal }} 条</i>
          </div>

          <div class="cmt-list" v-loading="commentsLoading">
            <div v-for="c in comments" :key="c.id" class="cmt">
              <div class="cmt-main">
                <span class="cmt-who">{{ c.authorName }}</span>
                <span class="cmt-time">{{ (c.createTime || '').slice(0, 16) }}</span>
                <p class="cmt-text">{{ c.content }}</p>
              </div>
              <el-button size="small" type="danger" plain @click="removeComment(c)">删除</el-button>
            </div>
            <p v-if="!comments.length && !commentsLoading" class="cmt-empty">暂无评论</p>
            <div class="pager-row" v-if="commentTotal > commentPageSize">
              <el-pagination
                v-model:current-page="commentPage"
                :page-size="commentPageSize"
                :total="commentTotal"
                layout="prev, pager, next"
                small
                background
                @current-change="loadComments"
              />
            </div>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="detail"
          :type="detail.status === 'published' ? 'warning' : 'success'"
          @click="toggleStatus(detail)"
        >
          {{ detail.status === 'published' ? '下架' : '恢复' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { confirmDelete } from '@/utils/confirm'
import {
  deleteAdminComment, deleteAdminPost, getAdminPost, getAdminPostComments,
  getAdminPosts, setAdminPostStatus,
} from '../api/admin'
import type { AdminCommentItem, AdminPostDetail, AdminPostItem } from '../api/admin'
import { unwrap } from '../api/util'

defineOptions({ name: 'AdminPosts' })

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const ATTACH_LABEL: Record<string, string> = {
  chat_snapshot: '对话快照', character_card: '角色卡', setting_bundle: '设定集', timeline_view: '时间线视图',
}
const attachLabel = (t: string) => ATTACH_LABEL[t] ?? t

const list = ref<AdminPostItem[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const status = ref('')
const category = ref('')
const keyword = ref('')

const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref<AdminPostDetail | null>(null)
const comments = ref<AdminCommentItem[]>([])
const commentTotal = ref(0)
const commentsLoading = ref(false)
const commentPage = ref(1)
const commentPageSize = 10

const load = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: AdminPostItem[] }>(
      await getAdminPosts({
        page: page.value,
        pageSize,
        status: status.value,
        category: category.value,
        keyword: keyword.value,
      }),
    )
    if (data) {
      list.value = data.list
      total.value = data.total
    }
  } finally {
    loading.value = false
  }
}

const search = () => {
  page.value = 1
  load()
}

const resetFilters = () => {
  status.value = ''
  category.value = ''
  keyword.value = ''
  search()
}

const openDetail = async (row: AdminPostItem) => {
  detailVisible.value = true
  detail.value = null
  comments.value = []
  commentTotal.value = 0
  commentPage.value = 1
  await Promise.all([loadDetail(row.id), loadComments(row.id)])
}

const loadDetail = async (id: number) => {
  detailLoading.value = true
  try {
    detail.value = unwrap<AdminPostDetail>(await getAdminPost(id))
  } finally {
    detailLoading.value = false
  }
}

const loadComments = async (id?: number) => {
  const postId = id ?? detail.value?.id
  if (!postId) return
  commentsLoading.value = true
  try {
    const data = unwrap<{ total: number; list: AdminCommentItem[] }>(
      await getAdminPostComments(postId, commentPage.value, commentPageSize),
    )
    if (data) {
      comments.value = data.list
      commentTotal.value = data.total
    }
  } finally {
    commentsLoading.value = false
  }
}

const toggleStatus = async (row: AdminPostItem | AdminPostDetail) => {
  const next = row.status === 'published' ? 'removed' : 'published'
  try {
    const res = unwrap<{ id: number; status: string; adminRemoved: boolean }>(
      await setAdminPostStatus(row.id, next),
    )
    if (!res) return
    ElMessage.success(next === 'removed' ? '已下架（作者不可自行恢复）' : '已恢复上架')
    await load()
    if (detail.value?.id === row.id) await loadDetail(row.id)
  } catch (e) {
    ElMessage.error((e as Error).message || '操作失败')
  }
}

const removePost = async (row: AdminPostItem) => {
  const ok = await confirmDelete(
    `将永久删除《${row.title}》及其全部评论、点赞收藏记录、配图与附件文件，且不可恢复。确定继续？`,
    '危险操作',
  )
  if (!ok) return
  try {
    const res = (await deleteAdminPost(row.id)) as { code?: number; msg?: string }
    if (res?.code !== 200) {
      ElMessage.warning(res?.msg || '删除失败')
      return
    }
    ElMessage.success('已删除')
    if (detail.value?.id === row.id) detailVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error((e as Error).message || '删除失败')
  }
}

const removeComment = async (c: AdminCommentItem) => {
  const ok = await confirmDelete(`将删除该条评论（${c.authorName}：${c.content.slice(0, 30)}…），确定继续？`, '危险操作')
  if (!ok) return
  try {
    const res = (await deleteAdminComment(c.id)) as { code?: number; msg?: string }
    if (res?.code !== 200) {
      ElMessage.warning(res?.msg || '删除失败')
      return
    }
    ElMessage.success('已删除评论')
    if (detail.value) {
      detail.value.commentCount = Math.max(0, detail.value.commentCount - 1)
    }
    await loadComments()
    await load()
  } catch (e) {
    ElMessage.error((e as Error).message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.post-title { color: var(--text-primary); font-weight: 600; }
.counts { font-size: 0.8125rem; color: var(--text-secondary); white-space: nowrap; }

/* ---------- 详情弹窗 ---------- */
.dt { min-height: 120px; }
.dt-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.dt-title { margin: 0 0 6px; font-size: 1.125rem; color: var(--text-primary); }
.dt-meta { margin: 0; font-size: 0.8125rem; color: var(--text-muted); }

.dt-content {
  margin: 14px 0 0;
  padding: 12px 14px;
  max-height: 300px;
  overflow-y: auto;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--surface-glass-border);
  font-size: 0.875rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
}

.dt-imgs { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.dt-img { width: 84px; height: 84px; border-radius: var(--radius-sm); cursor: zoom-in; }

.dt-attach { margin: 12px 0 0; font-size: 0.8125rem; color: var(--text-secondary); }

.cmt-list { display: flex; flex-direction: column; gap: 8px; }
.cmt {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--surface-glass-border);
}
.cmt-main { min-width: 0; }
.cmt-who { font-size: 0.8125rem; font-weight: 600; color: var(--text-primary); }
.cmt-time { margin-left: 8px; font-size: 0.72rem; color: var(--text-muted); }
.cmt-text { margin: 4px 0 0; font-size: 0.8125rem; color: var(--text-secondary); word-break: break-word; }
.cmt-empty { margin: 6px 0; font-size: 0.8125rem; color: var(--text-muted); }

@media (max-width: 768px) {
  .cf-row :deep(.el-input), .cf-row :deep(.el-select) { width: 100%; max-width: none !important; }
}
/* 操作列按钮排布：贴紧防换行 */
:deep(.el-table .el-button + .el-button) { margin-left: 8px; }
</style>

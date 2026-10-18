<template>
  <div class="sticky-page">
    <header class="page-head">
      <div>
        <h1 class="page-title">灵感墙管理</h1>
        <p class="page-sub">便签查看与清理 · 关键词匹配用户名 / 昵称</p>
      </div>
    </header>

    <div class="cf-row">
      <el-select v-model="done" placeholder="全部状态" @change="search">
        <el-option label="全部状态" value="" />
        <el-option label="未完成" :value="false" />
        <el-option label="已完成" :value="true" />
      </el-select>
      <el-input
        v-model="keyword"
        class="cf-grow"
        style="max-width: 240px"
        placeholder="搜索用户名 / 昵称"
        clearable
        :prefix-icon="Search"
        @keyup.enter="search"
        @clear="search"
      />
      <el-button @click="resetFilters">重置</el-button>
    </div>

    <div class="section-rule">
      <strong>便签列表</strong>
      <span class="sr-line"></span>
      <i class="sr-count">共 {{ total }} 条</i>
    </div>

    <section class="c-card table-card rise-in">
      <el-table :data="list" v-loading="loading" size="large">
        <el-table-column prop="id" label="ID" width="66" />
        <el-table-column label="内容" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="note-content">{{ row.content || '（空便签）' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="userName" label="用户" width="130" show-overflow-tooltip />
        <el-table-column label="颜色" width="80">
          <template #default="{ row }">
            <span class="color-dot" :style="{ background: COLOR_MAP[row.color] || '#888' }" :title="row.color" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.done ? 'success' : 'info'" effect="plain">{{ row.done ? '已完成' : '未完成' }}</el-tag>
            <el-tag v-if="row.inPool" class="pool-tag" type="warning" effect="plain">池中</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="150">
          <template #default="{ row }">{{ (row.updateTime || row.createTime || '').slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openView(row)">查看</el-button>
            <el-button size="small" type="danger" @click="removeNote(row)">删除</el-button>
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

    <!-- 查看：完整正文 + 配图 -->
    <el-dialog v-model="viewVisible" title="便签内容" width="560px">
      <div v-if="viewing" class="nv">
        <p class="nv-meta">
          {{ viewing.userName }} · {{ viewing.color }}
          · {{ viewing.done ? '已完成' : '未完成' }}{{ viewing.inPool ? ' · 素材池' : '' }}
          · {{ viewing.updateTime || viewing.createTime }}
        </p>
        <p class="nv-content">{{ viewing.content || '（空便签）' }}</p>
        <div v-if="viewing.images.length" class="nv-imgs">
          <el-image
            v-for="u in viewing.images"
            :key="u"
            :src="u"
            :preview-src-list="viewing.images"
            fit="cover"
            class="nv-img"
            preview-teleported
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="viewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { confirmDelete } from '@/utils/confirm'
import { deleteAdminSticky, getAdminSticky } from '../api/admin'
import type { AdminStickyItem } from '../api/admin'
import { unwrap } from '../api/util'

defineOptions({ name: 'AdminSticky' })

const COLOR_MAP: Record<string, string> = {
  yellow: '#e8c96a', pink: '#e59ab6', blue: '#7fb3e3', green: '#8fce9b', purple: '#b79ae0',
}

const list = ref<AdminStickyItem[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const done = ref<boolean | ''>('')

const viewVisible = ref(false)
const viewing = ref<AdminStickyItem | null>(null)

const load = async () => {
  loading.value = true
  try {
    const data = unwrap<{ total: number; list: AdminStickyItem[] }>(
      await getAdminSticky({
        page: page.value,
        pageSize,
        keyword: keyword.value,
        done: done.value === '' ? null : done.value,
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
  keyword.value = ''
  done.value = ''
  search()
}

const openView = (row: AdminStickyItem) => {
  viewing.value = row
  viewVisible.value = true
}

const removeNote = async (row: AdminStickyItem) => {
  const brief = (row.content || '').slice(0, 30)
  const ok = await confirmDelete(
    `将删除 ${row.userName} 的便签（${brief || '空内容'}${(row.content || '').length > 30 ? '…' : ''}）及其正文文件，确定继续？`,
    '危险操作',
  )
  if (!ok) return
  try {
    const res = (await deleteAdminSticky(row.id)) as { code?: number; msg?: string }
    if (res?.code !== 200) {
      ElMessage.warning(res?.msg || '删除失败')
      return
    }
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    ElMessage.error((e as Error).message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.note-content { color: var(--text-secondary); }
.color-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  vertical-align: middle;
}
.pool-tag { margin-left: 6px; }

.nv-meta { margin: 0 0 10px; font-size: 0.8125rem; color: var(--text-muted); }
.nv-content {
  margin: 0;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--surface-glass-border);
  font-size: 0.875rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 380px;
  overflow-y: auto;
}
.nv-imgs { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.nv-img { width: 84px; height: 84px; border-radius: var(--radius-sm); cursor: zoom-in; }

@media (max-width: 768px) {
  .cf-row :deep(.el-input), .cf-row :deep(.el-select) { width: 100%; max-width: none !important; }
}
/* 操作列按钮排布：贴紧防换行 */
:deep(.el-table .el-button + .el-button) { margin-left: 8px; }
</style>

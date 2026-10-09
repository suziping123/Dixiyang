<template>
  <div class="admin-page">
    <FloatingNav />
    <header class="page-head">
      <h1>管理后台</h1>
      <el-input
        v-model="keyword"
        class="search-box"
        placeholder="搜索用户名 / 昵称"
        clearable
        :prefix-icon="Search"
        @keyup.enter="searchUsers"
        @clear="searchUsers"
      />
    </header>

    <!-- 总览卡片 -->
    <section class="stat-cards" v-loading="statsLoading">
      <div v-for="c in statCards" :key="c.label" class="stat-card">
        <span class="stat-num">{{ c.value }}</span>
        <span class="stat-label">{{ c.label }}</span>
      </div>
    </section>

    <section class="cat-row" v-if="stats">
      <span class="cat-chip" v-for="c in stats.postCategories" :key="c.category">
        {{ catLabel(c.category) }}<i>{{ c.count }}</i>
      </span>
    </section>

    <!-- 用户管理 -->
    <section class="user-panel">
      <h2>用户管理 <em>共 {{ userTotal }} 人</em></h2>
      <el-table :data="users" v-loading="usersLoading" size="large">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column label="注册时间" min-width="150">
          <template #default="{ row }">{{ (row.createTime || '').slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="large">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.role === 'admin' ? 'info' : 'warning'"
              @click="toggleRole(row)"
            >
              {{ row.role === 'admin' ? '取消管理员' : '设为管理员' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="userTotal"
        layout="prev, pager, next"
        background
        @current-change="loadUsers"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import FloatingNav from '@/components/FloatingNav.vue'
import { getAdminStats, getAdminUsers, updateUserRole } from '@/api/adminApi'
import type { AdminStats, AdminUserItem } from '@/api/adminApi'

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const stats = ref<AdminStats | null>(null)
const statsLoading = ref(false)
const users = ref<AdminUserItem[]>([])
const usersLoading = ref(false)
const userTotal = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')

const statCards = computed(() => [
  { label: '用户', value: stats.value?.totals.users ?? '-' },
  { label: '小说', value: stats.value?.totals.novels ?? '-' },
  { label: '广场帖子', value: stats.value?.totals.posts ?? '-' },
  { label: '对话会话', value: stats.value?.totals.sessions ?? '-' },
])

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    stats.value = unwrap<AdminStats>(await getAdminStats())
  } finally {
    statsLoading.value = false
  }
}

const loadUsers = async () => {
  usersLoading.value = true
  try {
    const data = unwrap<{ total: number; list: AdminUserItem[] }>(
      await getAdminUsers(page.value, pageSize, keyword.value),
    )
    if (data) {
      users.value = data.list
      userTotal.value = data.total
    }
  } finally {
    usersLoading.value = false
  }
}

const searchUsers = () => {
  page.value = 1
  loadUsers()
}

const toggleRole = async (row: AdminUserItem) => {
  const next = row.role === 'admin' ? 'user' : 'admin'
  try {
    unwrap(await updateUserRole(row.id, next))
    row.role = next
    ElMessage.success(next === 'admin' ? '已设为管理员' : '已取消管理员')
  } catch (e) {
    ElMessage.error((e as Error).message || '操作失败')
  }
}

onMounted(async () => {
  try {
    await loadStats()
    await loadUsers()
  } catch (e) {
    if ((e as Error).message?.includes('管理员') || (e as { response?: { status?: number } }).response?.status === 403) {
      ElMessage.error('需要管理员权限')
    }
  }
})
</script>

<style scoped>
.admin-page {
  position: relative;
  min-height: 100vh;
  padding: 28px 32px 60px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}
.page-head h1 { font-size: 26px; color: var(--text-on-page); margin: 0; }
.search-box { width: 260px; }

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}
.stat-card {
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: 12px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stat-num { font-size: 30px; font-weight: 700; color: var(--accent-cyan); }
.stat-label { font-size: 13px; color: var(--text-secondary); }

.cat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 22px; }
.cat-chip {
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--text-on-card);
}
.cat-chip i { font-style: normal; margin-left: 6px; color: var(--accent-primary); font-weight: 600; }

.user-panel {
  background: var(--surface-card);
  border: 1px solid var(--surface-glass-border);
  border-radius: 12px;
  padding: 20px;
}
.user-panel h2 { margin: 0 0 14px; font-size: 18px; color: var(--text-on-card); }
.user-panel h2 em { font-style: normal; font-size: 13px; font-weight: 400; color: var(--text-muted); margin-left: 8px; }
.user-panel :deep(.el-pagination) { margin-top: 14px; justify-content: flex-end; }

@media (max-width: 768px) {
  .admin-page { padding: 18px 16px 60px; padding-right: 64px; }
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
  .search-box { width: 160px; }
  .user-panel { overflow-x: auto; }
}
</style>

<template>
  <div class="users-page">
    <header class="page-head">
      <h1>用户管理</h1>
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

    <section class="user-panel">
      <h2>用户列表 <em>共 {{ userTotal }} 人</em></h2>
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
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getAdminUsers, updateUserRole } from '../api/admin'
import type { AdminUserItem } from '../api/admin'
import { unwrap } from '../api/util'

const users = ref<AdminUserItem[]>([])
const usersLoading = ref(false)
const userTotal = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')

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
    const res = (await updateUserRole(row.id, next)) as { code?: number; msg?: string }
    if (res?.code !== 200) {
      ElMessage.warning(res?.msg || '操作失败')
      return
    }
    row.role = next
    ElMessage.success(next === 'admin' ? '已设为管理员' : '已取消管理员')
  } catch (e) {
    ElMessage.error((e as Error).message || '操作失败')
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}
.page-head h1 { font-size: 24px; color: var(--c-text); margin: 0; }
.search-box { width: 260px; }

.user-panel {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: 20px;
}
.user-panel h2 { margin: 0 0 14px; font-size: 18px; color: var(--c-text); }
.user-panel h2 em { font-style: normal; font-size: 13px; font-weight: 400; color: var(--c-text-3); margin-left: 8px; }
.user-panel :deep(.el-pagination) { margin-top: 14px; justify-content: flex-end; }

@media (max-width: 768px) {
  .search-box { width: 160px; }
  .user-panel { overflow-x: auto; }
}
</style>

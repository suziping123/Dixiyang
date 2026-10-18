<template>
  <div class="users-page">
    <header class="page-head">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-sub">账号角色调整 · 搜索用户名 / 昵称</p>
      </div>
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

    <div class="section-rule">
      <strong>用户列表</strong>
      <span class="sr-line"></span>
      <i class="sr-count">共 {{ userTotal }} 人</i>
    </div>

    <section class="c-card table-card rise-in">
      <el-table :data="users" v-loading="usersLoading" size="large">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column label="注册时间" min-width="150">
          <template #default="{ row }">{{ (row.createTime || '').slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="large" effect="plain">
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
      <div class="pager-row">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="userTotal"
          layout="prev, pager, next"
          background
          @current-change="loadUsers"
        />
      </div>
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

defineOptions({ name: 'AdminUsers' })

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
.search-box { width: 260px; }
@media (max-width: 768px) {
  .search-box { width: 100%; }
}
</style>

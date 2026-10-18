<template>
  <div class="login-wrap">
    <section class="login-card rise-in">
      <header class="lg-brand">
        <img class="lg-logo" :src="logo" alt="DIXIYANG">
        <h1>管理控制台</h1>
        <p class="lg-sub">DIXIYANG CONSOLE · 独立入口</p>
      </header>

      <!-- 仅演示构建（GitHub Pages）显示 -->
      <p v-if="IS_DEMO" class="demo-notice">
        演示站点 · 任意用户名与密码（至少 6 位）即可进入 · 数据均为演示
      </p>

      <form class="login-form" @submit.prevent="onSubmit">
        <label class="field">
          <span class="field-label">管理员账号</span>
          <el-input v-model="username" placeholder="用户名" :prefix-icon="User" autocomplete="username" />
        </label>
        <label class="field">
          <span class="field-label">密码</span>
          <el-input
            v-model="password"
            type="password"
            placeholder="密码"
            show-password
            :prefix-icon="Lock"
            autocomplete="current-password"
          />
        </label>
        <el-button class="submit" type="primary" size="large" :loading="loading" native-type="submit">
          登录控制台
        </el-button>
      </form>

      <footer class="lg-foot">
        <a href="./index.html">← 返回用户端</a>
      </footer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import logo from '@/assets/logoByGpt.png'
import { adminLogin } from '../api/admin'
import type { AdminSession } from '../api/admin'
import { unwrap } from '../api/util'
import { setAdminSession } from '../utils/session'
import { IS_DEMO } from '@/utils/demo'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

const onSubmit = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const data = unwrap<AdminSession>(await adminLogin(username.value, password.value))
    if (!data) return
    setAdminSession(data.token, data.user.username, data.user.nickname)
    ElMessage.success('登录成功')
    router.replace('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 背景层叠约定：登录页根容器 relative + z-index，内容才画在 #theme-bg 之上 */
.login-wrap {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.login-card {
  width: min(92vw, 400px);
  padding: 32px 28px 24px;
  border-radius: var(--radius-md);
  background: var(--glass-bg-strong);
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
  border: 1px solid var(--surface-glass-border);
  box-shadow: var(--shadow-card);
}
.lg-brand { text-align: center; margin-bottom: 18px; }
.lg-logo { width: 46px; height: 46px; border-radius: 12px; margin: 0 auto 10px; }
.lg-brand h1 { margin: 0; font-size: 1.375rem; letter-spacing: 2px; color: var(--text-primary); }
.lg-sub { margin: 6px 0 0; font-size: 0.75rem; letter-spacing: 2px; color: var(--text-muted); }

/* 演示说明条（仅 IS_DEMO 渲染，与用户端登录页同语言） */
.demo-notice {
  margin: 0 0 14px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  line-height: 1.5;
  text-align: center;
  color: #f5e9c9;
  background: rgba(18, 20, 28, 0.62);
  border: 1px solid rgba(245, 233, 201, 0.28);
}

.login-form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.8125rem; color: var(--text-secondary); }
.submit { width: 100%; margin-top: 6px; }

.lg-foot { margin-top: 18px; text-align: center; font-size: 0.8125rem; }
.lg-foot a { color: var(--text-muted); }
.lg-foot a:hover { color: var(--accent-cyan); }
</style>

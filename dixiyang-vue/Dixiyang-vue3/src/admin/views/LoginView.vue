<template>
  <div class="console-login">
    <section class="login-card">
      <header class="brand">
        <span class="brand-mark">D</span>
        <h1>管理控制台</h1>
        <p class="brand-sub">DIXIYANG CONSOLE · 独立入口</p>
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

      <footer class="login-foot">
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
.console-login {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
}
/* 背景：暗底 + 双色径向光（与用户端同族但更克制） */
.console-login::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(480px 320px at 18% 12%, rgba(40, 196, 212, 0.14), transparent 70%),
    radial-gradient(520px 360px at 84% 88%, rgba(168, 85, 247, 0.16), transparent 72%);
  pointer-events: none;
}
.login-card {
  position: relative;
  width: min(92vw, 420px);
  padding: 34px 30px 26px;
  border-radius: var(--radius-md);
  background: rgba(18, 20, 28, 0.78);
  border: 1px solid var(--c-border);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(10px);
}
.brand { text-align: center; margin-bottom: 18px; }
.brand-mark {
  display: inline-flex;
  width: 46px;
  height: 46px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-weight: 800;
  font-size: 24px;
  color: #0d0d0f;
  background: linear-gradient(135deg, var(--c-cyan), var(--c-accent));
  margin-bottom: 10px;
}
.brand h1 { margin: 0; font-size: 22px; letter-spacing: 2px; }
.brand-sub { margin: 6px 0 0; font-size: 12px; letter-spacing: 2px; color: var(--c-text-3); }

.demo-notice {
  margin: 0 0 14px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  line-height: 1.5;
  text-align: center;
  color: #f5e9c9;
  background: rgba(245, 233, 201, 0.08);
  border: 1px solid rgba(245, 233, 201, 0.25);
}

.login-form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; color: var(--c-text-2); }
.submit { width: 100%; margin-top: 6px; }

.login-foot { margin-top: 18px; text-align: center; font-size: 13px; }
.login-foot a { color: var(--c-text-3); text-decoration: none; }
.login-foot a:hover { color: var(--c-cyan); }
</style>

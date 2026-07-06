<template>
  <div class="auth-container">
    <video class="background-video" autoplay loop playsinline muted>
      <source src="/videos/卡比.mp4" type="video/mp4">
    </video>

    <header class="system-title">
      <h1 class="loginHead">DIXIYANG ENGINE</h1>
      <p class="loginFooter">沉浸式内容创作 · 智能分发引擎</p>
    </header>

    <main class="auth-box" :class="{ 'right-panel-active': isSignUp }">
      <!-- 注册面板 -->
      <section class="form-container sign-up-container">
        <el-form :model="registerForm" :rules="rules" label-position="top">
          <h2 class="text-2xl font-bold mb-6">创建账号</h2>
          <el-form-item prop="nickname" required>
            <el-input v-model="registerForm.nickname" placeholder="昵称" :prefix-icon="UserFilled" />
          </el-form-item>
          <el-form-item prop="username" required>
            <el-input v-model="registerForm.username" placeholder="姓名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="email" required>
            <div class="email-with-code">
              <el-input v-model="registerForm.email" placeholder="邮箱" :prefix-icon="Message" />
              <el-button
                class="send-code-btn"
                :disabled="codeCooldown > 0"
                @click="sendCode(registerForm.email, 'REGISTER')"
              >
                {{ codeCooldown > 0 ? `${codeCooldown}s` : '发送验证码' }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item prop="code" required>
            <el-input v-model="registerForm.code" placeholder="请输入验证码" :prefix-icon="Key">
            </el-input>
          </el-form-item>
          <el-form-item prop="password" required>
            <el-input v-model="registerForm.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-button type="primary" class="auth-btn" @click="handleRegister">注册</el-button>
        </el-form>
      </section>

      <!-- 登录面板 -->
      <section class="form-container sign-in-container">
        <el-form :model="loginForm" :rules="rules" label-position="top" @keyup.enter="handleLogin">
          <h2 class="text-2xl font-bold mb-6">欢迎回来</h2>

          <!-- 密码登录 -->
          <template v-if="loginMode === 'password'">
            <el-form-item prop="username" required>
              <el-input v-model="loginForm.username" placeholder="用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password" required>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
            </el-form-item>
          </template>

          <!-- 验证码登录 -->
          <template v-else>
            <el-form-item prop="email" required>
              <el-input v-model="loginForm.email" placeholder="邮箱" :prefix-icon="Message" />
            </el-form-item>
            <el-form-item prop="code" required>
              <div class="email-with-code">
                <el-input v-model="loginForm.code" placeholder="验证码" :prefix-icon="Key">
                </el-input>
                <el-button
                  class="send-code-btn"
                  :disabled="codeCooldown > 0"
                  @click="sendCode(loginForm.email, 'LOGIN')"
                >
                  {{ codeCooldown > 0 ? `${codeCooldown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>
          </template>

          <div class="login-mode-switch">
            <a href="#" @click.prevent="toggleLoginMode">
              {{ loginMode === 'password' ? '验证码登录' : '密码登录' }}
            </a>
          </div>
          <el-button type="primary" class="auth-btn" @click="handleLogin">登录</el-button>
        </el-form>
      </section>

      <section class="overlay-container">
        <div class="overlay">
          <div class="overlay-panel overlay-left">
            <h2 class="text-white text-2xl font-bold">已有账号？</h2>
            <p class="text-white my-4">请使用您的个人信息进行登录</p>
            <el-button plain class="ghost" @click="togglePanel(false)">去登录</el-button>
          </div>
          <div class="overlay-panel overlay-right">
            <h2 class="text-white text-2xl font-bold">你好，朋友！</h2>
            <p class="text-white my-4">输入您的详细资料，开始您的文学之旅</p>
            <el-button plain class="ghost" @click="togglePanel(true)">去注册</el-button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Lock, Message, User, UserFilled, Key } from '@element-plus/icons-vue'
import { gsap } from 'gsap'
import { onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'

const {
  rules, isSignUp, loginMode, loginForm, registerForm,
  togglePanel, toggleLoginMode, handleLogin, handleRegister,
  sendCode, codeCooldown
} = useAuth()

onMounted(() => {
  gsap.from(".system-title", { y: -100, opacity: 0, duration: 1.2, ease: "elastic.out(1, 0.5)" })
  gsap.from(".auth-box", { scale: 0.8, opacity: 0, duration: 1, delay: 0.5, ease: "power2.out" })
})
</script>

<style scoped>
.auth-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  overflow: hidden;
  background: #000;
}

.background-video {
  position: absolute;
  top: 50%; left: 50%;
  min-width: 100%; min-height: 100%;
  transform: translate(-50%, -50%);
  object-fit: cover;
  z-index: 0;
  filter: brightness(0.6);
}

.system-title {
  position: absolute;
  top: 5%;
  z-index: 10;
  text-align: center;
}

.loginHead {
  font-size: 3rem;
  font-weight: 900;
  background: linear-gradient(to bottom, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.5));
}

.loginFooter { color: #ccc; letter-spacing: 2px; }

.auth-box {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.5);
  width: 800px;
  height: 500px;
  overflow: hidden;
}

.form-container {
  position: absolute;
  top: 0; height: 100%;
  width: 50%;
  transition: all 0.6s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  background: white;
}

.sign-in-container { left: 0; z-index: 2; }
.sign-up-container { left: 0; opacity: 0; z-index: 1; }

.auth-box.right-panel-active .sign-in-container { transform: translateX(100%); opacity: 0; }
.auth-box.right-panel-active .sign-up-container { transform: translateX(100%); opacity: 1; z-index: 5; animation: show 0.6s; }

.overlay-container {
  position: absolute;
  top: 0; left: 50%;
  width: 50%; height: 100%;
  overflow: hidden;
  transition: transform 0.6s ease-in-out;
  z-index: 100;
}

.auth-box.right-panel-active .overlay-container { transform: translateX(-100%); }

.overlay {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  height: 100%; width: 200%;
  position: relative; left: -100%;
  transform: translateX(0);
  transition: transform 0.6s ease-in-out;
}

.auth-box.right-panel-active .overlay { transform: translateX(50%); }

.overlay-panel {
  position: absolute;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  top: 0; height: 100%; width: 50%;
  text-align: center;
  padding: 0 40px;
  transition: transform 0.6s ease-in-out;
}

.overlay-right { right: 0; }
.overlay-left { transform: translateX(-20%); }
.auth-box.right-panel-active .overlay-left { transform: translateX(0); }

.auth-btn {
  margin-top: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  border-radius: 25px;
  padding: 12px 40px;
  color: var(--text-primary);
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
}

.auth-btn:hover { transform: scale(1.05); }

.ghost {
  background: transparent;
  border: 2px solid #fff;
  border-radius: 25px;
  color: #fff;
}

@keyframes show {
  0%, 49.99% { opacity: 0; z-index: 1; }
  50%, 100% { opacity: 1; z-index: 5; }
}

/* 验证码相关样式 */
.email-with-code {
  display: flex;
  gap: 8px;
  width: 100%;
}
.email-with-code .el-input {
  flex: 1;
}
.send-code-btn {
  flex-shrink: 0;
  height: 32px;
  font-size: 13px;
  border-radius: 6px;
}

.login-mode-switch {
  text-align: right;
  margin-bottom: 8px;
}
.login-mode-switch a {
  color: #6366f1;
  text-decoration: none;
  font-size: 13px;
}
.login-mode-switch a:hover {
  text-decoration: underline;
}
</style>

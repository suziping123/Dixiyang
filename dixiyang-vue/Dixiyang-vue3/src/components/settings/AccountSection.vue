<template>
  <SettingsSection
    title="账户"
    description="昵称与邮箱会立即保存；修改密码需先通过当前密码验证。"
  >
    <!-- 基本信息 -->
    <form class="info-form" @submit.prevent @keyup.enter="enterSubmit(saveAccountInfo, $event)">
      <SettingRow label="昵称" desc="其他创作者在协作与分享中看到的名字" stacked>
        <input
          v-model="accountForm.nickname"
          type="text"
          placeholder="输入昵称"
          autocomplete="nickname"
          @blur="saveAccountInfo"
        />
      </SettingRow>
      <SettingRow label="邮箱" desc="用于账号找回与重要通知，不对外公开" stacked>
        <input
          v-model="accountForm.email"
          type="email"
          placeholder="输入邮箱地址"
          autocomplete="email"
          @blur="saveAccountInfo"
        />
      </SettingRow>
    </form>

    <div class="row-divider"></div>

    <!-- 修改密码 -->
    <form class="pwd-form" @submit.prevent @keyup.enter="enterSubmit(changePassword, $event)">
      <h3 class="sub-title"><Lock /> 修改密码</h3>
      <SettingRow label="当前密码" stacked>
        <input
          v-model="pwd.oldPassword"
          type="password"
          placeholder="输入当前密码"
          autocomplete="current-password"
        />
      </SettingRow>
      <SettingRow label="新密码" desc="至少 6 位" stacked>
        <input
          v-model="pwd.newPassword"
          type="password"
          placeholder="输入新密码"
          autocomplete="new-password"
        />
      </SettingRow>
      <SettingRow label="确认新密码" stacked>
        <input
          v-model="pwd.confirm"
          type="password"
          placeholder="再次输入新密码"
          autocomplete="new-password"
        />
      </SettingRow>
      <div class="pwd-actions">
        <button class="btn btn-primary" type="submit" :disabled="pwdLoading">
          <Loading v-if="pwdLoading" class="spin" />
          {{ pwdLoading ? '保存中…' : '保存新密码' }}
        </button>
      </div>
    </form>

    <div class="row-divider"></div>

    <!-- 会话 -->
    <SettingRow label="登录会话" desc="登出后需重新登录，本地草稿与外观设置不受影响" stacked>
      <button class="btn btn-danger" type="button" @click="handleLogout">
        <SwitchButton /> 登出当前设备
      </button>
    </SettingRow>
  </SettingsSection>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Lock, SwitchButton } from '@element-plus/icons-vue'
import SettingsSection from '@/components/SettingsSection.vue'
import SettingRow from '@/components/settings/SettingRow.vue'
import { useUser } from '@/composables/useUser'
import { useUserStore } from '@/stores/UserStore'
import http from '@/utils/http'
import { confirmDelete } from '@/utils/confirm'
import { enterSubmit } from '@/utils/enterSubmit'

const router = useRouter()
const userStore = useUserStore()
const { accountForm, saveAccountInfo } = useUser()

// 修改密码表单
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const pwdLoading = ref(false)

/**
 * 修改密码：三步校验通过后调 POST /user/password（后端校验旧密码）
 */
const changePassword = async () => {
  if (!pwd.oldPassword || !pwd.newPassword || !pwd.confirm) {
    ElMessage.warning('请完整填写三项密码')
    return
  }
  if (pwd.newPassword.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (pwd.newPassword !== pwd.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  pwdLoading.value = true
  try {
    await http.post('/user/password', {
      oldPassword: pwd.oldPassword,
      newPassword: pwd.newPassword,
    })
    ElMessage.success('密码已修改，下次登录请使用新密码')
    pwd.oldPassword = ''
    pwd.newPassword = ''
    pwd.confirm = ''
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '修改失败，请稍后再试')
  } finally {
    pwdLoading.value = false
  }
}

const handleLogout = async () => {
  const ok = await confirmDelete('确认要登出当前会话吗？')
  if (!ok) return
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.info-form,
.pwd-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sub-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.sub-title svg {
  width: 16px;
  height: 16px;
}

.row-divider {
  height: 1px;
  background: var(--border-color);
}

.pwd-actions {
  display: flex;
  justify-content: flex-end;
}

.spin {
  animation: settings-spin 1s linear infinite;
}

@keyframes settings-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

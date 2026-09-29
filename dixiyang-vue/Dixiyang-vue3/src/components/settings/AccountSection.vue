<template>
  <SettingsSection
    title="账户"
    description="昵称失焦即保存；更换邮箱需通过新邮箱验证码确认；修改密码需先通过当前密码验证。"
  >
    <!-- 基本信息 -->
    <form class="info-form" @submit.prevent @keyup.enter="enterSubmit(saveAccountInfo, $event)">
      <SettingRow label="昵称" desc="其他创作者在协作与分享中看到的名字" stacked>
        <input
          v-model="accountForm.nickname"
          type="text"
          placeholder="输入昵称"
          autocomplete="nickname"
          @blur="onNicknameBlur"
        />
        <FieldError :message="accountErrors.nickname" />
      </SettingRow>

      <!-- 邮箱：不再 blur 即改，改为「更换邮箱」+ 新邮箱验证码流程 -->
      <SettingRow label="邮箱" desc="用于账号找回与重要通知；更换需在新邮箱收验证码确认" stacked>
        <div class="email-current">
          <input :value="accountForm.email" type="email" readonly tabindex="-1" aria-label="当前邮箱" />
          <button class="btn btn-ghost" type="button" @click="toggleEmailEdit">
            {{ emailEditing ? '收起' : '更换邮箱' }}
          </button>
        </div>

        <div v-if="emailEditing" class="email-change">
          <input
            v-model="emailForm.newEmail"
            type="email"
            placeholder="输入新邮箱"
            autocomplete="off"
            @blur="validateEmailField('newEmail')"
          />
          <div class="email-code-row">
            <input
              v-model="emailForm.code"
              type="text"
              placeholder="6 位验证码"
              maxlength="6"
              autocomplete="one-time-code"
              @blur="validateEmailField('code')"
            />
            <button
              class="btn btn-ghost"
              type="button"
              :disabled="emailCodeCooldown > 0"
              @click="sendChangeEmailCode"
            >
              {{ emailCodeCooldown > 0 ? `${emailCodeCooldown}s 后重发` : '发送验证码' }}
            </button>
          </div>
          <FieldError :message="emailErrors.newEmail" />
          <FieldError :message="emailErrors.code" />
          <div class="email-actions">
            <button class="btn btn-primary" type="button" @click="confirmChangeEmail">确认更换</button>
          </div>
        </div>
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
          @blur="validatePwd('oldPassword')"
        />
        <FieldError :message="pwdErrors.oldPassword" />
      </SettingRow>
      <SettingRow label="新密码" desc="至少 6 位" stacked>
        <input
          v-model="pwd.newPassword"
          type="password"
          placeholder="输入新密码"
          autocomplete="new-password"
          @blur="onNewPwdBlur"
        />
        <FieldError :message="pwdErrors.newPassword" />
      </SettingRow>
      <SettingRow label="确认新密码" stacked>
        <input
          v-model="pwd.confirm"
          type="password"
          placeholder="再次输入新密码"
          autocomplete="new-password"
          @blur="validatePwd('confirm')"
        />
        <FieldError :message="pwdErrors.confirm" />
      </SettingRow>
      <div class="pwd-actions">
        <button class="btn btn-primary" type="submit" :disabled="pwdLoading">
          <Loading v-if="pwdLoading" class="spin" />
          {{ pwdLoading ? '保存中…' : '保存信息' }}
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
import FieldError from '@/components/ui/FieldError.vue'
import { useUser } from '@/composables/useUser'
import { useFormValidation } from '@/composables/useFormValidation'
import { useUserStore } from '@/stores/UserStore'
import http, { assertApiResponse } from '@/utils/http'
import { friendlyError } from '@/utils/errorText'
import { confirmDelete } from '@/utils/confirm'
import { enterSubmit } from '@/utils/enterSubmit'

const router = useRouter()
const userStore = useUserStore()
const {
  accountForm,
  saveAccountInfo,
  accountErrors,
  validateAccountField,
  validateAccountAll,
  emailForm,
  emailErrors,
  emailCodeCooldown,
  validateEmailField,
  sendChangeEmailCode,
  changeEmail,
  cancelChangeEmail,
} = useUser()

// 邮箱更换面板（默认收起）
const emailEditing = ref(false)

const toggleEmailEdit = () => {
  emailEditing.value = !emailEditing.value
  if (!emailEditing.value) cancelChangeEmail()
}

/** 确认更换：字段 + 验证码校验通过并提交成功后收起 */
const confirmChangeEmail = async () => {
  const ok = await changeEmail()
  if (ok) emailEditing.value = false
}

// 修改密码表单
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const pwdLoading = ref(false)

// 密码三项实时校验（confirm 走跨字段 validator）
const pwdV = useFormValidation(
  {
    oldPassword: [{ required: true, message: '请输入当前密码' }],
    newPassword: [
      { required: true, message: '请输入新密码' },
      { min: 6, message: '新密码至少 6 位' },
    ],
    confirm: [
      { required: true, message: '请再次输入新密码' },
      {
        validator: (value, form) =>
          value === form.newPassword ? null : '两次输入的新密码不一致',
      },
    ],
  },
  pwd as unknown as Record<string, string>,
)
const { errors: pwdErrors, validateField: validatePwd, validateAll: validatePwdAll, clearAll: clearPwdErrors } = pwdV

/** 新密码 blur 后，已显示的「确认」错误需要联动复查 */
const onNewPwdBlur = () => {
  validatePwd('newPassword')
  if (pwd.confirm) validatePwd('confirm')
}

/** 昵称 blur：先校验，通过才触发保存（邮箱不走此路径，需验证码） */
const onNicknameBlur = () => {
  validateAccountField('nickname')
  if (validateAccountAll(['nickname'])) saveAccountInfo()
}

/**
 * 修改密码：字段级校验通过后调 POST /user/password（后端校验旧密码）
 */
const changePassword = async () => {
  if (!validatePwdAll()) return

  pwdLoading.value = true
  try {
    const res = await http.post('/user/password', {
      oldPassword: pwd.oldPassword,
      newPassword: pwd.newPassword,
    })
    // 拦截器对 code:500 也 resolve，必须自行判断业务码
    const apiRes = assertApiResponse(res)
    if (apiRes.code !== 200) {
      ElMessage.error(friendlyError(apiRes.msg, '修改失败，请稍后再试'))
      return
    }
    ElMessage.success('密码已修改，下次登录请使用新密码')
    pwd.oldPassword = ''
    pwd.newPassword = ''
    pwd.confirm = ''
    clearPwdErrors()
  } catch (e) {
    ElMessage.error(e instanceof Error ? friendlyError(e.message, '修改失败，请稍后再试') : '修改失败，请稍后再试')
  } finally {
    pwdLoading.value = false
  }
}

const handleLogout = async () => {
  const ok = await confirmDelete('确认要登出当前会话吗？', '警告')
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

/* ---- 更换邮箱 ---- */
/* 当前邮箱一行：只读展示 + 右侧按钮（覆盖 SettingRow 的 .btn 100%/320px 约束） */
.email-current {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.email-current input {
  flex: 1;
  min-width: 0;
  color: var(--text-secondary);
}

.email-current .btn {
  width: auto !important;
  max-width: none !important;
  flex-shrink: 0;
  padding: 9px 14px;
}

.email-change {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding-top: 4px;
}

.email-code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.email-code-row input {
  flex: 1;
  min-width: 0;
}

.email-code-row .btn {
  width: auto !important;
  max-width: none !important;
  flex-shrink: 0;
  padding: 9px 14px;
  white-space: nowrap;
}

.email-code-row .btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.email-actions {
  display: flex;
  justify-content: center;
}

.email-actions .btn {
  width: 100%;
  max-width: 320px;
}

.pwd-actions {
  display: flex;
  justify-content: center;
}

.pwd-actions .btn {
  width: 100%;
  max-width: 320px;
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

/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-20 10:29:35
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-20 20:30:50
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\composables\useUser.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
/* src/views/auth/useUser.ts */
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import http, { assertApiResponse } from '@/utils/http'
import { useUserStore } from '@/stores/UserStore'
import { useFormValidation } from '@/composables/useFormValidation'
import { friendlyError } from '@/utils/errorText'

const EMAIL_RE = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

export function useUser() {
  const userStore = useUserStore()

  // 1. 初始化表单（先给默认值，避免undefined）
  const accountForm = reactive({
    nickname: userStore.nickname || '',
    email: userStore.email || ''
  })

  // 脏值检测快照：记录「已保存」的值，与表单一致则 blur 不发请求、不弹提示
  const snapshot = {
    nickname: accountForm.nickname,
    email: accountForm.email,
  }

  // 字段级实时校验：错误由 FieldError 内联显示，不再弹 toast
  const accountV = useFormValidation(
    {
      nickname: [{ required: true, message: '请输入昵称' }],
      email: [{ pattern: EMAIL_RE, message: '邮箱格式不正确' }],
    },
    accountForm as unknown as Record<string, string>,
  )

  // ---- 更换邮箱：独立表单（后端要求 purpose=CHG_EMAIL 验证码）----
  const emailForm = reactive({ newEmail: '', code: '' })
  const emailV = useFormValidation(
    {
      newEmail: [
        { required: true, message: '请输入新邮箱' },
        { pattern: EMAIL_RE, message: '邮箱格式不正确' },
      ],
      code: [{ required: true, message: '请输入验证码' }],
    },
    emailForm as unknown as Record<string, string>,
  )

  // 发码 60s 倒计时（与 useAuth 同款）
  const emailCodeCooldown = ref(0)
  let emailCooldownTimer: ReturnType<typeof setInterval> | null = null

  const startEmailCooldown = () => {
    emailCodeCooldown.value = 60
    if (emailCooldownTimer) clearInterval(emailCooldownTimer)
    emailCooldownTimer = setInterval(() => {
      emailCodeCooldown.value--
      if (emailCodeCooldown.value <= 0) {
        clearInterval(emailCooldownTimer!)
        emailCooldownTimer = null
      }
    }, 1000)
  }

  onBeforeUnmount(() => {
    if (emailCooldownTimer) clearInterval(emailCooldownTimer)
  })

  /** 给新邮箱发送更换验证码（purpose=CHG_EMAIL，后端 60s 限流 / 5 分钟有效） */
  const sendChangeEmailCode = async (): Promise<boolean> => {
    if (!emailV.validateField('newEmail')) return false
    if (emailForm.newEmail === snapshot.email) {
      ElMessage.info('与当前邮箱相同，无需更换')
      return false
    }
    try {
      const res = await http.post('/auth/send-code', {
        email: emailForm.newEmail,
        purpose: 'CHG_EMAIL',
      })
      const apiRes = assertApiResponse(res)
      if (apiRes.code === 200) {
        ElMessage.success('验证码已发送')
        startEmailCooldown()
        return true
      }
      ElMessage.error(friendlyError(apiRes.msg, '验证码发送失败'))
      return false
    } catch (e) {
      ElMessage.error('网络请求异常')
      console.error('发送更换邮箱验证码失败：', e)
      return false
    }
  }

  /** 提交新邮箱 + 验证码；成功返回 true（由调用方收起面板） */
  const changeEmail = async (): Promise<boolean> => {
    if (!emailV.validateAll()) return false
    try {
      const res = await http.post('/user/update', {
        email: emailForm.newEmail,
        code: emailForm.code,
      })
      const apiRes = assertApiResponse(res)
      if (apiRes.code === 200) {
        accountForm.email = emailForm.newEmail
        snapshot.email = emailForm.newEmail
        userStore.setEmail(emailForm.newEmail)
        emailForm.newEmail = ''
        emailForm.code = ''
        emailV.clearAll()
        ElMessage.success('邮箱已更换')
        return true
      }
      // 验证码错误/过期、邮箱被占用 → 后端原文经 friendlyError 映射，原值只进 console
      ElMessage.error(friendlyError(apiRes.msg, '邮箱更换失败，请稍后再试'))
      return false
    } catch (e) {
      ElMessage.error('系统繁忙，请稍后再试')
      console.error('更换邮箱失败：', e)
      return false
    }
  }

  /** 取消更换：清空草稿与错误 */
  const cancelChangeEmail = () => {
    emailForm.newEmail = ''
    emailForm.code = ''
    emailV.clearAll()
  }

  // 2. 页面加载时，从后端获取最新用户信息（关键！同步数据库最新数据）
  const fetchUserInfo = async () => {
    try {
      const res = await http.get('/user/info') // 需后端新增这个接口
      const apiRes = assertApiResponse<{ nickname: string; email: string }>(res)
      if (apiRes.code === 200) {
        // 更新Pinia和表单的最新数据
        userStore.setNickname(apiRes.data.nickname)
        userStore.setEmail(apiRes.data.email)
        accountForm.nickname = apiRes.data.nickname
        accountForm.email = apiRes.data.email
        // 后端值即「已保存」基准
        snapshot.nickname = apiRes.data.nickname
        snapshot.email = apiRes.data.email
      }
    } catch (e) {
      console.error('获取用户信息失败：', e)
    }
  }

  // 3. 昵称保存：校验通过 + 值确实变了才请求（避免点一下输入框就弹「更新成功」）
  //    注意：只提交 nickname —— 邮箱必须走 changeEmail（带验证码），不能混提
  const saveAccountInfo = async () => {
    if (!accountV.validateAll(['nickname'])) return

    // 脏值检测：与快照一致 → 未修改，静默返回（不发接口、不弹提示）
    if (accountForm.nickname === snapshot.nickname) return

    try {
      const res = await http.post('/user/update', { nickname: accountForm.nickname })

      // 关键修复：直接用res.code，不是res.data.code（拦截器已处理）
      const apiRes = assertApiResponse<Record<string, unknown>>(res)
      if (apiRes.code === 200) {
        // 同步更新Pinia状态
        userStore.setNickname(accountForm.nickname)
        // 成功才更新快照（失败下次失焦自动重试）
        snapshot.nickname = accountForm.nickname
        ElMessage.success('更新成功')
      } else {
        ElMessage.error(friendlyError(apiRes.msg, '保存失败，请稍后再试'))
      }
    } catch (e) {
      ElMessage.error('系统繁忙，请稍后再试')
      console.error('更新失败：', e)
    }
  }

  // 4. 页面挂载时获取最新用户信息
  onMounted(() => {
    fetchUserInfo()
  })

  return {
    accountForm,
    saveAccountInfo,
    fetchUserInfo,
    accountErrors: accountV.errors,
    validateAccountField: accountV.validateField,
    validateAccountAll: accountV.validateAll,
    // 更换邮箱
    emailForm,
    emailErrors: emailV.errors,
    emailCodeCooldown,
    validateEmailField: emailV.validateField,
    sendChangeEmailCode,
    changeEmail,
    cancelChangeEmail,
  }
}

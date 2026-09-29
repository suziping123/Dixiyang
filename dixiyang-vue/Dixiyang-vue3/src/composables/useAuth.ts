import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http, { assertApiResponse } from '@/utils/http'
import { useUserStore } from '@/stores/UserStore'
import { loadFromServer } from '@/composables/useBackgroundConfig'
import { useFormValidation } from '@/composables/useFormValidation'
import { friendlyError } from '@/utils/errorText'
import type { LoginResponse, RegisterResponse } from '@/api/types'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function useAuth() {
  const router = useRouter()
  const userStore = useUserStore()
  const isSignUp = ref(false)
  const loginMode = ref<'password' | 'code'>('password') // 登录方式切换

  const loginForm = reactive({ username: '', password: '', email: '', code: '' })
  const registerForm = reactive({ nickname: '', username: '', email: '', password: '', code: '' })

  // 字段级实时校验（错误经 FieldError 内联显示，不再弹 toast）
  const loginV = useFormValidation(
    {
      username: [{ required: true, message: '请输入用户名' }],
      password: [{ required: true, message: '请输入密码' }, { min: 6, message: '密码至少 6 位' }],
      email: [
        { required: true, message: '请输入邮箱' },
        { pattern: EMAIL_RE, message: '邮箱格式不正确' },
      ],
      code: [{ required: true, message: '请输入验证码' }],
    },
    loginForm as unknown as Record<string, string>,
  )

  const registerV = useFormValidation(
    {
      nickname: [{ required: true, message: '请输入昵称' }],
      username: [{ required: true, message: '请输入姓名' }],
      email: [
        { required: true, message: '请输入邮箱' },
        { pattern: EMAIL_RE, message: '邮箱格式不正确' },
      ],
      password: [
        { required: true, message: '请输入密码' },
        { min: 6, message: '密码长度至少为 6 位' },
      ],
      code: [{ required: true, message: '请输入验证码' }],
    },
    registerForm as unknown as Record<string, string>,
  )

  // 验证码倒计时
  const codeCooldown = ref(0)
  let cooldownTimer: ReturnType<typeof setInterval> | null = null

  const togglePanel = (status: boolean) => {
    isSignUp.value = status
    // 切面板清掉对面板的残留错误
    registerV.clearAll()
    loginV.clearAll()
  }

  const toggleLoginMode = () => {
    loginMode.value = loginMode.value === 'password' ? 'code' : 'password'
    loginV.clearAll()
  }

  // 发送验证码（邮箱格式校验已在 validateField 完成）
  const sendCode = async (email: string, purpose: 'LOGIN' | 'REGISTER') => {
    try {
      const res = await http.post('/auth/send-code', { email, purpose })
      const apiRes = assertApiResponse(res)
      if (apiRes.code === 200) {
        ElMessage.success('验证码已发送')
        startCooldown()
        return true
      }
      ElMessage.error(friendlyError(apiRes.msg, '验证码发送失败'))
      return false
    } catch {
      ElMessage.error('网络请求异常')
      return false
    }
  }

  /** 发送登录验证码：先做字段校验，再请求 */
  const sendLoginCode = async () => {
    if (!loginV.validateField('email')) return false
    return sendCode(loginForm.email, 'LOGIN')
  }

  /** 发送注册验证码：先做字段校验，再请求 */
  const sendRegisterCode = async () => {
    if (!registerV.validateField('email')) return false
    return sendCode(registerForm.email, 'REGISTER')
  }

  // 开始倒计时
  const startCooldown = () => {
    codeCooldown.value = 60
    if (cooldownTimer) clearInterval(cooldownTimer)
    cooldownTimer = setInterval(() => {
      codeCooldown.value--
      if (codeCooldown.value <= 0) {
        clearInterval(cooldownTimer!)
        cooldownTimer = null
      }
    }, 1000)
  }

  // 登录：按当前模式只校验对应字段
  const loginKeys = () =>
    loginMode.value === 'password' ? ['username', 'password'] : ['email', 'code']

  // 验证码登录
  const handleLoginByCode = async () => {
    if (!loginV.validateAll(['email', 'code'])) return
    try {
      const res = await http.post('/auth/login-by-code', {
        email: loginForm.email,
        code: loginForm.code,
      })
      const apiRes = assertApiResponse<{ token: string; user: LoginResponse }>(res)
      if (apiRes.code === 200) {
        const { token, user } = apiRes.data
        if (!user) {
          ElMessage.error('用户信息缺失')
          return
        }
        userStore.setLoginInfo(token, user.username, String(user.userId), user.nickname!, user.email || '')
        loadFromServer()
        ElMessage.success(`欢迎回来, ${user.nickname}`)
        router.push('/home')
      } else {
        ElMessage.error(friendlyError(apiRes.msg, '登录失败'))
      }
    } catch {
      ElMessage.error('网络请求异常')
    }
  }

  // 密码登录
  const handleLogin = async () => {
    if (loginMode.value === 'code') {
      return handleLoginByCode()
    }
    if (!loginV.validateAll(loginKeys())) return
    try {
      const res = await http.post('/auth/login', {
        username: loginForm.username,
        password: loginForm.password,
      })
      const apiRes = assertApiResponse<{ token: string; user: LoginResponse }>(res)
      if (apiRes.code === 200) {
        const { token, user } = apiRes.data
        if (!user) {
          ElMessage.error('用户信息缺失')
          return
        }
        userStore.setLoginInfo(token, user.username, String(user.userId), user.nickname!, user.email || '')
        loadFromServer()
        ElMessage.success(`欢迎回来, ${user.nickname}`)
        router.push('/home')
      } else {
        ElMessage.error(friendlyError(apiRes.msg, '登录失败'))
      }
    } catch {
      ElMessage.error('网络请求异常')
    }
  }

  // 注册（带验证码）
  const handleRegister = async () => {
    if (!registerV.validateAll()) return
    try {
      const res = await http.post('/auth/register', { ...registerForm })
      const apiRes = assertApiResponse<RegisterResponse>(res)
      if (apiRes.code === 200) {
        ElMessage.success('注册成功，请登录')
        togglePanel(false)
        Object.assign(registerForm, { nickname: '', username: '', email: '', password: '', code: '' })
      } else {
        ElMessage.error(friendlyError(apiRes.msg, '注册失败'))
      }
    } catch {
      ElMessage.error('网络请求异常')
    }
  }

  return {
    isSignUp, loginMode, loginForm, registerForm,
    togglePanel, toggleLoginMode, handleLogin, handleRegister,
    sendLoginCode, sendRegisterCode, codeCooldown,
    loginErrors: loginV.errors,
    registerErrors: registerV.errors,
    validateLoginField: loginV.validateField,
    validateRegisterField: registerV.validateField,
    clearLoginErrors: loginV.clearAll,
    clearRegisterErrors: registerV.clearAll,
  }
}

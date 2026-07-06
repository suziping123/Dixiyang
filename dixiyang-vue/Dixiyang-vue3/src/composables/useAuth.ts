import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http, { assertApiResponse } from '@/utils/http'
import { useUserStore } from '@/stores/UserStore'
import { loadFromServer } from '@/composables/useBackgroundConfig'
import type { LoginResponse, RegisterResponse } from '@/api/types'

export function useAuth() {
  const router = useRouter()
  const userStore = useUserStore()
  const isSignUp = ref(false)
  const loginMode = ref<'password' | 'code'>('password') // 登录方式切换

  const loginForm = reactive({ username: '', password: '', email: '', code: '' })
  const registerForm = reactive({ nickname: '', username: '', email: '', password: '', code: '' })

  // 验证码倒计时
  const codeCooldown = ref(0)
  let cooldownTimer: ReturnType<typeof setInterval> | null = null

  const togglePanel = (status: boolean) => { isSignUp.value = status }

  const toggleLoginMode = () => {
    loginMode.value = loginMode.value === 'password' ? 'code' : 'password'
  }

  // 发送验证码
  const sendCode = async (email: string, purpose: 'LOGIN' | 'REGISTER') => {
    if (!email) {
      ElMessage.warning('请输入邮箱')
      return false
    }
    const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailReg.test(email)) {
      ElMessage.warning('邮箱格式不正确')
      return false
    }
    try {
      const res = await http.post('/auth/send-code', { email, purpose })
      const apiRes = assertApiResponse(res)
      if (apiRes.code === 200) {
        ElMessage.success('验证码已发送')
        startCooldown()
        return true
      } else {
        ElMessage.error(apiRes.msg || '发送失败')
        return false
      }
    } catch {
      ElMessage.error('网络请求异常')
      return false
    }
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

  // 验证码登录
  const handleLoginByCode = async () => {
    if (!loginForm.email || !loginForm.code) {
      return ElMessage.warning('请填写邮箱和验证码')
    }
    try {
      const res = await http.post('/auth/login-by-code', {
        email: loginForm.email,
        code: loginForm.code
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
        ElMessage.error(apiRes.msg || '登录失败')
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
    if (!loginForm.username || !loginForm.password) {
      return ElMessage.warning('请填写完整登录信息')
    }
    try {
      const res = await http.post('/auth/login', {
        username: loginForm.username,
        password: loginForm.password
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
        ElMessage.error(apiRes.msg || '登录失败')
      }
    } catch {
      ElMessage.error('网络请求异常')
    }
  }

  // 注册（带验证码）
  const handleRegister = async () => {
    const { nickname, username, email, password, code } = registerForm
    if (!nickname || !username || !email || !password) {
      return ElMessage.warning('所有字段均为必填项')
    }
    const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailReg.test(email)) {
      return ElMessage.warning('请输入有效的邮箱地址')
    }
    if (password.length < 6) {
      return ElMessage.warning('密码长度至少为 6 位')
    }
    if (!code) {
      return ElMessage.warning('请先获取并填写验证码')
    }

    try {
      const res = await http.post('/auth/register', { ...registerForm })
      const apiRes = assertApiResponse<RegisterResponse>(res)
      if (apiRes.code === 200) {
        ElMessage.success('注册成功，请登录')
        togglePanel(false)
        Object.assign(registerForm, { nickname: '', username: '', email: '', password: '', code: '' })
      } else {
        ElMessage.error(apiRes.msg || '注册失败')
      }
    } catch {
      ElMessage.error('网络请求异常')
    }
  }

  const rules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码不能少于6位', trigger: 'blur' }
    ]
  }

  return {
    rules, isSignUp, loginMode, loginForm, registerForm,
    togglePanel, toggleLoginMode, handleLogin, handleRegister,
    sendCode, codeCooldown
  }
}

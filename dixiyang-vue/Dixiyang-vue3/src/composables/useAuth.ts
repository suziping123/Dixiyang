/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-18 16:19:09
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-19 11:15:02
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\views\auth\useAuth.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '@/utils/http'
import { useUserStore } from '@/stores/UserStore'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import type { LoginResponse, RegisterResponse } from '@/api/types'

export function useAuth() {
  const router = useRouter()
  const userStore = useUserStore()
  const bgConfig = useBackgroundConfig()
  const isSignUp = ref(false)

  const loginForm = reactive({ username: '', password: '' })
  const registerForm = reactive({ nickname: '', username: '', email: '', password: '' })

  const togglePanel = (status: boolean) => { isSignUp.value = status }

  const handleLogin = async () => {
    if (!loginForm.username || !loginForm.password) {
      return ElMessage.warning('请填写完整登录信息')
    }
    try {
      const res = await http.post<string , LoginResponse>('/auth/login', loginForm)
      console.log('后端返回的原始数据:', res) // 加上这一行！
      if (res.code === 200) {
        console.log('data内容:', res.data) // 看看里面有没有 token 和 user
        const { token, user } = res.data
        // 修复：增加用户信息存在性校验，并使用非空断言满足 TS 类型要求
        if (!user) {
          ElMessage.error('用户信息缺失')
          return
        }
        userStore.setLoginInfo(token, user.username, user.id, user.nickname!, user.email)
        ElMessage.success(`欢迎回来, ${user.nickname}`)

        // 🆕 登录成功后，自动从后端加载用户的背景配置
        await bgConfig.loadFromBackend()

        router.push('/home')
      } else {

        ElMessage.error(res.msg || '登录失败')
      }
    } catch (e) {
      ElMessage.error('网络请求异常')
    }
  }

  // useAuth.ts 内部修改 handleRegister

const handleRegister = async () => {
  // 1. 基础非空校验
  const { nickname, username, email, password } = registerForm
  if (!nickname || !username || !email || !password) {
    return ElMessage.warning('所有字段均为必填项')
  }

  // 2. 邮箱格式校验 (正则)
  const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailReg.test(email)) {
    return ElMessage.warning('请输入有效的邮箱地址')
  }

  // 3. 密码长度校验
  if (password.length < 6) {
    return ElMessage.warning('密码长度至少为 6 位')
  }

  // 4. 校验通过，发送请求
  try {
    const res = await http.post<string, RegisterResponse>('/auth/register', registerForm)
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      togglePanel(false) // 自动切换回登录面板
      // 清空注册表单内容
      Object.assign(registerForm, { nickname: '', username: '', email: '', password: '' })
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (e) {
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

  return { rules, isSignUp, loginForm, registerForm, togglePanel, handleLogin, handleRegister }
}

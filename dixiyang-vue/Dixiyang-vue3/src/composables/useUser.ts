/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-20 10:29:35
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-20 20:30:50
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\composables\useUser.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
/* src/views/auth/useUser.ts */
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/utils/http'
import { useUserStore } from '@/stores/UserStore'

export function useUser() {
  const userStore = useUserStore()

  // 1. 初始化表单（先给默认值，避免undefined）
  const accountForm = reactive({
    nickname: userStore.nickname || '',
    email: userStore.email || ''
  })

  // 2. 页面加载时，从后端获取最新用户信息（关键！同步数据库最新数据）
  const fetchUserInfo = async () => {
    try {
      const res = await http.get('/user/info') // 需后端新增这个接口
      if (res.code === 200) {
        // 更新Pinia和表单的最新数据
        userStore.setNickname(res.data.nickname)
        userStore.setEmail(res.data.email)
        accountForm.nickname = res.data.nickname
        accountForm.email = res.data.email
      }
    } catch (e) {
      console.error('获取用户信息失败：', e)
    }
  }

  // 新增：简单的规则校验函数
  const validateForm = () => {
    // 校验昵称
    if (!accountForm.nickname.trim()) {
      ElMessage.warning('请输入昵称')
      return false
    }
    // 校验邮箱格式
    const emailReg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (accountForm.email && !emailReg.test(accountForm.email)) {
      ElMessage.warning('邮箱格式不正确')
      return false
    }
    return true
  }
  // 3. 修复保存逻辑（解析响应+同步状态）
  const saveAccountInfo = async () => {
    if (!validateForm()) return

    try {
      // 调用更新接口
      const res = await http.post('/user/update', accountForm)

      // 关键修复：直接用res.code，不是res.data.code（拦截器已处理）
      if (res.code === 200) {
        // 同步更新Pinia状态
        userStore.setNickname(accountForm.nickname)
        userStore.setEmail(accountForm.email)
        ElMessage.success('更新成功')

        // 可选：强制刷新表单显示（保险）
        accountForm.nickname = accountForm.nickname
        accountForm.email = accountForm.email
      } else {
        ElMessage.error(res.msg || '更新失败')
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

  // ✅ 修复：只保留表单用到的规则，字段名和表单一一对应
  const rules = {
    nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
    ]
  }

  return { rules, accountForm, saveAccountInfo, fetchUserInfo }
}

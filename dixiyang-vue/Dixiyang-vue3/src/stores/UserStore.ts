/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-18 15:55:26
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-20 10:20:44
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\stores\UserStore.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const nickname = ref(localStorage.getItem('nickname') || '')
  const email = ref(localStorage.getItem('email') || '')

  const setLoginInfo = (newToken: string, newUsername: string, newId: string, newNickname: string, newEmail: string) => {
    token.value = newToken
    username.value = newUsername
    userId.value = newId
    nickname.value = newNickname
    email.value = newEmail

    localStorage.setItem('token', newToken)
    localStorage.setItem('username', newUsername)
    localStorage.setItem('userId', newId)
    localStorage.setItem('nickname', newNickname)
    localStorage.setItem('email', newEmail)
  }

  const setNickname = (newNickname: string) => {
    nickname.value = newNickname
    localStorage.setItem('nickname', newNickname)

  }

  const setEmail = (newEmail: string) => {
    email.value = newEmail
    localStorage.setItem('email', newEmail)
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    userId.value = ''
    nickname.value = ''
    email.value = ''
    localStorage.clear()
  }

  return { token, username, userId, nickname, email, setLoginInfo, setNickname, setEmail, logout }
})

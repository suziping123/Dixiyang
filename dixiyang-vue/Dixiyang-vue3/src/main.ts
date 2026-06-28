import './assets/main.css'
import './assets/icon-utils.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { initTheme } from '@/composables/useBackgroundConfig'

// 修复旧版 localStorage 中 "undefined" 字符串导致的 userId 问题
const uid = localStorage.getItem('userId')
if (uid && (uid === 'undefined' || uid === 'null' || isNaN(Number(uid)))) {
  localStorage.removeItem('userId')
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('nickname')
  localStorage.removeItem('email')
}

initTheme()

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')

import './assets/main.css'
import './assets/icon-utils.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { initTheme } from '@/composables/useBackgroundConfig'
import { isTokenValid, clearAuth } from '@/utils/auth'

// 清理脏 token（"undefined"/"null" 字符串）及过期 token
const storedToken = localStorage.getItem('token')
const uid = localStorage.getItem('userId')
if (uid && (uid === 'undefined' || uid === 'null' || isNaN(Number(uid)))) {
  clearAuth()
} else if (storedToken && !isTokenValid(storedToken)) {
  clearAuth()
}

initTheme()

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')

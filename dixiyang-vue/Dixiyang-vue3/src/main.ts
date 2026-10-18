import './assets/main.css'
import './assets/icon-utils.css'
// 落地页样式：tokens → 基座 → 章节（须在 main.css 之后，保持未分层顺序）
import './styles/landing/tokens.css'
import './styles/landing/landing-base.css'
import './styles/landing/landing-sections.css'

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

// 演示构建（GitHub Pages）：挂载前先装 mock 适配器——
// 否则"带旧 token 直达页面"时，首个数据请求会赶在动态 import 前发出，泄漏到真实网络
async function bootstrap() {
  if (import.meta.env.VITE_DEMO === '1') {
    try {
      const [{ installDemoAdapter }, { default: http }] = await Promise.all([
        import('./utils/demo/adapter'),
        import('./utils/http'),
      ])
      installDemoAdapter(http)
    } catch {
      // 适配器加载失败：静默降级，页面照常渲染
    }
  }
  app.mount('#app')
}

bootstrap()

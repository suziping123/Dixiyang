// 管理控制台入口（admin.html）：与用户端（src/main.ts）分开的壳
// 设计系统对齐：复用用户端设计系统（token/玻璃/弹窗全局规则），导入顺序与用户端一致
import '../assets/main.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './styles/console.css'

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'
import { initConsoleBackground } from './utils/theme'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)

// 背景层：读同源 localStorage 缓存（用户端选过的背景）→ #theme-bg（与用户端同一机制）
void initConsoleBackground()

// 演示构建（GitHub Pages）：挂载前先装 mock 适配器——
// 否则"带旧 token 直达控制台"时，Dashboard 首个请求会赶在动态 import 前发出，泄漏到真实网络
async function bootstrap() {
  if (import.meta.env.VITE_DEMO === '1') {
    try {
      const [{ installDemoAdapter }, { default: http }] = await Promise.all([
        import('@/utils/demo/adapter'),
        import('./api/http'),
      ])
      installDemoAdapter(http)
    } catch {
      // 适配器加载失败：静默降级，页面照常渲染
    }
  }
  app.mount('#app')
}

bootstrap()

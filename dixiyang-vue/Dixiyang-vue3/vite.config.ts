import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// 临时禁用 vueDevTools 解决 ERR_ABORTED 问题
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8084',
        changeOrigin: true
      }
    },
    hmr: {
      overlay: false // 禁用 HMR 错误覆盖层
    }
  },
  plugins: [
    vue(),
    // vueDevTools(), // 注释掉，解决 ERR_ABORTED 问题
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

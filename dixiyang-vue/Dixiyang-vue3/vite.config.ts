import { fileURLToPath, URL } from 'node:url'
import { execFile } from 'node:child_process'
import { existsSync } from 'node:fs'

import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
// 临时禁用 vueDevTools 解决 ERR_ABORTED 问题
// import vueDevTools from 'vite-plugin-vue-devtools'

// dev 启动时自动建立 adb reverse 隧道（手机 localhost 直达本机端口，免手动/免防火墙）
const ADB_CANDIDATES = [
  'D:\\Users\\Lenovo\\Desktop\\platform-tools-latest-windows\\platform-tools\\adb.exe',
  `${process.env.LOCALAPPDATA}\\Android\\Sdk\\platform-tools\\adb.exe`,
  'D:\\Vivo\\pcsuite\\adb\\adb.exe'
]

function autoAdbReverse(): Plugin {
  return {
    name: 'auto-adb-reverse',
    configureServer() {
      const adb = ADB_CANDIDATES.find((p) => existsSync(p))
      if (!adb) return
      for (const port of [5173, 8084]) {
        execFile(adb, ['reverse', `tcp:${port}`, `tcp:${port}`], { timeout: 5000 }, (err) => {
          if (err) return // 手机未连/adb 异常：静默跳过，不阻塞启动
          console.log(`  ➜  adb reverse tcp:${port} ✓`)
        })
      }
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  server: {
    // 监听所有网卡（含网线/USB 共享网络），局域网设备用本机 IP 访问
    host: true,
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
    autoAdbReverse(),
    // vueDevTools(), // 注释掉，解决 ERR_ABORTED 问题
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

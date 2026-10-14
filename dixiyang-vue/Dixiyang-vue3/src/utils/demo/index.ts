// 演示模式（GitHub Pages 静态站专用）—— 仅当构建时注入 VITE_DEMO=1 才激活
// 真实开发（dev）与生产构建不读 .env.gh-pages，IS_DEMO 恒 false，行为零影响
// 本文件保持轻量（不含 mock 数据），mock 数据经动态 import 隔离在 ./adapter
export const IS_DEMO = import.meta.env.VITE_DEMO === '1'

/** 生成一个本地可校验通过的演示 JWT（exp 设 10 年后，isTokenValid 只解 payload 查 exp） */
export function makeDemoToken(): string {
  const payload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + 10 * 365 * 86400, sub: 'demo' }))
  return `demo.${payload}.demo`
}

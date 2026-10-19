import type { Component } from 'vue'

/**
 * FloatingNav 注册项（2026-10-18 复用改造）：
 * - 用户端 App.vue 不传 items → 默认 5 主页（行为不变）
 * - 管理控制台（admin.html）传自己的页面表（见 admin/menu.ts ADMIN_NAV_ITEMS）
 */
export interface FloatingNavItem {
  icon: Component
  label: string
  /** SPA 路由：组件内 router.push */
  path?: string
  /** 整页跳转（跨入口/外链，如「返回用户端」./index.html） */
  href?: string
  /** 危险样式（如「退出登录」） */
  danger?: boolean
  /** 无 path/href 条目的标识：点击经 select 事件交由父级处理 */
  key?: string
}

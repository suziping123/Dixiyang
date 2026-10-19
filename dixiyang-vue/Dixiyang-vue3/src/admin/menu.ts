// 控制台页面注册表：侧栏菜单、多页签与窄屏悬浮导航共用同一份定义
import type { Component } from 'vue'
import { Collection, DataBoard, HomeFilled, Notebook, SwitchButton, User } from '@element-plus/icons-vue'
import type { FloatingNavItem } from '@/components/FloatingNav.types'

export interface ConsolePage {
  path: string // 路由路径（hash 路由）
  name: string // 路由名
  title: string // 菜单/页签标题
  icon: Component
  keepName: string // 组件名（keep-alive include 用；与视图 defineOptions 一致）
}

export const CONSOLE_PAGES: ConsolePage[] = [
  { path: '/', name: 'admin-dashboard', title: '仪表盘', icon: DataBoard, keepName: 'AdminDashboard' },
  { path: '/users', name: 'admin-users', title: '用户管理', icon: User, keepName: 'AdminUsers' },
  { path: '/posts', name: 'admin-posts', title: '广场管理', icon: Collection, keepName: 'AdminPosts' },
  { path: '/sticky', name: 'admin-sticky', title: '灵感墙管理', icon: Notebook, keepName: 'AdminSticky' },
]

/** 固定首签（不可关闭） */
export const FIXED_TAB = 'admin-dashboard'

export const pageByRouteName = (name: unknown) => CONSOLE_PAGES.find((p) => p.name === name)

export const pageByName = (name: string) => CONSOLE_PAGES.find((p) => p.name === name)

/**
 * 窄屏 / 触屏悬浮导航注册项（复用用户端 FloatingNav 组件）：
 * 4 个控制台页面 + 返回用户端（跨入口整页跳转）+ 退出登录（无 path，经 select 交 LayoutView 处理）
 */
export const ADMIN_NAV_ITEMS: FloatingNavItem[] = [
  ...CONSOLE_PAGES.map((p) => ({ icon: p.icon, label: p.title, path: p.path })),
  { icon: HomeFilled, label: '返回用户端', href: './index.html' },
  { icon: SwitchButton, label: '退出登录', danger: true, key: 'logout' },
]

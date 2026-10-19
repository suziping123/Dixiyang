// 控制台页面注册表：侧栏菜单、多页签与窄屏悬浮导航共用（图标 = 控制台语义图标，与用户端导航图标明确区分）
import type { Component } from 'vue'
import { ChatDotSquare, DataBoard, HomeFilled, SwitchButton } from '@element-plus/icons-vue'
import type { FloatingNavItem } from '@/components/FloatingNav.types'
import { BooksNavIcon, UsersNavIcon } from './icons'

export interface ConsolePage {
  path: string // 路由路径（hash 路由）
  name: string // 路由名
  title: string // 菜单/页签标题
  icon: Component
  keepName: string // 组件名（keep-alive include 用；与视图 defineOptions 一致）
}

export const CONSOLE_PAGES: ConsolePage[] = [
  { path: '/', name: 'admin-dashboard', title: '仪表盘', icon: DataBoard, keepName: 'AdminDashboard' },
  { path: '/users', name: 'admin-users', title: '用户管理', icon: UsersNavIcon, keepName: 'AdminUsers' },
  { path: '/posts', name: 'admin-posts', title: '广场管理', icon: ChatDotSquare, keepName: 'AdminPosts' },
  { path: '/sticky', name: 'admin-sticky', title: '灵感墙管理', icon: BooksNavIcon, keepName: 'AdminSticky' },
]

/** 固定首签（不可关闭） */
export const FIXED_TAB = 'admin-dashboard'

export const pageByRouteName = (name: unknown) => CONSOLE_PAGES.find((p) => p.name === name)

export const pageByName = (name: string) => CONSOLE_PAGES.find((p) => p.name === name)

/**
 * 窄屏 / 触屏悬浮导航注册项（复用用户端 FloatingNav 组件，**独立注册**）：
 * - 不派生自 CONSOLE_PAGES：条目顺序与图标按移动端语义单独挑选（管理对象一律"复数"图标：
 *   多个人 / 多本书），路径需与路由保持一致（改路由时同步此处）
 * - 4 个控制台页面 + 返回用户端（跨入口整页跳转）+ 退出登录（无 path，经 select 交 LayoutView 处理）
 */
export const ADMIN_NAV_ITEMS: FloatingNavItem[] = [
  { icon: DataBoard, label: '仪表盘', path: '/' },
  { icon: UsersNavIcon, label: '用户管理', path: '/users' },
  { icon: ChatDotSquare, label: '广场管理', path: '/posts' },
  { icon: BooksNavIcon, label: '灵感墙管理', path: '/sticky' },
  { icon: HomeFilled, label: '返回用户端', href: './index.html' },
  { icon: SwitchButton, label: '退出登录', danger: true, key: 'logout' },
]

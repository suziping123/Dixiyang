/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-18 13:44:43
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-19 23:22:19
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\router\index.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from "../views/LoginView.vue"
import HomeView from '../views/HomeView.vue'
import LandingView from '../views/LandingView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import SettingsView from '../views/SettingsView.vue'
import NovelEditorView from '../views/NovelEditorView.vue'
import CharacterManagerView from '../views/CharacterManagerView.vue'
import RagAssistantView from '../views/RagAssistantView.vue'
import RagKnowledgeView from '../views/RagKnowledgeView.vue'
import { isTokenValid, clearAuth } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
      meta: { title: 'DIXIYANG · AI 小说创作平台 — 让 AI 记得你写过的一切', public: true } // 对外介绍页，免登录
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true, title: '我的创作宇宙 · DIXIYANG' } // 需要认证
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { hideNav: true } // 标记：隐藏导航
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true } // 需要认证
    },

    {
      path: '/novel-editor/:id',
      name: 'novel-editor',
      component: NovelEditorView,
      meta: { requiresAuth: true }
    },
    {
      path: '/novel/:novelId/characters',
      name: 'character-manager',
      component: CharacterManagerView,
      meta: { requiresAuth: true }
    },
    {
      path: '/rag-assistant',
      name: 'rag-assistant',
      component: RagAssistantView,
      meta: { requiresAuth: true }
    },
    {
      path: '/rag-knowledge',
      name: 'rag-knowledge',
      component: RagKnowledgeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/novel/:novelId/timeline',
      name: 'timeline',
      component: () => import('../views/TimelineView.vue'),
      meta: { requiresAuth: true }
    },
    {
      // 设计过的 404：未匹配路由统一落此
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: { hideNav: true, title: '页面未找到 · DIXIYANG', public: true }
    },
  ],
})

// 免登录白名单：对外介绍页与 404（meta.public）
// 路由守卫：每次切换页面前都会执行
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  // 校验 token 存在且未过期（本地解 JWT exp），无效则清理
  const valid = isTokenValid(token)
  if (!valid && token) clearAuth()

  // 标题跟随路由
  if (to.meta.title) document.title = String(to.meta.title)

  if (to.path === '/login') {
    if (valid) return next('/home')
    return next()
  }

  // 免登录白名单（落地页 / 与 404）直接放行
  if (to.meta.public) {
    return next()
  }

  // 未登录或 token 无效/过期 → 跳登录页（拦截器行为保持不变）
  if (!valid) {
    return next('/login')
  }

  next()
})

export default router

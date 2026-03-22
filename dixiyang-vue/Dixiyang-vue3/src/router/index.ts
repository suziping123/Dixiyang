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
import SettingsView from '../views/SettingsView.vue'
import NovelEditorView from '../views/NovelEditorView.vue'
import { useUserStore } from '../stores/UserStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
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
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true } // 只有标记了这个的才需要检查
    },
    {
      path: '/novel-editor/:id',
      name: 'novel-editor',
      component: NovelEditorView,
      meta: { requiresAuth: true }
    },
  ],
})

// 路由守卫：每次切换页面前都会执行
router.beforeEach((to, from, next) => {
  // 直接从本地存储拿，最稳妥
  const token = localStorage.getItem('token')

  if (to.path === '/login') {
    if (token) return next('/home')
    return next()
  }

  // 如果没有 token，且不是去登录页
  if (!token) {
    return next('/login')
  }

  next()
})

export default router

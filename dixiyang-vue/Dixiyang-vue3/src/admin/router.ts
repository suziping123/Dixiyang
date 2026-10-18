// 控制台路由：hash 模式——GitHub Pages 无服务端 rewrite，hash 深链零配置可用（admin.html#/users）
import { createRouter, createWebHashHistory } from 'vue-router'
import { clearAdminSession, getAdminToken, hasValidAdminToken } from './utils/session'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'admin-login',
      component: () => import('./views/LoginView.vue'),
      meta: { public: true, title: '后台登录 · DIXIYANG 控制台' },
    },
    {
      path: '/',
      component: () => import('./views/LayoutView.vue'),
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('./views/DashboardView.vue'),
          meta: { title: '仪表盘 · DIXIYANG 控制台' },
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('./views/UsersView.vue'),
          meta: { title: '用户管理 · DIXIYANG 控制台' },
        },
        {
          path: 'posts',
          name: 'admin-posts',
          component: () => import('./views/PostsManageView.vue'),
          meta: { title: '广场管理 · DIXIYANG 控制台' },
        },
        {
          path: 'sticky',
          name: 'admin-sticky',
          component: () => import('./views/StickyManageView.vue'),
          meta: { title: '灵感墙管理 · DIXIYANG 控制台' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  if (to.meta.title) document.title = String(to.meta.title)
  const valid = hasValidAdminToken()
  // 脏 token 清理（过期/伪造直接清掉，避免反复判定）
  if (!valid && getAdminToken()) clearAdminSession()
  if (!valid && !to.meta.public) return { name: 'admin-login' }
  if (valid && to.name === 'admin-login') return { path: '/' }
  return true
})

export default router

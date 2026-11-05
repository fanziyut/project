import { createRouter, createWebHistory } from 'vue-router'

import { fetchMe } from './auth'
import DashboardView from './views/DashboardView.vue'
import JobsView from './views/JobsView.vue'
import LoginView from './views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/jobs', name: 'jobs', component: JobsView },
  ],
})

// 未登录访问业务页面时跳转到登录页，登录后回到原页面
router.beforeEach(async (to) => {
  if (to.meta.public) return true
  const user = await fetchMe()
  if (!user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router

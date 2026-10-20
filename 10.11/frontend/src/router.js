import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from './views/DashboardView.vue'
import JobsView from './views/JobsView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/jobs', name: 'jobs', component: JobsView },
  ],
})

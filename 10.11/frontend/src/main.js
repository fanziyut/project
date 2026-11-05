import { createApp } from 'vue'

import App from './App.vue'
import { auth } from './auth'
import router from './router'
import './style.css'

createApp(App).use(router).mount('#app')

// 任意接口返回 401（会话过期）时，清除登录态并回到登录页
window.addEventListener('auth:unauthorized', () => {
  if (!auth.user && auth.checked && router.currentRoute.value.name === 'login') return
  auth.user = null
  auth.checked = true
  router.replace({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
})

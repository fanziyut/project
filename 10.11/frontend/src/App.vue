<template>
  <div class="header">
    <div class="header-inner">
      <div>
        <h1>招聘数据分析可视化平台</h1>
        <p class="subtitle">数据源：就业信息网 · 前后端分离 (Vue3 + Flask + SQLite)</p>
      </div>

      <div class="header-actions">
        <nav v-if="auth.user" class="nav">
          <RouterLink to="/dashboard">数据仪表盘</RouterLink>
          <RouterLink to="/jobs">岗位明细</RouterLink>
        </nav>

        <div v-if="auth.user" class="user-box">
          <span class="user-name">{{ auth.user.displayName }}</span>
          <button class="logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>
  </div>

  <router-view />

  <div class="footer">招聘数据分析可视化平台 | 数据来源于就业信息网公开信息</div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { auth, logout } from './auth'

const router = useRouter()

async function handleLogout() {
  await logout()
  router.replace({ name: 'login' })
}
</script>

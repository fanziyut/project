<template>
  <div class="header">
    <div class="header-inner">
      <div>
        <h1>招聘数据分析可视化平台</h1>
        <p class="subtitle">数据源：就业信息网 · 前后端分离 (Vue3 + Flask + SQLite)</p>
      </div>
      <nav class="nav">
        <RouterLink to="/dashboard">数据仪表盘</RouterLink>
        <RouterLink to="/jobs">岗位明细</RouterLink>
      </nav>
    </div>
  </div>

  <router-view />

  <div class="footer">招聘数据分析可视化平台 | 数据来源于就业信息网公开信息</div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

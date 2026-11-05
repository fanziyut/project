<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <span class="login-logo">📊</span>
        <h2>招聘数据分析可视化平台</h2>
        <p>请登录后查看数据</p>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <label class="login-field">
          <span>用户名</span>
          <input v-model.trim="form.username" autocomplete="username" placeholder="请输入用户名" />
        </label>
        <label class="login-field">
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            placeholder="请输入密码"
          />
        </label>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button class="btn login-btn" type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>

        <p class="login-hint">默认账号：admin / admin123</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { login } from '../auth'

const router = useRouter()
const route = useRoute()

const form = reactive({ username: 'admin', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await login(form.username, form.password)
    router.replace(route.query.redirect || '/dashboard')
  } catch (e) {
    error.value = e.response?.data?.message || '登录失败，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}
</script>

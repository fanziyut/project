import { reactive } from 'vue'

import { getMe, loginApi, logoutApi } from './api'

export const auth = reactive({ user: null, checked: false })

/** 获取当前登录用户，结果缓存，避免每次跳转都请求接口。 */
export async function fetchMe(force = false) {
  if (auth.checked && !force) return auth.user
  try {
    auth.user = await getMe()
  } catch {
    auth.user = null
  } finally {
    auth.checked = true
  }
  return auth.user
}

export async function login(username, password) {
  auth.user = await loginApi(username, password)
  auth.checked = true
  return auth.user
}

export async function logout() {
  try {
    await logoutApi()
  } finally {
    auth.user = null
    auth.checked = true
  }
}

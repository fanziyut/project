import axios from 'axios'

// 开发环境由 vite 代理转发到 Flask 后端
const http = axios.create({ baseURL: '/api', timeout: 30000, withCredentials: true })

// 会话失效（401）时通知应用跳回登录页
http.interceptors.response.use(
  (res) => res,
  (error) => {
    // /auth/me 的 401 由路由守卫处理，避免重复跳转
    const url = error.config?.url || ''
    if (error.response?.status === 401 && !url.includes('/auth/me')) {
      window.dispatchEvent(new Event('auth:unauthorized'))
    }
    return Promise.reject(error)
  },
)

export const loginApi = (username, password) =>
  http.post('/auth/login', { username, password }).then((res) => res.data.user)
export const logoutApi = () => http.post('/auth/logout')
export const getMe = () => http.get('/auth/me').then((res) => res.data.user)

export const getDashboard = () => http.get('/stats/dashboard').then((res) => res.data)
export const getJobs = (params) => http.get('/jobs', { params }).then((res) => res.data)
export const getJobDetail = (id) => http.get(`/jobs/${id}`).then((res) => res.data)
export const getFilters = () => http.get('/jobs/filters').then((res) => res.data)

import axios from 'axios'

// 开发环境由 vite 代理转发到 Flask 后端
const http = axios.create({ baseURL: '/api', timeout: 30000 })

export const getDashboard = () => http.get('/stats/dashboard').then((res) => res.data)
export const getJobs = (params) => http.get('/jobs', { params }).then((res) => res.data)
export const getJobDetail = (id) => http.get(`/jobs/${id}`).then((res) => res.data)
export const getFilters = () => http.get('/jobs/filters').then((res) => res.data)

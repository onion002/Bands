/**
 * 统计数据服务
 * 处理仪表板统计数据相关的API调用
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      window.location.href = '/auth/login'
    }

    const errorMessage = error.response?.data?.error || error.message || '请求失败'
    return Promise.reject({ error: errorMessage })
  }
)

export interface DashboardStats {
  bands: {
    count: number
    change: number
  }
  members: {
    count: number
    change: number
  }
  events: {
    count: number
    change: number
  }
  activeEvents: number
}

export interface RecentActivity {
  id: string
  icon: string
  text: string
  time: string
  timestamp: string
}

/**
 * 获取仪表板统计数据
 */
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/api/stats/dashboard')
  return response
}

/**
 * 获取最近活动记录
 */
export const getRecentActivities = async (): Promise<RecentActivity[]> => {
  const response = await api.get('/api/stats/recent-activities')
  return response
}

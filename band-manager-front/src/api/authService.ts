import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// 用户类型
export type UserType = 'admin' | 'user'

// 用户接口
export interface User {
  id: number
  username: string
  email?: string
  user_type: UserType
  display_name: string
  avatar_url?: string
  is_active: boolean
  created_at: string
}

// 注册数据接口
export interface RegisterData {
  username: string
  email: string
  password: string
  user_type: UserType
  display_name?: string
  developer_key?: string
}

// 登录数据接口
export interface LoginData {
  login: string // 用户名或邮箱
  password: string
}

// 认证响应接口
export interface AuthResponse {
  message: string
  user: User
  token: string
}

// 验证响应接口
export interface VerifyResponse {
  valid: boolean
  user?: User
  error?: string
}

// 创建axios实例
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api/auth`,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // 允许跨域请求携带凭证
})

// 请求拦截器 - 添加token
authApi.interceptors.request.use(
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
authApi.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      // 可以在这里触发登出事件或跳转到登录页
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

export const AuthService = {
  // 用户注册
  async register(data: RegisterData): Promise<AuthResponse> {
    return authApi.post('/register', data)
  },

  // 用户登录
  async login(data: LoginData): Promise<AuthResponse> {
    return authApi.post('/login', data)
  },

  // 获取用户信息
  async getProfile(): Promise<{ user: User }> {
    return authApi.get('/profile')
  },

  // 更新用户信息
  async updateProfile(data: Partial<User>): Promise<{ message: string; user: User }> {
    return authApi.put('/profile', data)
  },

  // 修改密码
  async changePassword(data: { old_password: string; new_password: string }): Promise<{ message: string }> {
    return authApi.post('/change-password', data)
  },

  // 验证token
  async verifyToken(token?: string): Promise<VerifyResponse> {
    return authApi.post('/verify-token', token ? { token } : {})
  },

  // 登出（清除本地存储）
  logout(): void {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
  },

  // 保存认证信息
  saveAuthInfo(token: string, user: User): void {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('user_info', JSON.stringify(user))
  },

  // 获取本地存储的token
  getToken(): string | null {
    return localStorage.getItem('auth_token')
  },

  // 获取本地存储的用户信息
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user_info')
    return userStr ? JSON.parse(userStr) : null
  },

  // 检查是否已登录
  isAuthenticated(): boolean {
    return !!this.getToken()
  },

  // 检查是否为管理员
  isAdmin(): boolean {
    const user = this.getStoredUser()
    return user?.user_type === 'admin'
  }
}

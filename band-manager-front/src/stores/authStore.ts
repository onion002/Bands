import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthService, type User, type LoginData, type RegisterData } from '@/api/authService'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string>('')

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.user_type === 'admin')
  const username = computed(() => user.value?.username || '')
  const displayName = computed(() => user.value?.display_name || user.value?.username || '')

  // 初始化 - 从本地存储恢复状态
  const initAuth = () => {
    const storedToken = AuthService.getToken()
    const storedUser = AuthService.getStoredUser()
    
    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = storedUser
    }
  }

  // 登录
  const login = async (loginData: LoginData) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await AuthService.login(loginData)
      
      // 保存认证信息
      token.value = response.token
      user.value = response.user
      AuthService.saveAuthInfo(response.token, response.user)
      
      return response
    } catch (err: any) {
      error.value = err.error || '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterData) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await AuthService.register(registerData)
      
      // 注册成功后自动登录
      token.value = response.token
      user.value = response.user
      AuthService.saveAuthInfo(response.token, response.user)
      
      return response
    } catch (err: any) {
      error.value = err.error || '注册失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    error.value = ''
    AuthService.logout()
  }

  // 获取用户信息
  const fetchProfile = async () => {
    try {
      loading.value = true
      const response = await AuthService.getProfile()
      user.value = response.user
      
      // 更新本地存储
      if (token.value) {
        AuthService.saveAuthInfo(token.value, response.user)
      }
      
      return response.user
    } catch (err: any) {
      error.value = err.error || '获取用户信息失败'
      // 如果获取失败，可能是token过期，执行登出
      if (err.error?.includes('token')) {
        logout()
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新用户信息
  const updateProfile = async (data: Partial<User>) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await AuthService.updateProfile(data)
      user.value = response.user
      
      // 更新本地存储
      if (token.value) {
        AuthService.saveAuthInfo(token.value, response.user)
      }
      
      return response
    } catch (err: any) {
      error.value = err.error || '更新用户信息失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await AuthService.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      })
      
      return response
    } catch (err: any) {
      error.value = err.error || '修改密码失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 上传头像
  const uploadAvatar = async (file: File) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await AuthService.uploadAvatar(file)
      user.value = response.user
      
      // 更新本地存储
      if (token.value) {
        AuthService.saveAuthInfo(token.value, response.user)
      }
      
      return response
    } catch (err: any) {
      error.value = err.error || '头像上传失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 验证token有效性
  const verifyToken = async () => {
    try {
      if (!token.value) return false
      
      const response = await AuthService.verifyToken()
      
      if (response.valid && response.user) {
        user.value = response.user
        return true
      } else {
        logout()
        return false
      }
    } catch (err) {
      logout()
      return false
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = ''
  }

  // 获取token（兼容性方法）
  const getToken = () => {
    return token.value || AuthService.getToken()
  }

  // 检查权限
  const hasPermission = (permission: 'admin' | 'user') => {
    if (!isAuthenticated.value) return false
    
    if (permission === 'admin') {
      return isAdmin.value
    }
    
    return true // 普通用户权限
  }

  return {
    // 状态
    user,
    token,
    loading,
    error,

    // 计算属性
    isAuthenticated,
    isAdmin,
    username,
    displayName,

    // 方法
    initAuth,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    uploadAvatar,
    verifyToken,
    clearError,
    hasPermission,
    getToken
  }
})

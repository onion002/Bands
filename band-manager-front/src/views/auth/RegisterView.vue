<template>
  <div class="auth-container">
    <!-- 左侧图片区域 -->
    <div class="auth-image-section">
      <div class="image-content">
        <div class="logo-section">
          <div class="logo">
            <i class="fas fa-music"></i>
          </div>
          <h1 class="brand-title">加入我们</h1>
          <p class="brand-subtitle">开始您的乐队管理之旅</p>
        </div>
        
        <div class="feature-list">
          <div class="feature-item">
            <i class="fas fa-shield-alt"></i>
            <span>安全可靠</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-rocket"></i>
            <span>快速上手</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-heart"></i>
            <span>免费使用</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧注册表单区域 -->
    <div class="auth-form-section">
      <div class="form-container">
        <div class="form-header">
          <h2>创建账户</h2>
          <p>填写信息以创建您的账户</p>
        </div>

        <form @submit.prevent="handleRegister" class="auth-form">
          <!-- 错误提示 -->
          <div v-if="error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>

          <!-- 用户类型选择 -->
          <div class="form-group">
            <label>账户类型</label>
            <div class="user-type-selector">
              <label class="type-option" :class="{ active: registerForm.user_type === 'user' }">
                <input
                  v-model="registerForm.user_type"
                  type="radio"
                  value="user"
                  :disabled="loading"
                />
                <div class="type-content">
                  <i class="fas fa-user"></i>
                  <span>普通用户</span>
                  <small>查看乐队信息</small>
                </div>
              </label>
              <label class="type-option" :class="{ active: registerForm.user_type === 'admin' }">
                <input
                  v-model="registerForm.user_type"
                  type="radio"
                  value="admin"
                  :disabled="loading"
                />
                <div class="type-content">
                  <i class="fas fa-crown"></i>
                  <span>管理员</span>
                  <small>管理乐队数据</small>
                </div>
              </label>
            </div>
          </div>

          <!-- 用户名输入 -->
          <div class="form-group">
            <label for="username">用户名</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                id="username"
                v-model="registerForm.username"
                type="text"
                placeholder="请输入用户名（3-20位字母数字下划线）"
                required
                :disabled="loading"
                @input="handleInputChange"
              />
            </div>
          </div>

          <!-- 邮箱输入 -->
          <div class="form-group">
            <label for="email">邮箱</label>
            <div class="input-wrapper">
              <i class="fas fa-envelope input-icon"></i>
              <input
                id="email"
                v-model="registerForm.email"
                type="email"
                placeholder="请输入邮箱地址"
                required
                :disabled="loading"
                @input="handleInputChange"
              />
            </div>
          </div>

          <!-- 显示名称输入 -->
          <div class="form-group">
            <label for="display_name">显示名称</label>
            <div class="input-wrapper">
              <i class="fas fa-id-card input-icon"></i>
              <input
                id="display_name"
                v-model="registerForm.display_name"
                type="text"
                placeholder="请输入显示名称（可选）"
                :disabled="loading"
                @input="handleInputChange"
              />
            </div>
          </div>

          <!-- 密码输入 -->
          <div class="form-group">
            <label for="password">密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                id="password"
                v-model="registerForm.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码（至少8位，包含字母和数字）"
                required
                :disabled="loading"
                @input="handleInputChange"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                :disabled="loading"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- 确认密码输入 -->
          <div class="form-group">
            <label for="confirm_password">确认密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                id="confirm_password"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="请再次输入密码"
                required
                :disabled="loading"
                @input="handleInputChange"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="loading"
              >
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- 开发者密钥输入（仅管理员） -->
          <div v-if="registerForm.user_type === 'admin'" class="form-group">
            <label for="developer_key">开发者密钥</label>
            <div class="input-wrapper">
              <i class="fas fa-key input-icon"></i>
              <input
                id="developer_key"
                v-model="registerForm.developer_key"
                type="password"
                placeholder="请输入开发者密钥"
                required
                :disabled="loading"
                @input="handleInputChange"
              />
            </div>
            <small class="form-hint">
              <i class="fas fa-info-circle"></i>
              管理员账户需要开发者密钥才能注册
            </small>
          </div>

          <!-- 注册按钮 -->
          <button
            type="submit"
            class="auth-button"
            :disabled="loading || !isFormValid"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-user-plus"></i>
            {{ loading ? '注册中...' : '注册账户' }}
          </button>
        </form>

        <!-- 登录链接 -->
        <div class="auth-footer">
          <p>
            已有账户？
            <router-link to="/auth/login" class="auth-link">
              立即登录
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import type { RegisterData, UserType } from '@/api/authService'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const registerForm = ref<RegisterData>({
  username: '',
  email: '',
  password: '',
  user_type: 'user' as UserType,
  display_name: '',
  developer_key: ''
})

// 界面状态
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const error = ref('')

// 表单验证
const isFormValid = computed(() => {
  const form = registerForm.value
  const basic = form.username && form.email && form.password && confirmPassword.value
  const passwordMatch = form.password === confirmPassword.value
  const adminKey = form.user_type === 'admin' ? form.developer_key : true
  
  return basic && passwordMatch && adminKey
})

// 处理注册
const handleRegister = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 验证密码匹配
    if (registerForm.value.password !== confirmPassword.value) {
      error.value = '两次输入的密码不一致'
      return
    }
    
    // 验证用户名格式
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(registerForm.value.username)) {
      error.value = '用户名只能包含字母、数字和下划线，长度3-20位'
      return
    }
    
    // 验证密码强度
    if (registerForm.value.password.length < 8) {
      error.value = '密码长度至少8位'
      return
    }
    
    if (!/[A-Za-z]/.test(registerForm.value.password) || !/\d/.test(registerForm.value.password)) {
      error.value = '密码必须包含字母和数字'
      return
    }
    
    await authStore.register(registerForm.value)
    
    // 注册成功，跳转到相应页面
    if (authStore.isAdmin) {
      router.push('/dashboard')
    } else {
      router.push('/public')
    }
  } catch (err: any) {
    error.value = err.error || '注册失败，请检查输入信息'
  } finally {
    loading.value = false
  }
}

// 清除错误信息
const clearError = () => {
  error.value = ''
  authStore.clearError()
}

// 监听输入变化，清除错误
const handleInputChange = () => {
  if (error.value) {
    clearError()
  }
}

onMounted(() => {
  // 如果已经登录，直接跳转
  if (authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      router.push('/dashboard')
    } else {
      router.push('/public')
    }
  }
})
</script>

<style scoped>
/* 继承登录页面的基础样式 */
.auth-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-image-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.auth-image-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.image-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
}

.logo-section {
  margin-bottom: 3rem;
}

.logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  backdrop-filter: blur(10px);
}

.logo i {
  font-size: 2rem;
  color: white;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  opacity: 0.9;
}

.feature-item i {
  font-size: 1.2rem;
}

.auth-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: white;
  overflow-y: auto;
}

.form-container {
  width: 100%;
  max-width: 450px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: #718096;
  font-size: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.error-message {
  background: #fed7d7;
  color: #c53030;
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

/* 用户类型选择器 */
.user-type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.type-option {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.type-option:hover {
  border-color: #667eea;
}

.type-option.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.type-option input[type="radio"] {
  display: none;
}

.type-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.type-content i {
  font-size: 1.5rem;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.type-content span {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

.type-content small {
  color: #718096;
  font-size: 0.8rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #a0aec0;
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
  background: white;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-wrapper input:disabled {
  background: #f7fafc;
  cursor: not-allowed;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #667eea;
}

.form-hint {
  color: #718096;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.auth-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.auth-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.auth-footer p {
  color: #718096;
  font-size: 0.9rem;
}

.auth-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.auth-link:hover {
  color: #764ba2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
  }
  
  .auth-image-section {
    min-height: 200px;
    flex: none;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .feature-list {
    flex-direction: row;
    justify-content: center;
    gap: 2rem;
  }
  
  .feature-item {
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.9rem;
  }
  
  .user-type-selector {
    grid-template-columns: 1fr;
  }
}
</style>

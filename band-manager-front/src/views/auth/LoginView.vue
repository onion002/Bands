<template>
  <div class="auth-container">
    <!-- 左侧图片区域 -->
    <div class="auth-image-section">
      <div class="image-content">
        <div class="logo-section">
          <div class="logo">
            <i class="fas fa-music"></i>
          </div>
          <h1 class="brand-title">乐队管理系统</h1>
          <p class="brand-subtitle">专业的乐队信息管理平台</p>
        </div>
        
        <div class="feature-list">
          <div class="feature-item">
            <i class="fas fa-users"></i>
            <span>成员管理</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-calendar-alt"></i>
            <span>活动安排</span>
          </div>
          <div class="feature-item">
            <i class="fas fa-chart-line"></i>
            <span>数据统计</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单区域 -->
    <div class="auth-form-section">
      <div class="form-container">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录您的账户以继续管理</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form">
          <!-- 错误提示 -->
          <div v-if="error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>

          <!-- 用户名/邮箱输入 -->
          <div class="form-group">
            <label for="login">用户名或邮箱</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                id="login"
                v-model="loginForm.login"
                type="text"
                placeholder="请输入用户名或邮箱"
                required
                :disabled="loading"
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
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                required
                :disabled="loading"
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

          <!-- 记住我 -->
          <div class="form-options">
            <label class="checkbox-wrapper">
              <input
                v-model="rememberMe"
                type="checkbox"
                :disabled="loading"
              />
              <span class="checkmark"></span>
              记住我
            </label>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            class="auth-button"
            :disabled="loading || !loginForm.login || !loginForm.password"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-sign-in-alt"></i>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 注册链接 -->
        <div class="auth-footer">
          <p>
            还没有账户？
            <router-link to="/auth/register" class="auth-link">
              立即注册
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import type { LoginData } from '@/api/authService'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const loginForm = ref<LoginData>({
  login: '',
  password: ''
})

// 界面状态
const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

// 处理登录
const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    
    await authStore.login(loginForm.value)
    
    // 登录成功，跳转到相应页面
    if (authStore.isAdmin) {
      router.push('/dashboard')
    } else {
      router.push('/public')
    }
  } catch (err: any) {
    error.value = err.error || '登录失败，请检查用户名和密码'
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
}

.form-container {
  width: 100%;
  max-width: 400px;
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

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #4a5568;
}

.checkbox-wrapper input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
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
}
</style>

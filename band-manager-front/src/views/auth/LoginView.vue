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

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.auth-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, $dark 0%, $darkgray 50%, $lightgray 100%);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 80%, rgba($primary, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba($secondary, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba($primary, 0.08) 0%, transparent 50%);
    animation: backgroundShift 20s ease-in-out infinite;
  }

  // 添加噪点纹理
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIiB4PSIwIiB5PSIwIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGZpbHRlcj0idXJsKCNhKSIgb3BhY2l0eT0iLjA1IiBkPSJNMCAwaDMwMHYzMDBIMHoiLz48L3N2Zz4=');
    opacity: 0.3;
    pointer-events: none;
  }

  @keyframes backgroundShift {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
}

.auth-image-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  position: relative;
  z-index: 1;

  @media (max-width: 768px) {
    display: none;
  }
}

.image-content {
  text-align: center;
  color: white;
  animation: fadeInUp 1s ease-out;

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

.logo-section {
  margin-bottom: 4rem;
}

.logo {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    background: linear-gradient(45deg, $primary, $secondary, $primary);
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba($primary, 0.4);

    &::before {
      opacity: 1;
    }
  }

  i {
    font-size: 2.5rem;
    color: white;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }
}

.brand-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, $white 0%, rgba($primary, 0.9) 50%, $white 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 20px rgba($primary, 0.3);
  line-height: 1.2;
  font-family: $font-family-display;
}

.brand-subtitle {
  font-size: 1.3rem;
  opacity: 0.9;
  margin-bottom: 0;
  font-weight: 300;
  letter-spacing: 0.5px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 1.2rem;
  opacity: 0.9;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  animation: slideInLeft 0.6s ease-out;
  animation-fill-mode: both;

  &:nth-child(1) { animation-delay: 0.2s; }
  &:nth-child(2) { animation-delay: 0.4s; }
  &:nth-child(3) { animation-delay: 0.6s; }

  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-30px);
    }
    to {
      opacity: 0.9;
      transform: translateX(0);
    }
  }

  &:hover {
    opacity: 1;
    transform: translateX(5px);
    background: rgba($primary, 0.2);
    border-color: rgba($primary, 0.4);
    box-shadow: 0 4px 15px rgba($primary, 0.2);
  }

  i {
    font-size: 1.5rem;
    color: rgba(255, 255, 255, 0.9);
  }
}

.auth-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: rgba($darkgray, 0.95);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
  border-left: 1px solid rgba($primary, 0.1);

  @media (max-width: 768px) {
    padding: 2rem 1rem;
    border-left: none;
    border-top: 1px solid rgba($primary, 0.1);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba($darkgray, 0.8) 0%, rgba($lightgray, 0.6) 100%);
    z-index: -1;
  }
}

.form-container {
  width: 100%;
  max-width: 450px;
  animation: slideInRight 1s ease-out;

  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(30px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
}

.form-header {
  text-align: center;
  margin-bottom: 3rem;

  h2 {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, $white 0%, rgba($primary, 0.9) 50%, $white 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    line-height: 1.2;
    font-family: $font-family-display;
  }

  p {
    color: $gray-300;
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
  }
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.error-message {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
  color: #dc2626;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
  animation: shake 0.5s ease-in-out;

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  i {
    font-size: 1.1rem;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  label {
    font-weight: 600;
    color: $white;
    font-size: 0.95rem;
    margin-left: 0.25rem;
    transition: color 0.3s ease;
  }
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;

  .input-icon {
    position: absolute;
    left: 1.25rem;
    color: $gray-400;
    z-index: 2;
    font-size: 1.1rem;
    transition: all 0.3s ease;
  }

  input {
    width: 100%;
    padding: 1.25rem 1.25rem 1.25rem 3.25rem;
    border: 2px solid rgba($white, 0.1);
    border-radius: 16px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: rgba($lightgray, 0.8);
    backdrop-filter: blur(10px);
    font-weight: 500;
    color: $white;

    &::placeholder {
      color: $gray-400;
      font-weight: 400;
    }

    &:focus {
      outline: none;
      border-color: $primary;
      background: rgba($lightgray, 0.95);
      box-shadow:
        0 0 0 4px rgba($primary, 0.1),
        0 8px 25px rgba($primary, 0.15);
      transform: translateY(-2px);

      ~ .input-icon {
        color: $primary;
        transform: scale(1.1);
      }
    }

    &:hover:not(:focus) {
      border-color: rgba($white, 0.2);
      background: rgba($lightgray, 0.9);
    }

    &:disabled {
      background: rgba($darkgray, 0.6);
      cursor: not-allowed;
      opacity: 0.6;
    }
  }
}

.password-toggle {
  position: absolute;
  right: 1.25rem;
  background: none;
  border: none;
  color: $gray-400;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  z-index: 2;

  &:hover {
    color: $primary;
    background: rgba($primary, 0.1);
    transform: scale(1.1);
  }

  i {
    font-size: 1.1rem;
  }
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin: 0.5rem 0;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: $gray-300;
  font-weight: 500;
  transition: color 0.3s ease;

  &:hover {
    color: $white;
  }

  input[type="checkbox"] {
    display: none;
  }
}

.checkmark {
  width: 22px;
  height: 22px;
  border: 2px solid rgba($white, 0.2);
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
  background: rgba($lightgray, 0.8);
  backdrop-filter: blur(10px);

  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 8px;
    background: linear-gradient(135deg, $primary, $secondary);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: -1;
  }
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark {
  background: linear-gradient(135deg, $primary, $secondary);
  border-color: transparent;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba($primary, 0.4);

  &::before {
    opacity: 1;
  }

  &::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 14px;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }
}

.auth-button {
  background: linear-gradient(135deg, $primary 0%, $secondary 100%);
  color: white;
  border: none;
  padding: 1.25rem 2rem;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  position: relative;
  overflow: hidden;
  box-shadow: $shadow-primary;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: $font-family-display;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
  }

  &:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba($primary, 0.4);
    background: linear-gradient(135deg, rgba($primary, 0.9) 0%, rgba($secondary, 0.9) 100%);

    &::before {
      left: 100%;
    }
  }

  &:active:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba($primary, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 4px 12px rgba($primary, 0.2);

    &::before {
      display: none;
    }
  }

  i {
    font-size: 1.2rem;
  }
}

.auth-footer {
  text-align: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba($white, 0.1);

  p {
    color: $gray-300;
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
  }
}

.auth-link {
  color: $primary;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.3s ease;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(135deg, $primary, $secondary);
    transition: width 0.3s ease;
  }

  &:hover {
    color: $secondary;
    transform: translateY(-1px);
    text-shadow: 0 0 10px rgba($primary, 0.5);

    &::after {
      width: 100%;
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .auth-container {
    .auth-image-section {
      padding: 2rem;
    }

    .auth-form-section {
      padding: 2rem;
    }
  }
}

@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
    min-height: 100vh;
  }

  .auth-image-section {
    min-height: 40vh;
    flex: none;
    padding: 2rem 1rem;

    .logo-section {
      margin-bottom: 2rem;
    }

    .logo {
      width: 80px;
      height: 80px;

      i {
        font-size: 2rem;
      }
    }

    .brand-title {
      font-size: 2.2rem;
    }

    .brand-subtitle {
      font-size: 1.1rem;
    }
  }

  .feature-list {
    flex-direction: row;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
  }

  .feature-item {
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.9rem;
    padding: 0.75rem 1rem;

    i {
      font-size: 1.2rem;
    }
  }

  .form-container {
    max-width: 100%;
  }

  .form-header {
    margin-bottom: 2rem;

    h2 {
      font-size: 2rem;
    }
  }

  .auth-form {
    gap: 1.5rem;
  }

  .input-wrapper input {
    padding: 1rem 1rem 1rem 2.75rem;
  }

  .auth-button {
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .auth-image-section {
    min-height: 30vh;
    padding: 1.5rem 1rem;
  }

  .brand-title {
    font-size: 1.8rem;
  }

  .feature-list {
    gap: 0.5rem;
  }

  .feature-item {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .auth-form-section {
    padding: 1.5rem 1rem;
  }

  .form-header h2 {
    font-size: 1.75rem;
  }

  .input-wrapper input {
    padding: 0.875rem 0.875rem 0.875rem 2.5rem;
    font-size: 0.95rem;
  }
}
</style>

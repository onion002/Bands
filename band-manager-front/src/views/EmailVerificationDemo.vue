<template>
  <div class="email-verification-demo">
    <div class="demo-container">
      <div class="demo-header">
        <h1>邮箱验证功能演示</h1>
        <p>测试邮箱验证码发送、验证和注册功能</p>
      </div>

      <div class="demo-content">
        <!-- 邮箱验证组件 -->
        <div class="demo-section">
          <h2>邮箱验证组件</h2>
          <EmailVerification 
            ref="emailVerificationRef"
            @email-verified="handleEmailVerified"
            @email-changed="handleEmailChanged"
          />
        </div>

        <!-- 注册表单 -->
        <div class="demo-section">
          <h2>注册表单</h2>
          <form @submit.prevent="handleRegister" class="demo-form">
            <div class="form-group">
              <label for="username">用户名</label>
              <input
                id="username"
                v-model="registerForm.username"
                type="text"
                placeholder="请输入用户名"
                required
                :disabled="loading"
              />
            </div>

            <div class="form-group">
              <label for="display_name">显示名称</label>
              <input
                id="display_name"
                v-model="registerForm.display_name"
                type="text"
                placeholder="请输入显示名称"
                :disabled="loading"
              />
            </div>

            <div class="form-group">
              <label for="password">密码</label>
              <input
                id="password"
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                required
                :disabled="loading"
              />
            </div>

            <div class="form-group">
              <label for="confirm_password">确认密码</label>
              <input
                id="confirm_password"
                v-model="confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                required
                :disabled="loading"
              />
            </div>

            <button
              type="submit"
              class="register-button"
              :disabled="loading || !isFormValid"
            >
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              <i v-else-if="!emailVerified" class="fas fa-envelope"></i>
              <i v-else class="fas fa-user-plus"></i>
              {{ loading ? '注册中...' : emailVerified ? '注册账户' : '请先验证邮箱' }}
            </button>
          </form>
        </div>

        <!-- 状态显示 -->
        <div class="demo-section">
          <h2>状态信息</h2>
          <div class="status-info">
            <div class="status-item">
              <span class="status-label">邮箱验证状态:</span>
              <span :class="['status-value', emailVerified ? 'success' : 'pending']">
                {{ emailVerified ? '已验证' : '未验证' }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">验证码:</span>
              <span class="status-value">{{ verificationCode || '未获取' }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">表单验证:</span>
              <span :class="['status-value', isFormValid ? 'success' : 'pending']">
                {{ isFormValid ? '通过' : '未通过' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>

        <!-- 成功提示 -->
        <div v-if="successMessage" class="success-message">
          <i class="fas fa-check-circle"></i>
          {{ successMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import type { RegisterWithVerificationData } from '@/api/authService'
import EmailVerification from '@/components/EmailVerification.vue'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const registerForm = ref({
  username: '',
  display_name: '',
  password: '',
  user_type: 'user' as const
})

// 界面状态
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const successMessage = ref('')

// 邮箱验证状态
const emailVerified = ref(false)
const verificationCode = ref('')
const emailVerificationRef = ref<InstanceType<typeof EmailVerification> | null>(null)

// 表单验证
const isFormValid = computed(() => {
  const form = registerForm.value
  const basic = form.username && form.password && confirmPassword.value
  const passwordMatch = form.password === confirmPassword.value
  const emailVerification = emailVerified.value
  
  return basic && passwordMatch && emailVerification
})

// 邮箱验证相关方法
const handleEmailVerified = (email: string, code: string) => {
  emailVerified.value = true
  verificationCode.value = code
  error.value = ''
  successMessage.value = '邮箱验证成功！现在可以注册了。'
}

const handleEmailChanged = (email: string) => {
  emailVerified.value = false
  verificationCode.value = ''
  error.value = ''
  successMessage.value = ''
}

// 处理注册
const handleRegister = async () => {
  try {
    loading.value = true
    error.value = ''
    successMessage.value = ''
    
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
    
    // 检查邮箱是否已验证
    if (!emailVerified.value) {
      error.value = '请先完成邮箱验证'
      return
    }
    
    // 使用邮箱验证注册
    const registerData: RegisterWithVerificationData = {
      ...registerForm.value,
      email: emailVerificationRef.value?.getEmail() || '',
      verification_code: verificationCode.value
    }
    
    await authStore.registerWithVerification(registerData)
    
    successMessage.value = '注册成功！正在跳转...'
    
    // 延迟跳转
    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)
    
  } catch (err: any) {
    error.value = err.error || '注册失败，请检查输入信息'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.email-verification-demo {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.demo-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.demo-header {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.demo-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.demo-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.demo-content {
  padding: 2rem;
}

.demo-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  background: #fafafa;
}

.demo-section h2 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
  font-weight: 600;
}

.demo-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #2196f3;
}

.register-button {
  padding: 1rem;
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.register-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.status-label {
  font-weight: 500;
  color: #333;
}

.status-value {
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.status-value.success {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-value.pending {
  background: #fff3e0;
  color: #f57c00;
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 1rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.success-message {
  background: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

@media (max-width: 768px) {
  .email-verification-demo {
    padding: 1rem;
  }
  
  .demo-container {
    border-radius: 12px;
  }
  
  .demo-header {
    padding: 1.5rem;
  }
  
  .demo-header h1 {
    font-size: 1.5rem;
  }
  
  .demo-content {
    padding: 1.5rem;
  }
}
</style>

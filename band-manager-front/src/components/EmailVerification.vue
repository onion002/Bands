<template>
  <div class="email-verification">
    <!-- 验证码输入区域 -->
    <div v-if="!codeSent" class="verification-section">
      <div class="form-group">
        <label for="verification-email">邮箱地址</label>
        <div class="input-wrapper">
          <i class="fas fa-envelope input-icon"></i>
          <input
            id="verification-email"
            v-model="email"
            type="email"
            placeholder="请输入邮箱地址"
            required
            :disabled="loading"
            @input="handleEmailInput"
          />
        </div>
        <small class="form-hint">
          <i class="fas fa-info-circle"></i>
          我们将向该邮箱发送验证码
        </small>
      </div>

      <button
        type="button"
        class="send-code-button"
        :disabled="loading || !isEmailValid"
        @click="sendVerificationCode"
      >
        <i v-if="loading" class="fas fa-spinner fa-spin"></i>
        <i v-else class="fas fa-paper-plane"></i>
        {{ loading ? '发送中...' : '发送验证码' }}
      </button>
    </div>

    <!-- 验证码输入区域 -->
    <div v-if="codeSent" class="verification-section">
      <div class="verification-header">
        <i class="fas fa-check-circle success-icon"></i>
        <span>验证码已发送到 {{ email }}</span>
      </div>

      <div class="form-group">
        <label for="verification-code">验证码</label>
        <div class="input-wrapper">
          <i class="fas fa-key input-icon"></i>
          <input
            id="verification-code"
            v-model="verificationCode"
            type="text"
            placeholder="请输入6位验证码"
            maxlength="6"
            required
            :disabled="loading"
            @input="handleCodeInput"
          />
        </div>
        <small class="form-hint">
          <i class="fas fa-clock"></i>
          验证码将在5分钟后过期
        </small>
      </div>

      <div class="verification-actions">
        <button
          type="button"
          class="verify-code-button"
          :disabled="loading || !isCodeValid"
          @click="verifyCode"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-check"></i>
          {{ loading ? '验证中...' : '验证验证码' }}
        </button>

        <button
          type="button"
          class="resend-code-button"
          :disabled="loading || countdown > 0"
          @click="resendCode"
        >
          <i class="fas fa-redo"></i>
          {{ countdown > 0 ? `${countdown}s后重发` : '重新发送' }}
        </button>
      </div>

      <div class="verification-footer">
        <button
          type="button"
          class="change-email-button"
          :disabled="loading"
          @click="changeEmail"
        >
          <i class="fas fa-edit"></i>
          更换邮箱
        </button>
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
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { AuthService } from '@/api/authService'

// Props
interface Props {
  initialEmail?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialEmail: ''
})

// Emits
const emit = defineEmits<{
  'email-verified': [email: string, code: string]
  'email-changed': [email: string]
}>()

// 响应式数据
const email = ref(props.initialEmail)
const verificationCode = ref('')
const codeSent = ref(false)
const loading = ref(false)
const error = ref('')
const successMessage = ref('')
const countdown = ref(0)
let countdownTimer: NodeJS.Timeout | null = null

// 计算属性
const isEmailValid = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.value)
})

const isCodeValid = computed(() => {
  return verificationCode.value.length === 6 && /^\d{6}$/.test(verificationCode.value)
})

// 方法
const handleEmailInput = () => {
  error.value = ''
  successMessage.value = ''
}

const handleCodeInput = () => {
  error.value = ''
  // 自动格式化验证码（只允许数字）
  verificationCode.value = verificationCode.value.replace(/\D/g, '')
}

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer!)
      countdownTimer = null
    }
  }, 1000)
}

const sendVerificationCode = async () => {
  try {
    loading.value = true
    error.value = ''
    successMessage.value = ''

    await AuthService.sendVerificationCode(email.value, 'register')
    
    codeSent.value = true
    successMessage.value = '验证码已发送，请查收邮件'
    startCountdown()
    
    emit('email-changed', email.value)
  } catch (err: any) {
    error.value = err.error || '发送验证码失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const verifyCode = async () => {
  try {
    loading.value = true
    error.value = ''
    successMessage.value = ''

    await AuthService.verifyEmail(email.value, verificationCode.value, 'register')
    
    successMessage.value = '验证码验证成功！'
    
    // 延迟一下再触发事件，让用户看到成功消息
    setTimeout(() => {
      emit('email-verified', email.value, verificationCode.value)
    }, 1000)
  } catch (err: any) {
    error.value = err.error || '验证码验证失败，请检查输入'
  } finally {
    loading.value = false
  }
}

const resendCode = async () => {
  if (countdown.value > 0) return
  
  try {
    loading.value = true
    error.value = ''
    successMessage.value = ''

    await AuthService.sendVerificationCode(email.value, 'register')
    
    successMessage.value = '验证码已重新发送'
    startCountdown()
  } catch (err: any) {
    error.value = err.error || '重新发送失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const changeEmail = () => {
  codeSent.value = false
  verificationCode.value = ''
  error.value = ''
  successMessage.value = ''
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

// 生命周期
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})

// 暴露方法给父组件
defineExpose({
  getEmail: () => email.value,
  getVerificationCode: () => verificationCode.value,
  isVerified: () => codeSent.value && successMessage.value === '验证码验证成功！'
})
</script>

<style scoped>
.email-verification {
  margin-bottom: 1.5rem;
}

.verification-section {
  margin-bottom: 1rem;
}

.verification-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 8px;
  color: #1976d2;
  font-weight: 500;
}

.success-icon {
  color: #4caf50;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #666;
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #2196f3;
}

.form-hint {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.send-code-button,
.verify-code-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
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

.send-code-button:hover:not(:disabled),
.verify-code-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.send-code-button:disabled,
.verify-code-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.verification-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.verify-code-button {
  flex: 2;
}

.resend-code-button {
  flex: 1;
  padding: 12px;
  background: #f5f5f5;
  color: #666;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.resend-code-button:hover:not(:disabled) {
  background: #e0e0e0;
  color: #333;
}

.resend-code-button:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.verification-footer {
  text-align: center;
}

.change-email-button {
  padding: 8px 16px;
  background: none;
  color: #2196f3;
  border: 1px solid #2196f3;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.change-email-button:hover:not(:disabled) {
  background: #2196f3;
  color: white;
}

.change-email-button:disabled {
  color: #ccc;
  border-color: #ccc;
  cursor: not-allowed;
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-size: 0.875rem;
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
  .verification-actions {
    flex-direction: column;
  }
  
  .verify-code-button,
  .resend-code-button {
    flex: none;
  }
}
</style>

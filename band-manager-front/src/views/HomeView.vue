<template>
  <div class="home-view">
    <!-- 未认证用户显示登录界面 -->
    <div v-if="!authStore.isAuthenticated" class="auth-landing">
      <div class="landing-container">
        <div class="landing-content">
          <div class="logo-section">
            <div class="logo">
              <i class="fas fa-music"></i>
            </div>
            <h1 class="brand-title">乐队管理系统</h1>
            <p class="brand-subtitle">专业的乐队信息管理平台</p>
          </div>

          <div class="auth-buttons">
            <router-link to="/auth/login" class="auth-btn login-btn">
              <i class="fas fa-sign-in-alt"></i>
              登录
            </router-link>
            <router-link to="/auth/register" class="auth-btn register-btn">
              <i class="fas fa-user-plus"></i>
              注册
            </router-link>
          </div>

          <div class="features">
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
    </div>

    <!-- 已认证用户根据类型跳转 -->
    <div v-else-if="authStore.isAuthenticated && !redirecting" class="redirecting">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>正在跳转...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const redirecting = ref(false)

onMounted(async () => {
  console.log('HomeView mounted')
  console.log('Initial auth state:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  })

  // 初始化认证状态
  authStore.initAuth()

  console.log('After initAuth:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  })

  // 如果有token但没有用户信息，验证token
  if (authStore.token && !authStore.user) {
    console.log('Verifying token...')
    const isValid = await authStore.verifyToken()
    console.log('Token verification result:', isValid)
  }

  // 如果用户已登录，根据用户类型跳转
  if (authStore.isAuthenticated) {
    console.log('User is authenticated, redirecting...')
    redirecting.value = true
    setTimeout(() => {
      if (authStore.isAdmin) {
        console.log('Redirecting to dashboard')
        router.push('/dashboard')
      } else {
        console.log('Redirecting to public')
        router.push('/public')
      }
    }, 1000)
  } else {
    console.log('User is not authenticated, showing landing page')
  }
})
</script>

<style scoped>
.home-view {
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
}

.auth-landing {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.auth-landing::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.landing-container {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
  max-width: 500px;
  padding: 2rem;
}

.logo-section {
  margin-bottom: 3rem;
}

.logo {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.logo i {
  font-size: 3rem;
  color: white;
}

.brand-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.auth-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 3rem;
}

.auth-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  min-width: 120px;
  justify-content: center;
}

.login-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.register-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

.register-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.9;
}

.feature-item i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.feature-item span {
  font-size: 1rem;
  font-weight: 500;
}

.redirecting {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-spinner {
  text-align: center;
  color: white;
}

.loading-spinner i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.loading-spinner p {
  font-size: 1.2rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .brand-title {
    font-size: 2.5rem;
  }

  .auth-buttons {
    flex-direction: column;
    align-items: center;
  }

  .auth-btn {
    width: 200px;
  }

  .features {
    gap: 1rem;
  }

  .feature-item {
    min-width: 80px;
  }

  .landing-container {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: 2rem;
  }

  .logo {
    width: 80px;
    height: 80px;
  }

  .logo i {
    font-size: 2.5rem;
  }
}
</style>
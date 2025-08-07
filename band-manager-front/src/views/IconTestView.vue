<template>
  <div class="icon-test-container">
    <div class="test-header">
      <h1>图标显示测试</h1>
      <p>验证Font Awesome图标是否正常显示</p>
    </div>

    <div class="test-sections">
      <!-- 基础图标测试 -->
      <div class="test-section">
        <h2>基础图标测试</h2>
        <div class="icon-grid">
          <div class="icon-item">
            <i class="fas fa-music"></i>
            <span>fa-music</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-users"></i>
            <span>fa-users</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-calendar-alt"></i>
            <span>fa-calendar-alt</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-chart-line"></i>
            <span>fa-chart-line</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-heart"></i>
            <span>fa-heart</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-star"></i>
            <span>fa-star</span>
          </div>
        </div>
      </div>

      <!-- 表单图标测试 -->
      <div class="test-section">
        <h2>表单图标测试</h2>
        <div class="icon-grid">
          <div class="icon-item">
            <i class="fas fa-user"></i>
            <span>fa-user</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-envelope"></i>
            <span>fa-envelope</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-lock"></i>
            <span>fa-lock</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-key"></i>
            <span>fa-key</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-eye"></i>
            <span>fa-eye</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-eye-slash"></i>
            <span>fa-eye-slash</span>
          </div>
        </div>
      </div>

      <!-- 操作图标测试 -->
      <div class="test-section">
        <h2>操作图标测试</h2>
        <div class="icon-grid">
          <div class="icon-item">
            <i class="fas fa-sign-in-alt"></i>
            <span>fa-sign-in-alt</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-user-plus"></i>
            <span>fa-user-plus</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-spinner fa-spin"></i>
            <span>fa-spinner (spin)</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-exclamation-circle"></i>
            <span>fa-exclamation-circle</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-info-circle"></i>
            <span>fa-info-circle</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-crown"></i>
            <span>fa-crown</span>
          </div>
        </div>
      </div>

      <!-- 特殊图标测试 -->
      <div class="test-section">
        <h2>特殊图标测试</h2>
        <div class="icon-grid">
          <div class="icon-item">
            <i class="fas fa-shield-alt"></i>
            <span>fa-shield-alt</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-rocket"></i>
            <span>fa-rocket</span>
          </div>
          <div class="icon-item">
            <i class="fas fa-id-card"></i>
            <span>fa-id-card</span>
          </div>
          <div class="icon-item">
            <i class="fab fa-github"></i>
            <span>fa-github (brand)</span>
          </div>
          <div class="icon-item">
            <i class="far fa-heart"></i>
            <span>fa-heart (regular)</span>
          </div>
          <div class="icon-item">
            <i class="fal fa-star" style="color: #ccc;"></i>
            <span>fa-star (light)</span>
          </div>
        </div>
      </div>

      <!-- 测试结果 -->
      <div class="test-section">
        <h2>测试结果</h2>
        <div class="test-result">
          <div class="result-item" :class="{ success: iconsLoaded, error: !iconsLoaded }">
            <i :class="iconsLoaded ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
            <span>{{ iconsLoaded ? 'Font Awesome 图标加载成功' : 'Font Awesome 图标加载失败' }}</span>
          </div>
          <div class="font-info">
            <p><strong>当前版本:</strong> Font Awesome 6.4.0</p>
            <p><strong>CDN地址:</strong> https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css</p>
            <p><strong>支持的前缀:</strong> fas (solid), far (regular), fab (brands), fal (light)</p>
          </div>
        </div>
      </div>
    </div>

    <div class="test-actions">
      <router-link to="/auth/login" class="test-button">
        <i class="fas fa-sign-in-alt"></i>
        测试登录页面
      </router-link>
      <router-link to="/auth/register" class="test-button">
        <i class="fas fa-user-plus"></i>
        测试注册页面
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const iconsLoaded = ref(false)

// 检测图标是否加载成功
const checkIconsLoaded = () => {
  // 创建一个测试元素来检查字体是否加载
  const testElement = document.createElement('i')
  testElement.className = 'fas fa-music'
  testElement.style.position = 'absolute'
  testElement.style.left = '-9999px'
  document.body.appendChild(testElement)
  
  // 检查元素的计算样式
  const computedStyle = window.getComputedStyle(testElement, '::before')
  const content = computedStyle.getPropertyValue('content')
  
  // 如果content不为空且不是'none'，说明图标加载成功
  iconsLoaded.value = content && content !== 'none' && content !== '""'
  
  // 清理测试元素
  document.body.removeChild(testElement)
}

onMounted(() => {
  // 延迟检查，确保CSS加载完成
  setTimeout(checkIconsLoaded, 1000)
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.icon-test-container {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background: $dark;
  color: $white;
}

.test-header {
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, $white 0%, $primary 50%, $secondary 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    font-family: $font-family-display;
  }
  
  p {
    color: $gray-300;
    font-size: 1.2rem;
  }
}

.test-sections {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.test-section {
  background: rgba($lightgray, 0.5);
  border: 1px solid rgba($white, 0.1);
  border-radius: 16px;
  padding: 2rem;
  
  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: $white;
    margin-bottom: 1.5rem;
    font-family: $font-family-display;
  }
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: rgba($darkgray, 0.8);
  border: 1px solid rgba($white, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba($primary, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba($primary, 0.15);
  }
  
  i {
    font-size: 2rem;
    color: $primary;
  }
  
  span {
    color: $gray-300;
    font-size: 0.9rem;
    font-family: monospace;
    text-align: center;
  }
}

.test-result {
  .result-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    
    &.success {
      background: rgba(34, 197, 94, 0.1);
      border: 1px solid rgba(34, 197, 94, 0.3);
      color: #22c55e;
    }
    
    &.error {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #ef4444;
    }
    
    i {
      font-size: 1.2rem;
    }
  }
  
  .font-info {
    background: rgba($darkgray, 0.5);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid rgba($white, 0.1);
    
    p {
      margin: 0.5rem 0;
      color: $gray-300;
      font-size: 0.9rem;
      
      strong {
        color: $white;
      }
    }
  }
}

.test-actions {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 3rem;
}

.test-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 2rem;
  background: linear-gradient(135deg, $primary, $secondary);
  color: white;
  text-decoration: none;
  border-radius: 16px;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: $shadow-primary;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba($primary, 0.4);
  }
}

@media (max-width: 768px) {
  .icon-test-container {
    padding: 1rem;
  }
  
  .icon-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .test-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .test-button {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
}
</style>

<template>
  <div class="error-page">
    <!-- 🎵 错误内容 -->
    <div class="error-content">
      <div class="error-icon">
        <i class="fa fa-exclamation-triangle"></i>
      </div>
      
      <h1 class="error-title">
        <span class="gradient-text">{{ errorCode }}</span>
      </h1>
      
      <h2 class="error-subtitle">{{ errorTitle }}</h2>
      
      <p class="error-description">{{ errorMessage }}</p>
      
      <!-- 🎨 操作按钮 -->
      <div class="error-actions">
        <button @click="goHome" class="btn btn-primary">
          <i class="fa fa-home"></i>
          返回首页
        </button>
        
        <button @click="goBack" class="btn btn-outline">
          <i class="fa fa-arrow-left"></i>
          返回上页
        </button>
        
        <button @click="refresh" class="btn btn-outline">
          <i class="fa fa-refresh"></i>
          刷新页面
        </button>
      </div>
    </div>
    
    <!-- 🌟 装饰元素 -->
    <div class="error-decoration">
      <div class="floating-note">♪</div>
      <div class="floating-note">♫</div>
      <div class="floating-note">♪</div>
      <div class="floating-note">♬</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 🎯 错误信息计算
const errorCode = computed(() => {
  return route.params.code || '404'
})

const errorTitle = computed(() => {
  const titles: Record<string, string> = {
    '404': '页面未找到',
    '403': '访问被拒绝',
    '500': '服务器错误',
    '503': '服务不可用'
  }
  return titles[errorCode.value] || '未知错误'
})

const errorMessage = computed(() => {
  const messages: Record<string, string> = {
    '404': '抱歉，您访问的页面不存在。可能是链接错误或页面已被移除。',
    '403': '您没有权限访问此页面。请联系管理员获取访问权限。',
    '500': '服务器内部错误。我们正在努力修复，请稍后再试。',
    '503': '服务暂时不可用。请稍后再试或联系技术支持。'
  }
  return messages[errorCode.value] || '发生了未知错误，请稍后再试。'
})

// 🎵 操作函数
const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

const refresh = () => {
  window.location.reload()
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.error-page {
  min-height: calc(100vh - 4rem);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
}

.error-content {
  text-align: center;
  max-width: 600px;
  z-index: 1;
  
  .error-icon {
    font-size: 6rem;
    color: $primary;
    margin-bottom: 2rem;
    animation: pulse 2s ease-in-out infinite;
    
    @media (max-width: 768px) {
      font-size: 4rem;
      margin-bottom: 1.5rem;
    }
  }
  
  .error-title {
    font-size: 8rem;
    font-weight: 900;
    margin: 0 0 1rem;
    line-height: 1;
    
    @media (max-width: 768px) {
      font-size: 6rem;
    }
    
    @media (max-width: 480px) {
      font-size: 4rem;
    }
  }
  
  .error-subtitle {
    font-size: 2rem;
    font-weight: 600;
    color: $white;
    margin: 0 0 1rem;
    
    @media (max-width: 768px) {
      font-size: 1.5rem;
    }
  }
  
  .error-description {
    font-size: 1.125rem;
    color: $gray-400;
    line-height: 1.6;
    margin: 0 0 3rem;
    
    @media (max-width: 768px) {
      font-size: 1rem;
      margin-bottom: 2rem;
    }
  }
  
  .error-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    
    @media (max-width: 480px) {
      flex-direction: column;
      align-items: center;
    }
  }
}

// 🌟 装饰动画
.error-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  
  .floating-note {
    position: absolute;
    font-size: 2rem;
    color: rgba($primary, 0.3);
    animation: float 6s ease-in-out infinite;
    
    &:nth-child(1) {
      top: 20%;
      left: 10%;
      animation-delay: 0s;
    }
    
    &:nth-child(2) {
      top: 60%;
      right: 15%;
      animation-delay: 1.5s;
    }
    
    &:nth-child(3) {
      bottom: 30%;
      left: 20%;
      animation-delay: 3s;
    }
    
    &:nth-child(4) {
      top: 40%;
      right: 30%;
      animation-delay: 4.5s;
    }
  }
}

// 🎨 动画定义
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.3;
  }
  25% {
    transform: translateY(-20px) rotate(5deg);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-10px) rotate(-5deg);
    opacity: 0.4;
  }
  75% {
    transform: translateY(-30px) rotate(3deg);
    opacity: 0.7;
  }
}
</style>

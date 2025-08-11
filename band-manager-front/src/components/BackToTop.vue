<template>
  <transition name="back-to-top">
    <button
      v-show="showButton"
      @click="scrollToTop"
      class="back-to-top-btn"
      :title="title"
      :class="{ 'is-visible': showButton }"
    >
      <i class="fa fa-arrow-up"></i>
      <span class="btn-text">{{ buttonText }}</span>
    </button>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  /** 按钮显示的文字 */
  buttonText?: string
  /** 按钮的title提示 */
  title?: string
  /** 滚动多少距离后显示按钮 */
  scrollThreshold?: number
  /** 按钮位置 */
  position?: 'right' | 'left'
  /** 按钮大小 */
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  buttonText: '返回顶部',
  title: '返回页面顶部',
  scrollThreshold: 300,
  position: 'right',
  size: 'medium'
})

const showButton = ref(false)

// 滚动事件处理
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  showButton.value = scrollTop > props.scrollThreshold
}

// 返回顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 监听滚动事件
onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.back-to-top-btn {
  position: fixed;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.75rem;
  background: rgba($primary, 0.9);
  border: 2px solid rgba($primary, 0.3);
  border-radius: 50%;
  color: $white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba($primary, 0.3);
  
  // 位置设置
  &.is-visible {
    opacity: 1;
    transform: translateY(0);
  }
  
  // 大小设置
  &.size-small {
    width: 3rem;
    height: 3rem;
    font-size: 0.875rem;
    
    .btn-text {
      font-size: 0.75rem;
    }
  }
  
  &.size-medium {
    width: 4rem;
    height: 4rem;
    font-size: 1rem;
    
    .btn-text {
      font-size: 0.875rem;
    }
  }
  
  &.size-large {
    width: 5rem;
    height: 5rem;
    font-size: 1.25rem;
    
    .btn-text {
      font-size: 1rem;
    }
  }
  
  // 位置设置
  &.position-right {
    right: 2rem;
  }
  
  &.position-left {
    left: 2rem;
  }
  
  // 底部位置（避免被移动端导航栏遮挡）
  bottom: 6rem;
  
  // 图标样式
  i {
    font-size: 1.2em;
    transition: transform 0.3s ease;
  }
  
  // 文字样式
  .btn-text {
    font-weight: 500;
    text-align: center;
    line-height: 1;
    opacity: 0.9;
  }
  
  // 悬停效果
  &:hover {
    background: rgba($primary, 1);
    border-color: rgba($primary, 0.6);
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba($primary, 0.4);
    
    i {
      transform: translateY(-2px);
    }
    
    .btn-text {
      opacity: 1;
    }
  }
  
  // 点击效果
  &:active {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba($primary, 0.3);
  }
  
  // 焦点样式
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba($primary, 0.3);
  }
}

// 过渡动画
.back-to-top-enter-active,
.back-to-top-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-to-top-enter-from,
.back-to-top-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.back-to-top-enter-to,
.back-to-top-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

// 响应式设计
@media (max-width: 768px) {
  .back-to-top-btn {
    // 移动端调整位置和大小
    &.size-medium {
      width: 3.5rem;
      height: 3.5rem;
      font-size: 0.875rem;
      
      .btn-text {
        font-size: 0.75rem;
      }
    }
    
    &.size-large {
      width: 4rem;
      height: 4rem;
      font-size: 1rem;
      
      .btn-text {
        font-size: 0.875rem;
      }
    }
    
    // 移动端位置调整
    &.position-right {
      right: 1rem;
    }
    
    &.position-left {
      left: 1rem;
    }
    
    bottom: 5rem;
  }
}

@media (max-width: 480px) {
  .back-to-top-btn {
    // 小屏幕进一步调整
    &.size-medium,
    &.size-large {
      width: 3rem;
      height: 3rem;
      font-size: 0.75rem;
      
      .btn-text {
        font-size: 0.625rem;
      }
    }
    
    padding: 0.5rem;
    
    .btn-text {
      display: none; // 小屏幕隐藏文字，只显示图标
    }
  }
}

// 深色主题适配
@media (prefers-color-scheme: dark) {
  .back-to-top-btn {
    background: rgba($primary, 0.95);
    border-color: rgba($primary, 0.4);
    box-shadow: 0 4px 20px rgba($primary, 0.4);
    
    &:hover {
      background: rgba($primary, 1);
      border-color: rgba($primary, 0.7);
      box-shadow: 0 8px 30px rgba($primary, 0.5);
    }
  }
}
</style>

<template>
  <div class="empty-state">
    <div class="empty-content">
      <i :class="iconClass"></i>
      <p>{{ message }}</p>
      <button v-if="showButton" @click="handleButtonClick">
        <i v-if="buttonIcon" :class="buttonIcon"></i>
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  // 图标类名
  iconClass: string
  // 显示的消息
  message: string
  // 是否显示按钮
  showButton?: boolean
  // 按钮文本
  buttonText?: string
  // 按钮图标
  buttonIcon?: string
}

interface Emits {
  (e: 'button-click'): void
}

const props = withDefaults(defineProps<Props>(), {
  showButton: true,
  buttonText: '添加数据',
  buttonIcon: 'fas fa-plus'
})

const emit = defineEmits<Emits>()

const handleButtonClick = () => {
  emit('button-click')
}
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 80px 20px;
  margin: 40px auto;
  max-width: 500px;
  background: linear-gradient(135deg, rgba(229, 57, 53, 0.1), rgba(229, 57, 53, 0.05));
  border: 2px dashed rgba(229, 57, 53, 0.3);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

/* 添加背景装饰 */
.empty-state::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(229, 57, 53, 0.05) 0%, transparent 70%);
  animation: pulse 4s ease-in-out infinite;
}

.empty-content {
  position: relative;
  z-index: 2;
}

.empty-content i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: #e53935;
  display: block;
  animation: bounce 2s ease-in-out infinite;
  text-shadow: 0 0 20px rgba(229, 57, 53, 0.3);
}

.empty-content p {
  font-size: 1.2rem;
  color: #ccc;
  margin-bottom: 30px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.empty-content button {
  background: linear-gradient(135deg, #e53935, #c62828);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(229, 57, 53, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.empty-content button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(229, 57, 53, 0.4);
  background: linear-gradient(135deg, #d32f2f, #b71c1c);
}

.empty-content button:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(229, 57, 53, 0.3);
}

/* 动画效果 */
@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .empty-state {
    padding: 60px 15px;
    margin: 20px auto;
  }
  
  .empty-content i {
    font-size: 3rem;
    margin-bottom: 15px;
  }
  
  .empty-content p {
    font-size: 1rem;
    margin-bottom: 20px;
  }
  
  .empty-content button {
    padding: 10px 20px;
    font-size: 0.9rem;
  }
}
</style>

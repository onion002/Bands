<template>
  <div class="poster-girl-control">
    <button 
      @click="togglePosterGirl" 
      class="control-btn"
      :title="isHidden ? '显示看板娘' : '隐藏看板娘'"
    >
      <i :class="isHidden ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
    </button>
    
    <button 
      @click="reloadPosterGirl" 
      class="control-btn"
      title="重载看板娘"
      v-show="!isHidden"
    >
      <i class="fas fa-redo"></i>
    </button>
    
    <button 
      @click="togglePosition" 
      class="control-btn"
      title="切换位置"
      v-show="!isHidden"
    >
      <i class="fas fa-arrows-alt"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props
interface Props {
  posterGirlRef?: any
}

const props = withDefaults(defineProps<Props>(), {
  posterGirlRef: undefined
})

// 响应式数据
const isHidden = ref(false)
const position = ref<'left' | 'right'>('right')

// 切换看板娘显示/隐藏
const togglePosterGirl = () => {
  isHidden.value = !isHidden.value
  if (props.posterGirlRef && typeof props.posterGirlRef.togglePosterGirl === 'function') {
    props.posterGirlRef.togglePosterGirl()
  }
}

// 重载看板娘
const reloadPosterGirl = () => {
  if (props.posterGirlRef && typeof props.posterGirlRef.reloadPosterGirl === 'function') {
    props.posterGirlRef.reloadPosterGirl()
  }
}

// 切换位置
const togglePosition = () => {
  position.value = position.value === 'right' ? 'left' : 'right'
  // 这里可以添加位置切换的逻辑
}
</script>

<style lang="scss" scoped>
.poster-girl-control {
  position: fixed;
  left: 20px;
  bottom: 20px;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
    transform: scale(1.1);
  }
  
  &:active {
    transform: scale(0.95);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .poster-girl-control {
    display: none; // 在移动设备上隐藏控制面板
  }
}
</style>

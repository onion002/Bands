<template>
  <div class="poster-girl-container">
    <!-- 看板娘容器 -->
    <div class="pio-container right" v-show="!isHidden">
      <div class="pio-action"></div>
      <canvas id="pio" width="280" height="250"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { defaultPosterGirlConfig, type PosterGirlConfig } from '@/config/posterGirl'

// 响应式数据
const isHidden = ref(false)
let pioInstance: any = null

// 看板娘配置 - 使用配置文件
const pioConfig: PosterGirlConfig = {
  ...defaultPosterGirlConfig,
  // 可以在这里覆盖默认配置
}

// 初始化看板娘
const initPosterGirl = () => {
  // 检查是否已经加载了必要的脚本
  if (typeof (window as any).Paul_Pio === 'undefined') {
    console.warn('看板娘脚本未加载，请检查文件路径')
    return
  }

  try {
    // 创建看板娘实例
    pioInstance = new (window as any).Paul_Pio(pioConfig)
    console.log('看板娘初始化成功！')
  } catch (error) {
    console.error('看板娘初始化失败:', error)
  }
}

// 重载看板娘（用于页面切换后）
const reloadPosterGirl = () => {
  if (pioInstance && typeof pioInstance.init === 'function') {
    pioInstance.init()
  }
}

// 显示/隐藏看板娘
const togglePosterGirl = () => {
  isHidden.value = !isHidden.value
  if (!isHidden.value && pioInstance) {
    reloadPosterGirl()
  }
}

// 暴露方法给父组件
defineExpose({
  reloadPosterGirl,
  togglePosterGirl
})

// 生命周期
onMounted(() => {
  // 延迟初始化，确保DOM和脚本都已加载
  setTimeout(() => {
    initPosterGirl()
  }, 1000)
})

onUnmounted(() => {
  // 清理实例
  if (pioInstance) {
    pioInstance = null
  }
})
</script>

<style lang="scss" scoped>
.poster-girl-container {
  position: fixed;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;
}

.pio-container {
  position: relative;
  pointer-events: auto;
  
  &.right {
    right: 0;
  }
  
  &.left {
    left: 0;
  }
}

.pio-action {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

#pio {
  display: block;
  max-width: 100%;
  height: auto;
}

// 响应式设计
@media (max-width: 768px) {
  .poster-girl-container {
    display: none; // 在移动设备上隐藏
  }
}
</style>

<template>
<div 
    class="poster-girl-container"
    ref="containerRef"
    :class="{ 'hidden': isHidden, 'dragging': isDragging, 'hidden-mobile': pioConfig.hidden }"
    :style="containerStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <!-- 看板娘主体 -->
    <div class="poster-girl-body" v-show="!isHidden">
      <!-- 操作按钮区域 -->
      <div class="pio-action" v-show="showActions">
        <!-- 音乐盒按钮 -->
        <div 
          class="pio-music pio-btn" 
          title="🎵 音乐盒演示"
          @click="navigateToMusicBox"
        >
          <i class="fas fa-music"></i>
        </div>
        
        <!-- 设置按钮 -->
        <div 
          class="pio-settings pio-btn" 
          title="🎭 看板娘设置"
          @click="navigateToSettings"
        >
          <i class="fas fa-cog"></i>
        </div>
        
        <!-- 模型切换按钮 -->
        <div 
          v-if="pioConfig.model && pioConfig.model.length > 1"
          class="pio-skin pio-btn" 
          title="🎲 随机切换模型"
          @click="switchModel"
        >
          <i class="fas fa-random"></i>
        </div>
        
        <!-- 音乐老师按钮 -->
        <div 
          class="pio-teacher pio-btn" 
          title="🎓 AI乐队顾问"
          @click="navigateToMusicTeacher"
        >
          <i class="fas fa-chalkboard-teacher"></i>
        </div>
        
        <!-- 关闭按钮 -->
        <div 
          class="pio-close pio-btn" 
          title="❌ 隐藏看板娘"
          @click="hidePosterGirl"
        >
          <i class="fas fa-times"></i>
        </div>
      </div>
      
      <!-- Live2D画布 -->
      <canvas 
        id="pio"
        ref="live2dCanvas"
        :width="pioConfig.size?.width || 280" 
        :height="pioConfig.size?.height || 250"
        @click="handleTouch"
        @touchstart="handleTouch"
      ></canvas>
      
      <!-- 对话框 -->
      <div 
        v-if="currentMessage"
        class="pio-dialog"
        :class="{ 'active': showDialog }"
      >
        {{ currentMessage }}
      </div>
    </div>
    
    <!-- 显示按钮（当隐藏时） -->
    <div 
      v-if="isHidden"
      class="pio-show"
      @click="showPosterGirl"
      title="显示看板娘"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, nextTick } from 'vue'
import { getCurrentConfig, saveConfig, type PosterGirlConfig } from '../config/posterGirl'
import { live2dService } from '../services/live2dService'
import { modelManager } from '../services/modelManager'

// 响应式数据
const isHidden = ref(false)
const isDragging = ref(false)
const showActions = ref(false)
const showDialog = ref(false)
const currentMessage = ref('')
const live2dCanvas = ref<HTMLCanvasElement>()
const live2dInstance = ref<any>(null)
const containerRef = ref<HTMLElement | null>(null)

// 拖拽相关
const dragStart = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 })
const containerSize = ref({ width: 0, height: 0 })

// 计算容器尺寸
const updateContainerSize = () => {
  const el = containerRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  containerSize.value.width = rect.width
  containerSize.value.height = rect.height
}

// 约束位置在窗口内
const clampPosition = (x: number, y: number) => {
  const maxX = Math.max(0, window.innerWidth - containerSize.value.width)
  const maxY = Math.max(0, window.innerHeight - containerSize.value.height)
  const clampedX = Math.min(Math.max(0, x), maxX)
  const clampedY = Math.min(Math.max(0, y), maxY)
  return { x: clampedX, y: clampedY }
}

// 看板娘配置
const pioConfig = ref<PosterGirlConfig>(getCurrentConfig())

// 计算容器样式
const containerStyle = computed(() => {
  const baseStyle = {
    position: 'fixed' as const,
    bottom: '2rem',
    right: '2rem',
    zIndex: 1000,
    cursor: isDragging.value ? 'move' : 'default'
  }
  
  // 如果配置了拖拽位置，使用保存的位置
  if (pioConfig.value.dragPosition) {
    return {
      ...baseStyle,
      left: `${pioConfig.value.dragPosition.x}px`,
      top: `${pioConfig.value.dragPosition.y}px`,
      bottom: 'auto',
      right: 'auto'
    }
  }
  
  return baseStyle
})

// 初始化Live2D
const initLive2D = async () => {
  try {
    const canvas = live2dCanvas.value
    if (!canvas) {
      console.error('Canvas元素未找到')
      return
    }

    console.log('🎭 开始初始化Live2D...')

    // 使用Live2D服务初始化
    const success = await live2dService.init(canvas)
    if (success) {
      // 初始化模型管理器
      await modelManager.init()
      
      // 加载默认模型
      const defaultModelPath = pioConfig.value.defaultModel
      const loadSuccess = await modelManager.loadDefaultModel(defaultModelPath)
      
      if (loadSuccess) {
        console.log('✅ Live2D初始化成功')
        showMessage('看板娘加载成功！🎉')
        
        // 显示模型统计信息
        const stats = modelManager.getModelStats()
        console.log(`📊 模型统计: ${stats.available}/${stats.total} 个可用`)
      } else {
        console.error('❌ 模型加载失败')
        showMessage('看板娘模型加载失败')
      }
    } else {
      console.error('❌ Live2D服务初始化失败')
      showMessage('Live2D初始化失败，请刷新页面重试')
    }
  } catch (error) {
    console.error('Live2D初始化异常:', error)
    showMessage('Live2D初始化出现异常')
  }
}



// 显示消息
const showMessage = (message: string | string[], duration: number = 3000) => {
  if (Array.isArray(message)) {
    currentMessage.value = message[Math.floor(Math.random() * message.length)]
  } else {
    currentMessage.value = message
  }
  
  showDialog.value = true
  
  setTimeout(() => {
    showDialog.value = false
    currentMessage.value = ''
  }, duration)
}

// 处理触摸事件
const handleTouch = () => {
  const touchMessages = pioConfig.value.content?.touch || ["你在干什么？", "再摸我就报警了！", "HENTAI!", "不可以这样欺负我啦！"]
  showMessage(touchMessages)
}

// 切换模型 - 随机切换
const switchModel = async () => {
  try {
    console.log('🎲 开始随机切换模型...')
    
    const result = await modelManager.switchToRandomModel()
    
    if (result.success) {
      console.log(`✅ 随机切换成功: ${result.modelName}`)
      
      const skinMessages = pioConfig.value.content?.skin || [
        `切换到了 ${result.modelName}！`,
        "新的造型怎么样？",
        "我换了个新形象~",
        "随机变身完成！✨"
      ]
      showMessage(skinMessages)
    } else {
      console.warn('⚠️ 模型切换失败')
      showMessage("模型切换失败，请稍后再试")
    }
  } catch (error) {
    console.error('模型切换异常:', error)
    showMessage("模型切换出错")
  }
}

// 隐藏看板娘
const hidePosterGirl = () => {
  isHidden.value = true
  localStorage.setItem('posterGirl', '0')
}

// 显示看板娘
const showPosterGirl = () => {
  isHidden.value = false
  localStorage.setItem('posterGirl', '1')
  showWelcomeMessage()
}

// 显示欢迎消息
const showWelcomeMessage = () => {
  if (pioConfig.value.tips) {
    // 时间相关提示
    const hour = new Date().getHours()
    let timeMessage = ''
    
    if (hour > 22 || hour <= 5) {
      timeMessage = "你是夜猫子呀？这么晚还不睡觉，明天起的来嘛"
    } else if (hour > 5 && hour <= 8) {
      timeMessage = "早上好！"
    } else if (hour > 8 && hour <= 11) {
      timeMessage = "上午好！工作顺利嘛，不要久坐，多起来走动走动哦！"
    } else if (hour > 11 && hour <= 14) {
      timeMessage = "中午了，工作了一个上午，现在是午餐时间！"
    } else if (hour > 14 && hour <= 17) {
      timeMessage = "午后很容易犯困呢，今天的运动目标完成了吗？"
    } else if (hour > 17 && hour <= 19) {
      timeMessage = "傍晚了！窗外夕阳的景色很美丽呢，最美不过夕阳红~"
    } else if (hour > 19 && hour <= 21) {
      timeMessage = "晚上好，今天过得怎么样？"
    } else if (hour > 21 && hour <= 23) {
      timeMessage = "已经这么晚了呀，早点休息吧，晚安~"
    }
    
    if (timeMessage) {
      showMessage(timeMessage)
      return
    }
  }
  
  // 默认欢迎消息
  const welcomeMessages = pioConfig.value.content?.welcome || ["欢迎来到乐队管理系统！🎸", "今天想要管理什么乐队呢？", "让我们一起创造美妙的音乐吧！🎵"]
  showMessage(welcomeMessages)
}

// 导航到音乐盒
const navigateToMusicBox = () => {
  window.location.href = '/music-box-demo'
}

// 导航到设置
const navigateToSettings = () => {
  window.location.href = '/poster-girl-settings'
}

// 导航到音乐老师页面
const navigateToMusicTeacher = () => {
  window.location.href = '/music-teacher'
}

// 拖拽功能
const startDrag = (event: MouseEvent | TouchEvent) => {
  if (pioConfig.value.mode !== 'draggable') return
  
  event.preventDefault()
  isDragging.value = true
  updateContainerSize()
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  dragStart.value = { x: clientX, y: clientY }
  
  if (pioConfig.value.dragPosition) {
    dragOffset.value = {
      x: clientX - pioConfig.value.dragPosition.x,
      y: clientY - pioConfig.value.dragPosition.y
    }
  } else {
    dragOffset.value = { x: 0, y: 0 }
  }
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', handleDrag)
  document.addEventListener('touchend', stopDrag)
}

const handleDrag = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  const newX = clientX - dragOffset.value.x
  const newY = clientY - dragOffset.value.y
  const { x: clampedX, y: clampedY } = clampPosition(newX, newY)
  
  // 保存拖拽位置
  if (!pioConfig.value.dragPosition) {
    pioConfig.value.dragPosition = { x: 0, y: 0 }
  }
  pioConfig.value.dragPosition.x = clampedX
  pioConfig.value.dragPosition.y = clampedY
  
  // 拖拽过程中只更新内存，结束时统一保存
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', handleDrag)
  document.removeEventListener('touchend', stopDrag)

  // 拖拽结束后保存，避免高频写入
  saveConfig(pioConfig.value)
}

// 重载看板娘
const reloadPosterGirl = () => {
  console.log('PosterGirl: reloadPosterGirl被调用')
  // 重新初始化Live2D
  nextTick(() => {
    initLive2D()
  })
}

// 切换显示/隐藏
const togglePosterGirl = () => {
  console.log('PosterGirl: togglePosterGirl被调用')
  console.log('PosterGirl: 当前隐藏状态:', isHidden.value)
  
  if (isHidden.value) {
    console.log('PosterGirl: 显示看板娘')
    showPosterGirl()
  } else {
    console.log('PosterGirl: 隐藏看板娘')
    hidePosterGirl()
  }
}

// 切换位置
const togglePosition = () => {
  // 切换左右位置
  if (pioConfig.value.dragPosition) {
    // 如果有拖拽位置，重置到默认位置
    pioConfig.value.dragPosition = undefined
    saveConfig(pioConfig.value)
  } else {
    // 切换到左侧
    pioConfig.value.dragPosition = { x: 20, y: window.innerHeight - 300 }
    saveConfig(pioConfig.value)
  }
  
  // 重新加载配置
  reloadPosterGirl()
}

// 暴露方法给父组件
defineExpose({
  reloadPosterGirl,
  togglePosterGirl,
  switchModel,
  togglePosition
})

// 监听设置变更（localStorage 跨标签）
const handleSettingsChange = () => {
  console.log('检测到配置变更，重新加载看板娘...')
  const newConfig = getCurrentConfig()
  pioConfig.value = newConfig
  
  // 重新初始化自定义提示
  cleanupCustomTips()
  setTimeout(() => {
    initCustomTips()
  }, 500)
  
  reloadPosterGirl()
}

// 监听同窗口自定义事件（设置页保存时派发）
const handleCustomConfigUpdated = (event: Event) => {
  const customEvent = event as CustomEvent
  if (customEvent.detail) {
    console.log('收到自定义配置更新事件:', customEvent.detail)
    pioConfig.value = customEvent.detail as PosterGirlConfig
    cleanupCustomTips()
    setTimeout(() => {
      initCustomTips()
    }, 500)
    reloadPosterGirl()
  }
}

// 监听来自设置页面的消息
const handleMessage = (event: MessageEvent) => {
  if (event.data.type === 'posterGirlConfigUpdated') {
    console.log('收到设置页面配置更新:', event.data.config)
    pioConfig.value = event.data.config
    
    // 重新初始化自定义提示
    cleanupCustomTips()
    setTimeout(() => {
      initCustomTips()
    }, 500)
    
    // 重新加载看板娘
    reloadPosterGirl()
  }
}

// 初始化自定义提示
const initCustomTips = () => {
  if (!pioConfig.value.content?.custom) return
  
  console.log('初始化自定义提示:', pioConfig.value.content.custom)
  
  // 存储事件处理器，便于清理
  ;(window as any).__posterGirlHandlers ||= new WeakMap<Element, { enter?: EventListener; touch?: EventListener }>()
  const handlerMap: WeakMap<Element, { enter?: EventListener; touch?: EventListener }> = (window as any).__posterGirlHandlers
  
  // 为每个自定义提示添加事件监听器
  pioConfig.value.content.custom.forEach((tip, index) => {
    if (!tip.selector) return
    
    try {
      const elements = document.querySelectorAll(tip.selector)
      console.log(`提示 ${index + 1}: 找到 ${elements.length} 个元素`)
      
      const buildMessage = (el: Element) => {
        if (tip.type === 'read') {
          const text = (el.textContent || '').trim() || '正在阅读…'
          return `📖 ${text}`
        }
        if (tip.type === 'link') {
          const anchor = el as HTMLAnchorElement
          const text = (anchor.textContent || '').trim() || anchor.getAttribute('href') || '即将打开链接'
          return `🔗 ${text}`
        }
        return tip.text || ''
      }
      
      elements.forEach((element, elementIndex) => {
        const onEnter: EventListener = () => {
          const msg = buildMessage(element)
          if (msg) showMessage(msg)
        }
        const onTouch: EventListener = () => {
          const msg = buildMessage(element)
          if (msg) showMessage(msg)
        }
        
        element.addEventListener('mouseenter', onEnter)
        element.addEventListener('touchstart', onTouch)
        handlerMap.set(element, { enter: onEnter, touch: onTouch })
        
        console.log(`为元素 ${elementIndex} 添加了提示事件`)
      })
    } catch (error) {
      console.error(`初始化提示 ${index + 1} 失败:`, error)
    }
  })
}

// 清理自定义提示事件
const cleanupCustomTips = () => {
  if (!pioConfig.value.content?.custom) return
  ;(window as any).__posterGirlHandlers ||= new WeakMap<Element, { enter?: EventListener; touch?: EventListener }>()
  const handlerMap: WeakMap<Element, { enter?: EventListener; touch?: EventListener }> = (window as any).__posterGirlHandlers
  
  pioConfig.value.content.custom.forEach((tip, index) => {
    if (!tip.selector) return
    
    try {
      const elements = document.querySelectorAll(tip.selector)
      elements.forEach((element) => {
        const handlers = handlerMap.get(element)
        if (handlers?.enter) element.removeEventListener('mouseenter', handlers.enter)
        if (handlers?.touch) element.removeEventListener('touchstart', handlers.touch)
        handlerMap.delete(element)
      })
    } catch (error) {
      console.error(`清理提示 ${index + 1} 失败:`, error)
    }
  })
}

// 生命周期
onMounted(async () => {
  console.log('PosterGirl组件挂载开始...')
  
  // 检查是否应该隐藏
  const posterGirlHidden = localStorage.getItem('posterGirl') === '0'
  isHidden.value = posterGirlHidden
  
  console.log('看板娘隐藏状态:', posterGirlHidden)
  console.log('2看板娘当前配置:', pioConfig.value)
  
  if (!posterGirlHidden) {
    console.log('开始初始化Live2D...')
    // 初始化Live2D
    await initLive2D()
    
    // 显示欢迎消息
    setTimeout(() => {
      showWelcomeMessage()
    }, 1000)
    
    // 初始化自定义提示
    setTimeout(() => {
      initCustomTips()
    }, 2000)
  } else {
    console.log('看板娘当前处于隐藏状态')
  }
  
  // 监听localStorage变化
  window.addEventListener('storage', handleSettingsChange)
  
  // 监听窗口尺寸变化，保持看板娘在可视区域内
  const onResize = () => {
    updateContainerSize()
    if (pioConfig.value.dragPosition) {
      const { x, y } = clampPosition(pioConfig.value.dragPosition.x, pioConfig.value.dragPosition.y)
      pioConfig.value.dragPosition.x = x
      pioConfig.value.dragPosition.y = y
    }
  }
  window.addEventListener('resize', onResize)
  
  // 监听来自设置页面的消息
  window.addEventListener('message', handleMessage)
  window.addEventListener('posterGirl:updated', handleCustomConfigUpdated as EventListener)
  
  // 监听鼠标悬停显示操作按钮
  const container = document.querySelector('.poster-girl-container')
  if (container) {
    container.addEventListener('mouseenter', () => {
      if (pioConfig.value.mode !== 'static') {
        showActions.value = true
      }
    })
    
    container.addEventListener('mouseleave', () => {
      showActions.value = false
    })
  }
  
  console.log('PosterGirl组件挂载完成')
})

onUnmounted(() => {
  window.removeEventListener('storage', handleSettingsChange)
  window.removeEventListener('resize', () => {})
  window.removeEventListener('message', handleMessage)
  window.removeEventListener('posterGirl:updated', handleCustomConfigUpdated as EventListener)
  
  // 清理拖拽事件监听器
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', handleDrag)
  document.removeEventListener('touchend', stopDrag)
  
  // 清理自定义提示事件
  cleanupCustomTips()
})
</script>

<style lang="scss" scoped>
.poster-girl-container {
  user-select: none;
  transition: transform 0.3s ease;
  position: fixed; /* 固定在视口，不随页面内容滚动 */
  inset: auto; /* 避免意外的定位继承 */
  
  &.dragging {
    transition: none;
  }
  
  &.hidden {
    .poster-girl-body {
      display: none;
    }
    
    .pio-show {
      display: block;
    }
  }
}

.poster-girl-body {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pio-action {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 99999;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  
  .pio-btn {
    pointer-events: auto;
    width: 2em;
    height: 2em;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 50%;
    margin-bottom: 0.5em;
    border: 2px solid rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    
    &:hover {
      transform: scale(1.1);
      border-color: #667eea;
      background: rgba(102, 126, 234, 0.9);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      
      i {
        color: #fff;
        transform: scale(1.1);
      }
    }
    
    i {
      font-size: 0.9em;
      color: #333;
      transition: all 0.3s ease;
    }
  }
  
  // 为不同按钮添加特殊效果
  .pio-music:hover {
    border-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.9);
    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
  }
  
  .pio-settings:hover {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.9);
    box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
  }
  
  .pio-skin:hover {
    border-color: #45b7d1;
    background: rgba(69, 183, 209, 0.9);
    box-shadow: 0 4px 12px rgba(69, 183, 209, 0.3);
  }
  
  .pio-teacher:hover {
    border-color: #96ceb4;
    background: rgba(150, 206, 180, 0.9);
    box-shadow: 0 4px 12px rgba(150, 206, 180, 0.3);
  }
  
  .pio-close:hover {
    border-color: #ff7675;
    background: rgba(255, 118, 117, 0.9);
    box-shadow: 0 4px 12px rgba(255, 118, 117, 0.3);
  }
}

.poster-girl-container:hover .pio-action {
  opacity: 1;
}

.pio-dialog {
  position: absolute;
  bottom: calc(100% - 2em);
  right: 1em;
  opacity: 0;
  visibility: hidden;
  font-size: 0.8em;
  min-width: 8em;
  background: #fff;
  color: #333;
  padding: 0.75em 1em;
  border-radius: 1em;
  border: 1px solid #eee;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  word-break: break-all;
  z-index: 1000;
  
  &.active {
    opacity: 1;
    visibility: visible;
  }
}

.pio-show {
  display: none;
  width: 3em;
  height: 3em;
  cursor: pointer;
  border-radius: 3em;
  border: 3px solid #fff;
  background: url('/poster-girl-assets/static/avatar.jpg') center/contain;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateX(0.5em);
  }
}

canvas {
  display: block;
  max-width: 100%;
  height: auto;
}

// 响应式设计
@media (max-width: 768px) {
  .poster-girl-container.hidden-mobile {
    display: none;
  }
}
</style>

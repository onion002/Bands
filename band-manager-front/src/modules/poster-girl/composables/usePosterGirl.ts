// 看板娘主要逻辑的组合式API
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { getCurrentConfig, saveConfig } from '../config/posterGirl'
import { live2dService } from '../services/live2dService'
import { modelManager } from '../services/modelManager'
import type { PosterGirlConfig, UsePosterGirlReturn } from '../types'

export function usePosterGirl(): UsePosterGirlReturn {
  // 响应式状态
  const isHidden = ref(false)
  const isDragging = ref(false)
  const showActions = ref(false)
  const showDialog = ref(false)
  const currentMessage = ref('')
  const live2dCanvas = ref<HTMLCanvasElement>()
  
  // 拖拽相关
  const dragStart = ref({ x: 0, y: 0 })
  const dragOffset = ref({ x: 0, y: 0 })
  
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
  
  // 导航方法
  const navigateToMusicBox = () => {
    window.location.href = '/music-box-demo'
  }
  
  const navigateToSettings = () => {
    window.location.href = '/poster-girl-settings'
  }
  
  const navigateToMusicTeacher = () => {
    window.location.href = '/music-teacher'
  }
  
  // 拖拽功能
  const startDrag = (event: MouseEvent | TouchEvent) => {
    if (pioConfig.value.mode !== 'draggable') return
    
    event.preventDefault()
    isDragging.value = true
    
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
    
    // 保存拖拽位置
    if (!pioConfig.value.dragPosition) {
      pioConfig.value.dragPosition = { x: 0, y: 0 }
    }
    pioConfig.value.dragPosition.x = newX
    pioConfig.value.dragPosition.y = newY
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
  
  return {
    // 状态
    isHidden,
    isDragging,
    showActions,
    showDialog,
    currentMessage,
    
    // 配置
    pioConfig,
    
    // 计算属性
    containerStyle,
    
    // 方法
    initLive2D,
    switchModel,
    showMessage,
    hidePosterGirl,
    showPosterGirl,
    handleTouch,
    
    // 导航方法
    navigateToMusicBox,
    navigateToSettings,
    navigateToMusicTeacher,
    
    // 拖拽相关
    startDrag,
    
    // 生命周期
    reloadPosterGirl,
    togglePosterGirl,
    togglePosition,
    
    // 内部引用
    live2dCanvas
  }
}

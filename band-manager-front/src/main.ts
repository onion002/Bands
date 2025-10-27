import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/authStore'

// 🎨 导入全局样式
import './assets/scss/global.scss'
import './assets/scss/components.scss'

// 🚀 导入动画系统
import { animationConfig, animationMonitor } from './utils/animationUtils'

// 🎭 延迟加载看板娘插件 - 只在需要时加载
const loadPosterGirlPlugin = async () => {
  const { posterGirlPlugin } = await import('@/modules/poster-girl')
  return posterGirlPlugin
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth()

// 🎨 初始化动画系统
if (process.env.NODE_ENV === 'development') {
  // 开发环境下启用性能监控
  animationMonitor.startMonitoring()

  // 输出动画配置信息
  console.log('🎨 动画系统已初始化')
  console.log('设备性能等级:', animationConfig.shouldUseComplexAnimations() ? 'High' : 'Medium/Low')
  console.log('减少动画偏好:', window.matchMedia('(prefers-reduced-motion: reduce)').matches)
}

// 🚀 延迟加载看板娘插件 - 提升初始加载性能
const initializePosterGirl = async () => {
  try {
    const posterGirlPlugin = await loadPosterGirlPlugin()
    
    app.use(posterGirlPlugin, {
      // 自动注册全局组件
      globalComponents: true,
      // 自动初始化
      autoInit: true,
      // 默认配置
      defaultConfig: {
        mode: 'draggable',  // 支持拖拽
        tips: true,         // 显示智能提示
        size: {
          width: 280,
          height: 250
        }
      }
    })
    
    console.log('🎭 看板娘插件已延迟加载')
  } catch (error) {
    console.warn('看板娘插件加载失败:', error)
  }
}

// 使用 requestIdleCallback 在浏览器空闲时加载看板娘
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    initializePosterGirl()
  }, { timeout: 5000 })
} else {
  // 降级方案：延迟加载
  setTimeout(initializePosterGirl, 2000)
}

app.mount('#app')
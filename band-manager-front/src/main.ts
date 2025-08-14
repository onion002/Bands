import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/authStore'

// 🎨 导入全局样式
import './assets/scss/global.scss'
import './assets/scss/components.scss'

// 🚀 导入性能监控
import { performanceMonitor } from './utils/performance'

// 📱 导入Service Worker管理器
import { swManager } from './utils/sw-register'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth()

// 🚀 异步初始化动画系统（仅在开发环境）
if (process.env.NODE_ENV === 'development') {
  import('./utils/animationUtils').then(({ animationConfig, animationMonitor }) => {
    // 启用性能监控
    animationMonitor.startMonitoring()

    // 输出动画配置信息
    console.log('🎨 动画系统已初始化')
    console.log('设备性能等级:', animationConfig.shouldUseComplexAnimations() ? 'High' : 'Medium/Low')
    console.log('减少动画偏好:', window.matchMedia('(prefers-reduced-motion: reduce)').matches)
  })
}

// 🎭 异步注册看板娘插件（减少初始包大小）
import('@/modules/poster-girl').then(({ posterGirlPlugin }) => {
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
})

// 📱 注册Service Worker（生产环境）
if (process.env.NODE_ENV === 'production') {
  swManager.register({
    scope: '/',
    updateViaCache: 'imports'
  }).then((registration) => {
    if (registration) {
      console.log('✅ Service Worker 注册成功')
      
      // 预缓存重要资源
      swManager.precache([
        '/',
        '/assets/css/global.css',
        '/assets/css/components.css'
      ])
    }
  }).catch((error) => {
    console.warn('Service Worker 注册失败:', error)
  })
}

// 📊 启动性能监控
performanceMonitor

app.mount('#app')
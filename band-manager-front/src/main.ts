import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/authStore'
import BackToTop from './components/BackToTop.vue'

// 🎨 导入全局样式
import './assets/scss/global.scss'
import './assets/scss/components.scss'

// 🚀 导入动画系统
import { animationConfig, animationMonitor } from './utils/animationUtils'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 全局注册组件
app.component('BackToTop', BackToTop)

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

app.mount('#app')
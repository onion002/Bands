/**
 * Service Worker 注册工具
 * 处理 Service Worker 的安装、更新和生命周期管理
 */

interface SWRegistrationOptions {
  scope?: string
  updateViaCache?: 'all' | 'imports' | 'none'
}

class ServiceWorkerManager {
  private registration: ServiceWorkerRegistration | null = null
  private updateFound = false

  constructor() {
    this.handleUpdate = this.handleUpdate.bind(this)
  }

  /**
   * 注册 Service Worker
   */
  async register(options: SWRegistrationOptions = {}): Promise<ServiceWorkerRegistration | null> {
    if (!('serviceWorker' in navigator)) {
      console.warn('⚠️ 浏览器不支持 Service Worker')
      return null
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: options.scope || '/',
        updateViaCache: options.updateViaCache || 'imports'
      })

      this.registration = registration
      console.log('✅ Service Worker 注册成功:', registration)

      // 监听更新
      this.setupUpdateListener(registration)

      // 监听消息
      this.setupMessageListener()

      return registration
    } catch (error) {
      console.error('❌ Service Worker 注册失败:', error)
      return null
    }
  }

  /**
   * 设置更新监听器
   */
  private setupUpdateListener(registration: ServiceWorkerRegistration) {
    // 监听 Service Worker 更新
    registration.addEventListener('updatefound', () => {
      console.log('🔄 发现 Service Worker 更新')
      this.updateFound = true

      const newWorker = registration.installing
      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            this.showUpdateNotification()
          }
        })
      }
    })

    // 监听 Service Worker 状态变化
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (this.updateFound) {
        console.log('✅ Service Worker 更新完成')
        this.updateFound = false
        // 可以在这里刷新页面或显示更新完成通知
        this.showUpdateCompleteNotification()
      }
    })
  }

  /**
   * 设置消息监听器
   */
  private setupMessageListener() {
    navigator.serviceWorker.addEventListener('message', (event) => {
      const { type, data } = event.data
      console.log('📨 收到 Service Worker 消息:', type, data)

      switch (type) {
        case 'CACHE_UPDATED':
          this.handleCacheUpdate(data)
          break
        case 'OFFLINE_MODE':
          this.handleOfflineMode(data)
          break
        default:
          console.log('未知消息类型:', type)
      }
    })
  }

  /**
   * 处理缓存更新
   */
  private handleCacheUpdate(data: any) {
    console.log('📦 缓存已更新:', data)
    // 可以在这里显示缓存更新通知
  }

  /**
   * 处理离线模式
   */
  private handleOfflineMode(data: any) {
    console.log('📡 进入离线模式:', data)
    // 可以在这里显示离线状态通知
  }

  /**
   * 显示更新通知
   */
  private showUpdateNotification() {
    // 创建更新通知
    const notification = document.createElement('div')
    notification.className = 'sw-update-notification'
    notification.innerHTML = `
      <div class="notification-content">
        <span>🔄 发现新版本，点击更新</span>
        <button class="update-btn">立即更新</button>
        <button class="dismiss-btn">稍后</button>
      </div>
    `

    // 添加样式
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #2196F3;
      color: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `

    // 更新按钮样式
    const updateBtn = notification.querySelector('.update-btn')
    if (updateBtn) {
      updateBtn.style.cssText = `
        background: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        margin-left: 12px;
        cursor: pointer;
        font-size: 14px;
      `
    }

    // 关闭按钮样式
    const dismissBtn = notification.querySelector('.dismiss-btn')
    if (dismissBtn) {
      dismissBtn.style.cssText = `
        background: transparent;
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        margin-left: 8px;
        cursor: pointer;
        font-size: 14px;
      `
    }

    // 添加事件监听器
    if (updateBtn) {
      updateBtn.addEventListener('click', () => {
        this.performUpdate()
        notification.remove()
      })
    }

    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => {
        notification.remove()
      })
    }

    // 显示通知
    document.body.appendChild(notification)

    // 5秒后自动隐藏
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove()
      }
    }, 5000)
  }

  /**
   * 显示更新完成通知
   */
  private showUpdateCompleteNotification() {
    const notification = document.createElement('div')
    notification.className = 'sw-update-complete'
    notification.innerHTML = `
      <div class="notification-content">
        <span>✅ 更新完成！页面将在3秒后刷新</span>
      </div>
    `

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `

    document.body.appendChild(notification)

    // 3秒后刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 3000)
  }

  /**
   * 执行更新
   */
  private async performUpdate() {
    if (this.registration && this.registration.waiting) {
      // 发送跳过等待消息
      this.registration.waiting.postMessage({ type: 'SKIP_WAITING' })
    }
  }

  /**
   * 检查更新
   */
  async checkForUpdate(): Promise<boolean> {
    if (!this.registration) {
      return false
    }

    try {
      await this.registration.update()
      return true
    } catch (error) {
      console.error('检查更新失败:', error)
      return false
    }
  }

  /**
   * 预缓存资源
   */
  async precache(urls: string[]): Promise<void> {
    if (!this.registration || !this.registration.active) {
      console.warn('Service Worker 未激活，无法预缓存')
      return
    }

    try {
      this.registration.active.postMessage({
        type: 'PRECACHE',
        data: { urls }
      })
      console.log('📦 预缓存请求已发送:', urls)
    } catch (error) {
      console.error('预缓存失败:', error)
    }
  }

  /**
   * 清理缓存
   */
  async cleanupCache(): Promise<void> {
    if (!this.registration || !this.registration.active) {
      console.warn('Service Worker 未激活，无法清理缓存')
      return
    }

    try {
      this.registration.active.postMessage({
        type: 'CLEANUP_CACHE'
      })
      console.log('🧹 缓存清理请求已发送')
    } catch (error) {
      console.error('清理缓存失败:', error)
    }
  }

  /**
   * 获取注册状态
   */
  getRegistration(): ServiceWorkerRegistration | null {
    return this.registration
  }

  /**
   * 检查是否支持 Service Worker
   */
  isSupported(): boolean {
    return 'serviceWorker' in navigator
  }

  /**
   * 检查是否已注册
   */
  isRegistered(): boolean {
    return this.registration !== null
  }
}

// 创建全局实例
export const swManager = new ServiceWorkerManager()

// 导出类型
export type { SWRegistrationOptions }

// 默认导出
export default swManager
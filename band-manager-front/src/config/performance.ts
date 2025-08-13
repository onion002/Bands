// 性能优化配置
export interface PerformanceConfig {
  // Live2D相关
  live2d: {
    maxTextureSize: number
    enableCache: boolean
    frameRateLimit: number
    enableLowPowerMode: boolean
  }
  
  // 图片优化
  images: {
    enableLazyLoading: boolean
    webpSupported: boolean
    maxImageSize: number
    compressionQuality: number
  }
  
  // 网络请求
  network: {
    timeout: number
    retryCount: number
    enableCache: boolean
    cacheTimeout: number
  }
  
  // 动画优化
  animation: {
    enableReducedMotion: boolean
    frameRateLimit: number
    enableGPUAcceleration: boolean
  }
}

// 检测浏览器性能等级
export function getDevicePerformance(): 'high' | 'medium' | 'low' {
  const cores = navigator.hardwareConcurrency || 4
  const memory = (navigator as any).deviceMemory || 4
  const connection = (navigator as any).connection
  const effectiveType = connection?.effectiveType || '4g'
  
  let score = 0
  
  // CPU评分
  if (cores >= 8) score += 3
  else if (cores >= 4) score += 2
  else score += 1
  
  // 内存评分
  if (memory >= 8) score += 3
  else if (memory >= 4) score += 2
  else score += 1
  
  // 网络评分
  if (effectiveType === '4g') score += 2
  else if (effectiveType === '3g') score += 1
  
  if (score >= 7) return 'high'
  if (score >= 4) return 'medium'
  return 'low'
}

// 检测WebP支持
function checkWebPSupport(): Promise<boolean> {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    canvas.width = 1
    canvas.height = 1
    const dataURL = canvas.toDataURL('image/webp')
    resolve(dataURL.indexOf('data:image/webp') === 0)
  })
}

// 根据设备性能生成配置
export async function generatePerformanceConfig(): Promise<PerformanceConfig> {
  const devicePerformance = getDevicePerformance()
  const webpSupported = await checkWebPSupport()
  
  const configs = {
    high: {
      live2d: {
        maxTextureSize: 2048,
        enableCache: true,
        frameRateLimit: 60,
        enableLowPowerMode: false
      },
      images: {
        enableLazyLoading: false,
        webpSupported,
        maxImageSize: 5 * 1024 * 1024, // 5MB
        compressionQuality: 0.9
      },
      network: {
        timeout: 10000,
        retryCount: 3,
        enableCache: true,
        cacheTimeout: 300000 // 5分钟
      },
      animation: {
        enableReducedMotion: false,
        frameRateLimit: 60,
        enableGPUAcceleration: true
      }
    },
    medium: {
      live2d: {
        maxTextureSize: 1024,
        enableCache: true,
        frameRateLimit: 30,
        enableLowPowerMode: false
      },
      images: {
        enableLazyLoading: true,
        webpSupported,
        maxImageSize: 3 * 1024 * 1024, // 3MB
        compressionQuality: 0.8
      },
      network: {
        timeout: 8000,
        retryCount: 2,
        enableCache: true,
        cacheTimeout: 180000 // 3分钟
      },
      animation: {
        enableReducedMotion: false,
        frameRateLimit: 30,
        enableGPUAcceleration: true
      }
    },
    low: {
      live2d: {
        maxTextureSize: 512,
        enableCache: true,
        frameRateLimit: 24,
        enableLowPowerMode: true
      },
      images: {
        enableLazyLoading: true,
        webpSupported,
        maxImageSize: 1 * 1024 * 1024, // 1MB
        compressionQuality: 0.7
      },
      network: {
        timeout: 5000,
        retryCount: 1,
        enableCache: true,
        cacheTimeout: 60000 // 1分钟
      },
      animation: {
        enableReducedMotion: true,
        frameRateLimit: 24,
        enableGPUAcceleration: false
      }
    }
  }
  
  return configs[devicePerformance]
}

// 性能监控器
export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private frameCount = 0
  private lastTime = 0
  private fps = 60
  private isMonitoring = false
  private memoryUsage = 0
  
  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }
  
  startMonitoring(): void {
    if (this.isMonitoring) return
    
    this.isMonitoring = true
    this.lastTime = performance.now()
    this.frameCount = 0
    
    const monitor = (currentTime: number) => {
      if (!this.isMonitoring) return
      
      this.frameCount++
      
      if (currentTime - this.lastTime >= 1000) {
        this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime))
        this.frameCount = 0
        this.lastTime = currentTime
        
        // 检测内存使用
        if ('memory' in performance) {
          this.memoryUsage = (performance as any).memory.usedJSHeapSize / 1024 / 1024
        }
        
        // 如果FPS过低或内存使用过高，发出警告
        if (this.fps < 24) {
          console.warn(`性能警告: FPS降至 ${this.fps}`)
          this.onPerformanceIssue('low_fps', { fps: this.fps })
        }
        
        if (this.memoryUsage > 100) { // 100MB
          console.warn(`内存警告: 使用量 ${this.memoryUsage.toFixed(2)}MB`)
          this.onPerformanceIssue('high_memory', { memory: this.memoryUsage })
        }
      }
      
      requestAnimationFrame(monitor)
    }
    
    requestAnimationFrame(monitor)
  }
  
  stopMonitoring(): void {
    this.isMonitoring = false
  }
  
  getCurrentFPS(): number {
    return this.fps
  }
  
  getMemoryUsage(): number {
    return this.memoryUsage
  }
  
  // 性能问题回调
  private onPerformanceIssue(type: 'low_fps' | 'high_memory', data: any): void {
    // 可以在这里实现性能优化策略
    if (type === 'low_fps') {
      // 降低帧率限制或禁用某些动画
    } else if (type === 'high_memory') {
      // 清理缓存或减少纹理质量
    }
  }
}

// 导出单例
export const performanceMonitor = PerformanceMonitor.getInstance()

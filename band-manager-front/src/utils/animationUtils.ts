// 🎨 动画性能优化工具
// 提供动画性能监控和优化功能

/**
 * 检测用户是否偏好减少动画
 */
export const prefersReducedMotion = (): boolean => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * 检测设备性能等级
 */
export const getDevicePerformance = (): 'high' | 'medium' | 'low' => {
  // 检测硬件并发数
  const cores = navigator.hardwareConcurrency || 4
  
  // 检测内存（如果可用）
  const memory = (navigator as any).deviceMemory || 4
  
  // 检测连接速度
  const connection = (navigator as any).connection
  const effectiveType = connection?.effectiveType || '4g'
  
  // 综合评分
  let score = 0
  
  // CPU 评分
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

/**
 * 动画配置管理器
 */
export class AnimationConfig {
  private static instance: AnimationConfig
  private performance: 'high' | 'medium' | 'low'
  private reducedMotion: boolean

  private constructor() {
    this.performance = getDevicePerformance()
    this.reducedMotion = prefersReducedMotion()
    
    // 监听偏好设置变化
    window.matchMedia('(prefers-reduced-motion: reduce)')
      .addEventListener('change', (e) => {
        this.reducedMotion = e.matches
      })
  }

  static getInstance(): AnimationConfig {
    if (!AnimationConfig.instance) {
      AnimationConfig.instance = new AnimationConfig()
    }
    return AnimationConfig.instance
  }

  /**
   * 获取动画持续时间
   */
  getDuration(baseDuration: number): number {
    if (this.reducedMotion) return 0.01
    
    switch (this.performance) {
      case 'high':
        return baseDuration
      case 'medium':
        return baseDuration * 0.8
      case 'low':
        return baseDuration * 0.6
      default:
        return baseDuration
    }
  }

  /**
   * 获取动画延迟
   */
  getDelay(baseDelay: number): number {
    if (this.reducedMotion) return 0
    
    switch (this.performance) {
      case 'high':
        return baseDelay
      case 'medium':
        return baseDelay * 0.7
      case 'low':
        return baseDelay * 0.5
      default:
        return baseDelay
    }
  }

  /**
   * 是否启用复杂动画
   */
  shouldUseComplexAnimations(): boolean {
    return !this.reducedMotion && this.performance === 'high'
  }

  /**
   * 是否启用粒子效果
   */
  shouldUseParticleEffects(): boolean {
    return !this.reducedMotion && this.performance !== 'low'
  }

  /**
   * 获取动画缓动函数
   */
  getEasing(): string {
    if (this.reducedMotion) return 'linear'
    
    switch (this.performance) {
      case 'high':
        return 'cubic-bezier(0.4, 0, 0.2, 1)'
      case 'medium':
        return 'ease-out'
      case 'low':
        return 'ease'
      default:
        return 'ease-out'
    }
  }
}

/**
 * 动画性能监控器
 */
export class AnimationMonitor {
  private frameCount = 0
  private lastTime = 0
  private fps = 60
  private isMonitoring = false

  /**
   * 开始监控 FPS
   */
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
        
        // 如果 FPS 过低，发出警告
        if (this.fps < 30) {
          console.warn(`动画性能警告: FPS 降至 ${this.fps}`)
        }
      }
      
      requestAnimationFrame(monitor)
    }
    
    requestAnimationFrame(monitor)
  }

  /**
   * 停止监控
   */
  stopMonitoring(): void {
    this.isMonitoring = false
  }

  /**
   * 获取当前 FPS
   */
  getCurrentFPS(): number {
    return this.fps
  }
}

/**
 * 动画优化工具函数
 */
export const animationUtils = {
  /**
   * 创建优化的 CSS 动画
   */
  createOptimizedAnimation(
    element: HTMLElement,
    keyframes: Keyframe[],
    options: KeyframeAnimationOptions
  ): Animation {
    const config = AnimationConfig.getInstance()
    
    // 调整动画选项
    const optimizedOptions = {
      ...options,
      duration: config.getDuration(options.duration as number || 300),
      delay: config.getDelay(options.delay as number || 0),
      easing: config.getEasing()
    }
    
    return element.animate(keyframes, optimizedOptions)
  },

  /**
   * 批量应用 will-change 属性
   */
  applyWillChange(elements: HTMLElement[], properties: string[]): void {
    const propertyString = properties.join(', ')
    elements.forEach(el => {
      el.style.willChange = propertyString
    })
  },

  /**
   * 清理 will-change 属性
   */
  clearWillChange(elements: HTMLElement[]): void {
    elements.forEach(el => {
      el.style.willChange = 'auto'
    })
  },

  /**
   * 创建交错动画
   */
  createStaggeredAnimation(
    elements: HTMLElement[],
    keyframes: Keyframe[],
    baseOptions: KeyframeAnimationOptions,
    staggerDelay = 100
  ): Animation[] {
    const config = AnimationConfig.getInstance()
    
    return elements.map((element, index) => {
      const options = {
        ...baseOptions,
        duration: config.getDuration(baseOptions.duration as number || 300),
        delay: config.getDelay((baseOptions.delay as number || 0) + (index * staggerDelay)),
        easing: config.getEasing()
      }
      
      return element.animate(keyframes, options)
    })
  },

  /**
   * 检测动画支持
   */
  supportsAnimation(): boolean {
    return 'animate' in HTMLElement.prototype
  },

  /**
   * 检测 CSS 动画支持
   */
  supportsCSSAnimation(): boolean {
    const testElement = document.createElement('div')
    return 'animationName' in testElement.style
  },

  /**
   * 检测 transform3d 支持
   */
  supportsTransform3D(): boolean {
    const testElement = document.createElement('div')
    testElement.style.transform = 'translate3d(0,0,0)'
    return testElement.style.transform !== ''
  }
}

/**
 * 动画队列管理器
 */
export class AnimationQueue {
  private queue: Array<() => Promise<void>> = []
  private isRunning = false

  /**
   * 添加动画到队列
   */
  add(animationFn: () => Promise<void>): void {
    this.queue.push(animationFn)
    if (!this.isRunning) {
      this.run()
    }
  }

  /**
   * 运行队列中的动画
   */
  private async run(): Promise<void> {
    if (this.queue.length === 0) {
      this.isRunning = false
      return
    }

    this.isRunning = true
    const animationFn = this.queue.shift()!
    
    try {
      await animationFn()
    } catch (error) {
      console.error('动画执行错误:', error)
    }
    
    // 继续执行下一个动画
    this.run()
  }

  /**
   * 清空队列
   */
  clear(): void {
    this.queue = []
    this.isRunning = false
  }
}

// 导出单例实例
export const animationConfig = AnimationConfig.getInstance()
export const animationMonitor = new AnimationMonitor()
export const animationQueue = new AnimationQueue()

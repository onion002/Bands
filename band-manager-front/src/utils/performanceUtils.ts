// 🚀 性能优化工具函数
// 提供懒加载、性能监控、资源预加载等功能

// =============================================================================
// 懒加载工具
// =============================================================================

/**
 * 智能懒加载组件
 * @param importFn 导入函数
 * @param fallback 加载中的占位符
 * @param errorFallback 错误时的占位符
 */
export function createLazyComponent<T>(
  importFn: () => Promise<T>,
  fallback?: any,
  errorFallback?: any
) {
  return defineAsyncComponent({
    loader: importFn,
    loadingComponent: fallback,
    errorComponent: errorFallback,
    delay: 200, // 延迟显示加载状态
    timeout: 10000, // 10秒超时
    onError(error, retry, fail, attempts) {
      if (attempts <= 3) {
        // 重试3次
        retry()
      } else {
        console.error('组件加载失败:', error)
        fail()
      }
    }
  })
}

/**
 * 图片懒加载
 * @param img 图片元素
 * @param src 图片源
 */
export function lazyLoadImage(img: HTMLImageElement, src: string) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        img.src = src
        img.classList.add('loaded')
        observer.unobserve(img)
      }
    })
  })
  
  observer.observe(img)
}

/**
 * 批量图片懒加载
 * @param selector 图片选择器
 */
export function lazyLoadImages(selector: string = 'img[data-src]') {
  const images = document.querySelectorAll<HTMLImageElement>(selector)
  
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement
        const src = img.dataset.src
        if (src) {
          img.src = src
          img.classList.add('loaded')
          imageObserver.unobserve(img)
        }
      }
    })
  })
  
  images.forEach(img => imageObserver.observe(img))
}

// =============================================================================
// 性能监控
// =============================================================================

/**
 * 性能监控器
 */
export class PerformanceMonitor {
  private metrics: Map<string, number> = new Map()
  private observers: Map<string, PerformanceObserver> = new Map()

  constructor() {
    this.initObservers()
  }

  /**
   * 初始化性能观察器
   */
  private initObservers() {
    // 监控长任务
    if ('PerformanceObserver' in window) {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.duration > 50) {
              console.warn('检测到长任务:', entry)
            }
          })
        })
        longTaskObserver.observe({ entryTypes: ['longtask'] })
        this.observers.set('longtask', longTaskObserver)
      } catch (e) {
        console.warn('长任务监控不可用:', e)
      }

      // 监控布局偏移
      try {
        const layoutShiftObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry: any) => {
            if (entry.value > 0.1) {
              console.warn('检测到布局偏移:', entry)
            }
          })
        })
        layoutShiftObserver.observe({ entryTypes: ['layout-shift'] })
        this.observers.set('layout-shift', layoutShiftObserver)
      } catch (e) {
        console.warn('布局偏移监控不可用:', e)
      }
    }
  }

  /**
   * 测量函数执行时间
   * @param name 测量名称
   * @param fn 要测量的函数
   */
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now()
    try {
      const result = await fn()
      const duration = performance.now() - start
      this.metrics.set(name, duration)
      
      if (duration > 100) {
        console.warn(`慢操作警告: ${name} 耗时 ${duration.toFixed(2)}ms`)
      }
      
      return result
    } catch (error) {
      const duration = performance.now() - start
      this.metrics.set(`${name}_error`, duration)
      throw error
    }
  }

  /**
   * 测量同步函数执行时间
   * @param name 测量名称
   * @param fn 要测量的函数
   */
  measure<T>(name: string, fn: () => T): T {
    const start = performance.now()
    try {
      const result = fn()
      const duration = performance.now() - start
      this.metrics.set(name, duration)
      
      if (duration > 50) {
        console.warn(`慢操作警告: ${name} 耗时 ${duration.toFixed(2)}ms`)
      }
      
      return result
    } catch (error) {
      const duration = performance.now() - start
      this.metrics.set(`${name}_error`, duration)
      throw error
    }
  }

  /**
   * 获取性能指标
   */
  getMetrics() {
    return Object.fromEntries(this.metrics)
  }

  /**
   * 清理资源
   */
  destroy() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
    this.metrics.clear()
  }
}

// =============================================================================
// 资源预加载
// =============================================================================

/**
 * 预加载关键资源
 * @param urls 要预加载的URL数组
 */
export function preloadResources(urls: string[]) {
  urls.forEach(url => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = url
    
    if (url.endsWith('.css')) {
      link.as = 'style'
    } else if (url.endsWith('.js')) {
      link.as = 'script'
    } else if (url.match(/\.(png|jpg|jpeg|gif|webp|svg)$/)) {
      link.as = 'image'
    }
    
    document.head.appendChild(link)
  })
}

/**
 * 预加载字体
 * @param fontFamily 字体族
 * @param weights 字重数组
 */
export function preloadFonts(fontFamily: string, weights: number[]) {
  weights.forEach(weight => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = `https://fonts.googleapis.com/css2?family=${fontFamily}:wght@${weight}&display=swap`
    link.as = 'style'
    document.head.appendChild(link)
  })
}

// =============================================================================
// 代码分割优化
// =============================================================================

/**
 * 智能代码分割
 * @param importFn 导入函数
 * @param priority 优先级 (high, medium, low)
 */
export function smartCodeSplit<T>(
  importFn: () => Promise<T>,
  priority: 'high' | 'medium' | 'low' = 'medium'
): () => Promise<T> {
  return () => {
    const loadPromise = importFn()
    
    // 根据优先级调整加载策略
    switch (priority) {
      case 'high':
        // 高优先级：立即加载
        return loadPromise
      case 'medium':
        // 中优先级：在空闲时加载
        if ('requestIdleCallback' in window) {
          return new Promise((resolve) => {
            requestIdleCallback(() => {
              loadPromise.then(resolve)
            }, { timeout: 1000 })
          })
        }
        return loadPromise
      case 'low':
        // 低优先级：延迟加载
        return new Promise((resolve) => {
          setTimeout(() => {
            loadPromise.then(resolve)
          }, 2000)
        })
      default:
        return loadPromise
    }
  }
}

// =============================================================================
// 内存管理
// =============================================================================

/**
 * 内存使用监控
 */
export function getMemoryUsage() {
  if ('memory' in performance) {
    const memory = (performance as any).memory
    return {
      used: Math.round(memory.usedJSHeapSize / 1048576 * 100) / 100, // MB
      total: Math.round(memory.totalJSHeapSize / 1048576 * 100) / 100, // MB
      limit: Math.round(memory.jsHeapSizeLimit / 1048576 * 100) / 100 // MB
    }
  }
  return null
}

/**
 * 清理内存
 */
export function cleanupMemory() {
  // 清理事件监听器
  const cleanupEventListeners = () => {
    // 这里可以添加清理特定事件监听器的逻辑
  }
  
  // 清理定时器
  const cleanupTimers = () => {
    // 这里可以添加清理定时器的逻辑
  }
  
  // 清理闭包引用
  const cleanupClosures = () => {
    // 这里可以添加清理闭包引用的逻辑
  }
  
  cleanupEventListeners()
  cleanupTimers()
  cleanupClosures()
  
  // 强制垃圾回收（如果可用）
  if ('gc' in window) {
    try {
      (window as any).gc()
    } catch (e) {
      // 忽略错误
    }
  }
}

// =============================================================================
// 网络优化
// =============================================================================

/**
 * 检测网络状态
 */
export function getNetworkInfo() {
  if ('connection' in navigator) {
    const connection = (navigator as any).connection
    return {
      effectiveType: connection.effectiveType, // 4g, 3g, 2g, slow-2g
      downlink: connection.downlink, // Mbps
      rtt: connection.rtt, // ms
      saveData: connection.saveData // 是否开启省流模式
    }
  }
  return null
}

/**
 * 根据网络状态调整加载策略
 */
export function adjustLoadingStrategy() {
  const networkInfo = getNetworkInfo()
  
  if (networkInfo) {
    if (networkInfo.effectiveType === 'slow-2g' || networkInfo.effectiveType === '2g') {
      // 慢速网络：减少并发请求，增加延迟
      return {
        maxConcurrent: 2,
        delay: 1000,
        timeout: 30000
      }
    } else if (networkInfo.effectiveType === '3g') {
      // 中速网络：中等并发
      return {
        maxConcurrent: 4,
        delay: 500,
        timeout: 15000
      }
    }
  }
  
  // 快速网络：默认设置
  return {
    maxConcurrent: 6,
    delay: 100,
    timeout: 10000
  }
}

// =============================================================================
// 导出
// =============================================================================

export const performanceMonitor = new PerformanceMonitor()

// 默认导出
export default {
  createLazyComponent,
  lazyLoadImage,
  lazyLoadImages,
  performanceMonitor,
  preloadResources,
  preloadFonts,
  smartCodeSplit,
  getMemoryUsage,
  cleanupMemory,
  getNetworkInfo,
  adjustLoadingStrategy
}
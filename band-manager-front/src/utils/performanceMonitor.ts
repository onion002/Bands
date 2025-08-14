/**
 * 性能监控工具
 * 用于监控应用性能、bundle加载时间和识别性能瓶颈
 */

export interface PerformanceMetrics {
  bundleLoadTime: number
  componentRenderTime: number
  apiResponseTime: number
  memoryUsage: number
  fps: number
}

export interface BundleMetrics {
  name: string
  size: number
  loadTime: number
  gzipSize: number
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = []
  private bundleMetrics: BundleMetrics[] = []
  private observers: PerformanceObserver[] = []

  constructor() {
    this.initObservers()
  }

  /**
   * 初始化性能观察器
   */
  private initObservers() {
    // 监控资源加载
    if ('PerformanceObserver' in window) {
      const resourceObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'resource') {
            this.trackResourceLoad(entry as PerformanceResourceTiming)
          }
        })
      })
      
      try {
        resourceObserver.observe({ entryTypes: ['resource'] })
        this.observers.push(resourceObserver)
      } catch (e) {
        console.warn('Resource timing not supported')
      }

      // 监控长任务
      const longTaskObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.duration > 50) { // 50ms以上的任务
            console.warn('Long task detected:', entry.duration, 'ms')
          }
        })
      })

      try {
        longTaskObserver.observe({ entryTypes: ['longtask'] })
        this.observers.push(longTaskObserver)
      } catch (e) {
        console.warn('Long task timing not supported')
      }
    }
  }

  /**
   * 跟踪资源加载
   */
  private trackResourceLoad(entry: PerformanceResourceTiming) {
    const name = entry.name
    const loadTime = entry.responseEnd - entry.startTime
    const size = entry.transferSize || 0

    // 只跟踪JS和CSS文件
    if (name.endsWith('.js') || name.endsWith('.css')) {
      this.bundleMetrics.push({
        name: name.split('/').pop() || name,
        size,
        loadTime,
        gzipSize: Math.round(size * 0.3) // 估算gzip大小
      })
    }
  }

  /**
   * 开始监控组件渲染时间
   */
  startComponentTimer(componentName: string): () => void {
    const startTime = performance.now()
    
    return () => {
      const renderTime = performance.now() - startTime
      this.metrics.push({
        bundleLoadTime: 0,
        componentRenderTime: renderTime,
        apiResponseTime: 0,
        memoryUsage: this.getMemoryUsage(),
        fps: this.getFPS()
      })

      if (renderTime > 16) { // 超过16ms (60fps)
        console.warn(`Component ${componentName} took ${renderTime.toFixed(2)}ms to render`)
      }
    }
  }

  /**
   * 监控API响应时间
   */
  trackApiCall<T>(apiCall: Promise<T>, endpoint: string): Promise<T> {
    const startTime = performance.now()
    
    return apiCall.finally(() => {
      const responseTime = performance.now() - startTime
      this.metrics.push({
        bundleLoadTime: 0,
        componentRenderTime: 0,
        apiResponseTime: responseTime,
        memoryUsage: this.getMemoryUsage(),
        fps: this.getFPS()
      })

      if (responseTime > 1000) { // 超过1秒
        console.warn(`API call to ${endpoint} took ${responseTime.toFixed(2)}ms`)
      }
    })
  }

  /**
   * 获取内存使用情况
   */
  private getMemoryUsage(): number {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return memory.usedJSHeapSize / 1024 / 1024 // MB
    }
    return 0
  }

  /**
   * 获取FPS
   */
  private getFPS(): number {
    // 简单的FPS计算
    return 60 // 默认值，实际实现需要更复杂的计算
  }

  /**
   * 获取性能报告
   */
  getPerformanceReport(): {
    metrics: PerformanceMetrics[]
    bundleMetrics: BundleMetrics[]
    summary: {
      avgRenderTime: number
      avgApiResponseTime: number
      totalBundleSize: number
      slowestBundle: BundleMetrics | null
    }
  } {
    const avgRenderTime = this.metrics.length > 0 
      ? this.metrics.reduce((sum, m) => sum + m.componentRenderTime, 0) / this.metrics.length 
      : 0

    const avgApiResponseTime = this.metrics.length > 0
      ? this.metrics.reduce((sum, m) => sum + m.apiResponseTime, 0) / this.metrics.length
      : 0

    const totalBundleSize = this.bundleMetrics.reduce((sum, b) => sum + b.size, 0)
    const slowestBundle = this.bundleMetrics.reduce((slowest, current) => 
      current.loadTime > (slowest?.loadTime || 0) ? current : slowest, null as BundleMetrics | null)

    return {
      metrics: this.metrics,
      bundleMetrics: this.bundleMetrics,
      summary: {
        avgRenderTime,
        avgApiResponseTime,
        totalBundleSize,
        slowestBundle
      }
    }
  }

  /**
   * 清理监控器
   */
  destroy() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }
}

// 创建全局实例
export const performanceMonitor = new PerformanceMonitor()

// 开发环境下的性能监控
if (process.env.NODE_ENV === 'development') {
  // 定期输出性能报告
  setInterval(() => {
    const report = performanceMonitor.getPerformanceReport()
    if (report.bundleMetrics.length > 0) {
      console.group('🚀 Performance Report')
      console.log('Bundle Metrics:', report.bundleMetrics)
      console.log('Performance Summary:', report.summary)
      console.groupEnd()
    }
  }, 30000) // 每30秒输出一次
}
/**
 * 性能监控工具
 * 用于监控应用性能指标，包括加载时间、渲染时间、内存使用等
 */

export interface PerformanceMetrics {
  // 页面加载指标
  pageLoadTime: number
  domContentLoaded: number
  firstContentfulPaint?: number
  largestContentfulPaint?: number
  
  // 组件渲染指标
  componentRenderTimes: Map<string, number>
  
  // 内存使用指标
  memoryUsage?: {
    usedJSHeapSize: number
    totalJSHeapSize: number
    jsHeapSizeLimit: number
  }
  
  // 网络请求指标
  networkRequests: {
    total: number
    failed: number
    averageResponseTime: number
  }
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics
  private startTime: number
  private componentTimers: Map<string, number> = new Map()

  constructor() {
    this.startTime = performance.now()
    this.metrics = {
      pageLoadTime: 0,
      domContentLoaded: 0,
      componentRenderTimes: new Map(),
      networkRequests: {
        total: 0,
        failed: 0,
        averageResponseTime: 0
      }
    }
    
    this.init()
  }

  private init() {
    // 监听页面加载事件
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.metrics.domContentLoaded = performance.now() - this.startTime
      })
    } else {
      this.metrics.domContentLoaded = performance.now() - this.startTime
    }

    // 监听页面完全加载
    window.addEventListener('load', () => {
      this.metrics.pageLoadTime = performance.now() - this.startTime
      this.reportMetrics()
    })

    // 监听性能指标
    this.observePerformanceMetrics()
    
    // 监听网络请求
    this.observeNetworkRequests()
  }

  private observePerformanceMetrics() {
    // 监听 First Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const paintObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              this.metrics.firstContentfulPaint = entry.startTime
            }
          }
        })
        paintObserver.observe({ entryTypes: ['paint'] })

        // 监听 Largest Contentful Paint
        const lcpObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.metrics.largestContentfulPaint = entry.startTime
          }
        })
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
      } catch (error) {
        console.warn('性能指标监听失败:', error)
      }
    }
  }

  private observeNetworkRequests() {
    // 使用 Performance API 监听网络请求
    if ('PerformanceObserver' in window) {
      try {
        const resourceObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'resource') {
              const resourceEntry = entry as PerformanceResourceTiming
              this.metrics.networkRequests.total++
              
              if (resourceEntry.responseEnd > 0) {
                const responseTime = resourceEntry.responseEnd - resourceEntry.requestStart
                this.updateAverageResponseTime(responseTime)
              }
            }
          }
        })
        resourceObserver.observe({ entryTypes: ['resource'] })
      } catch (error) {
        console.warn('网络请求监听失败:', error)
      }
    }
  }

  private updateAverageResponseTime(newTime: number) {
    const current = this.metrics.networkRequests.averageResponseTime
    const total = this.metrics.networkRequests.total
    this.metrics.networkRequests.averageResponseTime = (current * (total - 1) + newTime) / total
  }

  // 开始组件渲染计时
  startComponentTimer(componentName: string) {
    this.componentTimers.set(componentName, performance.now())
  }

  // 结束组件渲染计时
  endComponentTimer(componentName: string) {
    const startTime = this.componentTimers.get(componentName)
    if (startTime) {
      const renderTime = performance.now() - startTime
      this.metrics.componentRenderTimes.set(componentName, renderTime)
      this.componentTimers.delete(componentName)
    }
  }

  // 获取内存使用情况
  getMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      this.metrics.memoryUsage = {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit
      }
    }
    return this.metrics.memoryUsage
  }

  // 报告性能指标
  reportMetrics() {
    const memoryUsage = this.getMemoryUsage()
    
    console.group('📊 性能指标报告')
    console.log('页面加载时间:', this.metrics.pageLoadTime.toFixed(2), 'ms')
    console.log('DOM内容加载时间:', this.metrics.domContentLoaded.toFixed(2), 'ms')
    
    if (this.metrics.firstContentfulPaint) {
      console.log('首次内容绘制:', this.metrics.firstContentfulPaint.toFixed(2), 'ms')
    }
    
    if (this.metrics.largestContentfulPaint) {
      console.log('最大内容绘制:', this.metrics.largestContentfulPaint.toFixed(2), 'ms')
    }
    
    console.log('网络请求总数:', this.metrics.networkRequests.total)
    console.log('平均响应时间:', this.metrics.networkRequests.averageResponseTime.toFixed(2), 'ms')
    
    if (memoryUsage) {
      console.log('内存使用:', {
        used: `${(memoryUsage.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
        total: `${(memoryUsage.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
        limit: `${(memoryUsage.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`
      })
    }
    
    console.log('组件渲染时间:')
    this.metrics.componentRenderTimes.forEach((time, component) => {
      console.log(`  ${component}: ${time.toFixed(2)} ms`)
    })
    
    console.groupEnd()
    
    // 发送到分析服务（如果配置了的话）
    this.sendToAnalytics()
  }

  private sendToAnalytics() {
    // 这里可以集成 Google Analytics、Mixpanel 等分析服务
    // 或者发送到自定义的分析端点
    if (process.env.NODE_ENV === 'production') {
      // 生产环境发送性能数据
      try {
        navigator.sendBeacon?.('/api/analytics/performance', JSON.stringify(this.metrics))
      } catch (error) {
        console.warn('发送性能数据失败:', error)
      }
    }
  }

  // 获取性能指标
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics }
  }

  // 重置指标
  reset() {
    this.startTime = performance.now()
    this.metrics = {
      pageLoadTime: 0,
      domContentLoaded: 0,
      componentRenderTimes: new Map(),
      networkRequests: {
        total: 0,
        failed: 0,
        averageResponseTime: 0
      }
    }
  }
}

// 创建全局性能监控实例
export const performanceMonitor = new PerformanceMonitor()

// Vue 组件性能监控指令
export const performanceDirective = {
  mounted(el: HTMLElement, binding: any) {
    const componentName = binding.value || 'Unknown'
    performanceMonitor.startComponentTimer(componentName)
    
    // 使用 MutationObserver 监听 DOM 变化完成
    const observer = new MutationObserver(() => {
      // 延迟一点时间确保渲染完成
      setTimeout(() => {
        performanceMonitor.endComponentTimer(componentName)
        observer.disconnect()
      }, 0)
    })
    
    observer.observe(el, { childList: true, subtree: true })
  }
}

// 导出性能监控工具
export default performanceMonitor
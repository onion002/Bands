// 增强的错误处理和重试机制
export interface RetryOptions {
  maxAttempts?: number
  delay?: number
  backoff?: 'linear' | 'exponential'
  shouldRetry?: (error: any, attempt: number) => boolean
}

export interface ErrorContext {
  component?: string
  action?: string
  userId?: string
  timestamp?: number
  userAgent?: string
  url?: string
  stack?: string
}

// 错误类型定义
export enum ErrorType {
  NETWORK = 'network',
  VALIDATION = 'validation',
  PERMISSION = 'permission',
  LIVE2D = 'live2d',
  UPLOAD = 'upload',
  UNKNOWN = 'unknown'
}

export interface AppError {
  type: ErrorType
  message: string
  code?: string | number
  context?: ErrorContext
  originalError?: any
  recoverable?: boolean
  userMessage?: string
}

// 错误处理器类
export class ErrorHandler {
  private static instance: ErrorHandler
  private errorQueue: AppError[] = []
  private maxQueueSize = 100
  
  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler()
    }
    return ErrorHandler.instance
  }
  
  // 创建标准化错误
  createError(
    type: ErrorType,
    message: string,
    context?: Partial<ErrorContext>,
    originalError?: any
  ): AppError {
    const error: AppError = {
      type,
      message,
      context: {
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        ...context
      },
      originalError,
      recoverable: this.isRecoverable(type, originalError)
    }
    
    // 生成用户友好的错误消息
    error.userMessage = this.generateUserMessage(error)
    
    return error
  }
  
  // 处理错误
  handleError(error: AppError): void {
    // 添加到错误队列
    this.addToQueue(error)
    
    // 根据错误类型进行不同处理
    switch (error.type) {
      case ErrorType.NETWORK:
        this.handleNetworkError(error)
        break
      case ErrorType.LIVE2D:
        this.handleLive2DError(error)
        break
      case ErrorType.UPLOAD:
        this.handleUploadError(error)
        break
      default:
        this.handleGenericError(error)
    }
    
    // 开发环境下输出详细错误信息
    if (import.meta.env.DEV) {
      console.group(`🚨 ${error.type.toUpperCase()} Error`)
      console.error('Message:', error.message)
      console.error('Context:', error.context)
      if (error.originalError) {
        console.error('Original Error:', error.originalError)
      }
      console.groupEnd()
    }
  }
  
  // 网络错误处理
  private handleNetworkError(error: AppError): void {
    // 检查网络连接状态
    if (!navigator.onLine) {
      this.showUserNotification('网络连接已断开，请检查网络设置', 'warning')
      return
    }
    
    // 根据HTTP状态码处理
    const status = error.originalError?.response?.status
    if (status === 401) {
      this.handleAuthError()
    } else if (status === 403) {
      this.showUserNotification('没有权限执行此操作', 'error')
    } else if (status >= 500) {
      this.showUserNotification('服务器暂时不可用，请稍后重试', 'error')
    } else {
      this.showUserNotification(error.userMessage || '网络请求失败', 'error')
    }
  }
  
  // Live2D错误处理
  private handleLive2DError(error: AppError): void {
    console.warn('Live2D错误:', error.message)
    
    // 尝试重新初始化Live2D
    if (error.recoverable) {
      setTimeout(() => {
        // 触发重新初始化事件
        window.dispatchEvent(new CustomEvent('live2d:reinit'))
      }, 2000)
    }
  }
  
  // 上传错误处理
  private handleUploadError(error: AppError): void {
    let message = '文件上传失败'
    
    if (error.message.includes('size')) {
      message = '文件大小超出限制'
    } else if (error.message.includes('type')) {
      message = '不支持的文件类型'
    } else if (error.message.includes('network')) {
      message = '网络连接问题，请稍后重试'
    }
    
    this.showUserNotification(message, 'error')
  }
  
  // 通用错误处理
  private handleGenericError(error: AppError): void {
    this.showUserNotification(error.userMessage || '操作失败', 'error')
  }
  
  // 认证错误处理
  private handleAuthError(): void {
    // 清除认证信息
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
    
    this.showUserNotification('登录已过期，请重新登录', 'warning')
    
    // 跳转到登录页
    setTimeout(() => {
      window.location.href = '/auth/login'
    }, 2000)
  }
  
  // 显示用户通知
  private showUserNotification(message: string, type: 'info' | 'warning' | 'error' | 'success'): void {
    // 这里可以集成到您的通知系统
    // 暂时使用console输出
    console.log(`[${type.toUpperCase()}] ${message}`)
    
    // 如果有看板娘，可以让她说话
    window.dispatchEvent(new CustomEvent('posterGirl:message', {
      detail: { message, type }
    }))
  }
  
  // 判断错误是否可恢复
  private isRecoverable(type: ErrorType, originalError?: any): boolean {
    switch (type) {
      case ErrorType.NETWORK:
        const status = originalError?.response?.status
        return status !== 401 && status !== 403
      case ErrorType.LIVE2D:
        return true
      case ErrorType.UPLOAD:
        return !originalError?.message?.includes('size')
      default:
        return false
    }
  }
  
  // 生成用户友好的错误消息
  private generateUserMessage(error: AppError): string {
    const messages = {
      [ErrorType.NETWORK]: '网络连接异常，请检查网络设置',
      [ErrorType.VALIDATION]: '输入信息有误，请检查后重试',
      [ErrorType.PERMISSION]: '没有权限执行此操作',
      [ErrorType.LIVE2D]: '看板娘加载失败，正在重试...',
      [ErrorType.UPLOAD]: '文件上传失败，请重试',
      [ErrorType.UNKNOWN]: '出现未知错误，请重试'
    }
    
    return messages[error.type] || messages[ErrorType.UNKNOWN]
  }
  
  // 添加到错误队列
  private addToQueue(error: AppError): void {
    this.errorQueue.push(error)
    
    // 限制队列大小
    if (this.errorQueue.length > this.maxQueueSize) {
      this.errorQueue.shift()
    }
  }
  
  // 获取错误统计
  getErrorStats(): { [key in ErrorType]: number } {
    const stats = Object.values(ErrorType).reduce((acc, type) => {
      acc[type] = 0
      return acc
    }, {} as { [key in ErrorType]: number })
    
    this.errorQueue.forEach(error => {
      stats[error.type]++
    })
    
    return stats
  }
  
  // 清空错误队列
  clearErrors(): void {
    this.errorQueue = []
  }
}

// 重试机制工具函数
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 'exponential',
    shouldRetry = (error, attempt) => attempt < maxAttempts
  } = options
  
  let lastError: any
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      
      if (!shouldRetry(error, attempt)) {
        break
      }
      
      if (attempt < maxAttempts) {
        const waitTime = backoff === 'exponential' 
          ? delay * Math.pow(2, attempt - 1)
          : delay * attempt
        
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }
  }
  
  throw lastError
}

// 网络请求包装器
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  context?: Partial<ErrorContext>
): Promise<T> {
  const errorHandler = ErrorHandler.getInstance()
  
  try {
    return await withRetry(apiCall, {
      maxAttempts: 3,
      shouldRetry: (error) => {
        // 不重试客户端错误（4xx）
        const status = error?.response?.status
        return !status || status >= 500 || status === 0
      }
    })
  } catch (error) {
    const appError = errorHandler.createError(
      ErrorType.NETWORK,
      '网络请求失败',
      context,
      error
    )
    
    errorHandler.handleError(appError)
    throw appError
  }
}

// 导出单例
export const errorHandler = ErrorHandler.getInstance()

// 全局错误处理器
export function setupGlobalErrorHandler(): void {
  // 捕获未处理的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    const error = errorHandler.createError(
      ErrorType.UNKNOWN,
      '未处理的Promise错误',
      { component: 'global' },
      event.reason
    )
    
    errorHandler.handleError(error)
    event.preventDefault()
  })
  
  // 捕获JavaScript运行时错误
  window.addEventListener('error', (event) => {
    const error = errorHandler.createError(
      ErrorType.UNKNOWN,
      event.message,
      {
        component: 'global',
        stack: event.error?.stack
      },
      event.error
    )
    
    errorHandler.handleError(error)
  })
  
  // 捕获资源加载错误
  window.addEventListener('error', (event) => {
    const target = event.target as HTMLElement
    if (target && target !== window) {
      const error = errorHandler.createError(
        ErrorType.NETWORK,
        `资源加载失败: ${(target as any).src || (target as any).href}`,
        { component: 'resource-loader' },
        event
      )
      
      errorHandler.handleError(error)
    }
  }, true)
}

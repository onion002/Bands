/**
 * 时间工具函数 - 统一处理东8区时间格式化
 */

/**
 * 将服务器返回的时间字符串转换为东8区时间并格式化
 * @param timeString - 服务器返回的时间字符串
 * @param format - 格式化类型：'datetime' | 'date' | 'time' | 'relative'
 * @returns 格式化后的时间字符串
 */
export function formatTime(timeString: string, format: 'datetime' | 'date' | 'time' | 'relative' = 'datetime'): string {
  if (!timeString) return ''
  
  try {
    // 如果服务器已经返回了格式化的东8区时间，直接使用
    if (timeString.includes('年') || timeString.includes('-') && timeString.includes(':')) {
      return timeString
    }
    
    // 否则按照ISO格式解析
    const date = new Date(timeString)
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return timeString
    }
    
    // 转换为东8区时间（中国标准时间）
    const options: Intl.DateTimeFormatOptions = {
      timeZone: 'Asia/Shanghai'
    }
    
    switch (format) {
      case 'datetime':
        return date.toLocaleString('zh-CN', {
          ...options,
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      
      case 'date':
        return date.toLocaleDateString('zh-CN', {
          ...options,
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
      
      case 'time':
        return date.toLocaleTimeString('zh-CN', {
          ...options,
          hour: '2-digit',
          minute: '2-digit'
        })
      
      case 'relative':
        return formatRelativeTime(date)
      
      default:
        return date.toLocaleString('zh-CN', options)
    }
  } catch (error) {
    console.warn('时间格式化失败:', error)
    return timeString
  }
}

/**
 * 格式化相对时间（如：刚刚、5分钟前、昨天等）
 * @param date - Date对象
 * @returns 相对时间字符串
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSeconds < 60) {
    return '刚刚'
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    // 超过一周显示具体日期
    return formatTime(date.toISOString(), 'date')
  }
}

/**
 * 格式化时间段（如音乐播放时间）
 * @param seconds - 秒数
 * @returns 格式化的时间字符串 (mm:ss 或 hh:mm:ss)
 */
export function formatDuration(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return '00:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  } else {
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
}

/**
 * 获取当前东8区时间
 * @returns Date对象
 */
export function getBeijingTime(): Date {
  const now = new Date()
  // 转换为北京时间
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const beijingTime = new Date(utc + (8 * 3600000)) // UTC+8
  return beijingTime
}

/**
 * 检查日期是否为今天
 * @param date - 要检查的日期
 * @returns 是否为今天
 */
export function isToday(date: Date): boolean {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

/**
 * 检查日期是否为昨天
 * @param date - 要检查的日期
 * @returns 是否为昨天
 */
export function isYesterday(date: Date): boolean {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return date.toDateString() === yesterday.toDateString()
}

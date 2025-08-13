// 图片处理和优化工具
export interface ImageLoadOptions {
  lazy?: boolean
  fallback?: string
  maxRetries?: number
  quality?: number
  format?: 'webp' | 'jpeg' | 'png'
}

// 检测WebP支持
export function supportsWebP(): Promise<boolean> {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    canvas.width = 1
    canvas.height = 1
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      resolve(false)
      return
    }
    
    // 创建一个简单的图像数据
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
    ctx.fillRect(0, 0, 1, 1)
    
    try {
      const dataURL = canvas.toDataURL('image/webp', 0.5)
      resolve(dataURL.startsWith('data:image/webp'))
    } catch {
      resolve(false)
    }
  })
}

// 智能图片URL生成器
export async function generateOptimizedImageUrl(
  originalUrl: string, 
  options: ImageLoadOptions = {}
): Promise<string> {
  const {
    quality = 0.8,
    format = 'webp'
  } = options
  
  // 如果原始URL已经是优化格式，直接返回
  if (originalUrl.includes('.webp') || originalUrl.includes('format=webp')) {
    return originalUrl
  }
  
  // 检测WebP支持
  const webpSupported = await supportsWebP()
  
  // 如果支持WebP且要求WebP格式
  if (webpSupported && format === 'webp') {
    // 这里可以实现将URL转换为WebP格式的逻辑
    // 例如：添加查询参数或使用CDN服务
    const url = new URL(originalUrl, window.location.origin)
    url.searchParams.set('format', 'webp')
    url.searchParams.set('quality', (quality * 100).toString())
    return url.toString()
  }
  
  return originalUrl
}

// 图片预加载器
export class ImagePreloader {
  private cache = new Map<string, HTMLImageElement>()
  private loading = new Set<string>()
  
  async preload(url: string, options: ImageLoadOptions = {}): Promise<HTMLImageElement> {
    // 检查缓存
    if (this.cache.has(url)) {
      return this.cache.get(url)!
    }
    
    // 检查是否正在加载
    if (this.loading.has(url)) {
      return new Promise((resolve) => {
        const checkLoaded = () => {
          if (this.cache.has(url)) {
            resolve(this.cache.get(url)!)
          } else {
            setTimeout(checkLoaded, 100)
          }
        }
        checkLoaded()
      })
    }
    
    this.loading.add(url)
    
    const { maxRetries = 3, fallback } = options
    let attempts = 0
    
    const loadImage = (): Promise<HTMLImageElement> => {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.crossOrigin = 'anonymous'
        
        img.onload = () => {
          this.cache.set(url, img)
          this.loading.delete(url)
          resolve(img)
        }
        
        img.onerror = () => {
          attempts++
          if (attempts < maxRetries) {
            // 重试
            setTimeout(() => {
              loadImage().then(resolve).catch(reject)
            }, 1000 * attempts)
          } else if (fallback && fallback !== url) {
            // 使用备用图片
            this.preload(fallback).then(resolve).catch(reject)
          } else {
            this.loading.delete(url)
            reject(new Error(`Failed to load image: ${url}`))
          }
        }
        
        img.src = url
      })
    }
    
    return loadImage()
  }
  
  // 清理缓存
  clearCache(): void {
    this.cache.clear()
  }
  
  // 获取缓存大小
  getCacheSize(): number {
    return this.cache.size
  }
  
  // 移除特定缓存
  removeFromCache(url: string): void {
    this.cache.delete(url)
  }
}

// 懒加载图片指令
export function createLazyImageDirective() {
  const imagePreloader = new ImagePreloader()
  
  return {
    mounted(el: HTMLImageElement, binding: any) {
      const { value: src, modifiers } = binding
      
      if (!src) return
      
      // 如果不启用懒加载，直接加载
      if (!modifiers.lazy) {
        imagePreloader.preload(src).then((img) => {
          el.src = img.src
        }).catch(() => {
          if (modifiers.fallback) {
            el.src = modifiers.fallback
          }
        })
        return
      }
      
      // 创建Intersection Observer进行懒加载
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              imagePreloader.preload(src).then((img) => {
                el.src = img.src
                el.classList.add('loaded')
              }).catch(() => {
                if (modifiers.fallback) {
                  el.src = modifiers.fallback
                }
                el.classList.add('error')
              })
              observer.unobserve(el)
            }
          })
        },
        {
          rootMargin: '50px' // 提前50px开始加载
        }
      )
      
      observer.observe(el)
      
      // 保存observer用于清理
      ;(el as any)._imageObserver = observer
    },
    
    unmounted(el: HTMLImageElement) {
      const observer = (el as any)._imageObserver
      if (observer) {
        observer.disconnect()
      }
    }
  }
}

// 图片压缩工具
export function compressImage(
  file: File, 
  quality: number = 0.8,
  maxWidth: number = 1920,
  maxHeight: number = 1080
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    if (!ctx) {
      reject(new Error('Canvas context not available'))
      return
    }
    
    img.onload = () => {
      // 计算新尺寸
      let { width, height } = img
      
      if (width > maxWidth) {
        height = (height * maxWidth) / width
        width = maxWidth
      }
      
      if (height > maxHeight) {
        width = (width * maxHeight) / height
        height = maxHeight
      }
      
      canvas.width = width
      canvas.height = height
      
      // 绘制图像
      ctx.drawImage(img, 0, 0, width, height)
      
      // 转换为Blob
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob)
          } else {
            reject(new Error('Failed to compress image'))
          }
        },
        'image/jpeg',
        quality
      )
    }
    
    img.onerror = () => {
      reject(new Error('Failed to load image for compression'))
    }
    
    img.src = URL.createObjectURL(file)
  })
}

// 导出单例
export const imagePreloader = new ImagePreloader()

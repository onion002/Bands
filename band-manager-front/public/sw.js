/**
 * Service Worker for Band Manager Frontend
 * 提供离线缓存、资源预加载、性能优化等功能
 */

const CACHE_NAME = 'band-manager-v1.0.0'
const STATIC_CACHE = 'static-v1.0.0'
const DYNAMIC_CACHE = 'dynamic-v1.0.0'
const API_CACHE = 'api-v1.0.0'

// 需要缓存的静态资源
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/assets/css/',
  '/assets/js/',
  '/assets/images/',
  '/poster-girl-assets/'
]

// 需要缓存的API端点
const API_ENDPOINTS = [
  '/api/auth/',
  '/api/bands/',
  '/api/members/',
  '/api/events/',
  '/api/community/',
  '/api/music/'
]

// 安装事件 - 缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('📦 缓存静态资源')
        return cache.addAll(STATIC_ASSETS)
      })
      .catch((error) => {
        console.warn('缓存静态资源失败:', error)
      })
  )
})

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('🗑️ 删除旧缓存:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
  )
})

// 拦截网络请求
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // 跳过非GET请求
  if (request.method !== 'GET') {
    return
  }

  // 跳过Chrome扩展等特殊请求
  if (url.protocol === 'chrome-extension:') {
    return
  }

  // 处理不同类型的请求
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE))
  } else if (isAPIRequest(request)) {
    event.respondWith(networkFirst(request, API_CACHE))
  } else {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE))
  }
})

// 判断是否为静态资源
function isStaticAsset(request) {
  const url = new URL(request.url)
  return url.pathname.startsWith('/assets/') ||
         url.pathname.startsWith('/poster-girl-assets/') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.jpg') ||
         url.pathname.endsWith('.gif') ||
         url.pathname.endsWith('.svg') ||
         url.pathname.endsWith('.woff') ||
         url.pathname.endsWith('.woff2')
}

// 判断是否为API请求
function isAPIRequest(request) {
  const url = new URL(request.url)
  return url.pathname.startsWith('/api/') ||
         url.pathname.startsWith('/uploads/')
}

// 缓存优先策略 - 适用于静态资源
async function cacheFirst(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }

    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.warn('缓存优先策略失败:', error)
    return new Response('离线内容不可用', { status: 503 })
  }
}

// 网络优先策略 - 适用于动态内容
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.log('网络请求失败，尝试从缓存获取:', error)
    
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }

    // 返回离线页面或错误信息
    if (request.destination === 'document') {
      return caches.match('/offline.html')
    }
    
    return new Response('离线内容不可用', { status: 503 })
  }
}

// 预缓存策略 - 预加载重要资源
async function precache(urls) {
  const cache = await caches.open(STATIC_CACHE)
  const promises = urls.map(url => {
    return cache.add(url).catch(error => {
      console.warn(`预缓存失败: ${url}`, error)
    })
  })
  return Promise.all(promises)
}

// 清理过期缓存
async function cleanupExpiredCache() {
  const cacheNames = await caches.keys()
  const now = Date.now()
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName)
    const requests = await cache.keys()
    
    for (const request of requests) {
      const response = await cache.match(request)
      if (response) {
        const headers = response.headers
        const cacheControl = headers.get('cache-control')
        const expires = headers.get('expires')
        
        // 检查缓存是否过期
        if (isExpired(cacheControl, expires, now)) {
          await cache.delete(request)
        }
      }
    }
  }
}

// 检查缓存是否过期
function isExpired(cacheControl, expires, now) {
  if (cacheControl) {
    const maxAge = cacheControl.match(/max-age=(\d+)/)
    if (maxAge) {
      return false // 暂时跳过max-age检查，简化逻辑
    }
  }
  
  if (expires) {
    const expiryTime = new Date(expires).getTime()
    return now > expiryTime
  }
  
  return false
}

// 定期清理过期缓存
setInterval(cleanupExpiredCache, 1000 * 60 * 60) // 每小时清理一次

// 消息处理 - 与主线程通信
self.addEventListener('message', (event) => {
  const { type, data } = event.data
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting()
      break
      
    case 'PRECACHE':
      precache(data.urls)
      break
      
    case 'CLEANUP_CACHE':
      cleanupExpiredCache()
      break
      
    default:
      console.log('未知消息类型:', type)
  }
})

// 推送通知处理
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json()
    const options = {
      body: data.body,
      icon: '/assets/images/icon-192x192.png',
      badge: '/assets/images/badge-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      },
      actions: [
        {
          action: 'explore',
          title: '查看详情',
          icon: '/assets/images/checkmark.png'
        },
        {
          action: 'close',
          title: '关闭',
          icon: '/assets/images/xmark.png'
        }
      ]
    }
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    )
  }
})

// 通知点击处理
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    )
  }
})

console.log('🚀 Service Worker 已激活')
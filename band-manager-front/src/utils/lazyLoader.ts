/**
 * 懒加载工具函数
 * 用于优化代码分割和减少初始bundle大小
 */

import { defineAsyncComponent, Component } from 'vue'

/**
 * 创建懒加载组件
 * @param importFn 动态导入函数
 * @param fallback 加载中的占位组件
 * @param errorComponent 错误时的组件
 */
export function createLazyComponent(
  importFn: () => Promise<{ default: Component }>,
  fallback?: Component,
  errorComponent?: Component
) {
  return defineAsyncComponent({
    loader: importFn,
    loadingComponent: fallback,
    errorComponent,
    delay: 200, // 200ms后显示loading
    timeout: 10000, // 10秒超时
    onError(error, retry, fail, attempts) {
      if (attempts <= 3) {
        // 重试3次
        retry()
      } else {
        fail()
      }
    }
  })
}

/**
 * 预加载组件
 * @param importFn 动态导入函数
 */
export function preloadComponent(importFn: () => Promise<{ default: Component }>) {
  // 在空闲时间预加载
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      importFn()
    })
  } else {
    // 降级到setTimeout
    setTimeout(() => {
      importFn()
    }, 1000)
  }
}

/**
 * 条件懒加载
 * @param condition 加载条件
 * @param importFn 动态导入函数
 * @param fallback 加载中的占位组件
 */
export function conditionalLazyLoad(
  condition: boolean,
  importFn: () => Promise<{ default: Component }>,
  fallback?: Component
) {
  if (condition) {
    return defineAsyncComponent({
      loader: importFn,
      loadingComponent: fallback,
      delay: 100
    })
  }
  return null
}

/**
 * 路由级别的懒加载
 * @param routePath 路由路径
 * @param importFn 动态导入函数
 */
export function createRouteLazyComponent(
  routePath: string,
  importFn: () => Promise<{ default: Component }>
) {
  return defineAsyncComponent({
    loader: () => {
      // 预加载相关路由
      if (routePath.includes('/admin')) {
        // 管理员路由预加载
        import('@/views/admin/AdminUsersView.vue')
        import('@/views/admin/AdminReportsView.vue')
      } else if (routePath.includes('/bands')) {
        // 乐队管理路由预加载
        import('@/views/bands/BandManagement.vue')
        import('@/views/bands/MemberManagement.vue')
      }
      return importFn()
    },
    delay: 150,
    timeout: 8000
  })
}
// 看板娘模块统一导出
// 🎭 看板娘模块 v1.0.0
// 独立的Live2D看板娘系统，支持模型切换、拖拽、自定义配置等功能

// =============================================================================
// 组件导出
// =============================================================================
export { default as PosterGirl } from './components/PosterGirl.vue'
export { default as PosterGirlSettings } from './components/PosterGirlSettings.vue'

// =============================================================================
// 服务导出
// =============================================================================
export { live2dService } from './services/live2dService'
export { modelManager } from './services/modelManager'

// =============================================================================
// 工具导出
// =============================================================================
export { validateModel, validateAllModels } from './utils/modelValidator'

// =============================================================================
// 配置导出
// =============================================================================
export {
  // 配置接口
  getCurrentConfig,
  saveConfig,
  
  // 默认配置
  defaultPosterGirlConfig,
  
  // 模型列表
  AVAILABLE_MODELS
} from './config/posterGirl'

// =============================================================================
// 类型导出
// =============================================================================
export type {
  PosterGirlConfig,
  ModelInfo,
  ModelSwitchResult,
  ModelStats,
  Live2DOptions,
  PosterGirlPluginOptions,
  ModelValidationResult,
  UsePosterGirlReturn,
  UseModelManagerReturn
} from './types'

// =============================================================================
// 组合式API导出
// =============================================================================
export { usePosterGirl } from './composables/usePosterGirl'
export { useModelManager } from './composables/useModelManager'

// =============================================================================
// Vue插件
// =============================================================================
import type { App } from 'vue'
import type { PosterGirlPluginOptions } from './types'
import PosterGirl from './components/PosterGirl.vue'
import PosterGirlSettings from './components/PosterGirlSettings.vue'

export const posterGirlPlugin = {
  install(app: App, options: PosterGirlPluginOptions = {}) {
    // 注册全局组件
    if (options.globalComponents !== false) {
      app.component('PosterGirl', PosterGirl)
      app.component('PosterGirlSettings', PosterGirlSettings)
    }
    
    // 提供全局配置
    if (options.defaultConfig) {
      app.provide('posterGirlConfig', options.defaultConfig)
    }
    
    // 自动初始化
    if (options.autoInit !== false) {
      console.log('🎭 看板娘插件已安装')
    }
  }
}

// =============================================================================
// 便捷函数
// =============================================================================

/**
 * 快速创建看板娘实例
 */
export function createPosterGirl(config?: Partial<import('./types').PosterGirlConfig>) {
  return {
    config,
    // 这里可以添加更多便捷方法
  }
}

/**
 * 批量验证模型
 */
export async function validatePosterGirlModels(modelPaths: string[]) {
  const { validateAllModels } = await import('./utils/modelValidator')
  return validateAllModels(modelPaths)
}

// =============================================================================
// 模块信息
// =============================================================================
export const POSTER_GIRL_MODULE_INFO = {
  name: '@band-manager/poster-girl',
  version: '1.0.0',
  description: 'Live2D看板娘系统 - 支持模型切换、拖拽、自定义配置',
  author: 'Band Manager Team',
  features: [
    'Live2D模型渲染',
    '随机模型切换',
    '拖拽定位',
    '自定义配置',
    '响应式设计',
    '组合式API',
    'TypeScript支持'
  ],
  dependencies: {
    vue: '^3.0.0'
  }
} as const

// =============================================================================
// 默认导出
// =============================================================================
export default posterGirlPlugin

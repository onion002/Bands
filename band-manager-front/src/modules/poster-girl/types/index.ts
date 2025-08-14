// 看板娘模块类型定义
export interface PosterGirlConfig {
  mode: 'static' | 'fixed' | 'draggable'
  hidden: boolean
  size: {
    width: number
    height: number
  }
  content: {
    welcome: string | string[]
    touch?: string | string[]
    skin?: [string, string]
    home?: string | string[]
    close?: string | string[]
    link?: string
    referer?: string
    custom?: Array<{
      selector: string
      type?: 'read' | 'link'
      text?: string
    }>
  }
  night?: string
  model: string[]
  defaultModel?: string
  tips?: boolean
  dragPosition?: {
    x: number
    y: number
  }
}

export interface ModelInfo {
  name: string
  path: string
  preview: string
  description: string
}

export interface ModelSwitchResult {
  success: boolean
  modelName: string
  modelPath: string
}

export interface ModelStats {
  total: number
  available: number
  current: string
}

export interface Live2DOptions {
  canvas?: HTMLCanvasElement
  modelPath?: string
  size?: {
    width: number
    height: number
  }
}

export interface PosterGirlPluginOptions {
  defaultConfig?: Partial<PosterGirlConfig>
  autoInit?: boolean
  globalComponents?: boolean
}

// 验证结果接口
export interface ModelValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
  modelInfo?: {
    name: string
    version: string
    hasTextures: boolean
    hasMotions: boolean
    hasPhysics: boolean
    hasVoices: boolean
  }
}

// 组合式API返回类型
export interface UsePosterGirlReturn {
  // 状态
  isHidden: Ref<boolean>
  isDragging: Ref<boolean>
  showActions: Ref<boolean>
  showDialog: Ref<boolean>
  currentMessage: Ref<string>
  
  // 配置
  pioConfig: Ref<PosterGirlConfig>
  
  // 计算属性
  containerStyle: ComputedRef<any>
  
  // 方法
  initLive2D: () => Promise<void>
  switchModel: () => Promise<void>
  showMessage: (message: string | string[], duration?: number) => void
  hidePosterGirl: () => void
  showPosterGirl: () => void
  handleTouch: () => void
  
  // 导航方法
  navigateToMusicBox: () => void
  navigateToSettings: () => void
  navigateToMusicTeacher: () => void
  
  // 拖拽相关
  startDrag: (event: MouseEvent | TouchEvent) => void
  
  // 生命周期
  reloadPosterGirl: () => void
  togglePosterGirl: () => void
  togglePosition: () => void
}

export interface UseModelManagerReturn {
  // 状态
  availableModels: Ref<string[]>
  currentModelIndex: Ref<number>
  isInitialized: Ref<boolean>
  
  // 方法
  init: () => Promise<void>
  loadDefaultModel: (defaultModelPath?: string) => Promise<boolean>
  switchToRandomModel: () => Promise<ModelSwitchResult>
  switchToNextModel: () => Promise<ModelSwitchResult>
  getCurrentModelPath: () => string
  getModelStats: () => ModelStats
  reset: () => void
}

// 导入Vue类型
import type { Ref, ComputedRef } from 'vue'

// 模型管理器的组合式API
import { ref } from 'vue'
import { modelManager } from '../services/modelManager'
import type { UseModelManagerReturn, ModelSwitchResult, ModelStats } from '../types'

export function useModelManager(): UseModelManagerReturn {
  // 响应式状态
  const availableModels = ref<string[]>([])
  const currentModelIndex = ref(0)
  const isInitialized = ref(false)
  
  // 初始化模型管理器
  const init = async (): Promise<void> => {
    try {
      await modelManager.init()
      availableModels.value = modelManager.getAvailableModels()
      isInitialized.value = true
    } catch (error) {
      console.error('模型管理器初始化失败:', error)
      isInitialized.value = false
    }
  }
  
  // 加载默认模型
  const loadDefaultModel = async (defaultModelPath?: string): Promise<boolean> => {
    const result = await modelManager.loadDefaultModel(defaultModelPath)
    if (result) {
      availableModels.value = modelManager.getAvailableModels()
      const stats = modelManager.getModelStats()
      currentModelIndex.value = availableModels.value.indexOf(stats.current)
    }
    return result
  }
  
  // 随机切换模型
  const switchToRandomModel = async (): Promise<ModelSwitchResult> => {
    const result = await modelManager.switchToRandomModel()
    if (result.success) {
      const stats = modelManager.getModelStats()
      currentModelIndex.value = availableModels.value.indexOf(stats.current)
    }
    return result
  }
  
  // 顺序切换到下一个模型
  const switchToNextModel = async (): Promise<ModelSwitchResult> => {
    const result = await modelManager.switchToNextModel()
    if (result.success) {
      const stats = modelManager.getModelStats()
      currentModelIndex.value = availableModels.value.indexOf(stats.current)
    }
    return result
  }
  
  // 获取当前模型路径
  const getCurrentModelPath = (): string => {
    return modelManager.getCurrentModelPath()
  }
  
  // 获取模型统计信息
  const getModelStats = (): ModelStats => {
    return modelManager.getModelStats()
  }
  
  // 重置模型管理器
  const reset = (): void => {
    modelManager.reset()
    availableModels.value = []
    currentModelIndex.value = 0
    isInitialized.value = false
  }
  
  return {
    // 状态
    availableModels,
    currentModelIndex,
    isInitialized,
    
    // 方法
    init,
    loadDefaultModel,
    switchToRandomModel,
    switchToNextModel,
    getCurrentModelPath,
    getModelStats,
    reset
  }
}

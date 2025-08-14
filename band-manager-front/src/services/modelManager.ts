// 模型管理器 - 处理模型切换和验证
import { AVAILABLE_MODELS } from '@/modules/poster-girl/config/posterGirl'
import { live2dService } from '@/modules/poster-girl/services/live2dService'

export class ModelManager {
  private static instance: ModelManager
  private availableModels: string[] = []
  private currentModelIndex = 0
  private isInitialized = false

  private constructor() {}

  static getInstance(): ModelManager {
    if (!ModelManager.instance) {
      ModelManager.instance = new ModelManager()
    }
    return ModelManager.instance
  }

  /**
   * 初始化模型管理器
   */
  async init(): Promise<void> {
    console.log('🎭 初始化模型管理器...')
    
    // 验证所有可用模型
    this.availableModels = []
    
    for (const model of AVAILABLE_MODELS) {
      const isValid = await this.validateModel(model.path)
      if (isValid) {
        this.availableModels.push(model.path)
        console.log(`✅ 模型可用: ${model.name}`)
      } else {
        console.warn(`❌ 模型不可用: ${model.name}`)
      }
    }

    if (this.availableModels.length === 0) {
      console.error('❌ 没有可用的模型')
      throw new Error('没有可用的模型')
    }

    console.log(`📊 共找到 ${this.availableModels.length} 个可用模型`)
    this.isInitialized = true
  }

  /**
   * 验证单个模型是否可用
   */
  private async validateModel(modelPath: string): Promise<boolean> {
    try {
      const response = await fetch(modelPath, { method: 'HEAD' })
      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * 获取所有可用模型
   */
  getAvailableModels(): string[] {
    return [...this.availableModels]
  }

  /**
   * 加载默认模型
   */
  async loadDefaultModel(defaultModelPath?: string): Promise<boolean> {
    if (!this.isInitialized) {
      await this.init()
    }

    let modelToLoad = defaultModelPath || this.availableModels[0]
    
    // 如果指定的默认模型不可用，使用第一个可用的
    if (!this.availableModels.includes(modelToLoad)) {
      console.warn(`⚠️ 指定的默认模型不可用: ${defaultModelPath}`)
      modelToLoad = this.availableModels[0]
    }

    // 设置当前索引
    this.currentModelIndex = this.availableModels.indexOf(modelToLoad)
    
    console.log(`🎯 加载默认模型: ${modelToLoad}`)
    return await live2dService.loadModel(modelToLoad)
  }

  /**
   * 随机切换模型
   */
  async switchToRandomModel(): Promise<{ success: boolean; modelName: string; modelPath: string }> {
    if (!this.isInitialized) {
      await this.init()
    }

    if (this.availableModels.length <= 1) {
      return {
        success: false,
        modelName: '无可切换模型',
        modelPath: ''
      }
    }

    // 生成随机索引，确保不是当前模型
    let randomIndex: number
    do {
      randomIndex = Math.floor(Math.random() * this.availableModels.length)
    } while (randomIndex === this.currentModelIndex && this.availableModels.length > 1)

    const newModelPath = this.availableModels[randomIndex]
    console.log(`🎲 随机切换到模型: ${newModelPath}`)

    const success = await live2dService.loadModel(newModelPath)
    
    if (success) {
      this.currentModelIndex = randomIndex
      const modelInfo = this.getModelInfo(newModelPath)
      return {
        success: true,
        modelName: modelInfo?.name || '未知模型',
        modelPath: newModelPath
      }
    } else {
      return {
        success: false,
        modelName: '加载失败',
        modelPath: newModelPath
      }
    }
  }

  /**
   * 按顺序切换到下一个模型
   */
  async switchToNextModel(): Promise<{ success: boolean; modelName: string; modelPath: string }> {
    if (!this.isInitialized) {
      await this.init()
    }

    if (this.availableModels.length <= 1) {
      return {
        success: false,
        modelName: '无可切换模型',
        modelPath: ''
      }
    }

    // 切换到下一个模型
    this.currentModelIndex = (this.currentModelIndex + 1) % this.availableModels.length
    const newModelPath = this.availableModels[this.currentModelIndex]
    
    console.log(`➡️ 切换到下一个模型: ${newModelPath}`)

    const success = await live2dService.loadModel(newModelPath)
    
    if (success) {
      const modelInfo = this.getModelInfo(newModelPath)
      return {
        success: true,
        modelName: modelInfo?.name || '未知模型',
        modelPath: newModelPath
      }
    } else {
      return {
        success: false,
        modelName: '加载失败',
        modelPath: newModelPath
      }
    }
  }

  /**
   * 获取当前模型路径
   */
  getCurrentModelPath(): string {
    return this.availableModels[this.currentModelIndex] || ''
  }

  /**
   * 获取模型信息
   */
  private getModelInfo(modelPath: string) {
    return AVAILABLE_MODELS.find(model => model.path === modelPath)
  }

  /**
   * 获取模型统计信息
   */
  getModelStats(): { total: number; available: number; current: string } {
    return {
      total: AVAILABLE_MODELS.length,
      available: this.availableModels.length,
      current: this.getCurrentModelPath()
    }
  }

  /**
   * 重置模型管理器
   */
  reset(): void {
    this.availableModels = []
    this.currentModelIndex = 0
    this.isInitialized = false
  }
}

// 导出单例
export const modelManager = ModelManager.getInstance()

// Live2D模型验证工具
import type { ModelValidationResult } from '../types'

export class ModelValidator {
  /**
   * 验证Live2D模型的完整性
   */
  static async validateModel(modelPath: string): Promise<ModelValidationResult> {
    const result: ModelValidationResult = {
      isValid: false,
      errors: [],
      warnings: []
    }

    try {
      // 1. 检查模型文件是否存在
      const modelResponse = await fetch(modelPath)
      if (!modelResponse.ok) {
        result.errors.push(`模型文件不存在: ${modelPath}`)
        return result
      }

      // 2. 解析模型配置
      const modelConfig = await modelResponse.json()
      
      // 3. 基本配置检查
      if (!modelConfig.model) {
        result.errors.push('缺少模型文件路径 (model)')
      }
      
      if (!modelConfig.textures || !Array.isArray(modelConfig.textures) || modelConfig.textures.length === 0) {
        result.errors.push('缺少纹理配置 (textures)')
      }

      // 4. 检查模型文件路径
      const basePath = modelPath.substring(0, modelPath.lastIndexOf('/'))
      
      // 检查.moc文件
      if (modelConfig.model) {
        const mocPath = `${basePath}/${modelConfig.model}`
        const mocExists = await this.checkFileExists(mocPath)
        if (!mocExists) {
          result.errors.push(`模型文件不存在: ${modelConfig.model}`)
        }
      }

      // 检查纹理文件
      let hasValidTextures = false
      if (modelConfig.textures) {
        for (const texture of modelConfig.textures) {
          const texturePath = `${basePath}/${texture}`
          const textureExists = await this.checkFileExists(texturePath)
          if (textureExists) {
            hasValidTextures = true
          } else {
            result.warnings.push(`纹理文件不存在: ${texture}`)
          }
        }
      }

      // 检查物理文件
      let hasPhysics = false
      if (modelConfig.physics) {
        const physicsPath = `${basePath}/${modelConfig.physics}`
        const physicsExists = await this.checkFileExists(physicsPath)
        if (physicsExists) {
          hasPhysics = true
        } else {
          result.warnings.push(`物理文件不存在: ${modelConfig.physics}`)
        }
      }

      // 检查动作文件
      let hasValidMotions = false
      if (modelConfig.motions) {
        for (const motionType in modelConfig.motions) {
          const motions = modelConfig.motions[motionType]
          if (Array.isArray(motions)) {
            for (const motion of motions) {
              if (motion.file) {
                const motionPath = `${basePath}/${motion.file}`
                const motionExists = await this.checkFileExists(motionPath)
                if (motionExists) {
                  hasValidMotions = true
                } else {
                  result.warnings.push(`动作文件不存在: ${motion.file}`)
                }
              }
            }
          }
        }
      }

      // 检查语音文件
      let hasVoices = false
      if (modelConfig.motions) {
        for (const motionType in modelConfig.motions) {
          const motions = modelConfig.motions[motionType]
          if (Array.isArray(motions)) {
            for (const motion of motions) {
              if (motion.sound) {
                const voicePath = `${basePath}/${motion.sound}`
                const voiceExists = await this.checkFileExists(voicePath)
                if (voiceExists) {
                  hasVoices = true
                } else {
                  result.warnings.push(`语音文件不存在: ${motion.sound}`)
                }
              }
            }
          }
        }
      }

      // 设置模型信息
      result.modelInfo = {
        name: modelConfig.name || '未知模型',
        version: modelConfig.version || '未知版本',
        hasTextures: hasValidTextures,
        hasMotions: hasValidMotions,
        hasPhysics: hasPhysics,
        hasVoices: hasVoices
      }

      // 判断是否有效
      result.isValid = result.errors.length === 0 && hasValidTextures

      if (result.isValid) {
        console.log(`✅ 模型验证通过: ${modelPath}`, result.modelInfo)
      } else {
        console.warn(`❌ 模型验证失败: ${modelPath}`, result.errors)
      }

    } catch (error) {
      result.errors.push(`模型验证时发生错误: ${error instanceof Error ? error.message : '未知错误'}`)
    }

    return result
  }

  /**
   * 验证所有配置的模型
   */
  static async validateAllModels(modelPaths: string[]): Promise<{ [key: string]: ModelValidationResult }> {
    const results: { [key: string]: ModelValidationResult } = {}
    
    for (const modelPath of modelPaths) {
      try {
        results[modelPath] = await this.validateModel(modelPath)
      } catch (error) {
        results[modelPath] = {
          isValid: false,
          errors: [`验证失败: ${error instanceof Error ? error.message : '未知错误'}`],
          warnings: []
        }
      }
    }

    return results
  }

  /**
   * 检查文件是否存在
   */
  private static async checkFileExists(filePath: string): Promise<boolean> {
    try {
      const response = await fetch(filePath, { method: 'HEAD' })
      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * 生成验证报告
   */
  static generateValidationReport(results: { [key: string]: ModelValidationResult }): string {
    let report = '📋 Live2D模型验证报告\n'
    report += '=' .repeat(50) + '\n\n'

    let validCount = 0
    let totalCount = 0

    for (const [modelPath, result] of Object.entries(results)) {
      totalCount++
      const modelName = modelPath.split('/').pop() || modelPath
      
      if (result.isValid) {
        validCount++
        report += `✅ ${modelName}\n`
        if (result.modelInfo) {
          report += `   📊 版本: ${result.modelInfo.version}\n`
          report += `   🎨 纹理: ${result.modelInfo.hasTextures ? '✓' : '✗'}\n`
          report += `   🎭 动作: ${result.modelInfo.hasMotions ? '✓' : '✗'}\n`
          report += `   ⚡ 物理: ${result.modelInfo.hasPhysics ? '✓' : '✗'}\n`
          report += `   🔊 语音: ${result.modelInfo.hasVoices ? '✓' : '✗'}\n`
        }
      } else {
        report += `❌ ${modelName}\n`
        result.errors.forEach(error => {
          report += `   💥 错误: ${error}\n`
        })
      }

      if (result.warnings.length > 0) {
        result.warnings.forEach(warning => {
          report += `   ⚠️ 警告: ${warning}\n`
        })
      }
      
      report += '\n'
    }

    report += '=' .repeat(50) + '\n'
    report += `📈 总结: ${validCount}/${totalCount} 个模型验证通过\n`

    if (validCount < totalCount) {
      report += '\n💡 建议:\n'
      report += '   1. 检查文件路径是否正确\n'
      report += '   2. 确认所有必需的文件都已上传\n'
      report += '   3. 验证模型配置文件的格式\n'
    }

    return report
  }
}

// 导出便捷函数
export const validateModel = ModelValidator.validateModel
export const validateAllModels = ModelValidator.validateAllModels

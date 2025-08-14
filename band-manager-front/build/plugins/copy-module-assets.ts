// 模块资源复制插件
import { Plugin } from 'vite'
import path from 'path'
import { existsSync, mkdirSync } from 'fs'
import { execSync } from 'child_process'

export interface ModuleAssetConfig {
  /** 模块名称 */
  name: string
  /** 源路径（相对于项目根目录） */
  srcPath: string
  /** 目标路径（相对于public目录） */
  destPath: string
  /** 是否启用（默认true） */
  enabled?: boolean
}

export interface CopyModuleAssetsOptions {
  /** 模块配置列表 */
  modules: ModuleAssetConfig[]
  /** 是否显示详细日志（默认true） */
  verbose?: boolean
}

/**
 * Vite插件：复制模块资源到public目录
 * 支持多模块、跨平台、可配置
 */
export function copyModuleAssetsPlugin(options: CopyModuleAssetsOptions): Plugin {
  const { modules, verbose = true } = options
  // 默认使用进程工作目录；在configResolved后会替换为Vite的root
  let projectRoot = process.cwd()

  return {
    name: 'copy-module-assets',

    // 获取Vite项目根目录，避免在monorepo从上层目录启动时解析错误
    configResolved(config) {
      projectRoot = config.root || projectRoot
      if (verbose) {
        console.log(`📁 copy-module-assets 使用根目录: ${projectRoot}`)
      }
    },

    // 开发/构建统一在开始阶段执行一次复制
    buildStart() {
      runCopyAll(modules, projectRoot, verbose)
    },

    // 兼容部分场景下buildStart不触发的dev环境，作为兜底
    configureServer() {
      runCopyAll(modules, projectRoot, verbose)
    }
  }
}

/**
 * 复制单个模块的资源
 */
function copyModuleAssets(config: ModuleAssetConfig, verbose: boolean, rootDir: string) {
  const { name, srcPath, destPath } = config
  
  // 解析绝对路径
  const srcBase = path.resolve(rootDir, srcPath)
  const publicBase = path.resolve(rootDir, 'public', destPath)
  
  // 检查源路径是否存在
  if (!existsSync(srcBase)) {
    if (verbose) console.warn(`⚠️ 模块 ${name} 源路径不存在: ${srcPath}`)
    return
  }
  
  // 创建目标目录
  if (!existsSync(publicBase)) {
    mkdirSync(publicBase, { recursive: true })
  }
  
  // 跨平台复制
  try {
    if (process.platform === 'win32') {
      execSync(`xcopy "${srcBase}" "${publicBase}" /E /I /Y /Q`, { stdio: 'ignore' })
    } else {
      execSync(`cp -r "${srcBase}"/* "${publicBase}"/`, { stdio: 'ignore' })
    }
    
    if (verbose) console.log(`📦 ${name} 资源已复制: ${srcPath} → public/${destPath}`)
  } catch (error) {
    throw new Error(`复制失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

function runCopyAll(modules: ModuleAssetConfig[], rootDir: string, verbose: boolean) {
  const enabledModules = modules.filter(m => m.enabled !== false)

  if (enabledModules.length === 0) {
    if (verbose) console.log('📦 没有需要复制的模块资源')
    return
  }

  for (const module of enabledModules) {
    try {
      copyModuleAssets(module, verbose, rootDir)
    } catch (error) {
      console.error(`❌ 复制模块 ${module.name} 资源失败:`, error)
    }
  }
}

/**
 * 预设配置：看板娘模块
 */
export const POSTER_GIRL_ASSET_CONFIG: ModuleAssetConfig = {
  name: '看板娘',
  srcPath: 'src/modules/poster-girl/assets',
  destPath: 'poster-girl-assets',
  enabled: true
}

/**
 * 预设配置：音乐盒模块（示例）
 */
export const MUSIC_BOX_ASSET_CONFIG: ModuleAssetConfig = {
  name: '音乐盒',
  srcPath: 'src/modules/music-box/assets',
  destPath: 'music-box-assets',
  enabled: false // 默认禁用，需要时开启
}

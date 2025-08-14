#!/usr/bin/env node

/**
 * 模块资源复制脚本
 * 使用方法: node scripts/copy-assets.js
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

// 模块配置
const MODULES = [
  {
    name: '看板娘',
    src: 'src/modules/poster-girl/assets',
    dest: 'public/poster-girl-assets',
    enabled: true
  },
  // 可以添加更多模块
  // {
  //   name: '音乐盒',
  //   src: 'src/modules/music-box/assets',
  //   dest: 'public/music-box-assets',
  //   enabled: false
  // }
]

function copyAssets() {
  const enabledModules = MODULES.filter(m => m.enabled)
  
  console.log('📦 开始复制模块资源...')
  
  for (const module of enabledModules) {
    try {
      const srcPath = path.resolve(module.src)
      const destPath = path.resolve(module.dest)
      
      // 检查源路径
      if (!fs.existsSync(srcPath)) {
        console.warn(`⚠️ ${module.name} 源路径不存在: ${module.src}`)
        continue
      }
      
      // 创建目标目录
      if (!fs.existsSync(destPath)) {
        fs.mkdirSync(destPath, { recursive: true })
      }
      
      // 复制文件
      if (process.platform === 'win32') {
        execSync(`xcopy "${srcPath}" "${destPath}" /E /I /Y /Q`, { stdio: 'inherit' })
      } else {
        execSync(`cp -r "${srcPath}"/* "${destPath}"/`, { stdio: 'inherit' })
      }
      
      console.log(`✅ ${module.name} 资源复制完成`)
      
    } catch (error) {
      console.error(`❌ ${module.name} 复制失败:`, error.message)
    }
  }
  
  console.log('📦 所有模块资源复制完成！')
}

// 如果直接运行此脚本
if (require.main === module) {
  copyAssets()
}

module.exports = { copyAssets }

/**
 * 然后在package.json中配置:
 * 
 * {
 *   "scripts": {
 *     "copy-assets": "node scripts/copy-assets.js",
 *     "dev": "npm run copy-assets && vite",
 *     "build": "npm run copy-assets && vite build",
 *     "preview": "npm run copy-assets && vite preview"
 *   }
 * }
 * 
 * 优势：
 * ✅ 完全独立于构建系统
 * ✅ 可以单独运行和测试
 * ✅ 配置清晰易懂
 * ✅ 无额外依赖
 * 
 * 劣势：
 * ⚠️ 需要在每个命令前手动调用
 * ⚠️ 开发时文件变化不会自动同步
 */

#!/usr/bin/env node

/**
 * Bundle分析脚本
 * 用于分析生产构建的bundle大小和性能
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// 颜色输出
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
}

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`)
}

function logHeader(message) {
  log(`\n${colors.bold}${colors.cyan}${message}${colors.reset}`)
  log('='.repeat(message.length))
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green)
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow)
}

function logError(message) {
  log(`❌ ${message}`, colors.red)
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue)
}

/**
 * 分析bundle大小
 */
function analyzeBundleSizes() {
  const distPath = path.join(__dirname, '../dist')
  
  if (!fs.existsSync(distPath)) {
    logError('dist目录不存在，请先运行 npm run build')
    return
  }

  const assetsPath = path.join(distPath, 'assets')
  if (!fs.existsSync(assetsPath)) {
    logError('assets目录不存在')
    return
  }

  const files = fs.readdirSync(assetsPath)
  const jsFiles = files.filter(file => file.endsWith('.js'))
  const cssFiles = files.filter(file => file.endsWith('.css'))

  logHeader('📊 Bundle大小分析')

  // 分析JS文件
  logHeader('JavaScript文件')
  const jsStats = jsFiles.map(file => {
    const filePath = path.join(assetsPath, file)
    const stats = fs.statSync(filePath)
    const sizeKB = Math.round(stats.size / 1024)
    const gzipSizeKB = Math.round(stats.size * 0.3) // 估算gzip大小
    
    return {
      name: file,
      size: stats.size,
      sizeKB,
      gzipSizeKB,
      path: filePath
    }
  }).sort((a, b) => b.size - a.size)

  jsStats.forEach(file => {
    const sizeColor = file.sizeKB > 500 ? colors.red : file.sizeKB > 200 ? colors.yellow : colors.green
    log(`${file.name.padEnd(40)} ${sizeColor}${file.sizeKB}KB${colors.reset} (gzip: ~${file.gzipSizeKB}KB)`)
  })

  // 分析CSS文件
  logHeader('CSS文件')
  const cssStats = cssFiles.map(file => {
    const filePath = path.join(assetsPath, file)
    const stats = fs.statSync(filePath)
    const sizeKB = Math.round(stats.size / 1024)
    const gzipSizeKB = Math.round(stats.size * 0.2) // CSS压缩率更高
    
    return {
      name: file,
      size: stats.size,
      sizeKB,
      gzipSizeKB,
      path: filePath
    }
  }).sort((a, b) => b.size - a.size)

  cssStats.forEach(file => {
    const sizeColor = file.sizeKB > 100 ? colors.red : file.sizeKB > 50 ? colors.yellow : colors.green
    log(`${file.name.padEnd(40)} ${sizeColor}${file.sizeKB}KB${colors.reset} (gzip: ~${file.gzipSizeKB}KB)`)
  })

  // 总体统计
  const totalJsSize = jsStats.reduce((sum, file) => sum + file.size, 0)
  const totalCssSize = cssStats.reduce((sum, file) => sum + file.size, 0)
  const totalSize = totalJsSize + totalCssSize

  logHeader('📈 总体统计')
  log(`JavaScript总大小: ${Math.round(totalJsSize / 1024)}KB (gzip: ~${Math.round(totalJsSize * 0.3 / 1024)}KB)`)
  log(`CSS总大小: ${Math.round(totalCssSize / 1024)}KB (gzip: ~${Math.round(totalCssSize * 0.2 / 1024)}KB)`)
  log(`总大小: ${Math.round(totalSize / 1024)}KB (gzip: ~${Math.round((totalJsSize * 0.3 + totalCssSize * 0.2) / 1024)}KB)`)

  // 性能建议
  logHeader('💡 性能优化建议')
  
  const largeJsFiles = jsStats.filter(file => file.sizeKB > 500)
  if (largeJsFiles.length > 0) {
    logWarning('发现大型JavaScript文件:')
    largeJsFiles.forEach(file => {
      log(`  - ${file.name}: ${file.sizeKB}KB`)
    })
    log('建议: 使用代码分割、懒加载或Tree Shaking优化')
  }

  const largeCssFiles = cssStats.filter(file => file.sizeKB > 100)
  if (largeCssFiles.length > 0) {
    logWarning('发现大型CSS文件:')
    largeCssFiles.forEach(file => {
      log(`  - ${file.name}: ${file.sizeKB}KB`)
    })
    log('建议: 使用CSS代码分割、移除未使用的样式')
  }

  if (totalSize / 1024 > 2000) { // 2MB
    logError('总bundle大小超过2MB，建议优化')
  } else if (totalSize / 1024 > 1000) { // 1MB
    logWarning('总bundle大小超过1MB，建议优化')
  } else {
    logSuccess('Bundle大小在合理范围内')
  }

  return {
    jsStats,
    cssStats,
    totalSize,
    totalJsSize,
    totalCssSize
  }
}

/**
 * 检查依赖大小
 */
function analyzeDependencies() {
  logHeader('📦 依赖分析')
  
  try {
    const packageJsonPath = path.join(__dirname, '../package.json')
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'))
    
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies }
    
    log('主要依赖:')
    Object.entries(dependencies).forEach(([name, version]) => {
      log(`  ${name}: ${version}`)
    })
    
    // 检查已知的大型依赖
    const largeDeps = ['marked', 'highlight.js', 'lodash', 'moment', 'date-fns']
    const foundLargeDeps = largeDeps.filter(dep => dependencies[dep])
    
    if (foundLargeDeps.length > 0) {
      logWarning('发现可能影响bundle大小的依赖:')
      foundLargeDeps.forEach(dep => {
        log(`  - ${dep}: 考虑使用轻量级替代方案`)
      })
    }
    
  } catch (error) {
    logError(`读取package.json失败: ${error.message}`)
  }
}

/**
 * 生成优化报告
 */
function generateOptimizationReport(stats) {
  logHeader('🔧 优化建议报告')
  
  const report = {
    timestamp: new Date().toISOString(),
    stats,
    recommendations: []
  }

  // 检查大型文件
  const largeFiles = stats.jsStats.filter(file => file.sizeKB > 500)
  if (largeFiles.length > 0) {
    report.recommendations.push({
      type: 'large_files',
      priority: 'high',
      description: `发现${largeFiles.length}个大型JavaScript文件`,
      files: largeFiles.map(f => f.name),
      suggestions: [
        '使用动态导入进行代码分割',
        '实现组件懒加载',
        '检查是否有未使用的代码',
        '考虑使用更轻量的依赖'
      ]
    })
  }

  // 检查CSS优化
  const largeCssFiles = stats.cssStats.filter(file => file.sizeKB > 100)
  if (largeCssFiles.length > 0) {
    report.recommendations.push({
      type: 'css_optimization',
      priority: 'medium',
      description: `发现${largeCssFiles.length}个大型CSS文件`,
      suggestions: [
        '使用PurgeCSS移除未使用的样式',
        '实现CSS代码分割',
        '压缩和优化CSS'
      ]
    })
  }

  // 总体建议
  if (stats.totalSize / 1024 > 1000) {
    report.recommendations.push({
      type: 'overall_optimization',
      priority: 'high',
      description: '总bundle大小超过1MB',
      suggestions: [
        '启用gzip压缩',
        '使用CDN加速',
        '实现资源预加载',
        '优化图片和字体资源'
      ]
    })
  }

  // 输出建议
  report.recommendations.forEach((rec, index) => {
    const priorityColor = rec.priority === 'high' ? colors.red : colors.yellow
    log(`\n${index + 1}. ${priorityColor}${rec.description}${colors.reset}`)
    log('   建议:')
    rec.suggestions.forEach(suggestion => {
      log(`   - ${suggestion}`)
    })
  })

  // 保存报告
  const reportPath = path.join(__dirname, '../bundle-analysis-report.json')
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))
  logSuccess(`优化报告已保存到: ${reportPath}`)

  return report
}

/**
 * 主函数
 */
function main() {
  try {
    logHeader('🚀 Bundle性能分析工具')
    
    const stats = analyzeBundleSizes()
    analyzeDependencies()
    generateOptimizationReport(stats)
    
    logSuccess('分析完成！')
    
  } catch (error) {
    logError(`分析失败: ${error.message}`)
    process.exit(1)
  }
}

// 如果直接运行此脚本
if (import.meta.url === `file://${process.argv[1]}`) {
  main()
}

export {
  analyzeBundleSizes,
  analyzeDependencies,
  generateOptimizationReport
}
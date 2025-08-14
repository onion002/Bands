#!/usr/bin/env node

/**
 * 🚀 性能检查脚本
 * 用于监控和分析应用性能指标
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取当前文件目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 性能检查配置
const CONFIG = {
  // 包大小阈值 (KB)
  thresholds: {
    js: {
      warning: 100,
      error: 500
    },
    css: {
      warning: 50,
      error: 200
    }
  },
  // 需要检查的目录
  distDir: 'dist',
  // 输出文件
  outputFile: 'performance-report.json'
};

/**
 * 分析构建产物
 */
function analyzeBuild() {
  const distPath = path.join(process.cwd(), CONFIG.distDir);
  
  if (!fs.existsSync(distPath)) {
    console.error('❌ 构建目录不存在，请先运行 npm run build');
    process.exit(1);
  }

  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalSize: 0,
      jsSize: 0,
      cssSize: 0,
      imageSize: 0,
      fontSize: 0
    },
    chunks: {
      js: [],
      css: [],
      images: [],
      fonts: []
    },
    issues: [],
    recommendations: []
  };

  // 分析文件
  analyzeDirectory(distPath, report);
  
  // 生成报告
  generateReport(report);
  
  return report;
}

/**
 * 分析目录结构
 */
function analyzeDirectory(dirPath, report, relativePath = '') {
  const items = fs.readdirSync(dirPath);
  
  items.forEach(item => {
    const fullPath = path.join(dirPath, item);
    const relativeItemPath = path.join(relativePath, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      analyzeDirectory(fullPath, report, relativeItemPath);
    } else {
      analyzeFile(fullPath, relativeItemPath, stat.size, report);
    }
  });
}

/**
 * 分析单个文件
 */
function analyzeFile(filePath, relativePath, size, report) {
  const ext = path.extname(filePath);
  const sizeKB = Math.round(size / 1024);
  
  // 更新总大小
  report.summary.totalSize += size;
  
  if (ext === '.js') {
    report.summary.jsSize += size;
    report.chunks.js.push({
      file: relativePath,
      size: sizeKB,
      sizeBytes: size
    });
    
    // 检查JS包大小
    if (sizeKB > CONFIG.thresholds.js.error) {
      report.issues.push({
        type: 'error',
        message: `JS包过大: ${relativePath} (${sizeKB}KB)`,
        file: relativePath,
        size: sizeKB
      });
    } else if (sizeKB > CONFIG.thresholds.js.warning) {
      report.issues.push({
        type: 'warning',
        message: `JS包较大: ${relativePath} (${sizeKB}KB)`,
        file: relativePath,
        size: sizeKB
      });
    }
  } else if (ext === '.css') {
    report.summary.cssSize += size;
    report.chunks.css.push({
      file: relativePath,
      size: sizeKB,
      sizeBytes: size
    });
    
    // 检查CSS包大小
    if (sizeKB > CONFIG.thresholds.css.error) {
      report.issues.push({
        type: 'error',
        message: `CSS包过大: ${relativePath} (${sizeKB}KB)`,
        file: relativePath,
        size: sizeKB
      });
    } else if (sizeKB > CONFIG.thresholds.css.warning) {
      report.issues.push({
        type: 'warning',
        message: `CSS包较大: ${relativePath} (${sizeKB}KB)`,
        file: relativePath,
        size: sizeKB
      });
    }
  } else if (['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'].includes(ext)) {
    report.summary.imageSize += size;
    report.chunks.images.push({
      file: relativePath,
      size: sizeKB,
      sizeBytes: size
    });
  } else if (['.woff', '.woff2', '.eot', '.ttf', '.otf'].includes(ext)) {
    report.summary.fontSize += size;
    report.chunks.fonts.push({
      file: relativePath,
      size: sizeKB,
      sizeBytes: size
    });
  }
}

/**
 * 生成性能报告
 */
function generateReport(report) {
  // 计算总大小 (MB)
  const totalMB = Math.round(report.summary.totalSize / (1024 * 1024) * 100) / 100;
  const jsMB = Math.round(report.summary.jsSize / (1024 * 1024) * 100) / 100;
  const cssMB = Math.round(report.summary.cssSize / (1024 * 1024) * 100) / 100;
  
  // 生成建议
  generateRecommendations(report);
  
  // 输出到控制台
  console.log('\n🚀 性能分析报告');
  console.log('='.repeat(50));
  console.log(`📅 生成时间: ${report.timestamp}`);
  console.log(`📦 总大小: ${totalMB}MB`);
  console.log(`🔧 JavaScript: ${jsMB}MB`);
  console.log(`🎨 CSS: ${cssMB}MB`);
  console.log(`🖼️  图片: ${Math.round(report.summary.imageSize / 1024)}KB`);
  console.log(`🔤 字体: ${Math.round(report.summary.fontSize / 1024)}KB`);
  
  // 显示问题
  if (report.issues.length > 0) {
    console.log('\n⚠️  发现的问题:');
    report.issues.forEach(issue => {
      const icon = issue.type === 'error' ? '❌' : '⚠️';
      console.log(`${icon} ${issue.message}`);
    });
  }
  
  // 显示建议
  if (report.recommendations.length > 0) {
    console.log('\n💡 优化建议:');
    report.recommendations.forEach((rec, index) => {
      console.log(`${index + 1}. ${rec}`);
    });
  }
  
  // 保存到文件
  const outputPath = path.join(process.cwd(), CONFIG.outputFile);
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  console.log(`\n📄 详细报告已保存到: ${CONFIG.outputFile}`);
  
  // 返回退出码
  const hasErrors = report.issues.some(issue => issue.type === 'error');
  process.exit(hasErrors ? 1 : 0);
}

/**
 * 生成优化建议
 */
function generateRecommendations(report) {
  const { jsSize, cssSize } = report.summary;
  
  // 检查JS包大小
  if (jsSize > 1024 * 1024) { // 1MB
    report.recommendations.push('JavaScript包过大，建议进一步代码分割');
  }
  
  // 检查CSS包大小
  if (cssSize > 200 * 1024) { // 200KB
    report.recommendations.push('CSS包过大，建议提取关键CSS并异步加载');
  }
  
  // 检查大文件
  const largeJsFiles = report.chunks.js.filter(chunk => chunk.size > 100);
  if (largeJsFiles.length > 0) {
    report.recommendations.push(`发现${largeJsFiles.length}个大JS文件，建议分析依赖关系`);
  }
  
  // 检查图片优化
  const largeImages = report.chunks.images.filter(img => img.size > 100);
  if (largeImages.length > 0) {
    report.recommendations.push(`发现${largeImages.length}个大图片文件，建议压缩或使用WebP格式`);
  }
  
  // 检查字体优化
  const largeFonts = report.chunks.fonts.filter(font => font.size > 50);
  if (largeFonts.length > 0) {
    report.recommendations.push(`发现${largeFonts.length}个大字体文件，建议使用font-display: swap`);
  }
  
  // 通用建议
  report.recommendations.push('考虑启用gzip/brotli压缩');
  report.recommendations.push('实现Service Worker缓存策略');
  report.recommendations.push('添加性能监控和分析');
}

/**
 * 主函数
 */
function main() {
  try {
    console.log('🔍 开始性能分析...');
    const report = analyzeBuild();
    console.log('✅ 性能分析完成');
  } catch (error) {
    console.error('❌ 性能分析失败:', error.message);
    process.exit(1);
  }
}

// 运行脚本
main();
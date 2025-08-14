import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { copyModuleAssetsPlugin, POSTER_GIRL_ASSET_CONFIG } from './build/plugins/copy-module-assets'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'

  return {
    plugins: [
      vue(),
      // 📦 模块资源复制插件
      copyModuleAssetsPlugin({
        modules: [
          POSTER_GIRL_ASSET_CONFIG,
          // 未来可以轻松添加其他模块：
          // MUSIC_BOX_ASSET_CONFIG,
          // OTHER_MODULE_ASSET_CONFIG
        ],
        verbose: isDev // 开发模式显示详细日志
      }),
      // 📊 Bundle 分析器（仅在生产构建时启用）
      !isDev && visualizer({
        filename: 'dist/bundle-analysis.html',
        open: false,
        gzipSize: true,
        brotliSize: true,
      })
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    server: {
      host: '0.0.0.0', // 允许外部访问
      port: 5173,
      proxy: {
        '/uploads': isDev ? 'http://localhost:5000' : 'http://47.108.249.242:5000',
        '/api': isDev ? 'http://localhost:5000' : 'http://47.108.249.242:5000'
      }
    },
    preview: {
      host: '0.0.0.0', // 生产预览也允许外部访问
      port: 3000
    },
    css: {
      preprocessorOptions: {
        scss: {
          quietDeps: true, // 静默依赖警告
          silenceDeprecations: ['legacy-js-api', 'mixed-decls', 'global-builtin', 'color-functions'],
          logger: {
            warn: () => {} // 完全静默警告
          }
        }
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false, // 生产环境不生成sourcemap
      minify: 'terser', // 使用 terser 进行更好的压缩
      terserOptions: {
        compress: {
          drop_console: !isDev, // 生产环境移除 console
          drop_debugger: !isDev, // 生产环境移除 debugger
        }
      },
      rollupOptions: {
        output: {
          // 🚀 优化的代码分割策略
          manualChunks: (id) => {
            // 将 node_modules 中的库分离到 vendor chunk
            if (id.includes('node_modules')) {
              if (id.includes('vue')) {
                return 'vue-vendor'
              }
              if (id.includes('marked') || id.includes('highlight.js')) {
                return 'markdown-vendor'
              }
              return 'vendor'
            }
            // 本地模块分块
            if (id.includes('@/modules/poster-girl')) {
              return 'poster-girl'
            }
            if (id.includes('@/components/MusicBox') || id.includes('@/views/MusicTeacherView')) {
              return 'music-components'
            }
          },
          // 优化 chunk 命名
          chunkFileNames: 'js/[name]-[hash].js',
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const ext = info[info.length - 1]
            if (/\.(css)$/.test(assetInfo.name)) {
              return `css/[name]-[hash].${ext}`
            }
            return `assets/[name]-[hash].${ext}`
          }
        }
      },
      // 设置 chunk 大小警告阈值
      chunkSizeWarningLimit: 1000,
      // 启用 CSS 代码分割
      cssCodeSplit: true
    },
    // 优化依赖预构建
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios'],
      exclude: ['@/modules/poster-girl'], // 排除本地模块
    },
    // 启用 esbuild 优化
    esbuild: {
      drop: isDev ? [] : ['console', 'debugger'],
      pure: isDev ? [] : ['console.log', 'console.info', 'console.debug']
    }
  }
})

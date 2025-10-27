import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { copyModuleAssetsPlugin, POSTER_GIRL_ASSET_CONFIG } from './build/plugins/copy-module-assets'

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
        '/uploads': isDev ? 'http://localhost:5000' : 'http://47.108.30.30:5000',
        '/api': isDev ? 'http://localhost:5000' : 'http://47.108.30.30:5000' // 新增这一行
      }
    },
    preview: {
      host: true, // 允许外部访问，禁用host检查
      port: 3000,
      allowedHosts: ['bands.icu', 'www.bands.icu', 'localhost', '127.0.0.1']
    },
    css: {
      preprocessorOptions: {
        scss: {
          quietDeps: true, // 静默依赖警告
          silenceDeprecations: ['legacy-js-api', 'mixed-decls', 'global-builtin', 'color-functions'], // 静默特定弃用警告
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
      minify: 'terser', // 使用terser进行更好的压缩
      terserOptions: {
        compress: {
          drop_console: !isDev, // 生产环境移除console
          drop_debugger: !isDev, // 生产环境移除debugger
          pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn']
        }
      },
      rollupOptions: {
        output: {
          // 🚀 优化的代码分割策略
          manualChunks: {
            // 核心Vue库
            'vue-core': ['vue', 'vue-router', 'pinia'],
            // 第三方库
            'vendor': ['axios'],
            // 工具库
            'utils': ['marked', 'highlight.js'],
            // 按功能分组的路由
            'admin': [
              'src/views/admin/AdminUsersView.vue',
              'src/views/admin/AdminReportsView.vue'
            ],
            'band-management': [
              'src/views/bands/BandManagement.vue',
              'src/views/bands/MemberManagement.vue',
              'src/views/bands/EventManagement.vue'
            ]
          },
          // 优化chunk命名
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk'
            return `js/[name]-[hash].js`
          },
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const ext = info[info.length - 1]
            if (/\.(css)$/.test(assetInfo.name)) {
              return `css/[name]-[hash].${ext}`
            }
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) {
              return `images/[name]-[hash].${ext}`
            }
            if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name)) {
              return `fonts/[name]-[hash].${ext}`
            }
            return `assets/[name]-[hash].${ext}`
          }
        }
      },
      // 设置chunk大小警告阈值
      chunkSizeWarningLimit: 500,
      // 启用CSS代码分割
      cssCodeSplit: true,
      // 优化依赖预构建
      optimizeDeps: {
        include: ['vue', 'vue-router', 'pinia', 'axios'],
        exclude: ['src/modules/poster-girl']
      }
    },
    // 优化依赖预构建
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios'],
      exclude: ['src/modules/poster-girl']
    }
  }
})

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
          pure_funcs: isDev ? [] : ['console.log', 'console.info', 'console.debug']
        }
      },
      rollupOptions: {
        output: {
          // 优化代码分割策略 - 基于实际依赖
          manualChunks: {
            // 核心框架库
            'vue-core': ['vue', 'vue-router', 'pinia'],
            // 按功能模块分割
            'admin': [
              './src/views/admin/AdminUsersView.vue',
              './src/views/admin/AdminReportsView.vue'
            ],
            'band-management': [
              './src/views/bands/BandManagement.vue',
              './src/views/bands/MemberManagement.vue',
              './src/views/bands/EventManagement.vue'
            ],
            'auth': [
              './src/views/auth/LoginView.vue',
              './src/views/auth/RegisterView.vue'
            ],
            'music-features': [
              './src/views/MusicTeacherView.vue',
              './src/views/MusicBoxDemo.vue'
            ]
          },
          // 优化chunk命名
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk'
            return `js/[name]-[hash].js`
          },
          // 优化资源命名
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name?.split('.') || []
            const ext = info[info.length - 1]
            if (/\.(css)$/.test(assetInfo.name || '')) {
              return `css/[name]-[hash].${ext}`
            }
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name || '')) {
              return `images/[name]-[hash].${ext}`
            }
            return `assets/[name]-[hash].${ext}`
          }
        },
        // 优化依赖处理
        external: [],
        // 优化模块解析
        treeshake: {
          moduleSideEffects: false,
          propertyReadSideEffects: false,
          unknownGlobalSideEffects: false
        }
      },
      // 设置chunk大小警告阈值
      chunkSizeWarningLimit: 1000,
      // 启用CSS代码分割
      cssCodeSplit: true,
      // 优化目标
      target: 'es2015'
    },
    // 优化依赖预构建
    optimizeDeps: {
      include: [
        'vue',
        'vue-router', 
        'pinia',
        'axios'
      ],
      exclude: [
        // 排除不需要预构建的依赖
      ]
    }
  }
})

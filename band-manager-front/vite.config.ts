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
        '/uploads': isDev ? 'http://localhost:5000' : 'http://localhost:5000',
        '/api': isDev ? 'http://localhost:5000' : 'http://localhost:5000' // 新增这一行
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
          pure_funcs: !isDev ? ['console.log', 'console.info', 'console.debug'] : [], // 生产环境移除特定函数
          passes: 2, // 多次压缩以获得更好的结果
        },
        mangle: {
          safari10: true, // 兼容Safari 10
          toplevel: true, // 混淆顶级作用域
        }
      },
      rollupOptions: {
        output: {
          // 优化chunk分割策略
          manualChunks: {
            // 核心Vue库
            'vue-core': ['vue', 'vue-router', 'pinia']
          },
          // 优化chunk命名
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk'
            return `js/[name]-[hash].js`
          },
          // 优化资源命名
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const ext = info[info.length - 1]
            if (/\.(css)$/.test(assetInfo.name)) {
              return `css/[name]-[hash].${ext}`
            }
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) {
              return `images/[name]-[hash].${ext}`
            }
            return `assets/[name]-[hash].${ext}`
          }
        },
        // 外部依赖配置
        external: [],
        // 优化依赖处理
        onwarn(warning, warn) {
          // 忽略某些警告
          if (warning.code === 'CIRCULAR_DEPENDENCY') return
          if (warning.code === 'UNUSED_EXTERNAL_IMPORT') return
          warn(warning)
        }
      },
      // 设置chunk大小警告限制
      chunkSizeWarningLimit: 1000,
      // 启用CSS代码分割
      cssCodeSplit: true,
      // 启用动态导入
      dynamicImportVarsOptions: {
        warnOnError: false,
        exclude: []
      },
      // 启用目标优化
      target: 'es2015',
      // 启用模块预加载
      modulePreload: {
        polyfill: true
      }
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
      ],
      // 强制预构建
      force: false
    },
    // 启用实验性功能
    experimental: {
      renderBuiltUrl(filename, { hostType }) {
        if (hostType === 'js') {
          return { js: `__VITE_BASE_URL__ + ${JSON.stringify(filename)}` }
        } else {
          return { relative: true }
        }
      }
    },
    // 定义环境变量
    define: {
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false,
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
    }
  }
})

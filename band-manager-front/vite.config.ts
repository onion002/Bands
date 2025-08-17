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
        '/uploads': isDev ? 'http://localhost:5000' : 'http://47.107.79.244:5000',
        '/api': isDev ? 'http://localhost:5000' : 'http://47.107.79.244:5000' // 新增这一行
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
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia']
          }
        }
      }
    }
  }
})

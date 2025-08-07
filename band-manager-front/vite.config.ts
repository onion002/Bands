import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'

  return {
    plugins: [vue()],
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
        '/api': isDev ? 'http://localhost:5000' : 'http://47.108.249.242:5000' // 新增这一行
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

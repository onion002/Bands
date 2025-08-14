import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { copyModuleAssetsPlugin, POSTER_GIRL_ASSET_CONFIG } from './build/plugins/copy-module-assets'

// 分析模式的Vite配置
export default defineConfig({
  mode: 'analyze',
  plugins: [
    vue(),
    copyModuleAssetsPlugin({
      modules: [POSTER_GIRL_ASSET_CONFIG],
      verbose: true
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // 分析模式启用sourcemap
    minify: false, // 分析模式不压缩
    rollupOptions: {
      output: {
        // 详细的chunk分析
        manualChunks: {
          'vue-core': ['vue', 'vue-router', 'pinia'],
          'vendor-marked': ['marked'],
          'vendor-highlight': ['highlight.js'],
          'poster-girl': [
            '@/modules/poster-girl/components/PosterGirl.vue',
            '@/modules/poster-girl/components/PosterGirlSettings.vue',
            '@/modules/poster-girl/services/live2dService',
            '@/modules/poster-girl/services/modelManager'
          ],
          'music-components': [
            '@/components/MusicBox.vue',
            '@/components/PosterGirl.vue'
          ],
          'admin-pages': [
            '@/views/admin/AdminUsersView.vue',
            '@/views/admin/AdminReportsView.vue',
            '@/views/bands/BandManagement.vue',
            '@/views/bands/MemberManagement.vue',
            '@/views/bands/EventManagement.vue'
          ]
        },
        // 详细的chunk信息
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      },
      // 详细的依赖分析
      onwarn(warning, warn) {
        // 显示所有警告以进行分析
        warn(warning)
      }
    },
    // 分析模式启用详细报告
    reportCompressedSize: true,
    chunkSizeWarningLimit: 1000
  },
  // 分析模式启用详细日志
  logLevel: 'info'
})
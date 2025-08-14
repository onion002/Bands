import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// 使用现成的vite-plugin-static-copy插件
// npm install vite-plugin-static-copy --save-dev

// import { viteStaticCopy } from 'vite-plugin-static-copy'

// export default defineConfig(({ mode }) => {
//   const isDev = mode === 'development'

//   return {
//     plugins: [
//       vue(),
//       // 📦 使用现成插件复制静态资源
//       viteStaticCopy({
//         targets: [
//           {
//             src: 'src/modules/poster-girl/assets/*',
//             dest: 'poster-girl-assets'
//           },
//           // 未来可以轻松添加其他模块：
//           // {
//           //   src: 'src/modules/music-box/assets/*',
//           //   dest: 'music-box-assets'
//           // }
//         ]
//       })
//     ],
//     // ... 其他配置
//   }
// })

/**
 * 方案2优势：
 * ✅ 使用成熟的开源插件
 * ✅ 功能丰富（支持glob、转换等）
 * ✅ 社区维护，bug更少
 * ✅ 配置简洁
 * 
 * 劣势：
 * ⚠️ 增加一个依赖
 * ⚠️ 需要学习插件API
 */

/// <reference types="vite/client" />

declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
  }
  
  // 解决Element Plus样式导入问题
  declare module 'element-plus/dist/index.css' {
    const css: string
    export default css
  }
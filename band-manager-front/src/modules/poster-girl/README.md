# 🎭 看板娘模块

这是一个独立的Live2D看板娘系统模块，支持模型切换、拖拽、自定义配置等功能。

## 📁 模块结构

```
src/modules/poster-girl/
├── index.ts                    # 统一导出文件
├── components/                 # Vue组件
│   ├── PosterGirl.vue         # 主看板娘组件
│   └── PosterGirlSettings.vue # 设置页面组件
├── services/                   # 服务层
│   ├── live2dService.ts       # Live2D渲染服务
│   └── modelManager.ts        # 模型管理器
├── composables/               # 组合式API
│   ├── usePosterGirl.ts       # 主要逻辑Composable
│   └── useModelManager.ts     # 模型管理Composable
├── config/                    # 配置文件
│   └── posterGirl.ts          # 看板娘配置
├── utils/                     # 工具函数
│   └── modelValidator.ts      # 模型验证工具
├── types/                     # 类型定义
│   └── index.ts               # 模块类型定义
└── assets/                    # 静态资源
```

## 🚀 使用方法

### 1. 组件使用

```vue
<template>
  <div>
    <!-- 直接使用组件 -->
    <PosterGirl />
    
    <!-- 或使用模块导入 -->
    <poster-girl />
  </div>
</template>

<script setup>
// 方式1: 直接导入组件
import { PosterGirl } from '@/modules/poster-girl'

// 方式2: 使用插件注册的全局组件（无需导入）
</script>
```

### 2. 组合式API使用

```vue
<script setup>
import { usePosterGirl, useModelManager } from '@/modules/poster-girl'

// 使用看板娘主要功能
const {
  isHidden,
  showMessage,
  switchModel,
  initLive2D
} = usePosterGirl()

// 使用模型管理器
const {
  availableModels,
  currentModelIndex,
  switchToRandomModel
} = useModelManager()

// 初始化
onMounted(async () => {
  await initLive2D()
})
</script>
```

### 3. 配置使用

```typescript
import { getCurrentConfig, saveConfig } from '@/modules/poster-girl'

// 获取当前配置
const config = getCurrentConfig()

// 修改配置
config.mode = 'draggable'
config.tips = true

// 保存配置
saveConfig(config)
```

### 4. Vue插件使用

```typescript
// main.ts
import { createApp } from 'vue'
import { posterGirlPlugin } from '@/modules/poster-girl'

const app = createApp(App)

// 注册插件
app.use(posterGirlPlugin, {
  // 自动注册全局组件
  globalComponents: true,
  // 自动初始化
  autoInit: true,
  // 默认配置
  defaultConfig: {
    mode: 'fixed',
    tips: true
  }
})
```

## 🔧 API文档

### 组件Props

#### PosterGirl

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| config | `PosterGirlConfig` | - | 自定义配置 |

### 组合式API

#### usePosterGirl()

返回看板娘的主要状态和方法：

```typescript
interface UsePosterGirlReturn {
  // 状态
  isHidden: Ref<boolean>
  isDragging: Ref<boolean>
  showActions: Ref<boolean>
  showDialog: Ref<boolean>
  currentMessage: Ref<string>
  
  // 配置
  pioConfig: Ref<PosterGirlConfig>
  
  // 方法
  initLive2D: () => Promise<void>
  switchModel: () => Promise<void>
  showMessage: (message: string | string[], duration?: number) => void
  hidePosterGirl: () => void
  showPosterGirl: () => void
  handleTouch: () => void
  
  // 导航方法
  navigateToMusicBox: () => void
  navigateToSettings: () => void
  navigateToMusicTeacher: () => void
  
  // 拖拽相关
  startDrag: (event: MouseEvent | TouchEvent) => void
  
  // 生命周期
  reloadPosterGirl: () => void
  togglePosterGirl: () => void
  togglePosition: () => void
}
```

#### useModelManager()

返回模型管理相关的状态和方法：

```typescript
interface UseModelManagerReturn {
  // 状态
  availableModels: Ref<string[]>
  currentModelIndex: Ref<number>
  isInitialized: Ref<boolean>
  
  // 方法
  init: () => Promise<void>
  loadDefaultModel: (defaultModelPath?: string) => Promise<boolean>
  switchToRandomModel: () => Promise<ModelSwitchResult>
  switchToNextModel: () => Promise<ModelSwitchResult>
  getCurrentModelPath: () => string
  getModelStats: () => ModelStats
  reset: () => void
}
```

### 服务API

#### live2dService

Live2D渲染服务：

```typescript
// 初始化
await live2dService.init(canvas)

// 加载模型
await live2dService.loadModel('/path/to/model.json')

// 销毁服务
live2dService.destroy()
```

#### modelManager

模型管理器：

```typescript
// 初始化
await modelManager.init()

// 随机切换模型
const result = await modelManager.switchToRandomModel()

// 获取统计信息
const stats = modelManager.getModelStats()
```

## 🎨 主题配置

看板娘支持丰富的配置选项：

```typescript
interface PosterGirlConfig {
  mode: 'static' | 'fixed' | 'draggable'  // 显示模式
  hidden: boolean                          // 是否隐藏
  size: {                                 // 尺寸配置
    width: number
    height: number
  }
  content: {                              // 消息内容
    welcome: string | string[]
    touch?: string | string[]
    skin?: [string, string]
    home?: string | string[]
    close?: string | string[]
    link?: string
    referer?: string
    custom?: Array<{
      selector: string
      type?: 'read' | 'link'
      text?: string
    }>
  }
  night?: string                          // 夜晚模式
  model: string[]                         // 可用模型列表
  defaultModel?: string                   // 默认模型
  tips?: boolean                          // 是否显示提示
  dragPosition?: {                        // 拖拽位置
    x: number
    y: number
  }
}
```

## 🔄 模型管理

### 模型格式

支持标准的Live2D模型格式：

```json
{
  "version": "1.0.0",
  "model": "model.moc",
  "textures": [
    "texture_00.png"
  ],
  "physics": "physics.json",
  "motions": {
    "idle": [
      {"file": "idle_01.mtn"}
    ],
    "tap_body": [
      {"file": "touch_01.mtn", "sound": "voice_01.wav"}
    ]
  }
}
```

### 添加新模型

1. 将模型文件放置在 `src\modules\poster-girl\assets\models` 目录下
2. 在配置文件中添加模型路径
3. 验证模型完整性

```typescript
import { validateModel } from '@/modules/poster-girl'

const result = await validateModel('/pio/models/new-model/model.json')
if (result.isValid) {
  console.log('模型验证成功！')
} else {
  console.error('模型验证失败:', result.errors)
}
```

## 🛠️ 开发指南

### 扩展组合式API

创建新的组合式API时，请遵循以下模式：

```typescript
// composables/useCustomFeature.ts
import { ref, computed } from 'vue'
import type { UseCustomFeatureReturn } from '../types'

export function useCustomFeature(): UseCustomFeatureReturn {
  const state = ref(false)
  
  const toggleState = () => {
    state.value = !state.value
  }
  
  return {
    state,
    toggleState
  }
}
```

### 添加新的服务

服务应该遵循单例模式：

```typescript
// services/customService.ts
class CustomService {
  private static instance: CustomService
  
  static getInstance(): CustomService {
    if (!this.instance) {
      this.instance = new CustomService()
    }
    return this.instance
  }
  
  private constructor() {
    // 初始化逻辑
  }
}

export const customService = CustomService.getInstance()
```

## 📚 相关文档

- [Live2D官方文档](https://www.live2d.com/)
- [Vue 3 组合式API](https://cn.vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript指南](https://www.typescriptlang.org/docs/)

## 🐛 问题排查

### 常见问题

1. **模型加载失败**
   - 检查模型文件路径是否正确
   - 验证模型文件完整性
   - 确认网络连接正常

2. **拖拽功能异常**
   - 确认配置中的 `mode` 设置为 `draggable`
   - 检查CSS样式是否冲突

3. **随机切换不生效**
   - 确认配置中有多个可用模型
   - 检查模型验证是否通过

### 调试模式

开启调试模式以获取详细日志：

```typescript
// 在浏览器控制台中设置
localStorage.setItem('poster-girl-debug', 'true')

// 然后刷新页面查看详细日志
```

## 📄 许可证

此模块遵循项目的开源许可证。

# Vue版本看板娘完全集成指南

## 🎯 概述

本项目已经完全将看板娘功能集成到Vue组件中，不再依赖外部的pio.js和pio.css文件。所有功能都通过Vue组件和TypeScript服务实现。

## ✨ 主要特性

### 🎭 核心功能
- **Live2D模型渲染** - 通过Canvas API实现
- **拖拽定位** - 支持自由拖拽到任意位置
- **交互提示** - 触摸、欢迎、时间等提示系统
- **模型切换** - 支持多个Live2D模型
- **响应式设计** - 适配不同屏幕尺寸

### 🎨 界面元素
- **操作按钮** - 音乐盒、设置、模型切换、关闭
- **对话框** - 动态显示各种提示信息
- **显示/隐藏** - 支持隐藏和重新显示
- **悬停效果** - 鼠标悬停时显示操作按钮

## 🏗️ 架构设计

### 📁 文件结构
```
src/
├── components/
│   └── PosterGirl.vue          # 主看板娘组件
├── services/
│   └── live2dService.ts        # Live2D服务
└── config/
    └── posterGirl.ts           # 配置管理
```

### 🔧 核心组件

#### PosterGirl.vue
- 主要的看板娘显示组件
- 处理所有用户交互
- 管理拖拽、显示/隐藏状态
- 集成Live2D服务

#### live2dService.ts
- Live2D模型加载和渲染
- Canvas上下文管理
- 脚本动态加载
- 服务生命周期管理

## 🚀 使用方法

### 1. 基本使用
```vue
<template>
  <PosterGirl ref="posterGirlRef" />
</template>

<script setup>
import PosterGirl from '@/components/PosterGirl.vue'
import { ref } from 'vue'

const posterGirlRef = ref()
</script>
```

### 2. 控制看板娘
```typescript
// 重载看板娘
posterGirlRef.value.reloadPosterGirl()

// 切换显示/隐藏
posterGirlRef.value.togglePosterGirl()
```

### 3. 配置自定义
```typescript
import { getCurrentConfig, saveConfig } from '@/config/posterGirl'

// 获取当前配置
const config = getCurrentConfig()

// 修改配置
config.content.welcome = ["自定义欢迎语"]
config.size.width = 320
config.size.height = 280

// 保存配置
saveConfig(config)
```

## ⚙️ 配置选项

### 基础配置
```typescript
interface PosterGirlConfig {
  mode: 'static' | 'fixed' | 'draggable'  // 显示模式
  hidden: boolean                          // 是否隐藏
  size: { width: number, height: number } // 尺寸
  tips?: boolean                          // 时间提示
}
```

### 内容配置
```typescript
content: {
  welcome: string | string[]              // 欢迎语
  touch?: string | string[]               // 触摸提示
  skin?: [string, string]                // 模型切换提示
  custom?: Array<{                       // 自定义提示
    selector: string
    type?: 'read' | 'link'
    text?: string
  }>
}
```

### 模型配置
```typescript
model: [
  "/pio/models/pio/model.json",          // 默认模型
  "/pio/models/remu/model.json"          // 备用模型
]
```

## 🎨 自定义样式

### 主题定制
```scss
.poster-girl-container {
  // 自定义容器样式
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.pio-action {
  // 自定义按钮样式
  span {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    &:hover {
      transform: scale(1.2);
    }
  }
}
```

### 响应式设计
```scss
@media (max-width: 768px) {
  .poster-girl-container {
    display: none; // 移动端隐藏
  }
}
```

## 🔄 拖拽功能

### 启用拖拽
```typescript
// 在配置中设置模式为draggable
config.mode = 'draggable'
```

### 拖拽位置保存
- 拖拽位置自动保存到localStorage
- 页面刷新后保持位置
- 支持触摸设备拖拽

## 🎭 Live2D集成

### 当前状态
- 使用Canvas API绘制占位符
- 支持动态加载Live2D脚本
- 预留模型加载接口

### 未来扩展
- 集成官方Live2D SDK
- 支持更多模型格式
- 添加动画和表情系统

## 🐛 故障排除

### 常见问题

#### 1. 看板娘不显示
- 检查组件是否正确引入
- 确认localStorage中的posterGirl值
- 查看控制台错误信息

#### 2. 拖拽不工作
- 确认mode设置为'draggable'
- 检查触摸事件支持
- 验证拖拽权限设置

#### 3. 配置不生效
- 检查配置文件格式
- 确认saveConfig调用成功
- 验证localStorage权限

### 调试技巧
```typescript
// 启用详细日志
console.log('看板娘配置:', getCurrentConfig())
console.log('Live2D服务状态:', live2dService.isReady())

// 检查DOM元素
console.log('Canvas元素:', document.querySelector('canvas'))
```

## 📱 移动端支持

### 触摸优化
- 支持触摸拖拽
- 触摸友好的按钮尺寸
- 响应式布局适配

### 性能优化
- 移动端自动隐藏
- 触摸事件节流
- 动画性能优化

## 🔮 未来计划

### 短期目标
- [ ] 完善Live2D模型加载
- [ ] 添加更多交互效果
- [ ] 优化拖拽体验

### 长期目标
- [ ] 支持3D模型
- [ ] 添加语音交互
- [ ] 集成AI助手功能

## 📄 许可证

本项目遵循GPL 2.0开源协议，基于保罗的看板娘插件重构而来。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

**注意**: 这是一个完全重构的Vue版本，与原始的pio.js插件在实现方式上有很大差异，但保持了相同的功能和用户体验。

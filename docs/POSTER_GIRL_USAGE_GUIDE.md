# 🎭 看板娘模块使用指南

## ✅ 模块重构完成

看板娘系统已成功重构为独立模块，现在使用最佳实践方式进行应用。

## 🚀 推荐使用方式

### 1. Vue插件方式（推荐⭐）

**已在 `main.ts` 中配置：**

```typescript
import { posterGirlPlugin } from '@/modules/poster-girl'

app.use(posterGirlPlugin, {
  globalComponents: true,  // 自动注册全局组件
  autoInit: true,         // 自动初始化
  defaultConfig: {
    mode: 'draggable',    // 支持拖拽
    tips: true,           // 显示智能提示
    size: {
      width: 280,
      height: 250
    }
  }
})
```

**使用效果：**
- ✅ 全局组件自动注册，无需手动导入
- ✅ 一次配置，全项目生效
- ✅ 智能的默认配置
- ✅ 自动初始化

### 2. 模板中直接使用

```vue
<template>
  <div>
    <!-- 直接使用全局组件，无需导入 -->
    <PosterGirl ref="posterGirlRef" />
  </div>
</template>

<script setup>
// 无需导入组件，已全局注册
import { ref } from 'vue'
const posterGirlRef = ref()
</script>
```

### 3. 组合式API使用（高级功能）

```vue
<script setup>
import { usePosterGirl, useModelManager } from '@/modules/poster-girl'

// 主要功能
const {
  isHidden,
  showMessage,
  switchModel,
  togglePosterGirl
} = usePosterGirl()

// 模型管理
const {
  availableModels,
  switchToRandomModel
} = useModelManager()

// 使用示例
const handleCustomAction = async () => {
  showMessage('你好！这是自定义消息')
  await switchToRandomModel()
}
</script>
```

## 📁 项目结构

```
src/
├── modules/
│   └── poster-girl/              # 看板娘模块
│       ├── index.ts              # 统一导出 + Vue插件
│       ├── components/           # Vue组件
│       ├── services/             # 服务层
│       ├── composables/          # 组合式API
│       ├── config/               # 配置
│       ├── utils/                # 工具函数
│       ├── types/                # 类型定义
│       └── README.md             # 详细文档
├── main.ts                       # 插件已注册 ✅
├── App.vue                       # 主应用使用组件 ✅
└── views/
    ├── PosterGirlDemo.vue        # 演示页面 ✅
    └── ...
```

## 🌟 新增功能

### 1. 演示页面
- **路径：** `/poster-girl-demo`
- **功能：** 展示所有API和功能
- **包含：** 状态监控、控制面板、API示例

### 2. 设置页面
- **路径：** `/poster-girl-settings`
- **功能：** 配置看板娘参数
- **支持：** 模型选择、外观设置、行为配置

### 3. 导航集成
- **位置：** 顶部导航栏
- **链接：** "🎭 看板娘" 直达演示页面

## 🔧 配置选项

### 默认配置（已优化）

```typescript
{
  mode: 'draggable',        // 可拖拽模式
  tips: true,               // 智能提示开启
  size: {                   // 合适的尺寸
    width: 280,
    height: 250
  },
  model: [                  // 支持多模型
    "/pio/models/pio/model.json",
    "/pio/models/remu/model.json", 
    "/pio/models/umaru/xiaomai.model.json"
  ],
  defaultModel: "/pio/models/pio/model.json"
}
```

### 自定义配置

```typescript
// 修改配置
import { getCurrentConfig, saveConfig } from '@/modules/poster-girl'

const config = getCurrentConfig()
config.mode = 'fixed'       // 固定位置
config.tips = false         // 关闭提示
saveConfig(config)
```

## 🎯 核心功能

### ✅ 已实现功能

1. **🎨 模型管理**
   - 随机模型切换
   - 多模型支持
   - 模型验证

2. **🖱️ 交互功能**
   - 拖拽定位
   - 触摸响应
   - 智能对话

3. **⚙️ 配置系统**
   - 持久化配置
   - 实时配置更新
   - 类型安全

4. **🔧 开发工具**
   - 组合式API
   - 完整类型定义
   - 详细文档

### 🚀 使用体验

- **👆 点击看板娘**：触发随机对话
- **🎲 点击切换按钮**：随机切换模型
- **👋 拖拽**：自由移动位置
- **⚙️ 设置**：个性化配置
- **💬 智能提示**：时间相关问候

## 📖 详细文档

- **模块README：** `src/modules/poster-girl/README.md`
- **API文档：** 包含完整的接口说明
- **使用示例：** 演示页面实际代码

## 🎉 重构成果

### ✅ 优化效果

1. **🏗️ 架构优化**
   - 模块化设计
   - 清晰的依赖关系
   - 易于维护和扩展

2. **💻 开发体验**
   - Vue插件一键使用
   - 组合式API灵活控制
   - 完整的TypeScript支持

3. **🎨 用户体验**
   - 流畅的交互动画
   - 智能的消息提示
   - 可自定义的外观

4. **📦 可移植性**
   - 独立的模块结构
   - 统一的导出接口
   - 完整的文档说明

## 🔍 快速开始

1. **查看演示：** 访问 `/poster-girl-demo`
2. **配置设置：** 访问 `/poster-girl-settings`  
3. **API使用：** 参考演示页面源码
4. **深入了解：** 阅读模块README

**现在就开始体验全新的看板娘系统吧！** 🎭✨

# 卡片组件使用指南

## 🎯 概述

我们已经将乐队、成员、活动卡片重构为可复用的组件，这些组件可以在所有页面中使用，确保样式一致性和代码复用性。

## 🎵 组件列表

### 1. BandCard - 乐队卡片组件
**文件位置**: `src/components/BandCard.vue`

### 2. MemberCard - 成员卡片组件  
**文件位置**: `src/components/MemberCard.vue`

### 3. EventCard - 活动卡片组件
**文件位置**: `src/components/EventCard.vue`

## 🔧 使用方法

### 基本用法

```vue
<template>
  <!-- 乐队卡片 -->
  <BandCard :band="bandData" />
  
  <!-- 成员卡片 -->
  <MemberCard :member="memberData" />
  
  <!-- 活动卡片 -->
  <EventCard :event="eventData" />
</template>

<script setup lang="ts">
import BandCard from '@/components/BandCard.vue'
import MemberCard from '@/components/MemberCard.vue'
import EventCard from '@/components/EventCard.vue'
</script>
```

### 高级用法

```vue
<template>
  <!-- 带批量选择功能的乐队卡片 -->
  <BandCard 
    :band="band" 
    :selected="selectedBands.includes(band.id)"
    :show-batch-checkbox="true"
    :show-actions="true"
    @selection-change="handleSelectionChange"
    @edit="handleEdit"
    @delete="handleDelete"
    @view="handleView"
  />
  
  <!-- 只读模式的成员卡片 -->
  <MemberCard 
    :member="member" 
    :show-actions="false"
  />
  
  <!-- 带播放按钮的活动卡片 -->
  <EventCard 
    :event="event" 
    :show-play-button="true"
    @play="handlePlay"
  />
</template>
```

## 📋 Props 配置

### BandCard Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `band` | `Band` | 必填 | 乐队数据对象 |
| `selected` | `boolean` | `false` | 是否被选中（批量模式） |
| `showBatchCheckbox` | `boolean` | `false` | 是否显示批量选择复选框 |
| `showPlayButton` | `boolean` | `false` | 是否显示播放按钮 |
| `showActions` | `boolean` | `false` | 是否显示操作按钮 |

### MemberCard Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `member` | `Member` | 必填 | 成员数据对象 |
| `selected` | `boolean` | `false` | 是否被选中（批量模式） |
| `showBatchCheckbox` | `boolean` | `false` | 是否显示批量选择复选框 |
| `showActions` | `boolean` | `false` | 是否显示操作按钮 |

### EventCard Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `event` | `Event` | 必填 | 活动数据对象 |
| `selected` | `boolean` | `false` | 是否被选中（批量模式） |
| `showBatchCheckbox` | `boolean` | `false` | 是否显示批量选择复选框 |
| `showActions` | `boolean` | `false` | 是否显示操作按钮 |

## 🎯 事件处理

### BandCard 事件

```typescript
// 批量选择变化
@selection-change="(value: boolean) => void"

// 播放
@play="() => void"

// 编辑
@edit="() => void"

// 删除
@delete="() => void"

// 查看详情
@view="() => void"
```

### MemberCard 事件

```typescript
// 批量选择变化
@selection-change="(value: boolean) => void"

// 编辑
@edit="() => void"

// 删除
@delete="() => void"

// 查看详情
@view="() => void"
```

### EventCard 事件

```typescript
// 批量选择变化
@selection-change="(value: boolean) => void"

// 编辑
@edit="() => void"

// 删除
@delete="() => void"

// 查看详情
@view="() => void"
```

## 📊 数据接口

### Band 接口

```typescript
interface Band {
  id: number
  name: string
  genre?: string
  year?: number
  bio?: string
  banner_image_url?: string
  member_count?: number
  primary_color?: string
}
```

### Member 接口

```typescript
interface Member {
  id: number
  name: string
  role?: string
  avatar_url?: string
  band_names?: string[]
  join_date?: string
  status?: string
}
```

### Event 接口

```typescript
interface Event {
  id: number
  title: string
  description?: string
  event_date: string
  venue?: string
  band_names?: string[]
  status: string
  poster_image_url?: string
}
```

## 🎨 样式特性

### 1. 响应式设计
- 自动适配不同屏幕尺寸
- 移动端友好的布局调整

### 2. 交互效果
- 悬停动画和过渡效果
- 图片缩放和颜色变化
- 平滑的动画过渡

### 3. 主题一致性
- 使用项目统一的色彩变量
- 一致的边框、圆角和阴影
- 统一的字体和间距规范

## 📱 响应式断点

- **桌面端**: ≥ 768px，完整布局
- **移动端**: < 768px，优化布局

## 🔄 迁移指南

### 从内联卡片迁移到组件

**之前**:
```vue
<div class="band-card card card-interactive">
  <!-- 复杂的卡片内容 -->
</div>
```

**现在**:
```vue
<BandCard :band="bandData" />
```

### 批量操作支持

```vue
<template>
  <div class="bands-grid">
    <BandCard
      v-for="band in bands"
      :key="band.id"
      :band="band"
      :selected="selectedBands.includes(band.id)"
      :show-batch-checkbox="batchMode"
      @selection-change="handleSelectionChange"
    />
  </div>
</template>

<script setup lang="ts">
const selectedBands = ref<number[]>([])
const batchMode = ref(false)

const handleSelectionChange = (bandId: number, selected: boolean) => {
  if (selected) {
    selectedBands.value.push(bandId)
  } else {
    selectedBands.value = selectedBands.value.filter(id => id !== bandId)
  }
}
</script>
```

## 🚀 性能优化

### 1. 组件懒加载
```vue
<script setup lang="ts">
// 按需导入组件
const BandCard = defineAsyncComponent(() => import('@/components/BandCard.vue'))
</script>
```

### 2. 虚拟滚动（大量数据）
```vue
<template>
  <VirtualList
    :items="bands"
    :item-height="300"
    v-slot="{ item }"
  >
    <BandCard :band="item" />
  </VirtualList>
</template>
```

## 🧪 测试建议

### 1. 组件测试
```typescript
import { mount } from '@vue/test-utils'
import BandCard from '@/components/BandCard.vue'

describe('BandCard', () => {
  it('renders band information correctly', () => {
    const band = { id: 1, name: 'Test Band', genre: 'Rock' }
    const wrapper = mount(BandCard, { props: { band } })
    
    expect(wrapper.text()).toContain('Test Band')
    expect(wrapper.text()).toContain('Rock')
  })
})
```

### 2. 事件测试
```typescript
it('emits edit event when edit button is clicked', async () => {
  const wrapper = mount(BandCard, { 
    props: { band: mockBand, showActions: true } 
  })
  
  await wrapper.find('.edit-btn').trigger('click')
  expect(wrapper.emitted('edit')).toBeTruthy()
})
```

## 🔧 维护建议

### 1. 样式更新
- 修改组件样式会自动应用到所有使用该组件的页面
- 避免在页面中覆盖组件样式

### 2. 功能扩展
- 新功能优先添加到组件中
- 保持组件的向后兼容性

### 3. 版本管理
- 组件更新时记录变更日志
- 重大更新时通知所有使用方

## ✨ 最佳实践

1. **统一使用**: 所有页面都使用这些组件，避免重复代码
2. **配置驱动**: 通过 props 控制组件行为，而不是修改组件内部逻辑
3. **事件处理**: 在父组件中处理业务逻辑，组件只负责展示和基础交互
4. **性能考虑**: 大量数据时考虑使用虚拟滚动或分页
5. **测试覆盖**: 为组件编写完整的单元测试

## 🎉 总结

通过使用这些可复用的卡片组件，我们实现了：

- ✅ **代码复用**: 避免重复的卡片代码
- ✅ **样式一致**: 所有页面的卡片样式完全一致
- ✅ **维护便利**: 修改样式只需要改一个地方
- ✅ **功能丰富**: 支持批量操作、操作按钮等高级功能
- ✅ **响应式设计**: 自动适配各种设备
- ✅ **类型安全**: 完整的 TypeScript 类型定义

现在可以在所有页面中统一使用这些组件，享受一致的视觉体验和便捷的维护体验！

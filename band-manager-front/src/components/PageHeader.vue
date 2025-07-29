<template>
  <div>
    <!-- 页面标题和操作按钮区域 -->
    <div class="section-header">
      <h1 @click="handleTitleClick" :style="{ cursor: titleClickable ? 'pointer' : 'default' }">
        {{ title }}
      </h1>
      <div class="button-group">
        <!-- 返回主页按钮 -->
        <button class="back-button" @click="handleBackClick">
          <i class="fas fa-arrow-left"></i> 返回主页
        </button>
        
        <!-- 批量删除切换按钮 -->
        <button 
          class="batch-toggle-btn" 
          @click="handleBatchToggle"
          :class="{ active: batchMode }"
        >
          <i class="fas fa-check-square"></i> 
          {{ batchMode ? '退出批量删除' : '批量删除' }}
        </button>
        
        <!-- 添加按钮 -->
        <button :class="addButtonClass" @click="handleAddClick">
          <i class="fas fa-plus"></i> {{ addButtonText }}
        </button>
      </div>
    </div>

    <!-- 批量操作工具栏 -->
    <div v-if="batchMode" class="batch-toolbar">
      <div class="batch-info">
        <span>已选择 {{ selectedCount }} 个{{ itemType }}</span>
        <button @click="handleSelectAll" class="select-all-btn">全选</button>
        <button @click="handleClearSelection" class="clear-selection-btn">清空</button>
      </div>
      <button 
        v-if="selectedCount > 0" 
        class="batch-delete-btn" 
        @click="handleBatchDelete"
      >
        <i class="fas fa-trash"></i> 删除选中项 ({{ selectedCount }})
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  // 页面标题
  title: string
  // 标题是否可点击
  titleClickable?: boolean
  // 批量模式状态
  batchMode: boolean
  // 选中项数量
  selectedCount: number
  // 项目类型（用于显示"已选择 X 个乐队/成员"）
  itemType: string
  // 添加按钮文本
  addButtonText: string
  // 添加按钮样式类
  addButtonClass?: string
}

interface Emits {
  (e: 'title-click'): void
  (e: 'back-click'): void
  (e: 'batch-toggle'): void
  (e: 'add-click'): void
  (e: 'select-all'): void
  (e: 'clear-selection'): void
  (e: 'batch-delete'): void
}

const props = withDefaults(defineProps<Props>(), {
  titleClickable: true,
  addButtonClass: 'add-btn'
})

const emit = defineEmits<Emits>()

const handleTitleClick = () => {
  if (props.titleClickable) {
    emit('title-click')
  }
}

const handleBackClick = () => {
  emit('back-click')
}

const handleBatchToggle = () => {
  emit('batch-toggle')
}

const handleAddClick = () => {
  emit('add-click')
}

const handleSelectAll = () => {
  emit('select-all')
}

const handleClearSelection = () => {
  emit('clear-selection')
}

const handleBatchDelete = () => {
  emit('batch-delete')
}
</script>

<style scoped lang="scss">
/* 顶部标题和按钮区域 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 30px 4px 15px 4px;
  border-bottom: 1px solid #333;
  
  h1 {
    font-size: 2.2rem;
    color: #e53935;
    margin: 0;
  }
  
  .button-group {
    display: flex;
    gap: 16px;
    align-items: center;
    
    .back-button {
      background: #333;
      color: rgb(247, 238, 238);
      border: none;
      padding: 8px 15px;
      border-radius: 30px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: #444;
      }
      
      i {
        margin-right: 5px;
      }
    }
    
    .batch-toggle-btn {
      background: #666;
      color: white;
      border: none;
      padding: 8px 15px;
      border-radius: 30px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: #777;
      }
      
      &.active {
        background: linear-gradient(to right, #ff9800, #f57c00);
      }
      
      i {
        margin-right: 5px;
      }
    }
    
    .add-btn,
    .add-band-btn,
    .add-member-btn,
    .add-event-btn {
      background: linear-gradient(to right, #e53935, #e35d5b);
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 30px;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
      }

      i {
        margin-right: 8px;
      }
    }
  }
}

/* 批量操作工具栏 */
.batch-toolbar {
  background: rgba(255, 152, 0, 0.1);
  border: 1px solid rgba(255, 152, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.select-all-btn, .clear-selection-btn {
  background: transparent;
  border: 1px solid #ff9800;
  color: #ff9800;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: #ff9800;
    color: white;
  }
}

.batch-delete-btn {
  background: linear-gradient(to right, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  }
  
  i {
    margin-right: 5px;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
    padding: 20px 4px 15px 4px;
  }
  
  .button-group {
    width: 100%;
    justify-content: space-between;
  }
  
  .batch-toolbar {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .batch-info {
    justify-content: center;
  }
}
</style>

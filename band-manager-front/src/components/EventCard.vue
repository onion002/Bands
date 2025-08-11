<template>
  <div class="event-card card card-interactive" :class="{ 'selected': selected }">
    <!-- 批量选择复选框 -->
    <div v-if="showBatchCheckbox" class="batch-checkbox">
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('selection-change', ($event.target as HTMLInputElement).checked)"
        class="checkbox"
      />
    </div>

    <!-- 左侧：活动海报 -->
    <div class="event-poster">
      <img
        v-if="event.poster_image_url"
        :src="getPosterImageUrl(event.poster_image_url)"
        :alt="event.title"
        class="poster-image"
        @error="handlePosterError"
      />
      <div v-else class="poster-placeholder">
        <i class="fa fa-calendar"></i>
        <span>{{ event.title }}</span>
      </div>
    </div>

    <!-- 右侧：活动信息 -->
    <div class="event-info">
      <h4 class="event-title">{{ event.title }}</h4>
      <p v-if="event.description" class="event-description">{{ event.description }}</p>
      
      <div class="event-details">
        <span v-if="event.venue" class="detail-item">
          <i class="fa fa-map-marker-alt"></i>
          {{ event.venue }}
        </span>
        <span v-if="event.band_names && event.band_names.length > 0" class="detail-item">
          <i class="fa fa-users"></i>
          {{ event.band_names.join('、') }}
        </span>
        <span class="detail-item status" :class="event.status">
          <i class="fa fa-circle"></i>
          {{ getStatusText(event.status) }}
        </span>
      </div>

      <!-- 操作按钮 -->
      <div v-if="showActions" class="event-actions">
        <button 
          @click="$emit('edit')" 
          class="action-btn edit-btn"
          title="编辑活动"
        >
          <i class="fa fa-edit"></i>
        </button>
        <button 
          @click="$emit('delete')" 
          class="action-btn delete-btn"
          title="删除活动"
        >
          <i class="fa fa-trash"></i>
        </button>
        <button 
          @click="$emit('view')" 
          class="action-btn view-btn"
          title="查看详情"
        >
          <i class="fa fa-eye"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface EventItem {
  id: number
  title: string
  description?: string
  event_date: string
  venue?: string
  band_names?: string[]
  status: string
  poster_image_url?: string
}

interface Props {
  event: EventItem
  selected?: boolean
  showBatchCheckbox?: boolean
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  showBatchCheckbox: false,
  showActions: false
})

// 定义事件
defineEmits<{
  'selection-change': [value: boolean]
  'edit': []
  'delete': []
  'view': []
}>()

// 格式化日期
const formatEventDay = (dateStr: string) => {
  return new Date(dateStr).getDate().toString()
}

const formatEventMonth = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short' })
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    upcoming: '即将售票',
    ongoing: '售票中',
    completed: '结束售票',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}
// 获取海报图片URL
const getPosterImageUrl = (imageUrl: string) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http')) return imageUrl
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  return API_BASE_URL + imageUrl
}
// 处理海报加载错误
const handlePosterError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
    console.warn('海报加载失败:', img.src)
  }
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.event-card {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 0;
  color: $white;
  height: 206px;
  background: rgba($darkgray, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: none;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
  }

  &.selected {
    transform: scale(0.98);
    border-color: $primary;
    box-shadow: 0 0 25px rgba($primary, 0.4);
    background: rgba($primary, 0.05);

    &::after {
      content: '';
      position: absolute;
      inset: -3px;
      background: linear-gradient(135deg, #ff2a6d, #05d9e8);
      border-radius: $border-radius-xl;
      pointer-events: none;
      z-index: 1;
      opacity: 0.6;
      filter: blur(2px);
    }
  }

  .batch-checkbox {
    position: absolute;
    top: 1rem;
    left: 1rem;
    z-index: 10;

    .checkbox {
      width: 20px;
      height: 20px;
      cursor: pointer;
      accent-color: $primary;
      border-radius: 4px;
    }
  }

  .event-poster {
    position: relative;
    width: 206px;
    height: 206px;
    overflow: hidden;
    flex-shrink: 0;
    border-radius: 0;
    box-shadow: none;
    border: none;

    .poster-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .poster-placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, rgba($gray-600, 0.6), rgba($gray-700, 0.8));
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: $gray-200;

      i {
        font-size: 3.5rem;
        margin-bottom: 0.75rem;
        color: $primary;
        opacity: 0.8;
      }

      span {
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
        font-size: 0.9rem;
      }
    }

    &:hover .poster-image {
      transform: scale(1.05);
    }
  }

  .event-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.2rem;
    gap: 0.6rem;
    min-width: 0;

    .event-title {
      font-size: 1.1rem;
      font-weight: 800;
      color: $white;
      line-height: 1.2;
      margin: 0;
    }

    .event-description {
      color: $gray-300;
      font-size: 0.875rem;
      line-height: 1.4;
      margin: 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .event-details {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: auto;

      .detail-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: $gray-300;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.25rem 0.75rem;
        background: rgba($white, 0.05);
        border-radius: 9999px;
        border: 1px solid rgba($white, 0.1);

        i {
          color: $primary;
          font-size: 0.75rem;
        }

        &.status {
          &.upcoming { 
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: $white;
            border-color: rgba(245, 158, 11, 0.3);
          }
          &.ongoing { 
            background: linear-gradient(135deg, #10b981, #059669);
            color: $white;
            border-color: rgba(16, 185, 129, 0.3);
          }
          &.completed { 
            background: linear-gradient(135deg, $gray-500, $gray-600);
            color: $white;
            border-color: rgba(107, 114, 128, 0.3);
          }
          &.cancelled { 
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: $white;
            border-color: rgba(239, 68, 68, 0.3);
          }
        }
      }
    }

    .event-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.5rem;

      .action-btn {
        background: none;
        border: none;
        color: $gray-400;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: $border-radius-sm;
        transition: all $transition-fast ease;

        &:hover {
          color: $primary;
          background: rgba($primary, 0.1);
        }

        &.edit-btn:hover {
          color: #3b82f6;
          background: rgba(59, 130, 246, 0.1);
        }

        &.delete-btn:hover {
          color: #ef4444;
          background: rgba(239, 68, 68, 0.1);
        }

        &.view-btn:hover {
          color: #10b981;
          background: rgba(16, 185, 129, 0.1);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .event-card {
    flex-direction: column;
    height: auto;
    gap: 0;
    
    .event-date {
      width: 100%;
      height: 120px;
    }
  }
}
</style>

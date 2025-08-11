<template>
  <div class="member-card card card-interactive" :class="{ 'selected': selected }">
    <!-- 批量选择复选框 -->
    <div v-if="showBatchCheckbox" class="batch-checkbox">
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('selection-change', ($event.target as HTMLInputElement).checked)"
        class="checkbox"
      />
    </div>

    <div class="member-avatar">
      <img 
        v-if="member.avatar_url" 
        :src="member.avatar_url" 
        :alt="member.name" 
        class="avatar-image"
      />
      <div v-else class="avatar-placeholder">
        <i class="fa fa-user"></i>
      </div>
      <div class="status-indicator"></div>
    </div>

    <div class="member-info">
      <h4 class="member-name">{{ member.name }}</h4>
      <div v-if="member.role" class="member-role">{{ member.role }}</div>
      
      <div v-if="member.band_names && member.band_names.length > 0" class="member-band">
        <i class="fa fa-music"></i>
        {{ member.band_names.join('、') }}
      </div>
      
      <div v-if="member.join_date" class="member-date">
        <i class="fa fa-calendar"></i>
        {{ formatDate(member.join_date) }}
      </div>

      <!-- 操作按钮 -->
      <div v-if="showActions" class="member-actions">
        <button 
          @click="$emit('edit')" 
          class="action-btn edit-btn"
          title="编辑成员"
        >
          <i class="fa fa-edit"></i>
        </button>
        <button 
          @click="$emit('delete')" 
          class="action-btn delete-btn"
          title="删除成员"
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
interface Member {
  id: number
  name: string
  role?: string
  avatar_url?: string
  band_names?: string[]
  join_date?: string
  status?: string
}

interface Props {
  member: Member
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
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.member-card {
  padding: 2rem;
  text-align: center;
  position: relative;

  &.selected {
    transform: scale(0.98);

    &::after {
      content: '';
      position: absolute;
      inset: -4px;
      border: 2px solid $primary;
      border-radius: $border-radius-xl;
      pointer-events: none;
      z-index: 1;
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

  .member-avatar {
    position: relative;
    width: 100px;
    height: 100px;
    margin: 0 auto 1.5rem;

    .avatar-image {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid rgba($primary, 0.3);
      transition: all $transition-normal ease;
    }

    .avatar-placeholder {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: rgba($lightgray, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid rgba($primary, 0.3);

      i {
        font-size: 2.5rem;
        color: $gray-400;
      }
    }

    .status-indicator {
      position: absolute;
      bottom: 8px;
      right: 8px;
      width: 16px;
      height: 16px;
      background: #10b981;
      border-radius: 50%;
      border: 2px solid $darkgray;
    }
  }

  .member-info {
    .member-name {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
    }

    .member-role {
      color: $primary;
      font-weight: 500;
      margin-bottom: 1rem;
      font-size: 0.875rem;
    }

    .member-band,
    .member-date {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      color: $gray-400;
      font-size: 0.875rem;
      margin-bottom: 0.5rem;

      i {
        color: $primary;
        width: 16px;
      }
    }

    .member-actions {
      display: flex;
      justify-content: center;
      gap: 0.5rem;
      margin-top: 1.5rem;

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

  &:hover {
    .member-avatar {
      .avatar-image {
        border-color: rgba($primary, 0.6);
        transform: scale(1.05);
      }
    }
  }
}
</style>

<template>
  <div class="band-card card card-interactive" :class="{ 'selected': selected }">
    <!-- 批量选择复选框 -->
    <div v-if="showBatchCheckbox" class="batch-checkbox">
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('selection-change', ($event.target as HTMLInputElement).checked)"
        class="checkbox"
      />
    </div>

    <div class="band-image">
      <img 
        v-if="band.banner_image_url" 
        :src="band.banner_image_url" 
        :alt="band.name" 
        class="band-image-content"
      />
      <div v-else class="image-placeholder">
        <i class="fa fa-music"></i>
        <span>{{ band.name }}</span>
      </div>
      <div class="image-overlay"></div>
      <div v-if="band.genre" class="band-genre">{{ band.genre }}</div>
      
      <!-- 播放按钮 -->
      <button 
        v-if="showPlayButton"
        @click="$emit('play')" 
        class="play-btn"
        :title="`播放 ${band.name}`"
      >
        <i class="fa fa-play"></i>
      </button>
    </div>

    <div class="band-info">
      <h4 class="band-title">{{ band.name }}</h4>
      <div v-if="band.year" class="band-year">{{ band.year }}年成立</div>
      <p v-if="band.bio" class="band-bio">{{ band.bio }}</p>
      
      <div class="band-stats">
        <div class="member-count">
          <i class="fa fa-users"></i>
          <span>{{ band.member_count || 0 }}人</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="showActions" class="band-actions">
        <button 
          @click="$emit('edit')" 
          class="action-btn edit-btn"
          title="编辑乐队"
        >
          <i class="fa fa-edit"></i>
        </button>
        <button 
          @click="$emit('delete')" 
          class="action-btn delete-btn"
          title="删除乐队"
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

interface Props {
  band: Band
  selected?: boolean
  showBatchCheckbox?: boolean
  showPlayButton?: boolean
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  showBatchCheckbox: false,
  showPlayButton: false,
  showActions: false
})

// 定义事件
defineEmits<{
  'selection-change': [value: boolean]
  'play': []
  'edit': []
  'delete': []
  'view': []
}>()
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.band-card {
  overflow: hidden;
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

  .band-image {
    position: relative;
    height: 200px;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform $transition-slow ease;
    }

    .image-placeholder {
      width: 100%;
      height: 100%;
      background: rgba($lightgray, 0.3);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: $gray-400;

      i {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: $primary;
      }

      span {
        font-weight: 500;
      }
    }

    .image-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(to top, rgba($dark, 0.8), transparent);
    }

    .band-genre {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba($primary, 0.9);
      color: $white;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .play-btn {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: none;
      border: none;
      color: $white;
      font-size: 3rem;
      cursor: pointer;
      opacity: 0;
      transition: all $transition-normal ease;

      &:hover {
        color: $primary;
        transform: translate(-50%, -50%) scale(1.1);
      }
    }
  }

  .band-info {
    padding: 1.5rem;

    .band-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
      transition: color $transition-normal ease;
    }

    .band-year {
      color: $primary;
      font-weight: 500;
      margin-bottom: 0.75rem;
      font-size: 0.875rem;
    }

    .band-bio {
      color: $gray-400;
      font-size: 0.875rem;
      line-height: 1.5;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .band-stats {
      margin-top: 1rem;

      .member-count {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: $gray-300;
        font-size: 0.875rem;
        font-weight: 500;

        i {
          color: $primary;
          font-size: 0.875rem;
        }
      }
    }

    .band-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;

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
    .band-image {
      img {
        transform: scale(1.1);
      }

      .play-btn {
        opacity: 1;
      }
    }

    .band-info .band-title {
      color: $primary;
    }
  }
}
</style>
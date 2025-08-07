<template>
  <div class="band-card" @click="handleCardClick">
    <!-- 🎨 乐队图片区域 -->
    <div class="band-image">
      <img
        v-if="band.banner_image_url"
        :src="band.banner_image_url"
        :alt="band.name"
        class="band-image-content"
      />
      <div v-else class="placeholder-image">
        <i class="fa fa-music"></i>
        <span>{{ band.name }}</span>
      </div>

      <!-- 图片遮罩 -->
      <div class="image-overlay"></div>

      <!-- 乐队类型标签 -->
      <div class="band-genre">{{ band.genre || '未分类' }}</div>

      <!-- 悬停播放按钮 -->
      <button class="play-btn" @click.stop="showBioDialog = true">
        <i class="fa fa-play-circle"></i>
      </button>
    </div>

    <!-- 🎵 乐队信息区域 -->
    <div class="band-content">
      <h3 class="band-title">{{ band.name }}</h3>
      <div class="band-year">{{ band.year }}年成立</div>
      <p class="band-bio">{{ band.bio || '暂无简介' }}</p>

      <!-- 乐队统计 -->
      <div class="band-stats">
        <div class="member-count">
          <i class="fa fa-users"></i>
          <span>{{ band.member_count || 0 }}人</span>
        </div>

        <!-- 操作按钮 -->
        <div class="band-actions">
          <button @click.stop="$emit('edit', band)" class="action-btn" title="编辑">
            <i class="fa fa-edit"></i>
          </button>
          <button @click.stop="$emit('upload', band)" class="action-btn" title="上传图片">
            <i class="fa fa-upload"></i>
          </button>
          <button @click.stop="$emit('delete', band)" class="action-btn delete" title="删除">
            <i class="fa fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 🌟 乐队简介弹窗 -->
    <div v-if="showBioDialog" class="modal-overlay" @click.self="showBioDialog = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ band.name }} - 乐队简介</h3>
          <button class="close-btn" @click="showBioDialog = false">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="bio-content">
            <p>{{ band.bio || '暂无简介信息' }}</p>
            <div class="band-details">
              <div class="detail-item">
                <strong>成立年份:</strong> {{ band.year }}
              </div>
              <div class="detail-item">
                <strong>音乐类型:</strong> {{ band.genre || '未分类' }}
              </div>
              <div class="detail-item">
                <strong>成员数量:</strong> {{ band.member_count || 0 }}人
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showBioDialog = false">关闭</button>
        </div>
      </div>
  </div>
</template>
  
<script setup lang="ts">
import { ref } from 'vue'
import type { PropType } from 'vue'
import type { Band } from '@/types'

const props = defineProps({
  band: {
    type: Object as PropType<Band>,
    required: true
  }
})

// 定义事件
defineEmits<{
  edit: [band: Band]
  upload: [band: Band]
  delete: [band: Band]
}>()

// 弹窗状态
const showBioDialog = ref(false)

// 处理卡片点击
const handleCardClick = () => {
  showBioDialog.value = true
}
</script>
  
<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
@use '@/assets/scss/mixins' as *;

// 🎨 优化的乐队卡片样式
.band-card {
  @include interactive-card;
  @include fade-in-up(0.6s, 30px);

  // 使用全局定义的 .band-card 样式基础上添加优化

  .placeholder-image {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: rgba($lightgray, 0.3);
    color: $gray-400;
    @include transition-optimized(background-color);

    i {
      font-size: 3rem;
      margin-bottom: 0.5rem;
      color: $primary;
      @include music-pulse(2s, 1.1);
    }

    span {
      font-weight: 500;
      @include transition-optimized(color);
    }

    &:hover {
      background: rgba($lightgray, 0.4);

      span {
        color: $primary;
      }
    }
  }

  .play-btn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: none;
    border: none;
    color: $white;
    font-size: 4rem;
    cursor: pointer;
    opacity: 0;
    @include transition-optimized(opacity transform color);
    @include hardware-acceleration;

    &:hover {
      color: $primary;
      transform: translate(-50%, -50%) scale(1.1) translateZ(0);
    }
  }

  &:hover .play-btn {
    opacity: 1;
  }

  // 添加进入动画延迟
  &:nth-child(1) { animation-delay: 0.1s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.3s; }
  &:nth-child(4) { animation-delay: 0.4s; }
  &:nth-child(5) { animation-delay: 0.5s; }
}

// 🌟 优化的弹窗样式
.modal-overlay {
  @include modal-backdrop;
  @include hardware-acceleration;
}

.modal {
  @include modal-enter;
  @include hardware-acceleration;
}

.bio-content {
  p {
    color: $gray-300;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    @include fade-in-up(0.5s, 20px, 0.1s);
  }

  .band-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    .detail-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: $gray-400;
      font-size: 0.875rem;
      @include fade-in-left(0.4s, 20px);
      @include transition-optimized(color);

      &:nth-child(1) { animation-delay: 0.2s; }
      &:nth-child(2) { animation-delay: 0.3s; }
      &:nth-child(3) { animation-delay: 0.4s; }

      strong {
        color: $primary;
        min-width: 80px;
        @include glow-text($primary, 0.3);
      }

      &:hover {
        color: $gray-200;
      }
    }
  }
}

// 🎨 响应式动画优化
@include respect-motion-preference;


  </style>
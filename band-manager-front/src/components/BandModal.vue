<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ mode === 'edit' ? '编辑乐队信息' : '添加新乐队' }}</h3>
        <button class="close-btn" @click="close">
          <i class="fa fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="save" class="band-form">
          <!-- 🎨 乐队图片上传区域 -->
          <div class="form-group image-upload-group">
            <label class="form-label">乐队图片</label>
            <div class="image-upload-area">
              <div class="image-preview">
                <img
                  v-if="formData.banner_image_url"
                  :src="formData.banner_image_url"
                  alt="乐队图片"
                  class="preview-image"
                />
                <div v-else class="image-placeholder">
                  <i class="fa fa-image"></i>
                  <span>点击上传图片</span>
                </div>
              </div>
              <div class="image-actions">
                <button type="button" class="btn btn-outline btn-sm" @click="triggerBandImageUpload">
                  <i class="fa fa-camera"></i>
                  上传图片
                </button>
                <button
                  v-if="formData.banner_image_url"
                  type="button"
                  class="btn btn-outline btn-sm btn-danger"
                  @click="removeBandImage"
                >
                  <i class="fa fa-trash"></i>
                  移除
                </button>
              </div>
            </div>
          </div>

          <!-- 🎵 基本信息 -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">乐队名称</label>
              <input
                type="text"
                v-model="formData.name"
                class="form-control"
                placeholder="输入乐队名称..."
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">音乐流派</label>
              <input
                type="text"
                v-model="formData.genre"
                class="form-control"
                placeholder="如：摇滚、流行、民谣..."
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">成立年份</label>
              <input
                type="number"
                v-model="formData.formedYear"
                class="form-control"
                :min="1900"
                :max="new Date().getFullYear()"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">成员数量</label>
              <input
                type="number"
                v-model="formData.memberCount"
                class="form-control"
                min="1"
                max="20"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">乐队简介</label>
            <textarea
              v-model="formData.description"
              class="form-control"
              rows="4"
              placeholder="介绍一下您的乐队..."
            ></textarea>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-outline" @click="close">
          取消
        </button>
        <button type="submit" class="btn btn-primary" @click="save">
          <i class="fa fa-save"></i>
          {{ mode === 'edit' ? '更新' : '创建' }}
        </button>
      </div>
    </div>

    <!-- 🌟 图片上传弹窗 -->
    <UploadModal
      v-if="showUploadModal"
      title="上传乐队图片"
      :upload-api="BandService.uploadBandImage"
      accept="image/*"
      :max-size="5"
      @uploaded="handleImageUploaded"
      @close="showUploadModal = false"
    />
  </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch, onMounted } from 'vue';
  import type { Band } from '@/types';
  import UploadModal from './UploadModal.vue';
  import { BandService } from '@/api/bandService';

  const props = defineProps({
    band: {
      type: Object as () => Band | null,
      default: null
    },
    mode: {
      type: String,
      default: 'add'
    }
  });
  
  const formData = ref({
    id: '',
    name: '',
    genre: '',
    formedYear: new Date().getFullYear(),
    description: '',
    memberCount: 4,
    banner_image_url: '' // 只存图片URL
  });
  
  const emit = defineEmits(['close', 'save']);
  
  // 当传入的band发生变化时更新表单数据
  watch(() => props.band, (newBand) => {
    if (newBand) {
      formData.value = {
        id: String(newBand.id),
        name: newBand.name,
        genre: newBand.genre,
        formedYear: newBand.year,
        description: newBand.bio,
        memberCount: newBand.member_count,
        banner_image_url: newBand.banner_image_url // 只存图片URL
      };
    }
  }, { immediate: true });
  
  // 关闭模态框
  const close = () => {
    emit('close');
  };
  
  // 保存乐队信息
  const save = () => {
    emit('save', {
      id: formData.value.id,
      name: formData.value.name,
      genre: formData.value.genre,
      year: formData.value.formedYear,
      bio: formData.value.description,
      member_count: formData.value.memberCount,
      banner_image_url: formData.value.banner_image_url // 只传图片URL
    });
  };

  // 控制 UploadModal 显示
  const showUploadModal = ref(false);
  const triggerBandImageUpload = () => {
    showUploadModal.value = true;
  };
  const handleImageUploaded = (imageUrl: string) => {
    formData.value.banner_image_url = imageUrl;
    showUploadModal.value = false;
  };
  const removeBandImage = () => {
    formData.value.banner_image_url = '';
  };
  </script>
  
<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
@use '@/assets/scss/mixins' as *;

// 🎨 优化的模态框样式
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba($dark, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
  @include modal-backdrop;
  @include hardware-acceleration;

  @media (max-width: 768px) {
    padding: 1rem;
  }
}

.modal {
  background: linear-gradient(135deg, rgba($darkgray, 0.95), rgba($lightgray, 0.9));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: $border-radius-xl;
  width: 100%;
  max-width: 650px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow:
    0 25px 50px rgba($dark, 0.5),
    0 0 0 1px rgba($primary, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  @include modal-enter;
  @include hardware-acceleration;

  .modal-header {
    padding: 2rem 2rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background: linear-gradient(135deg, rgba($primary, 0.1), rgba($secondary, 0.05));

    h3 {
      font-size: 1.75rem;
      font-weight: 700;
      background: $gradient-primary;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
      text-shadow: 0 2px 10px rgba($primary, 0.3);
    }

    .close-btn {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: $gray-400;
      cursor: pointer;
      padding: 0.75rem;
      border-radius: 50%;
      transition: all $transition-fast ease;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        color: $white;
        background: rgba($primary, 0.2);
        border-color: rgba($primary, 0.4);
        transform: rotate(90deg);
      }

      i {
        font-size: 1.25rem;
      }
    }
  }

  .modal-body {
    padding: 2rem;
    max-height: 60vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba($primary, 0.5);
      border-radius: 3px;

      &:hover {
        background: rgba($primary, 0.7);
      }
    }
  }

  .modal-footer {
    padding: 1rem 2rem 2rem;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.02);

    @media (max-width: 480px) {
      flex-direction: column;
    }
  }
}
// 🎨 表单样式
.band-form {
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;

    @media (max-width: 480px) {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }

  .form-group {
    margin-bottom: 1.5rem;

    &.image-upload-group {
      margin-bottom: 2rem;
    }

    .form-label {
      display: block;
      margin-bottom: 0.5rem;
      color: $white;
      font-weight: 500;
      font-size: 0.875rem;
    }

    .form-control {
      width: 100%;
      padding: 1rem 1.25rem;
      background: rgba($lightgray, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: $border-radius-lg;
      color: $white;
      font-size: 0.9rem;
      transition: all $transition-normal ease;
      backdrop-filter: blur(10px);

      &::placeholder {
        color: rgba(255, 255, 255, 0.5);
      }

      &:focus {
        outline: none;
        border-color: $primary;
        background: rgba($lightgray, 0.6);
        box-shadow:
          0 0 0 3px rgba($primary, 0.15),
          0 4px 12px rgba($primary, 0.1);
        transform: translateY(-1px) translateZ(0);
        will-change: transform;
      }

      &:hover:not(:focus) {
        border-color: rgba(255, 255, 255, 0.25);
        background: rgba($lightgray, 0.5);
      }

      &:invalid {
        border-color: #ef4444;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
      }
    }

    textarea.form-control {
      resize: vertical;
      min-height: 100px;
    }
  }
}

// 🌟 图片上传区域
.image-upload-area {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: $border-radius-lg;
  border: 1px solid rgba(255, 255, 255, 0.1);

  .image-preview {
    width: 140px;
    height: 140px;
    border-radius: $border-radius-lg;
    overflow: hidden;
    border: 2px dashed rgba($primary, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba($primary, 0.05);
    transition: all $transition-normal ease;
    position: relative;

    &:hover {
      border-color: rgba($primary, 0.6);
      background: rgba($primary, 0.1);
      transform: scale(1.02);
    }

    .preview-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: calc($border-radius-lg - 2px);
    }

    .image-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: rgba(255, 255, 255, 0.6);
      text-align: center;
      padding: 1rem;

      i {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        color: $primary;
        opacity: 0.8;
      }

      span {
        font-size: 0.8rem;
        font-weight: 500;
      }
    }
  }

  .image-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
  }
}

// 🎨 响应式动画优化
@include respect-motion-preference;
</style>
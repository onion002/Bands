<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ mode === 'edit' ? '编辑成员信息' : '添加新成员' }}</h2>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="save">
          <!-- 头像上传区域 -->
          <div class="form-group avatar-section">
            <label>成员头像</label>
            <div class="avatar-upload-area">
              <div class="avatar-preview">
                <img
                  v-if="formData.avatar_url"
                  :src="getAvatarUrl(formData.avatar_url)"
                  alt="成员头像"
                  class="avatar-image"
                >
                <div v-else class="avatar-placeholder">
                  <i class="fas fa-user"></i>
                </div>
              </div>
              <div class="avatar-actions">
                <button
                  type="button"
                  class="upload-avatar-btn"
                  @click="showUploadModal = true"
                >
                  <i class="fas fa-camera"></i> 选择头像
                </button>
                <button
                  v-if="formData.avatar_url"
                  type="button"
                  class="remove-avatar-btn"
                  @click="removeAvatar"
                >
                  <i class="fas fa-trash"></i> 移除
                </button>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>成员姓名 *</label>
            <input
              type="text"
              v-model="formData.name"
              required
              placeholder="请输入成员姓名"
            >
          </div>
          
          <div class="form-group">
            <label>角色/职位</label>
            <input 
              type="text" 
              v-model="formData.role" 
              placeholder="如：主唱、吉他手、鼓手等"
            >
          </div>
          
          <div class="form-group">
            <label>所属乐队 *</label>
            <select v-model="formData.band_id" required>
              <option value="">请选择乐队</option>
              <option 
                v-for="band in bands" 
                :key="band.id" 
                :value="band.id"
              >
                {{ band.name }}
              </option>
            </select>
          </div>
          
          <!-- 恢复为原生 input[type=date] 日期输入框 -->
          <div class="form-group">
            <label>加入日期 *</label>
            <input 
              type="date" 
              v-model="formData.join_date" 
              required
              :max="today"
              class="custom-date-input"
              placeholder="选择日期"
            >
          </div>
          
          <div class="form-buttons">
            <button type="button" class="cancel-btn" @click="close">取消</button>
            <button type="submit" class="save-btn" :disabled="!isFormValid">
              {{ mode === 'edit' ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 头像上传弹窗 -->
    <UploadModal
      v-if="showUploadModal"
      title="上传成员头像"
      :uploadApi="uploadMemberAvatar"
      accept="image/jpeg,image/png,image/gif,image/webp"
      :maxSize="5 * 1024 * 1024"
      @uploaded="handleAvatarUploaded"
      @close="showUploadModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import type { Member, Band } from '@/types';
import { BandService } from '@/api/bandService';
import { MemberService } from '@/api/memberService';
import UploadModal from './UploadModal.vue';

const props = defineProps({
  member: {
    type: Object as () => Member | null,
    default: null
  },
  mode: {
    type: String,
    default: 'add'
  }
});

const formData = ref({
  id: 0,
  name: '',
  role: '',
  band_id: '',
  join_date: '',
  avatar_url: ''
});

const bands = ref<Band[]>([]);
const showUploadModal = ref(false);
const selectedAvatarFile = ref<File | null>(null);
const emit = defineEmits(['close', 'save']);

// 获取今天的日期（用于限制日期选择）
const today = computed(() => {
  return new Date().toISOString().split('T')[0];
});

// 表单验证
const isFormValid = computed(() => {
  return formData.value.name.trim() !== '' && 
         formData.value.band_id !== '' && 
         formData.value.join_date !== '';
});

// 当传入的member发生变化时更新表单数据
watch(() => props.member, (newMember) => {
  if (newMember) {
    formData.value = {
      id: newMember.id,
      name: newMember.name,
      role: newMember.role || '',
      band_id: String(newMember.band_id),
      join_date: newMember.join_date,
      avatar_url: newMember.avatar_url || ''
    };
  } else {
    // 重置表单
    formData.value = {
      id: 0,
      name: '',
      role: '',
      band_id: '',
      join_date: '', // 初始化formData.join_date为''
      avatar_url: ''
    };
  }
}, { immediate: true });

// 获取乐队列表
const fetchBands = async () => {
  try {
    const result = await BandService.getBands();
    bands.value = Array.isArray(result.items) ? result.items : [];
  } catch (error) {
    console.error('获取乐队列表失败:', error);
  }
};

// 创建一个临时的上传API函数
const uploadMemberAvatar = async (file: File) => {
  // 这里只是为了配合UploadModal的接口，实际上传逻辑在save方法中处理
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    selectedAvatarFile.value = file;
    resolve({ url });
  });
};

// 处理头像上传完成
const handleAvatarUploaded = (url: string) => {
  formData.value.avatar_url = url;
  showUploadModal.value = false;
};

// 移除头像
const removeAvatar = () => {
  formData.value.avatar_url = '';
  selectedAvatarFile.value = null;
};

// 关闭模态框
const close = () => {
  emit('close');
};

// 保存成员信息
const save = () => {
  if (!isFormValid.value) {
    return;
  }

  const memberData = {
    id: formData.value.id,
    name: formData.value.name.trim(),
    role: formData.value.role.trim(),
    band_id: parseInt(formData.value.band_id),
    join_date: formData.value.join_date,
    avatar_url: formData.value.avatar_url,
    avatarFile: selectedAvatarFile.value // 传递选中的文件
  };

  emit('save', memberData);
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
function getAvatarUrl(avatar_url: string) {
  if (!avatar_url) {
    // 返回默认头像图片URL（请替换为你的默认头像路径）
    return '/default-avatar.png';
  }
  if (avatar_url.startsWith('http') || avatar_url.startsWith('blob:')) return avatar_url;
  return API_BASE_URL + avatar_url;
}

// 组件挂载时获取乐队列表
onMounted(() => {
  fetchBands();
});
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

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

  @media (max-width: 768px) {
    padding: 1rem;
  }
}

.modal-container {
  background: linear-gradient(135deg, rgba($darkgray, 0.95), rgba($lightgray, 0.9));
  backdrop-filter: blur(20px);
  border-radius: $border-radius-xl;
  width: 550px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow:
    0 25px 50px rgba($dark, 0.5),
    0 0 0 1px rgba($primary, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: modalSlideIn $transition-normal ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2rem 1rem;
  background: linear-gradient(135deg, rgba($primary, 0.1), rgba($secondary, 0.05));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  h2 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    background: $gradient-primary;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 2px 10px rgba($primary, 0.3);
  }
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
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
  font-size: 1.25rem;

  &:hover {
    color: $white;
    background: rgba($primary, 0.2);
    border-color: rgba($primary, 0.4);
    transform: rotate(90deg);
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

.form-group {
  margin-bottom: 1.5rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: $white;
    font-size: 0.875rem;
  }

  input,
  select,
  textarea {
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
      transform: translateY(-1px);
    }

    &:hover:not(:focus) {
      border-color: rgba(255, 255, 255, 0.25);
      background: rgba($lightgray, 0.5);
    }
  }
}

// 🌟 头像上传区域
.avatar-section {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: $border-radius-lg;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;

  input[type="file"] {
    display: none;
  }
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba($primary, 0.1);
  border: 3px solid rgba($primary, 0.3);
  transition: all $transition-normal ease;
  position: relative;

  &:hover {
    border-color: rgba($primary, 0.5);
    transform: scale(1.05);
  }

  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar-placeholder {
    color: rgba($primary, 0.7);
    font-size: 2.5rem;
  }
}

.avatar-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.upload-avatar-btn,
.remove-avatar-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.upload-avatar-btn {
  background: linear-gradient(135deg, $primary, $secondary);
  color: white;
  box-shadow: 0 4px 15px rgba($primary, 0.3);

  &:hover {
    background: linear-gradient(135deg, darken($primary, 10%), darken($secondary, 10%));
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba($primary, 0.4);
  }
}

.remove-avatar-btn {
  background: rgba(239, 68, 68, 0.8);
  color: white;
  border: 1px solid rgba(239, 68, 68, 0.5);

  &:hover {
    background: rgba(239, 68, 68, 1);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
  }
}

// 选择框样式
select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.75rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 3rem;
  cursor: pointer;

  option {
    background: $darkgray;
    color: $white;
    padding: 0.5rem;
  }
}

// 日期输入框样式
.custom-date-input[type="date"] {
  &::-webkit-calendar-picker-indicator {
    filter: invert(1);
    cursor: pointer;
  }

  &::-webkit-input-placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  &::-moz-placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  &:-ms-input-placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
}

// 表单按钮区域
.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem 2rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);

  @media (max-width: 480px) {
    flex-direction: column;
    padding: 1rem;
  }
}

.cancel-btn,
.save-btn {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all $transition-normal ease;
  min-width: 120px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-2px);
  }
}

.save-btn {
  background: linear-gradient(135deg, $primary, $secondary);
  color: white;
  box-shadow: 0 4px 15px rgba($primary, 0.3);

  &:hover {
    background: linear-gradient(135deg, darken($primary, 10%), darken($secondary, 10%));
    box-shadow: 0 6px 20px rgba($primary, 0.4);
    transform: translateY(-2px);
  }

  &:disabled {
    background: rgba(255, 255, 255, 0.2);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}

@media (max-width: 768px) {
  .modal-container {
    width: 95vw;
    margin: 1rem;
  }

  .modal-header,
  .modal-body {
    padding: 1.5rem;
  }

  .form-buttons {
    padding: 1rem 1.5rem 1.5rem;
  }
}
</style>


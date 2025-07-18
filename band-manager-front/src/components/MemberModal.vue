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
                <input
                  type="file"
                  ref="avatarInput"
                  accept="image/*"
                  @change="handleAvatarChange"
                  style="display: none;"
                >
                <button
                  type="button"
                  class="upload-avatar-btn"
                  @click="triggerAvatarUpload"
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import type { Member, Band } from '@/types';
import { BandService } from '@/api/bandService';
import DatePicker from 'vue-datepicker-next';
import 'vue-datepicker-next/index.css';

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
const avatarInput = ref<HTMLInputElement | null>(null);
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

// 触发头像文件选择
const triggerAvatarUpload = () => {
  if (avatarInput.value) {
    avatarInput.value.click();
  }
};

// 存储选中的头像文件
const selectedAvatarFile = ref<File | null>(null);

// 处理头像文件选择
const handleAvatarChange = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const file = input.files[0];

    // 检查文件类型
    if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
      alert('不支持的文件类型，请上传 JPG、PNG、GIF 或 WEBP 格式');
      return;
    }

    // 检查文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('文件大小超过 5MB 限制');
      return;
    }

    // 存储文件用于后续上传
    selectedAvatarFile.value = file;

    // 创建预览URL
    formData.value.avatar_url = URL.createObjectURL(file);
  }
};

// 移除头像
const removeAvatar = () => {
  formData.value.avatar_url = '';
  selectedAvatarFile.value = null;
  if (avatarInput.value) {
    avatarInput.value.value = '';
  }
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

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  max-height: auto;
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(229, 57, 53, 0.3);
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(229, 57, 53, 0.8);
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.6rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: white;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s, transform 0.3s;
}
.close-btn:hover {
  background-color: rgba(255,255,255,0.1);
  color: #fff;
  transform: rotate(90deg);
}

.modal-body {
  padding: 20px;
  box-sizing: border-box;
}

.form-group {
  margin-bottom: 16px;
  width: 100%;
  max-width: 400px;
  min-width: 200px;
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #ccc;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  max-width: 400px;
  min-width: 200px;
  margin-left: auto;
  margin-right: auto;
  display: block;
  box-sizing: border-box;
  padding: 12px 15px;
  border: none;
  border-radius: 6px;
  background: rgba(255,255,255,0.15);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  background: rgba(255,255,255,0.15);
  box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.5);
}

/* 头像上传区域样式适配深色 */
.avatar-section {
  text-align: center;
  margin-bottom: 25px;
}
.avatar-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
.avatar-upload-area input[type="file"] {
  display: none;
}
.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #23232e;
}
.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-placeholder {
  color: #888;
  font-size: 2rem;
}
.avatar-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
.upload-avatar-btn,
.remove-avatar-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}
.upload-avatar-btn {
  background: linear-gradient(to right, #1976d2, #2196f3);
  color: white;
}
.upload-avatar-btn:hover {
  background: #1565c0;
}
.remove-avatar-btn {
  background: rgba(229, 57, 53, 0.8);
  color: white;
}
.remove-avatar-btn:hover {
  background: #b71c1c;
}

.form-group select {
  background: #23232e;
  color: #fff;
}
.form-group select option {
  background: #23232e;
  color: #fff;
}

/* 只保留原生 input[type=date] 的深色样式，删除无用的第三方日期组件样式 */
.custom-date-input[type="date"] {
  background: #23232e;
  color: #fff;
  border: none;
  width: 100%;
  max-width: 400px;
  min-width: 200px;
  margin-left: auto;
  margin-right: auto;
  display: block;
  box-sizing: border-box;
  padding: 12px 15px;
  font-size: 1rem;
  height: 43px;
  border-radius: 6px;
}
.custom-date-input[type="date"]::-webkit-input-placeholder { color: #888; }
.custom-date-input[type="date"]::-moz-placeholder { color: #888; }
.custom-date-input[type="date"]:-ms-input-placeholder { color: #888; }
.custom-date-input[type="date"]::placeholder { color: #888; }

.form-group input[type="text"] {
  background: #23232e;
  color: #fff;
  border: none;
  width: 100%;
  max-width: 400px;
  min-width: 200px;
  margin-left: auto;
  margin-right: auto;
  display: block;
  box-sizing: border-box;
  padding: 12px 15px;
  font-size: 1rem;
  height: 43px;
  border-radius: 6px;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #333;
}
.cancel-btn,
.save-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}
.cancel-btn {
  background: rgba(255,255,255,0.1);
  color: #ccc;
}
.cancel-btn:hover {
  background: rgba(255,255,255,0.2);
}
.save-btn {
  background: linear-gradient(to right, #e53935, #e35d5b);
  color: white;
}
.save-btn:hover {
  box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .modal-container {
    width: 98vw;
    max-width: 98vw;
    min-width: 0;
    padding: 0;
  }
  .modal-body {
    padding: 10px;
  }
}
</style>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ mode === 'add' ? '添加演出活动' : '编辑演出活动' }}</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fa fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="event-form">
          <!-- 🎵 基本信息 -->
          <div class="form-group">
            <label class="form-label">活动标题 *</label>
            <input
              type="text"
              v-model="formData.title"
              class="form-control"
              placeholder="请输入活动标题..."
              maxlength="200"
              required
            />
            <div class="char-count">{{ formData.title.length }}/200</div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">所属乐队 *</label>
              <select v-model="formData.band_id" class="form-control" required>
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

            <div class="form-group">
              <label class="form-label">活动状态</label>
              <select v-model="formData.status" class="form-control">
                <option value="upcoming">即将开始</option>
                <option value="ongoing">进行中</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">演出时间 *</label>
              <input
                type="datetime-local"
                v-model="formData.event_date"
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">票价 (元)</label>
              <input
                type="number"
                v-model="formData.ticket_price"
                class="form-control"
                min="0"
                step="0.01"
                placeholder="0.00"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">演出场地</label>
              <input
                type="text"
                v-model="formData.venue"
                class="form-control"
                placeholder="请输入演出场地..."
                maxlength="200"
              />
            </div>

            <div class="form-group">
              <label class="form-label">场地容量</label>
              <input
                type="number"
                v-model="formData.capacity"
                class="form-control"
                min="1"
                placeholder="场地容量"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">详细地址</label>
            <input
              type="text"
              v-model="formData.address"
              class="form-control"
              placeholder="请输入详细地址..."
              maxlength="500"
            />
          </div>
          <div class="form-group">
            <label class="form-label">活动描述</label>
            <textarea
              v-model="formData.description"
              class="form-control"
              rows="4"
              placeholder="请输入活动描述..."
              maxlength="1000"
            ></textarea>
            <div class="char-count">{{ formData.description.length }}/1000</div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-outline" @click="$emit('close')">
          取消
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="handleSubmit"
          :disabled="loading"
        >
          <i class="fa fa-save"></i>
          {{ loading ? '保存中...' : (mode === 'add' ? '添加' : '保存') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { Event } from '@/types';
import UploadModal from './UploadModal.vue';
import { BandService } from '@/api/bandService';
import { EventService } from '@/api/eventService';

const props = defineProps({
  event: {
    type: Object as () => Event | null,
    default: null
  },
  mode: {
    type: String,
    default: 'add'
  }
});

const emit = defineEmits(['close', 'submit']);

const loading = ref(false);
const showUploadModal = ref(false);
const bands = ref<any[]>([]);

const formData = ref({
  id: 0,
  title: '',
  description: '',
  event_date: '',
  venue: '',
  address: '',
  ticket_price: undefined as number | undefined,
  capacity: undefined as number | undefined,
  status: 'upcoming' as 'upcoming' | 'ongoing' | 'completed' | 'cancelled',
  band_id: '',
  poster_image_url: ''
});

// 当传入的event发生变化时更新表单数据
watch(() => props.event, (newEvent) => {
  if (newEvent) {
    formData.value = {
      id: newEvent.id,
      title: newEvent.title,
      description: newEvent.description || '',
      event_date: newEvent.event_date,
      venue: newEvent.venue || '',
      address: newEvent.address || '',
      ticket_price: newEvent.ticket_price,
      capacity: newEvent.capacity,
      status: newEvent.status,
      band_id: String(newEvent.band_id),
      poster_image_url: newEvent.poster_image_url || ''
    };
  } else {
    // 重置表单
    formData.value = {
      id: 0,
      title: '',
      description: '',
      event_date: '',
      venue: '',
      address: '',
      ticket_price: undefined,
      capacity: undefined,
      status: 'upcoming',
      band_id: '',
      poster_image_url: ''
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

// 打开上传模态框
const openUploadModal = () => {
  showUploadModal.value = true;
};

// 上传海报 API
const uploadPosterApi = async (file: File) => {
  console.log('uploadPosterApi 被调用，文件:', file.name, file.type)
  
  const formData = new FormData()
  formData.append('file', file)
  
  console.log('FormData 创建完成，准备发送请求')
  
  try {
    const result = await EventService.uploadPoster(formData)
    console.log('EventService.uploadPoster 返回:', result)
    return result
  } catch (error: any) {
    console.error('EventService.uploadPoster 错误:', error)
    throw error
  }
}

// 处理上传成功
const handleUploadSuccess = (imageUrl: string) => {
  console.log('handleUploadSuccess 被调用')
  console.log('接收到的图片URL:', imageUrl)
  console.log('当前 formData.poster_image_url:', formData.value.poster_image_url)
  
  formData.value.poster_image_url = imageUrl;
  showUploadModal.value = false;
  
  console.log('更新后的 formData.poster_image_url:', formData.value.poster_image_url)
  console.log('完整的 formData:', formData.value)
};

// 提交表单
const handleSubmit = async () => {
  try {
    // 基本验证
    if (!formData.value.title.trim()) {
      alert('请输入活动标题');
      return;
    }
    if (!formData.value.band_id) {
      alert('请选择乐队');
      return;
    }
    if (!formData.value.event_date) {
      alert('请选择演出时间');
      return;
    }

    loading.value = true;

    const submitData = {
      ...formData.value,
      band_id: parseInt(formData.value.band_id)
    };

    console.log('提交的数据:', submitData)
    console.log('海报URL:', submitData.poster_image_url)

    emit('submit', submitData);
  } catch (error) {
    console.error('表单提交失败:', error);
  } finally {
    loading.value = false;
  }
};

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

.modal {
  background: linear-gradient(135deg, rgba($darkgray, 0.95), rgba($lightgray, 0.9));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: $border-radius-xl;
  width: 100%;
  max-width: 750px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow:
    0 25px 50px rgba($dark, 0.5),
    0 0 0 1px rgba($primary, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  animation: modalSlideIn $transition-normal ease;

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
    padding: 2rem 2rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
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
    flex: 1;
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
    flex-shrink: 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.02);

    @media (max-width: 480px) {
      flex-direction: column;
    }
  }
}
// 🎨 表单样式
.event-form {
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
        transform: translateY(-1px);
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

    select.form-control {
      cursor: pointer;
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
      background-position: right 0.75rem center;
      background-repeat: no-repeat;
      background-size: 1.5em 1.5em;
      padding-right: 3rem;

      option {
        background: $darkgray;
        color: $white;
        padding: 0.5rem;
      }
    }

    textarea.form-control {
      resize: vertical;
      min-height: 120px;
      line-height: 1.6;
    }

    .char-count {
      text-align: right;
      font-size: 0.75rem;
      color: rgba(255, 255, 255, 0.5);
      margin-top: 0.5rem;
      font-weight: 500;

      &.warning {
        color: #fbbf24;
      }

      &.danger {
        color: #ef4444;
      }
    }

    // 表单标签增强
    .form-label {
      position: relative;

      &::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: $gradient-primary;
        transition: width $transition-normal ease;
      }

      &:hover::after {
        width: 100%;
      }
    }

    // 必填字段标识
    .required::after {
      content: ' *';
      color: $primary;
      font-weight: bold;
    }
  }
}


</style>











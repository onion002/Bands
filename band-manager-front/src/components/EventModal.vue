<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ mode === 'add' ? '添加演出活动' : '编辑演出活动' }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="event-form">
          <div class="form-group">
            <label>活动标题 *</label>
            <input
              type="text"
              v-model="formData.title"
              placeholder="请输入活动标题"
              maxlength="200"
              required
            />
            <div class="char-count">{{ formData.title.length }}/200</div>
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

          <div class="form-group">
            <label>演出时间 *</label>
            <input
              type="datetime-local"
              v-model="formData.event_date"
              required
            />
          </div>

          <div class="form-group">
            <label>演出场地</label>
            <input
              type="text"
              v-model="formData.venue"
              placeholder="请输入演出场地"
              maxlength="200"
            />
          </div>

          <div class="form-group">
            <label>详细地址</label>
            <input
              type="text"
              v-model="formData.address"
              placeholder="请输入详细地址"
              maxlength="500"
            />
          </div>

          <div class="form-row">
            <div class="form-group half">
              <label>票价(元)</label>
              <div class="price-input-wrapper">
                <span class="price-prefix">¥</span>
                <input
                  type="number"
                  v-model="formData.ticket_price"
                  min="0"
                  step="0.01"
                  placeholder="请输入票价"
                />
                <span class="price-suffix">元</span>
              </div>
            </div>
            <div class="form-group half">
              <label>场地容量</label>
              <input
                type="number"
                v-model="formData.capacity"
                min="1"
                placeholder="场地容量"
              />
            </div>
          </div>

          <div class="form-group">
            <label>活动状态 *</label>
            <div class="status-selector">
              <button
                type="button"
                class="status-option"
                :class="{ active: formData.status === 'upcoming' }"
                @click="formData.status = 'upcoming'"
              >
                即将开始
              </button>
              <button
                type="button"
                class="status-option"
                :class="{ active: formData.status === 'ongoing' }"
                @click="formData.status = 'ongoing'"
              >
                进行中
              </button>
              <button
                type="button"
                class="status-option"
                :class="{ active: formData.status === 'completed' }"
                @click="formData.status = 'completed'"
              >
                已完成
              </button>
              <button
                type="button"
                class="status-option"
                :class="{ active: formData.status === 'cancelled' }"
                @click="formData.status = 'cancelled'"
              >
                已取消
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>活动描述</label>
            <textarea
              v-model="formData.description"
              rows="4"
              placeholder="请输入活动描述"
              maxlength="1000"
            ></textarea>
            <div class="char-count">{{ formData.description.length }}/1000</div>
          </div>

          <div class="form-group">
            <label>海报图片</label>
            <div class="poster-upload-section">
              <input
                type="text"
                v-model="formData.poster_image_url"
                placeholder="海报图片URL"
                readonly
              />
              <button
                type="button"
                class="upload-btn"
                @click="openUploadModal"
              >
                上传海报
              </button>
            </div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-cancel" @click="$emit('close')">取消</button>
        <button
          type="button"
          class="btn-primary"
          @click="handleSubmit"
          :disabled="loading"
        >
          {{ loading ? '保存中...' : (mode === 'add' ? '添加' : '保存') }}
        </button>
      </div>

      <UploadModal
        v-if="showUploadModal"
        title="上传演出活动海报"
        :upload-api="uploadPosterApi"
        accept="image/*"
        :max-size="5 * 1024 * 1024"
        url-field="poster_url"
        @uploaded="handleUploadSuccess"
        @close="showUploadModal = false"
      />
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
/* 模态框遮罩层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 模态框容器 */
.modal-container {
  background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
  border-radius: 12px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(229, 57, 53, 0.3);
  width: 700px;
  max-width: 90vw;
  height: 85vh;
  max-height: 800px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 模态框头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(229, 57, 53, 0.8);
  flex-shrink: 0;

  h2 {
    font-size: 1.6rem;
    font-weight: 600;
    color: white;
    margin: 0;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 18px;
    color: white;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
}

/* 模态框主体 */
.modal-body {
  padding: 18px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 表单样式 */
.event-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 18px;
  height: 100%;

  .form-group {
    display: flex;
    flex-direction: column;

    /* 活动标题 - 占满整行 */
    &:nth-child(1) {
      grid-column: 1 / -1;
    }

    /* 所属乐队和演出时间 - 并排显示 */
    &:nth-child(2), &:nth-child(3) {
      /* 默认占一列 */
    }

    /* 演出场地和详细地址 - 并排显示 */
    &:nth-child(4), &:nth-child(5) {
      /* 默认占一列 */
    }

    /* 票价和场地容量的行 */
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      grid-column: 1 / -1;
      
      .form-group.half {
        display: flex;
        flex-direction: column;
        margin: 0;
      }
    }

    /* 活动状态 - 占一列 */
    &:nth-child(7) {
      /* 默认占一列 */
    }

    /* 活动描述 - 占满整行 */
    &:nth-child(8) {
      grid-column: 1 / -1;
    }

    /* 海报图片 - 占满整行 */
    &:nth-child(9) {
      grid-column: 1 / -1;
    }

    label {
      font-weight: 600;
      color: #fff;
      margin-bottom: 5px;
      font-size: 13px;
      flex-shrink: 0;
    }

    input, select, textarea {
      padding: 9px 11px;
      border: none;
      border-radius: 5px;
      background: rgba(255, 255, 255, 0.15);
      color: white;
      font-size: 13px;
      transition: all 0.3s ease;
      box-sizing: border-box;
      flex: 1;

      &::placeholder {
        color: rgba(255, 255, 255, 0.6);
      }

      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      &:focus {
        outline: none;
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.5);
      }
    }

    select {
      background: #23232e;
      color: #fff;
      
      option {
        background: #23232e;
        color: #fff;
      }
    }

    textarea {
      resize: none;
      height: 70px;
    }

    .char-count {
      text-align: right;
      font-size: 10px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 2px;
      flex-shrink: 0;
    }
  }

  .price-input-wrapper {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 5px;
    overflow: hidden;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }

    &:focus-within {
      box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.5);
    }

    .price-prefix, .price-suffix {
      background: rgba(0, 0, 0, 0.2);
      padding: 9px 11px;
      color: rgba(255, 255, 255, 0.8);
      font-size: 13px;
    }

    input {
      border: none;
      flex: 1;
      margin: 0;
      background: transparent;
      padding: 9px 11px;

      &:focus {
        box-shadow: none;
      }
    }
  }
}

/* 海报上传区域 */
.poster-upload-section {
  display: flex;
  align-items: center;
  gap: 10px;

  input {
    flex: 1;
  }

  .upload-btn {
    background: linear-gradient(to right, #e53935, #e35d5b);
    color: white;
    border: none;
    padding: 9px 14px;
    border-radius: 5px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
    font-size: 13px;

    &:hover {
      box-shadow: 0 4px 12px rgba(229, 57, 53, 0.4);
      transform: translateY(-1px);
    }
  }
}

/* 模态框底部 */
.modal-footer {
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-shrink: 0;

  button {
    padding: 9px 22px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 13px;

    &.btn-cancel {
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: #ccc;

      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }

    &.btn-primary {
      background: linear-gradient(to right, #e53935, #e35d5b);
      border: none;
      color: white;

      &:hover:not(:disabled) {
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.4);
        transform: translateY(-1px);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
    }
  }
}

/* 状态选择器样式 */
.status-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 5px;

  .status-option {
    padding: 8px 16px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
      color: rgba(255, 255, 255, 0.9);
      border-color: rgba(255, 255, 255, 0.3);
    }

    &.active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-color: #667eea;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
  }
}

@media (max-width: 768px) {
  .modal-container {
    width: 95vw;
    height: 90vh;
  }
  
  .modal-body {
    padding: 14px;
  }
  
  .event-form {
    grid-template-columns: 1fr;
    gap: 10px;
    
    .form-row {
      grid-template-columns: 1fr;
      gap: 10px;
    }
  }
}
</style>











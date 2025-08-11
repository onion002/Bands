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
          <!-- 活动标题 -->
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
          </div>

          <!-- 参加乐队选择 -->
          <div class="form-group">
            <label class="form-label">参加乐队 *</label>
            <div class="band-selection">
              <!-- 已选择的乐队标签 -->
              <div class="selected-bands" v-if="formData.band_ids.length > 0">
                <div 
                  v-for="bandId in formData.band_ids" 
                  :key="bandId"
                  class="selected-band-tag"
                >
                  {{ getBandName(bandId) }}
                  <button 
                    type="button" 
                    class="remove-band-btn"
                    @click="removeBand(bandId)"
                  >
                    <i class="fa fa-times"></i>
                  </button>
                </div>
              </div>
              
              <!-- 乐队选择按钮 -->
              <div class="band-select-button">
                <button 
                  type="button"
                  class="select-bands-btn"
                  @click="openBandSelectionModal"
                >
                  <i class="fa fa-plus"></i>
                  {{ formData.band_ids.length > 0 ? `已选择 ${formData.band_ids.length} 个乐队` : '请选择乐队' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 活动状态 -->
          <div class="form-group">
            <label class="form-label">活动状态</label>
            <select v-model="formData.status" class="form-control">
              <option value="upcoming">即将售票</option>
              <option value="ongoing">售票中</option>
              <option value="completed">结束售票</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>

          <!-- 活动图片上传 -->
          <div class="form-group">
            <label class="form-label">活动图片</label>
            <div class="image-upload-area">
              <div class="image-preview">
                <img
                  v-if="formData.image_url"
                  :src="formData.image_url"
                  alt="活动图片"
                  class="preview-image"
                />
                <div v-else class="image-placeholder" @click="showUploadModal = true">
                  <i class="fa fa-image"></i>
                  <span>点击上传图片</span>
                </div>
              </div>
              <div class="image-actions">
                <button type="button" class="btn btn-outline btn-sm" @click="showUploadModal = true">
                  <i class="fa fa-camera"></i>
                  上传图片
                </button>
                <button
                  v-if="formData.image_url"
                  type="button"
                  class="btn btn-outline btn-sm btn-danger"
                  @click="removeImage"
                >
                  <i class="fa fa-trash"></i>
                  移除
                </button>
              </div>
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
              rows="3"
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

    <!-- 图片上传弹窗 -->
    <UploadModal
      v-if="showUploadModal"
      title="上传活动图片"
      :upload-api="uploadEventImage"
      accept="image/*"
      :max-size="5 * 1024 * 1024"
      @uploaded="handleImageUploaded"
      @close="showUploadModal = false"
    />

    <!-- 乐队选择模态框 -->
    <div class="band-selection-modal" v-if="showBandSelectionModal">
      <div class="band-selection-overlay" @click="closeBandSelectionModal"></div>
      <div class="band-selection-content">
        <div class="band-selection-header">
          <h3>选择参加乐队</h3>
          <button class="close-modal-btn" @click="closeBandSelectionModal">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <div class="band-selection-search">
          <input
            type="text"
            v-model="bandSearchKeyword"
            placeholder="搜索乐队..."
            class="search-input"
          />
        </div>

        <div class="band-selection-list">
          <div 
            v-for="band in filteredBands"
            :key="band.id"
            class="band-selection-item"
            @click="toggleBandSelection(band.id)"
          >
            <div class="checkbox-wrapper">
              <input 
                type="checkbox" 
                :checked="tempSelectedBands.includes(band.id)"
                @click.stop
              />
              <span class="checkmark"></span>
            </div>
            <span class="band-name">{{ band.name }}</span>
          </div>
          
          <div v-if="filteredBands.length === 0" class="no-bands">
            {{ bandSearchKeyword ? '没有找到匹配的乐队' : '没有可选的乐队' }}
          </div>
        </div>

        <div class="band-selection-footer">
          <button 
            type="button" 
            class="btn btn-outline"
            @click="clearAllSelections"
          >
            全部取消
          </button>
          <div class="footer-right">
            <button 
              type="button" 
              class="btn btn-outline"
              @click="cancelBandSelection"
            >
              取消
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="confirmBandSelection"
            >
              确定
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, onUnmounted } from 'vue';
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
const showBandSelectionModal = ref(false);
const bands = ref<any[]>([]);
const bandSearchKeyword = ref('');
const tempSelectedBands = ref<number[]>([]);

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
  band_ids: [] as number[],
  image_url: ''
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
      band_ids: newEvent.band_ids || [],
      image_url: newEvent.poster_image_url || ''
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
      band_ids: [],
      image_url: ''
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

// 计算过滤后的乐队列表
const filteredBands = computed(() => {
  if (!bandSearchKeyword.value.trim()) {
    return bands.value;
  }
  const keyword = bandSearchKeyword.value.toLowerCase();
  return bands.value.filter(band => 
    band.name.toLowerCase().includes(keyword)
  );
});

// 根据乐队ID获取乐队名称
const getBandName = (bandId: number) => {
  const band = bands.value.find(b => b.id === bandId);
  return band ? band.name : '未知乐队';
};

// 移除乐队
const removeBand = (bandId: number) => {
  const index = formData.value.band_ids.indexOf(bandId);
  if (index > -1) {
    formData.value.band_ids.splice(index, 1);
  }
};

// 打开乐队选择模态框
const openBandSelectionModal = () => {
  tempSelectedBands.value = [...formData.value.band_ids];
  bandSearchKeyword.value = '';
  showBandSelectionModal.value = true;
};

// 关闭乐队选择模态框
const closeBandSelectionModal = () => {
  showBandSelectionModal.value = false;
  tempSelectedBands.value = [];
  bandSearchKeyword.value = '';
};

// 切换乐队选择状态
const toggleBandSelection = (bandId: number) => {
  const index = tempSelectedBands.value.indexOf(bandId);
  if (index > -1) {
    // 如果已选择，则移除
    tempSelectedBands.value.splice(index, 1);
  } else {
    // 如果未选择，则添加
    tempSelectedBands.value.push(bandId);
  }
};

// 全部取消选择
const clearAllSelections = () => {
  tempSelectedBands.value = [];
};

// 取消选择（恢复原状态）
const cancelBandSelection = () => {
  closeBandSelectionModal();
};

// 确认选择
const confirmBandSelection = () => {
  formData.value.band_ids = [...tempSelectedBands.value];
  closeBandSelectionModal();
};

// 上传活动图片的API包装函数
const uploadEventImage = async (file: File) => {
  try {
    console.log('开始上传活动图片:', file.name);
    const formData = new FormData();
    formData.append('file', file);
    const response = await EventService.uploadPoster(formData);
    console.log('活动图片上传响应:', response);

    // 确保返回正确的格式，UploadModal期望的是 { url: string }
    const imageUrl = (response as any).url || (response as any).poster_url || response.data?.url || response.data?.poster_url;
    if (!imageUrl) {
      throw new Error('服务器返回的响应中没有找到图片URL');
    }

    return { url: imageUrl };
  } catch (error) {
    console.error('活动图片上传失败:', error);
    throw error;
  }
};

// 处理图片上传成功
const handleImageUploaded = (imageUrl: string) => {
  console.log('图片上传成功:', imageUrl);
  formData.value.image_url = imageUrl;
  showUploadModal.value = false;
};

// 移除图片
const removeImage = () => {
  formData.value.image_url = '';
};

// 提交表单
const handleSubmit = async () => {
  try {
    // 基本验证
    if (!formData.value.title.trim()) {
      alert('请输入活动标题');
      return;
    }
    if (!formData.value.band_ids || formData.value.band_ids.length === 0) {
      alert('请选择至少一个乐队');
      return;
    }
    if (!formData.value.event_date) {
      alert('请选择演出时间');
      return;
    }

    loading.value = true;

    const submitData = {
      ...formData.value,
      poster_image_url: formData.value.image_url
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

onUnmounted(() => {
  // 清理工作
});
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
@use 'sass:color';

// 活动模态框样式优化
.modal-overlay {
  @media (min-width: 1025px) {
    align-items: flex-start;
    padding-top: 40px;
  }

  @media (max-width: 768px) {
    align-items: flex-end;
  }
}

.modal {
  max-width: 750px;
  display: flex;
  flex-direction: column;

  @media (min-width: 1025px) {
    max-height: calc(100vh - 100px);
  }

  .modal-header {
    padding: 1.25rem 1.5rem 0.75rem;
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
    padding: 0.5rem;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;

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
    flex-shrink: 0;
  }
}

// 表单样式
.event-form {
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 0.25rem;

    @media (max-width: 480px) {
      grid-template-columns: 1fr;
      gap: 0.5rem;
    }
  }

  .form-group {
    margin-bottom: 0.25rem;

    .form-label {
      display: block;
      color: $white;
      font-weight: 500;
      font-size: 0.8rem;
      margin-bottom: 0.25rem;
    }

    .form-control {
      width: 100%;
      padding: 0.5rem 0.75rem;
      background: rgba($lightgray, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: $border-radius-lg;
      color: $white;
      font-size: 0.85rem;
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
      min-height: 100px;
      line-height: 1.5;
    }

    .char-count {
      text-align: right;
      font-size: 0.7rem;
      color: rgba(255, 255, 255, 0.5);
      font-weight: 500;
      margin-top: 0.25rem;

      &.warning {
        color: #fbbf24;
      }

      &.danger {
        color: #ef4444;
      }
    }
  }
}

// 图片上传区域
.image-upload-area {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: $border-radius-lg;
  border: 1px solid rgba(255, 255, 255, 0.1);

  .image-preview {
    width: 120px;
    height: 120px;
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
      max-width: 100%;
      max-height: 100%;
      object-fit: cover;
      object-position: center;
      border-radius: calc($border-radius-lg - 2px);
      display: block;
    }

    .image-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: rgba(255, 255, 255, 0.6);
      text-align: center;
      padding: 1rem;
      width: 100%;
      height: 100%;
      cursor: pointer;

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
    padding-top: 0.5rem;
  }
}

// 乐队选择样式
.band-selection {
  .selected-bands {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
    min-height: 1.25rem;
    padding: 0.125rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: $border-radius-md;
    border: 1px solid rgba(255, 255, 255, 0.1);

    .selected-band-tag {
      display: flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.25rem 0.5rem;
      background: rgba($secondary, 0.2);
      border: 1px solid rgba($secondary, 0.4);
      border-radius: $border-radius-sm;
      color: $white;
      font-size: 0.75rem;
      font-weight: 500;
      transition: all $transition-normal ease;

      &:hover {
        background: rgba($secondary, 0.3);
        border-color: rgba($secondary, 0.6);
        transform: translateY(-1px);
      }

      .remove-band-btn {
        background: none;
        border: none;
        color: rgba($secondary, 0.8);
        cursor: pointer;
        padding: 0.15rem;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all $transition-normal ease;

        &:hover {
          background: rgba($secondary, 0.2);
          color: $secondary;
        }

        i {
          font-size: 0.65rem;
        }
      }
    }
  }

  .band-select-button {
    .select-bands-btn {
      width: 100%;
      padding: 0.75rem 1rem;
      background: rgba($primary, 0.1);
      border: 2px dashed rgba($primary, 0.3);
      border-radius: $border-radius-lg;
      color: $white;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all $transition-normal ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;

      &:hover {
        background: rgba($primary, 0.2);
        border-color: rgba($primary, 0.5);
        transform: translateY(-1px);
      }

      i {
        font-size: 0.8rem;
        color: $primary;
      }
    }
  }
}

// 乐队选择模态框样式
.band-selection-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;

  .band-selection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba($black, 0.7);
    backdrop-filter: blur(5px);
  }

  .band-selection-content {
    position: relative;
    background: $darkgray;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: $border-radius-lg;
    box-shadow: 0 8px 32px rgba($black, 0.4);
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(10px);

    .band-selection-header {
      padding: 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        color: $white;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
      }

      .close-modal-btn {
        background: none;
        border: none;
        color: $gray-400;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 50%;
        transition: all $transition-normal ease;

        &:hover {
          color: $white;
          background: rgba(255, 255, 255, 0.1);
        }

        i {
          font-size: 1.1rem;
        }
      }
    }

    .band-selection-search {
      padding: 1rem 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      .search-input {
        width: 100%;
        padding: 0.75rem 1rem;
        background: rgba($lightgray, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: $border-radius-md;
        color: $white;
        font-size: 0.9rem;
        transition: all $transition-normal ease;

        &::placeholder {
          color: rgba(255, 255, 255, 0.5);
        }

        &:focus {
          outline: none;
          border-color: $primary;
          background: rgba($lightgray, 0.5);
          box-shadow: 0 0 0 3px rgba($primary, 0.2);
        }
      }
    }

    .band-selection-list {
      flex: 1;
      overflow-y: auto;
      padding: 0.5rem 0;
      max-height: 400px;

      .band-selection-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all $transition-normal ease;

        &:hover {
          background: rgba($primary, 0.1);
        }

        .checkbox-wrapper {
          position: relative;
          width: 20px;
          height: 20px;

          input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            width: 100%;
            height: 100%;
          }

          .checkmark {
            position: absolute;
            top: 0;
            left: 0;
            width: 20px;
            height: 20px;
            background: rgba($lightgray, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            transition: all $transition-normal ease;

            &::after {
              content: '';
              position: absolute;
              left: 6px;
              top: 2px;
              width: 5px;
              height: 10px;
              border: solid $white;
              border-width: 0 2px 2px 0;
              transform: rotate(45deg);
              opacity: 0;
              transition: opacity $transition-normal ease;
            }
          }

          input[type="checkbox"]:checked ~ .checkmark {
            background: $primary;
            border-color: $primary;

            &::after {
              opacity: 1;
            }
          }
        }

        .band-name {
          color: $white;
          font-size: 0.95rem;
          font-weight: 500;
        }
      }

      .no-bands {
        padding: 2rem;
        text-align: center;
        color: $gray-400;
        font-size: 0.9rem;
      }
    }

    .band-selection-footer {
      padding: 1.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;

      .footer-right {
        display: flex;
        gap: 0.75rem;
      }

      .btn {
        padding: 0.75rem 1.5rem;
        border-radius: $border-radius-md;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all $transition-normal ease;
        cursor: pointer;

        &.btn-outline {
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: $white;

          &:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.3);
          }
        }

        &.btn-primary {
          background: $primary;
          border: 1px solid $primary;
          color: $white;

          &:hover {
            background: darken($primary, 10%);
            border-color: darken($primary, 10%);
            transform: translateY(-1px);
          }
        }
      }
    }
  }
}
</style>

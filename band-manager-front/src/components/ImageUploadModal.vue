<template>
  <div class="modal-overlay" @click.self="close">
    <div class="upload-modal">
      <div class="modal-header">
        <h2>上传乐队图片</h2>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 上传区域 -->
        <div v-if="!previewUrl" class="upload-area" @dragover.prevent @drop="handleDrop">
          <i class="fas fa-cloud-upload-alt"></i>
          <p>拖放图片到这里或</p>
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" hidden>
          <button class="select-file" @click="triggerFileInput">选择图片</button>
          <p class="hint">支持 JPG, PNG, GIF 格式，最大 5MB</p>
        </div>
        
        <!-- 预览区域 -->
        <div v-else class="preview-area">
          <img :src="previewUrl" alt="预览图">
          <div class="preview-actions">
            <button class="cancel-btn" @click="clearPreview">重新选择</button>
            <button class="upload-btn" @click="startUpload" :disabled="uploading">
              {{ uploading ? '上传中...' : '确认上传' }}
            </button>
          </div>
        </div>
        
        <!-- 上传进度 -->
        <div v-if="uploading" class="progress-container">
          <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>
        
        <!-- 上传结果 -->
        <div v-if="result" class="result-message" :class="{ success: result.success, error: !result.success }">
          <i :class="['fas', result.success ? 'fa-check-circle' : 'fa-exclamation-circle']"></i>
          <span>{{ result.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BandService } from '@/api/bandService'

// 新增：定义 props 和 emits
const props = defineProps<{ bandId?: number }>()
const emit = defineEmits<{
  (e: 'uploaded', bandId: number | null, imageUrl: string): void
  (e: 'close'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const uploading = ref(false)
const progress = ref(0)
const result = ref<{ success: boolean; message: string; url?: string } | null>(null)

// 触发文件选择
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 处理文件选择
const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    processFile(input.files[0])
  }
}

// 处理拖放
const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    processFile(e.dataTransfer.files[0])
  }
}

// 处理文件
const processFile = (selectedFile: File) => {
  // 检查文件类型
  if (!['image/jpeg', 'image/png', 'image/gif'].includes(selectedFile.type)) {
    result.value = {
      success: false,
      message: '不支持的文件类型，请上传 JPG、PNG 或 GIF 格式'
    }
    return
  }
  
  // 检查文件大小 (5MB)
  if (selectedFile.size > 5 * 1024 * 1024) {
    result.value = {
      success: false,
      message: '文件大小超过 5MB 限制'
    }
    return
  }
  
  file.value = selectedFile
  previewUrl.value = URL.createObjectURL(selectedFile)
  result.value = null
}

// 清除预览
const clearPreview = () => {
  previewUrl.value = null
  file.value = null
  result.value = null
}

// 开始上传
const startUpload = async () => {
  if (!file.value) return

  uploading.value = true
  result.value = null

  try {
    const response: any = await BandService.uploadBandImage(file.value)
    const imageUrl = response.url

    result.value = {
      success: true,
      message: '图片上传成功',
      url: imageUrl
    }

    // 上传成功后 emit uploaded 事件，通知父组件
    if (imageUrl) {
      // 如果有 bandId 作为 prop，emit bandId，否则 emit null
      emit('uploaded', props.bandId || null, imageUrl)
    }

    setTimeout(() => {
      if (imageUrl) {
        close()
      }
    }, 1500)
  } catch (err: any) {
    result.value = {
      success: false,
      message: '上传失败: ' + (err.message || '服务器错误')
    }
  } finally {
    uploading.value = false
  }
}

// 关闭模态框
const close = () => {
  // Implement the close logic here
}
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.upload-modal {
  background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(229, 57, 53, 0.3);
  overflow: hidden;

  .modal-header {
    background: rgba(229, 57, 53, 0.8);
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h2 {
      margin: 0;
      color: white;
      font-size: 1.6rem;
    }
    
    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 1.5rem;
      cursor: pointer;
      transition: transform 0.3s ease;
      
      &:hover {
        transform: rotate(90deg);
      }
    }
  }
  
  .modal-body {
    padding: 25px;
    
    .upload-area {
      border: 2px dashed #555;
      border-radius: 8px;
      padding: 40px 20px;
      text-align: center;
      
      i {
        font-size: 3.5rem;
        color: #e53935;
        margin-bottom: 15px;
        display: block;
      }
      
      p {
        margin: 0 0 15px;
        color: #bbb;
      }
      
      .select-file {
        background: linear-gradient(to right, #e53935, #e35d5b);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
        }
      }
      
      .hint {
        margin-top: 15px;
        font-size: 0.85rem;
        color: #888;
      }
    }
    
    .preview-area {
      text-align: center;
      
      img {
        max-width: 100%;
        max-height: 300px;
        border-radius: 8px;
        border: 1px solid #555;
        margin-bottom: 20px;
      }
      
      .preview-actions {
        display: flex;
        justify-content: center;
        gap: 15px;
        
        button {
          padding: 10px 25px;
          border: none;
          border-radius: 30px;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &.cancel-btn {
            background: #444;
            color: #ddd;
            
            &:hover {
              background: #555;
            }
          }
          
          &.upload-btn {
            background: linear-gradient(to right, #4caf50, #81c784);
            color: white;
            
            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
            }
            
            &:disabled {
              background: #888;
              cursor: not-allowed;
            }
          }
        }
      }
    }
    
    .progress-container {
      height: 8px;
      background: #333;
      border-radius: 4px;
      margin: 20px 0;
      overflow: hidden;
      
      .progress-bar {
        height: 100%;
        background: linear-gradient(to right, #e53935, #e35d5b);
        transition: width 0.3s ease;
      }
    }
    
    .result-message {
      padding: 15px;
      border-radius: 8px;
      text-align: center;
      margin-top: 15px;
      
      i {
        margin-right: 10px;
        font-size: 1.2rem;
      }
      
      &.success {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
      }
      
      &.error {
        background: rgba(229, 57, 53, 0.2);
        color: #e53935;
      }
    }
  }
}
</style>
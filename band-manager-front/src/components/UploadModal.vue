<template>
  <div class="modal-overlay" @click.self="close">
    <div class="upload-modal">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 上传区域 -->
        <div v-if="!previewUrl" class="upload-area" @dragover.prevent @drop="handleDrop">
          <i class="fas fa-user-circle"></i>
          <p>拖放图片到这里或</p>
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" hidden>
          <button class="select-file" @click="triggerFileInput">选择图片</button>
          <p class="hint">支持 JPG, PNG, GIF 格式，最大 5MB</p>
        </div>
        
        <!-- 预览区域 -->
        <div v-else class="preview-area">
          <img :src="previewUrl" alt="预览头像">
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

// 通用图片上传弹窗组件
const props = defineProps<{
  title: string,
  uploadApi: (file: File) => Promise<any>,
  accept?: string,
  maxSize?: number,
  // 可选：上传成功后返回的url字段名
  urlField?: string
}>()
const emit = defineEmits<{
  (e: 'uploaded', url: string): void
  (e: 'close'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const uploading = ref(false)
const progress = ref(0)
const result = ref<{ success: boolean; message: string; url?: string } | null>(null)

const acceptType = props.accept || 'image/*'
const maxFileSize = props.maxSize || 5 * 1024 * 1024
const urlField = props.urlField || 'url'

const triggerFileInput = () => {
  if (fileInput.value) fileInput.value.click()
}
const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    processFile(input.files[0])
  }
}
const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    processFile(e.dataTransfer.files[0])
  }
}
const processFile = (selectedFile: File) => {
  console.log('处理文件:', selectedFile.name, selectedFile.type, selectedFile.size)
  console.log('接受的类型:', acceptType)
  
  // 修复文件类型验证逻辑
  let isValidType = false
  
  // 如果 acceptType 是 "image/*"，检查文件类型是否以 "image/" 开头
  if (acceptType === 'image/*') {
    isValidType = selectedFile.type.startsWith('image/')
  } else {
    // 处理其他具体的 MIME 类型
    const acceptTypes = acceptType.split(',').map(type => type.trim())
    isValidType = acceptTypes.includes(selectedFile.type)
  }
  
  console.log('文件类型验证结果:', isValidType)
  
  if (!isValidType) {
    result.value = {
      success: false,
      message: `不支持的文件类型，请上传图片文件 (支持: JPG, PNG, GIF, WEBP)`
    }
    return
  }
  
  if (selectedFile.size > maxFileSize) {
    result.value = {
      success: false,
      message: `文件大小超过 ${(maxFileSize / 1024 / 1024).toFixed(1)}MB 限制`
    }
    return
  }
  
  file.value = selectedFile
  previewUrl.value = URL.createObjectURL(selectedFile)
  result.value = null
  
  console.log('文件处理完成，准备预览')
}
const clearPreview = () => {
  previewUrl.value = null
  file.value = null
  result.value = null
}
const startUpload = async () => {
  if (!file.value) return
  
  console.log('开始上传文件:', file.value.name, file.value.type)
  
  uploading.value = true
  result.value = null
  progress.value = 0
  
  try {
    const progressInterval = setInterval(() => {
      if (progress.value < 90) progress.value += 10
    }, 100)
    
    console.log('调用上传 API...')
    const response: any = await props.uploadApi(file.value)
    console.log('上传响应:', response)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    // 修复URL获取逻辑，支持多种字段名
    const url = response[urlField] || response.url || response.poster_url
    console.log('提取的URL:', url, '使用字段:', urlField)
    
    result.value = {
      success: true,
      message: '图片上传成功',
      url
    }
    
    if (url) {
      emit('uploaded', url)
    } else {
      throw new Error('响应中未找到图片URL')
    }
    
    setTimeout(() => {
      if (url) close()
    }, 1500)
  } catch (err: any) {
    console.error('上传失败:', err)
    result.value = {
      success: false,
      message: '上传失败: ' + (err.message || '服务器错误')
    }
  } finally {
    uploading.value = false
  }
}
const close = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.upload-modal {
  background: linear-gradient(135deg, rgba(30, 30, 46, 0.95), rgba(44, 44, 62, 0.9));
  backdrop-filter: blur(20px);
  border-radius: 20px;
  width: 550px;
  max-width: 90vw;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 42, 109, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  animation: modalSlideIn 0.3s ease;
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
  background: linear-gradient(135deg, rgba(255, 42, 109, 0.8), rgba(5, 217, 232, 0.6));
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.75rem;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
  border-color: rgba(255, 255, 255, 0.4);
}

.modal-body {
  padding: 30px;
  color: white;
}

.upload-area {
  border: 2px dashed rgba(255, 42, 109, 0.4);
  border-radius: 16px;
  padding: 50px 30px;
  text-align: center;
  transition: all 0.3s ease;
  background: rgba(255, 42, 109, 0.05);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
  }

  &:hover {
    border-color: rgba(255, 42, 109, 0.7);
    background: rgba(255, 42, 109, 0.1);
    transform: translateY(-2px);

    &::before {
      left: 100%;
    }
  }
}

.upload-area i {
  font-size: 4rem;
  color: #ff2a6d;
  margin-bottom: 20px;
  display: block;
  opacity: 0.8;
}

.upload-area p {
  margin: 0 0 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.select-file {
  background: linear-gradient(135deg, #ff2a6d, #05d9e8);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 42, 109, 0.3);
}

.select-file:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 42, 109, 0.4);
  background: linear-gradient(135deg, #e6246a, #04c4d1);
}

.hint {
  margin-top: 20px !important;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.preview-area {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-area img {
  max-width: 250px;
  max-height: 250px;
  border-radius: 16px;
  object-fit: cover;
  margin-bottom: 25px;
  border: 3px solid #ff2a6d;
  box-shadow: 0 8px 25px rgba(255, 42, 109, 0.3);
  transition: transform 0.3s ease;

  &:hover {
    transform: scale(1.02);
  }
}

.preview-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.cancel-btn, .upload-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.upload-btn {
  background: linear-gradient(135deg, #ff2a6d, #05d9e8);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 42, 109, 0.3);
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 42, 109, 0.4);
  background: linear-gradient(135deg, #e6246a, #04c4d1);
}

.upload-btn:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.progress-container {
  margin: 25px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  height: 10px;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: shimmer 2s infinite;
  }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-bar {
  height: 100%;
  background: linear-gradient(135deg, #ff2a6d, #05d9e8);
  transition: width 0.3s ease;
  border-radius: 12px;
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: progressShine 1.5s infinite;
  }
}

@keyframes progressShine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.result-message {
  margin-top: 25px;
  padding: 18px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.result-message.success {
  background: rgba(40, 167, 69, 0.15);
  border: 1px solid rgba(40, 167, 69, 0.4);
  color: #4ade80;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
}

.result-message.error {
  background: rgba(220, 53, 69, 0.15);
  border: 1px solid rgba(220, 53, 69, 0.4);
  color: #f87171;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
}

@media (max-width: 768px) {
  .upload-modal {
    width: 95%;
    margin: 10px;
  }
  
  .modal-header, .modal-body {
    padding: 15px;
  }
  
  .preview-actions {
    flex-direction: column;
  }
  
  .cancel-btn, .upload-btn {
    width: 100%;
  }
}
</style>

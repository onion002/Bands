<template>
  <div class="modal-overlay" @click.self="close">
    <div class="upload-modal">
      <div class="modal-header">
        <h2>上传成员头像</h2>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 上传区域 -->
        <div v-if="!previewUrl" class="upload-area" @dragover.prevent @drop="handleDrop">
          <i class="fas fa-user-circle"></i>
          <p>拖放头像到这里或</p>
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" hidden>
          <button class="select-file" @click="triggerFileInput">选择头像</button>
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
import { MemberService } from '@/api/memberService'

// 定义 props 和 emits
const props = defineProps<{ 
  memberId: number
  memberName: string
}>()
const emit = defineEmits<{
  (e: 'uploaded', memberId: number, avatarUrl: string): void
  (e: 'close'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const uploading = ref(false)
const progress = ref(0)
const result = ref<{ success: boolean; message: string; avatar_url?: string } | null>(null)

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
  progress.value = 0

  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 100)

    const response: any = await MemberService.uploadMemberAvatar(props.memberId, file.value)
    
    clearInterval(progressInterval)
    progress.value = 100

    result.value = {
      success: true,
      message: '头像上传成功',
      avatar_url: response.avatar_url
    }

    // 上传成功后 emit uploaded 事件，通知父组件
    if (response.avatar_url) {
      emit('uploaded', props.memberId, response.avatar_url)
    }

    setTimeout(() => {
      if (response.avatar_url) {
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
  background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(229, 57, 53, 0.3);
  overflow: hidden;
}

.modal-header {
  background: rgba(229, 57, 53, 0.8);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
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
}

.close-btn:hover {
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px;
  color: white;
}

.upload-area {
  border: 2px dashed #555;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  transition: border-color 0.3s ease;
}

.upload-area:hover {
  border-color: #e53935;
}

.upload-area i {
  font-size: 3.5rem;
  color: #e53935;
  margin-bottom: 15px;
  display: block;
}

.upload-area p {
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
}

.select-file:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
}

.hint {
  margin-top: 15px !important;
  font-size: 0.85rem;
  color: #888;
}

.preview-area {
  text-align: center;
}

.preview-area img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 20px;
  border: 3px solid #e53935;
}

.preview-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.cancel-btn, .upload-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 30px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #666;
  color: white;
}

.cancel-btn:hover {
  background: #777;
}

.upload-btn {
  background: linear-gradient(to right, #e53935, #e35d5b);
  color: white;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
}

.upload-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.progress-container {
  margin: 20px 0;
  background: #333;
  border-radius: 10px;
  overflow: hidden;
  height: 8px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(to right, #e53935, #e35d5b);
  transition: width 0.3s ease;
}

.result-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-message.success {
  background: rgba(40, 167, 69, 0.2);
  border: 1px solid #28a745;
  color: #28a745;
}

.result-message.error {
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid #dc3545;
  color: #dc3545;
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

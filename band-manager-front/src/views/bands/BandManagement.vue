<template>
  <div class="band-management">
    <!-- 页面标题 -->
    <div class="section-header">
      <h1>乐队管理</h1>
      <div class="button-group">
        <button class="back-button" @click="goToHome">
          <i class="fas fa-arrow-left"></i> 返回主页
        </button>
        <button class="add-band-btn" @click="openCreateModal">
          <i class="fas fa-plus"></i> 添加新乐队
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> 加载中...
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-state">
      {{ error }}
      <button @click="fetchBands">重试</button>
    </div>
    
    <!-- 空状态 -->
    <div v-if="!loading && bands.length === 0" class="empty-state">
      <i class="fas fa-music"></i>
      <p>暂无乐队数据</p>
      <button @click="openCreateModal">添加第一支乐队</button>
    </div>
    
    <!-- 乐队列表 -->
    <div v-if="!loading && bands.length > 0" class="band-list">
      <div v-for="band in bands" :key="band.id" class="band-item">
        <div class="band-card">
          <div class="band-image" :style="{ backgroundColor: '#444' }">
            <img
              v-if="band.banner_image_url"
              :src="band.banner_image_url"
              class="band-image-content"
              @click="openBioDialog(band)"
              style="cursor: pointer;"
            >
            <div v-else class="image-placeholder">
              <i class="fas fa-music"></i>
              <span>乐队图片</span>
            </div>
            <!-- 上传图片按钮 -->
            <button class="upload-button" @click="openImageUpload(band)">
              <i class="fas fa-camera"></i> 上传图片
            </button>
          </div>
          <div class="band-info">
            <h3 class="band-name">{{ band.name }}</h3>
            <p class="band-genre">{{ band.genre }}</p>
            <p class="band-year">成立年份: {{ band.year }}</p>
            <div class="band-actions">
              <button @click="editBand(band)" class="action-btn edit">
                <i class="fas fa-edit"></i> 编辑
              </button>
              <button @click="deleteBand(band)" class="action-btn delete">
                <i class="fas fa-trash"></i> 删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加乐队模态框 -->
    <BandModal 
      v-if="showCreateModal"
      mode="add"
      @close="closeCreateModal"
      @save="createNewBand"
    />
    
    <!-- 编辑乐队模态框 -->
    <BandModal 
      v-if="showEditModal"
      :band="selectedBand"
      mode="edit"
      @close="closeEditModal"
      @save="updateBand"
    />
    
    <!-- 图片上传模态框 -->
    <ImageUploadModal 
      v-if="showImageUploadModal"
      :band-id="selectedBand?.id"
      @close="closeImageUpload"
      @uploaded="handleImageUploaded"
    />
    
    <!-- 乐队简介弹窗 -->
    <div v-if="showBioDialog" class="bio-dialog-overlay" @click.self="closeBioDialog">
      <div class="bio-dialog">
        <h3>乐队简介</h3>
        <div class="bio-content">{{ bioDialogBand?.bio || '暂无简介' }}</div>
        <button class="close-bio-btn" @click="closeBioDialog">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { BandService } from '@/api/bandService'
import BandModal from '@/components/BandModal.vue'
import ImageUploadModal from '@/components/ImageUploadModal.vue'

const router = useRouter()
const bands = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showImageUploadModal = ref(false)
const selectedBand = ref<any>(null)

// 乐队简介弹窗相关
const showBioDialog = ref(false)
const bioDialogBand = ref<any>(null)
const openBioDialog = (band: any) => {
  // 用 bands 列表里最新的 band
  const latest = bands.value.find(b => b.id === band.id) || band
  bioDialogBand.value = latest
  showBioDialog.value = true
}
const closeBioDialog = () => {
  showBioDialog.value = false
  bioDialogBand.value = null
}

// 获取乐队列表
const fetchBands = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await BandService.getBands()
    console.log('bands api result:', result)
    bands.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    error.value = '获取乐队列表失败: ' + err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 返回主页
const goToHome = () => {
  router.push('/')
}

// 打开创建模态框
const openCreateModal = () => {
  showCreateModal.value = true
}

// 关闭创建模态框
const closeCreateModal = () => {
  showCreateModal.value = false
}

// 创建新乐队
const createNewBand = async (bandData: any) => {
  try {
    await BandService.createBand(bandData)
    await fetchBands()
    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    closeCreateModal()
  } catch (err) {
    error.value = '创建乐队失败'
    console.error('创建乐队失败:', err)
  }
}

// 打开编辑模态框
const editBand = (band: any) => {
  selectedBand.value = band
  showEditModal.value = true
}

// 关闭编辑模态框
const closeEditModal = () => {
  showEditModal.value = false
  selectedBand.value = null
}

// 更新乐队
const updateBand = async (bandData: any) => {
  try {
    await BandService.updateBand(bandData.id, bandData)
    await fetchBands() // 强制刷新
    // 用最新 bands 数据同步 bioDialogBand
    if (showBioDialog.value && bioDialogBand.value?.id === bandData.id) {
      const latest = bands.value.find(b => b.id === bandData.id)
      if (latest) bioDialogBand.value = latest
    }
    closeEditModal()
  } catch (err) {
    error.value = '更新乐队失败'
    console.error('更新乐队失败:', err)
  }
}

// 删除乐队
const deleteBand = async (band: any) => {
  if (!confirm(`确定删除乐队 "${band.name}" 吗?`)) return
  try {
    await BandService.deleteBand(band.id)
    await fetchBands()
  } catch (err) {
    error.value = '删除乐队失败'
    console.error('删除乐队失败:', err)
  }
}

// 打开图片上传模态框
const openImageUpload = (band: any) => {
  selectedBand.value = band
  showImageUploadModal.value = true
}

// 关闭图片上传模态框
const closeImageUpload = () => {
  showImageUploadModal.value = false
  selectedBand.value = null
}

// 处理图片上传完成
const handleImageUploaded = async (bandId: number | null, imageUrl: string) => {
  if (bandId == null) return;
  // 上传图片后，更新数据库中的 banner_image_url 字段
  try {
    const band = bands.value.find(b => b.id === bandId);
    await BandService.updateBand(bandId, {
      name: band.name,
      year: band.year,
      genre: band.genre,
      member_count: band.member_count,
      bio: band.bio,
      banner_image_url: imageUrl
    });
    await fetchBands(); // 刷新乐队列表，确保图片能显示
  } finally {
    closeImageUpload();
  }
}

onMounted(() => {
  fetchBands()
})
</script>

<style scoped lang="scss">
.band-management {
  background-color: #111;
  color: white;
  min-height: 100vh;
  padding: 20px;
  position: relative;
  overflow-y: auto;
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 30px 0 15px 0;
    border-bottom: 1px solid #333;
    
    h1 {
      font-size: 2.2rem;
      color: #e53935;
      margin: 0;
    }
    
    .button-group {
      display: flex;
      gap: 16px;
      align-items: center;
      
      .back-button {
        background: #333;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 30px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: #444;
        }
        i {
          margin-right: 5px;
        }
      }
      
      .add-band-btn {
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
        i {
          margin-right: 8px;
        }
      }
    }
  }
  
  // 状态指示器样式
  .loading-state, .error-state, .empty-state {
    text-align: center;
    padding: 50px 20px;
    font-size: 1.2rem;
    
    i {
      font-size: 3rem;
      margin-bottom: 15px;
      color: #e53935;
    }
    
    button {
      margin-top: 15px;
      padding: 10px 20px;
      background: linear-gradient(to right, #e53935, #e35d5b);
      color: white;
      border: none;
      border-radius: 30px;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s ease;
    }
  }
  
  .error-state {
    button {
      background: #333;
    }
  }
  
  .band-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
    min-height: 100vh;
    
    .band-item {
      .band-card {
        background: #222;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
        
        &:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2);
        }
        
        .band-image {
          height: 180px;
          background-color: #444;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          
          .image-placeholder {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            z-index: 1;
            
            i {
              font-size: 3.5rem;
              display: block;
              margin-bottom: 10px;
              color: rgba(229, 57, 53, 0.7);
            }
            
            span {
              font-size: 1.2rem;
            }
          }
          
          .band-image-content {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
          }
          
          .upload-button {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            z-index: 2;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(229, 57, 53, 0.7);
            }
            
            i {
              margin-right: 5px;
            }
          }
        }
        
        .band-info {
          padding: 15px;
          
          .band-name {
            font-size: 1.5rem;
            margin: 0 0 5px;
            color: white;
          }
          
          .band-genre, .band-year {
            font-size: 1rem;
            color: #aaa;
            margin: 5px 0;
          }
          
          .band-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 15px;
            
            .action-btn {
              padding: 8px 15px;
              border: none;
              border-radius: 4px;
              font-size: 0.9rem;
              font-weight: 500;
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover {
                transform: translateY(-2px);
              }
              
              i {
                margin-right: 5px;
              }
              
              &.edit {
                background: rgba(41, 121, 255, 0.8);
                color: white;
              }
              
              &.delete {
                background: rgba(229, 57, 53, 0.8);
                color: white;
              }
            }
          }
        }
      }
    }
  }
}

.bio-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.bio-dialog {
  background: #222;
  color: #fff;
  border-radius: 10px;
  padding: 30px 30px 20px 30px;
  min-width: 300px;
  max-width: 90vw;
  box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  text-align: left;
  position: relative;
}
.bio-dialog h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #e53935;
}
.bio-content {
  margin-bottom: 20px;
  white-space: pre-wrap;
  word-break: break-all;
}
.close-bio-btn {
  background: #e53935;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 8px 24px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.close-bio-btn:hover {
  background: #b71c1c;
}
</style>
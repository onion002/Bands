<template>
  <!-- 乐队管理页面主容器 -->
  <div class="band-management">
    <!-- 页面标题和操作按钮区域 -->
    <div class="section-header">
      <h1>乐队管理</h1>
      <div class="button-group">
        <!-- 返回主页按钮 -->
        <button class="back-button" @click="goToHome">
          <i class="fas fa-arrow-left"></i> 返回主页
        </button>
        <!-- 添加新乐队按钮 -->
        <button class="add-band-btn" @click="openCreateModal">
          <i class="fas fa-plus"></i> 添加新乐队
        </button>
      </div>
    </div>
    
    <!-- 加载状态指示器 -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> 加载中...
    </div>
    
    <!-- 错误提示区域 -->
    <div v-if="error" class="error-state">
      {{ error }}
      <button @click="fetchBands">重试</button>
    </div>
    
    <!-- 数据为空时的提示 -->
    <div v-if="!loading && bands.length === 0" class="empty-state">
      <i class="fas fa-music"></i>
      <p>暂无乐队数据</p>
      <button @click="openCreateModal">添加第一支乐队</button>
    </div>
    
    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="filter-group">
        <label>按乐队种类筛选：</label>
        <select v-model="selectedGenre" @change="handleGenreFilter">
          <option value="">全部种类</option>
          <option v-for="genre in genreOptions" :key="genre" :value="genre">{{ genre }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>搜索乐队：</label>
        <input
          type="text"
          v-model="searchKeyword"
          @input="handleSearch"
          placeholder="输入乐队名称或流派"
        >
      </div>
    </div>
    
    <!-- 乐队列表展示 -->
    <div v-if="!loading && bands.length > 0" class="band-list">
      <div v-for="band in paginatedBands" :key="band.id" class="band-item">
        <div class="band-card">
          <!-- 乐队图片区域 -->
          <div class="band-image" :style="{ backgroundColor: '#444' }">
            <!-- 如果有图片则显示图片，否则显示占位符 -->
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
          <!-- 乐队信息区域 -->
          <div class="band-info">
            <h3 class="band-name">{{ band.name }}</h3>
            <p class="band-genre">{{ band.genre }}</p>
            <p class="band-year">成立年份: {{ band.year }}</p>
            <div class="band-actions">
              <!-- 编辑按钮 -->
              <button @click="editBand(band)" class="action-btn edit">
                <i class="fas fa-edit"></i> 编辑
              </button>
              <!-- 删除按钮 -->
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
// 引入 Vue 相关 API
import { ref, onMounted, nextTick, computed } from 'vue'
// 引入路由
import { useRouter } from 'vue-router'
// 引入乐队相关 API 服务
import { BandService } from '@/api/bandService'
// 引入乐队信息编辑模态框组件
import BandModal from '@/components/BandModal.vue'
// 引入图片上传模态框组件
import ImageUploadModal from '@/components/ImageUploadModal.vue'

// 路由实例
const router = useRouter()
// 乐队列表数据
const bands = ref<any[]>([])
// 加载状态
const loading = ref(false)
// 错误信息
const error = ref('')
// 控制添加乐队模态框显示
const showCreateModal = ref(false)
// 控制编辑乐队模态框显示
const showEditModal = ref(false)
// 控制图片上传模态框显示
const showImageUploadModal = ref(false)
// 当前选中的乐队（用于编辑/上传图片）
const selectedBand = ref<any>(null)

// 乐队简介弹窗相关状态
const showBioDialog = ref(false) // 是否显示简介弹窗
const bioDialogBand = ref<any>(null) // 当前简介弹窗展示的乐队
// 打开简介弹窗，显示指定乐队的简介
const openBioDialog = (band: any) => {
  // 用 bands 列表里最新的 band 数据，防止信息不同步
  const latest = bands.value.find(b => b.id === band.id) || band
  bioDialogBand.value = latest
  showBioDialog.value = true
}
// 关闭简介弹窗
const closeBioDialog = () => {
  showBioDialog.value = false
  bioDialogBand.value = null
}

// 筛选和搜索状态
const selectedGenre = ref('')
const searchKeyword = ref('')

// 计算所有乐队种类（去重）
const genreOptions = computed(() => {
  const set = new Set<string>()
  bands.value.forEach(b => b.genre && set.add(b.genre))
  return Array.from(set)
})

// 处理种类筛选
const handleGenreFilter = () => {
  currentPage.value = 1
}
// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

// 计算属性：筛选和搜索后的乐队列表
const filteredBands = computed(() => {
  let result = bands.value
  if (selectedGenre.value) {
    result = result.filter(b => b.genre === selectedGenre.value)
  }
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    result = result.filter(b =>
      b.name.toLowerCase().includes(kw) ||
      (b.genre && b.genre.toLowerCase().includes(kw))
    )
  }
  return result
})

// 分页后的乐队列表
const paginatedBands = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredBands.value.slice(start, start + pageSize.value)
})

// 获取乐队列表数据
const fetchBands = async () => {
  try {
    loading.value = true
    error.value = ''
    // 调用后端 API 获取乐队数据
    const result = await BandService.getBands()
    console.log('bands api result:', result)
    // 赋值到 bands 列表
    bands.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    error.value = '获取乐队列表失败: ' + err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 跳转到主页
const goToHome = () => {
  router.push('/')
}

// 打开添加乐队模态框
const openCreateModal = () => {
  showCreateModal.value = true
}
// 关闭添加乐队模态框
const closeCreateModal = () => {
  showCreateModal.value = false
}

// 创建新乐队
const createNewBand = async (bandData: any) => {
  try {
    // 调用 API 创建乐队
    await BandService.createBand(bandData)
    // 刷新乐队列表
    await fetchBands()
    // 等待 DOM 更新后滚动到底部
    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    closeCreateModal()
  } catch (err) {
    error.value = '创建乐队失败'
    console.error('创建乐队失败:', err)
  }
}

// 打开编辑乐队模态框
const editBand = (band: any) => {
  selectedBand.value = band
  showEditModal.value = true
}
// 关闭编辑乐队模态框
const closeEditModal = () => {
  showEditModal.value = false
  selectedBand.value = null
}

// 更新乐队信息
const updateBand = async (bandData: any) => {
  try {
    // 调用 API 更新乐队
    await BandService.updateBand(bandData.id, bandData)
    // 刷新乐队列表
    await fetchBands() // 强制刷新
    // 如果简介弹窗正在显示且是当前乐队，则同步简介信息
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
  // 弹窗确认
  if (!confirm(`确定删除乐队 "${band.name}" 吗?`)) return
  try {
    // 调用 API 删除乐队
    await BandService.deleteBand(band.id)
    // 刷新乐队列表
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

// 处理图片上传完成后的回调
const handleImageUploaded = async (bandId: number | null, imageUrl: string) => {
  if (bandId == null) return;
  // 上传图片后，更新数据库中的 banner_image_url 字段
  try {
    // 找到当前乐队
    const band = bands.value.find(b => b.id === bandId);
    // 更新乐队信息，带上新图片地址
    await BandService.updateBand(bandId, {
      name: band.name,
      year: band.year,
      genre: band.genre,
      member_count: band.member_count,
      bio: band.bio,
      banner_image_url: imageUrl
    });
    // 刷新乐队列表，确保图片能显示
    await fetchBands(); 
  } finally {
    closeImageUpload();
  }
}

// 组件挂载时自动拉取乐队数据
onMounted(() => {
  fetchBands()
})
</script>

<style scoped lang="scss">
.band-management {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: white;
  min-height: 100vh;
  width: 100%;
  margin-top: 30px;
  box-sizing: border-box;
  position: relative;
  overflow-y: auto;
  padding-left: 32px;
  padding-right: 32px;
  padding-top: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 30px 4px 15px 4px;
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
      color: rgb(247, 238, 238);
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

/* 筛选区域样式（与成员管理一致） */
.filter-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  flex-wrap: wrap;
  border: 1px solid #333;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: white;
  white-space: nowrap;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #555;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
  background: #333;
  color: white;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #e53935;
  box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.25);
}

// 乐队列表区域，内容区加较小左右内边距
.band-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); // 自适应列宽
  gap: 25px; // 卡片间距
  padding: 0 4px 20px 4px; // 减少底部内边距，减小纵向间距
  .band-item {
    // 单个乐队卡片
    .band-card {
      background: #222; // 卡片背景
      border-radius: 8px; // 圆角
      overflow: hidden;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); // 阴影
      transition: transform 0.3s ease;
      &:hover {
        transform: translateY(-5px); // 悬停上浮
        box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2); // 悬停阴影
      }
      // 乐队图片区域
      .band-image {
        height: 180px; // 图片高度
        background-color: #444; // 默认背景色
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        // 图片占位符（无图片时显示）
        .image-placeholder {
          text-align: center;
          color: rgba(255, 255, 255, 0.7);
          z-index: 1;
          i {
            font-size: 3.5rem; // 占位图标大号
            display: block;
            margin-bottom: 10px;
            color: rgba(229, 57, 53, 0.7);
          }
          span {
            font-size: 1.2rem;
          }

        }
        // 图片内容（有图片时显示）
        .band-image-content {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          object-fit: cover; // 图片自适应裁剪
          z-index: 1;
        }
        // 上传图片按钮，悬浮在图片右下角
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
            background: rgba(229, 57, 53, 0.7); // 悬停变色
          }
          i {
            margin-right: 5px;
          }
        }
      }
      // 乐队信息区域
      .band-info {
        padding: 15px; // 内边距
        .band-name {
          font-size: 1.5rem; // 乐队名字号
          margin: 0 0 5px;
          color: white;
        }
        .band-genre, .band-year {
          font-size: 1rem;
          color: #aaa; // 次要信息色
          margin: 5px 0;
        }
        // 操作按钮区域（编辑、删除）
        .band-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px; // 按钮间距
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
              transform: translateY(-2px); // 悬停上浮
            }
            i {
              margin-right: 5px;
            }
            &.edit {
              background: rgba(41, 121, 255, 0.8); // 编辑按钮色
              color: white;
            }
            &.delete {
              background: rgba(229, 57, 53, 0.8); // 删除按钮色
              color: white;
            }
          }
        }
      }
    }
  }
}

// 简介弹窗遮罩层样式，覆盖全屏并居中内容
.bio-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6); // 半透明黑色背景
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000; // 高层级
}
// 简介弹窗内容样式，居中显示，圆角卡片
.bio-dialog {
  background: #222;
  color: #fff;
  border-radius: 10px;
  padding: 30px 30px 20px 30px;
  min-width: 300px;
  max-width: 90vw;
  box-shadow: 0 8px 30px rgba(0,0,0,0.5); // 阴影
  text-align: left;
  position: relative;
}
// 简介弹窗标题样式
.bio-dialog h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #e53935;
}
// 简介内容区域，支持换行和长词断行
.bio-content {
  margin-bottom: 20px;
  white-space: pre-wrap;
  word-break: break-all;
}
// 关闭简介弹窗按钮样式
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
  background: #b71c1c; // 悬停变深
}
</style>
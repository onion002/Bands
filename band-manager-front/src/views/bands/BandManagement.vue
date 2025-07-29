<template>
  <!-- 乐队管理页面主容器 -->
  <div class="band-management">
    <!-- 内容容器 - 居中显示 -->
    <div class="content-container">
      <!-- 页面标题和操作按钮区域 -->
      <PageHeader
        title="乐队管理"
        :batch-mode="batchMode"
        :selected-count="selectedBands.length"
        item-type="乐队"
        add-button-text="添加新乐队"
        add-button-class="add-band-btn"
        @title-click="goToHome"
        @back-click="goToHome"
        @batch-toggle="toggleBatchMode"
        @add-click="openCreateModal"
        @select-all="selectAll"
        @clear-selection="clearSelection"
        @batch-delete="batchDeleteBands"
      />

      <!-- 筛选区域 -->
      <FilterSection
        select-label="按乐队种类筛选"
        :select-value="selectedGenre"
        select-placeholder="全部种类"
        :select-options="genreOptions.map(genre => ({ value: genre, label: genre }))"
        search-label="搜索乐队"
        :search-value="searchKeyword"
        search-placeholder="输入乐队名称或流派"
        @select-change="handleGenreChange"
        @search-input="handleSearchInput"
      />

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
      <EmptyState
        v-if="!loading && bands.length === 0"
        icon-class="fas fa-music"
        message="暂无乐队数据"
        button-text="添加第一支乐队"
        button-icon="fas fa-plus"
        @button-click="openCreateModal"
      />
      
      <!-- 乐队列表展示 -->
      <div v-if="!loading && filteredBands.length > 0" class="band-list">
        <div v-for="band in paginatedBands" :key="band.id" class="band-item">
          <div class="band-card" :class="{ 'batch-mode': batchMode }">
            <!-- 批量删除模式下显示复选框 -->
            <div v-if="batchMode" class="band-checkbox">
              <input 
                type="checkbox" 
                :value="band.id" 
                v-model="selectedBands"
              >
            </div>
            
            <!-- 乐队图片区域 -->
            <div class="band-image" :style="{ backgroundColor: '#444' }">
              <!-- 如果有图片则显示图片，否则显示占位符 -->
              <img
                v-if="band.banner_image_url"
                :src="getBandImageUrl(band.banner_image_url)"
                class="band-image-content"
                @click="openBioDialog(band)"
                style="cursor: pointer;"
                @error="handleImageError"
              >
              <div v-else class="image-placeholder">
                <i class="fas fa-music"></i>
                <span>乐队图片</span>
              </div>
            </div>
            <!-- 乐队信息区域 -->
            <div class="band-info">
              <h3 class="band-name">{{ band.name }}</h3>
              <p class="band-genre">流派:{{ band.genre || '未设置流派' }}</p>
              <p class="band-year">成立年份: {{ band.year || '未设置' }}</p>
              <p class="band-member-count">成员数量: {{ band.member_count || 0 }} 人</p>
              <p class="band-bio-preview" v-if="band.bio" @click="openBioDialog(band)" style="cursor: pointer;">
                简介: {{ band.bio.length > 30 ? band.bio.substring(0, 30) + '...' : band.bio }}
              </p>
              <p class="band-bio-preview" v-else>简介: 暂无简介</p>
              <div v-if="!batchMode" class="band-actions">
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

      <!-- 分页控件 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="page-btn"
        >
          <i class="fas fa-chevron-left"></i>
        </button>

        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>

        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="page-btn"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
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

      <!-- 简介弹窗 -->
      <div v-if="showBioDialog" class="bio-modal-overlay" @click.self="closeBioDialog">
        <div class="bio-modal">
          <div class="bio-modal-header">
            <h3>{{ bioDialogBand?.name }} - 乐队简介</h3>
            <button @click="closeBioDialog" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="bio-modal-content">
            <p v-if="bioDialogBand?.bio">{{ bioDialogBand.bio }}</p>
            <p v-else class="no-bio">暂无简介信息</p>
          </div>
        </div>
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
// 引入可复用组件
import PageHeader from '@/components/PageHeader.vue'
import FilterSection from '@/components/FilterSection.vue'
import EmptyState from '@/components/EmptyState.vue'


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
const handleGenreChange = (value: string | number) => {
  selectedGenre.value = value as string
  currentPage.value = 1
}

// 处理搜索输入
const handleSearchInput = (value: string) => {
  searchKeyword.value = value
  currentPage.value = 1
}

// 分页状态
const currentPage = ref(1)
const pageSize = ref(6) 

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

// 计算属性：总页数
const totalPages = computed(() => {
  return Math.ceil(filteredBands.value.length / pageSize.value)
})

// 分页切换
const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

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
  if (!confirm(`确定删除乐队 "${band.name}" 吗？\n\n⚠️ 此操作将同时删除：\n• 乐队的所有历史图片\n• 乐队成员的所有头像\n• 乐队成员记录\n\n此操作不可撤销！`)) return
  try {
    loading.value = true

    // 1. 先强制清理该乐队的所有图片
    try {
      const cleanupResponse = await BandService.cleanupAllBandImages(band.id)
      console.log(`清理乐队 "${band.name}" 的图片:`, cleanupResponse.data)
    } catch (cleanupErr) {
      console.warn('清理乐队图片时出现警告:', cleanupErr)
      // 继续执行删除操作，不因为清理失败而中断
    }

    // 2. 调用 API 删除乐队
    const response = await BandService.deleteBand(band.id)

    // 3. 强制清理所有未使用的图片（解决格式2文件问题）
    try {
      const forceCleanupResponse = await BandService.forceCleanupAllUnusedImages()
      console.log('强制清理未使用图片:', forceCleanupResponse.data)
    } catch (forceCleanupErr) {
      console.warn('强制清理未使用图片时出现警告:', forceCleanupErr)
    }

    // 显示删除结果
    if (response.data?.deleted_files_count > 0) {
      console.log(`删除乐队 "${band.name}" 成功，共删除了 ${response.data.deleted_files_count} 个图片文件`)
    }

    // 刷新乐队列表
    await fetchBands()
  } catch (err: any) {
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '删除乐队失败: ' + errorMessage
    console.error('删除乐队失败:', err)
  } finally {
    loading.value = false
  }
}



// 获取乐队图片URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const getBandImageUrl = (imageUrl: string) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http')) return imageUrl
  return API_BASE_URL + imageUrl
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  console.warn('图片加载失败:', img.src)
}

// 组件挂载时自动拉取乐队数据
onMounted(() => {
  fetchBands()
})

// 添加批量删除相关状态和方法
const batchMode = ref(false)
const selectedBands = ref<number[]>([])

const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedBands.value = []
  }
}

const selectAll = () => {
  selectedBands.value = paginatedBands.value.map(band => band.id)
}

const clearSelection = () => {
  selectedBands.value = []
}

const batchDeleteBands = async () => {
  if (selectedBands.value.length === 0) return

  const bandNames = selectedBands.value.map(id => {
    const band = bands.value.find(b => b.id === id)
    return band?.name || '未知'
  }).join('、')

  if (!confirm(`确定要删除以下 ${selectedBands.value.length} 个乐队吗？\n${bandNames}\n\n⚠️ 此操作将同时删除：\n• 乐队的所有历史图片\n• 乐队成员的所有头像\n• 乐队成员记录\n\n此操作不可撤销！`)) {
    return
  }

  try {
    loading.value = true

    // 1. 先为每个乐队强制清理图片
    console.log('开始清理各个乐队的图片...')
    const cleanupPromises = selectedBands.value.map(async (bandId) => {
      try {
        const response = await BandService.cleanupAllBandImages(bandId)
        console.log(`清理乐队 ${bandId} 的图片:`, response.data)
        return response.data
      } catch (err) {
        console.warn(`清理乐队 ${bandId} 图片时出现警告:`, err)
        return null
      }
    })

    await Promise.all(cleanupPromises)
    console.log('各个乐队图片清理完成')

    // 2. 使用批量删除API
    console.log('开始批量删除乐队...')
    const response = await BandService.batchDeleteBands(selectedBands.value)
    console.log('批量删除API调用成功:', response.data)

    // 3. 强制清理所有未使用的图片（解决格式2文件问题）
    console.log('开始强制清理所有未使用的图片...')
    try {
      const forceCleanupResponse = await BandService.forceCleanupAllUnusedImages()
      console.log('批量删除后强制清理未使用图片:', forceCleanupResponse.data)
    } catch (forceCleanupErr) {
      console.warn('强制清理未使用图片时出现警告:', forceCleanupErr)
      // 强制清理失败不应该影响主流程
    }

    // 清空选择
    selectedBands.value = []

    // 刷新乐队列表
    console.log('刷新乐队列表...')
    await fetchBands()

    // 显示删除结果
    if (response && response.data) {
      const result = response.data
      console.log('批量删除乐队成功:', result)

      // 可以在这里显示更详细的删除信息
      if (result.total_deleted_files && result.total_deleted_files > 0) {
        console.log(`共删除了 ${result.total_deleted_files} 个图片文件`)
      }

      // 显示成功消息给用户
      console.log(`成功删除 ${result.deleted_bands?.length || selectedBands.value.length} 个乐队`)
    } else {
      console.log('批量删除乐队成功')
    }

  } catch (err: any) {
    console.error('批量删除乐队失败:', err)
    console.error('错误详情:', err.response?.data)

    // 更详细的错误处理
    let errorMessage = '未知错误'
    if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.message) {
      errorMessage = err.message
    }

    error.value = '批量删除乐队失败: ' + errorMessage
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">

/* 乐队管理页面样式 */

.band-management {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: white;
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  position: relative;
  overflow-y: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 15px;
}

/* 内容容器 - 居中显示 */
.content-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background: transparent;
  min-height: calc(100vh - 120px);
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}


/* 状态指示器样式（加载、错误），内容区加较小左右内边距 */
.loading-state, .error-state {
  text-align: center;
  padding: 50px 4px; /* 上下和左右内边距 */
  font-size: 1.2rem;
  i {
    font-size: 3rem; /* 图标大号显示 */
    margin-bottom: 15px;
    color: #e53935; /* 图标高亮色 */
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

/* 错误状态下的按钮样式，背景色更深 */
.error-state {
  button {
    background: #333;
  }
}


// 乐队列表区域，内容区加较小左右内边距
.band-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* 自适应列宽 */
  gap: 25px; /* 卡片间距 */
  padding: 0 4px 20px 4px; /* 减少底部内边距，减小纵向间距 */
  .band-item {
    .band-card {
      background: #222;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
      transition: transform 0.3s ease;
      min-height: 340px;
      display: flex;
      flex-direction: column;
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2);
      }
      .band-image {
        width: 100%;
        height: 180px;
        background-color: #444;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        .band-image-content {
          width: 100%;
          height: 100%;
          object-fit: cover;
          border-radius: 8px 8px 0 0;
          display: block;
          position: static;
          background: #222;
        }
        .image-placeholder {
          width: 100%;
          height: 100%;
          border-radius: 8px 8px 0 0;
          background: #666;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #fff;
          font-size: 2.5rem;
          z-index: 1;
          i {
            font-size: 3rem;
            margin-bottom: 8px;
            color: rgba(229, 57, 53, 0.7);
          }
          span {
            font-size: 1rem;
            color: #eee;
          }
        }
      }
      .band-info {
        padding: 15px 15px 60px 15px; /* 底部多留空间给按钮 */
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        position: relative;
        .band-name {
          font-size: 1.5rem;
          font-weight: bold;
          margin: 0 0 5px 0;
          color: white;
          text-align: left;
        }
        .band-genre, .band-year {
          font-size: 1rem;
          color: #aaa;
          margin: 5px 0 0 0;
          text-align: left;
        }
        .band-actions {
          /* 保证按钮区和文字区有足够间距 */
          margin-top: 18px;
        }
      }

      .band-actions {
        position: absolute;
        right: 15px;
        bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: flex-end; /* 确保靠右对齐 */
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
            background: linear-gradient(to right, #007bff, #0056b3);
            color: white;
            &:hover {
              box-shadow: 0 3px 10px rgba(0, 123, 255, 0.3);
            }
          }
          &.delete {
            background: linear-gradient(to right, #dc3545, #c82333);
            color: white;
            &:hover {
              box-shadow: 0 3px 10px rgba(220, 53, 69, 0.3);
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

/* 批量操作工具栏 */
.batch-toolbar {
  background: rgba(255, 152, 0, 0.1);
  border: 1px solid rgba(255, 152, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.select-all-btn, .clear-selection-btn {
  background: transparent;
  border: 1px solid #ff9800;
  color: #ff9800;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.select-all-btn:hover, .clear-selection-btn:hover {
  background: #ff9800;
  color: white;
}

.batch-delete-btn {
  background: linear-gradient(to right, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.batch-delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.band-card {
  position: relative;
  
  &.batch-mode {
    .band-actions {
      display: none; /* 批量模式下隐藏单个操作按钮 */
    }
  }
}

.band-checkbox {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 10;
}

.band-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #ff9800;
}

/* 简介弹窗样式 */
.bio-modal-overlay {
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

.bio-modal {
  background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(229, 57, 53, 0.3);
}

.bio-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(229, 57, 53, 0.8);
  border-radius: 12px 12px 0 0;
}

.bio-modal-header h3 {
  margin: 0;
  color: white;
  font-size: 1.4rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.bio-modal-content {
  padding: 20px;
  color: white;
  line-height: 1.6;
}

.no-bio {
  color: #888;
  font-style: italic;
}

/* 乐队信息区域新增样式 */
.band-member-count {
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 4px;
}

.band-bio-preview {
  font-size: 0.9rem;
  color: #ccc;
  margin-bottom: 8px;
  line-height: 1.4;
}

.band-bio-preview:hover {
  color: #e53935;
  text-decoration: underline;
}



/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 30px 4px;
  margin-top: 20px;
}

.page-btn {
  padding: 10px 15px;
  border: 1px solid #555;
  background: #333;
  color: white;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;

  &:hover:not(:disabled) {
    background: linear-gradient(to right, #e53935, #e35d5b);
    border-color: #e53935;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(229, 57, 53, 0.3);
  }

  &:disabled {
    background: #555;
    color: #888;
    cursor: not-allowed;
    border-color: #555;
  }
}

.page-info {
  font-weight: 500;
  color: white;
  font-size: 1rem;
}
</style>

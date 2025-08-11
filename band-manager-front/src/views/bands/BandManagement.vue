<template>
  <div class="band-management">
    <!-- 🎵 页面头部 -->
    <div class="page-header">
      <h1>
        <span class="gradient-text">乐队管理</span>
      </h1>
      <p>管理您的乐队信息，创建精彩的音乐世界</p>
    </div>

    <!-- 🎨 操作工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button
          v-if="!batchMode"
          @click="openCreateModal"
          class="btn btn-primary"
        >
          <i class="fa fa-plus"></i>
          添加新乐队
        </button>

        <button
          v-if="bands.length > 0"
          @click="toggleBatchMode"
          class="btn btn-outline"
        >
          <i class="fa fa-check-square"></i>
          {{ batchMode ? '退出批量' : '批量操作' }}
        </button>
      </div>

      <div class="toolbar-right" v-if="batchMode && selectedBands.length > 0">
        <span class="selection-count">已选择 {{ selectedBands.length }} 个乐队</span>
        <button @click="selectAll" class="btn btn-outline btn-sm">全选</button>
        <button @click="clearSelection" class="btn btn-outline btn-sm">清空</button>
        <button @click="batchDeleteBands" class="btn btn-danger btn-sm">
          <i class="fa fa-trash"></i>
          批量删除
        </button>
      </div>
    </div>

    <!-- 🎯 筛选区域 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>乐队类型</label>
          <select v-model="selectedGenre" @change="handleGenreChange" class="form-control">
            <option value="">全部类型</option>
            <option v-for="genre in genreOptions" :key="genre" :value="genre">
              {{ genre }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>搜索乐队</label>
          <input
            v-model="searchKeyword"
            @input="handleSearchInput"
            type="text"
            placeholder="输入乐队名称或流派..."
            class="form-control"
          />
        </div>

        <div class="filter-actions">
          <button @click="resetFilters" class="btn btn-outline btn-sm">
            <i class="fa fa-refresh"></i>
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- 🔄 加载状态 -->
    <div v-if="loading" class="loading-section">
      <div class="loading-content">
        <div class="loading-spinner animate-pulse-slow">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <p>正在加载乐队信息...</p>
      </div>
    </div>

    <!-- ⚠️ 错误状态 -->
    <div v-else-if="error" class="error-section">
      <div class="error-content">
        <i class="fa fa-exclamation-triangle"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="fetchBands" class="btn btn-primary">
          <i class="fa fa-refresh"></i>
          重新加载
        </button>
      </div>
    </div>

    <!-- 🌟 空状态 -->
    <div v-else-if="bands.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fa fa-music"></i>
      </div>
      <h3>还没有乐队</h3>
      <p>开始创建您的第一个乐队，展示您的音乐才华</p>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fa fa-plus"></i>
        创建乐队
      </button>
    </div>

    <!-- 🎵 乐队网格展示 -->
    <div v-else class="bands-grid">
      <BandCard
        v-for="band in paginatedBands"
        :key="band.id"
        :band="band"
        :selected="batchMode && selectedBands.includes(band.id)"
        :show-batch-checkbox="batchMode"
        :show-play-button="true"
        :show-actions="!batchMode"
        @selection-change="(selected) => handleBandSelection(band.id, selected)"
        @play="openBioDialog(band)"
        @edit="editBand(band)"
        @delete="deleteBand(band)"
        @view="openBioDialog(band)"
      />
    </div>

    <!-- 🌟 乐队简介弹窗 -->
    <div v-if="showBioDialog" class="modal-overlay" @click.self="closeBioDialog">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ bioDialogBand?.name }} - 乐队简介</h3>
          <button class="close-btn" @click="closeBioDialog">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="bio-content">
            <p>{{ bioDialogBand?.bio || '暂无简介信息' }}</p>
            <div class="band-details">
              <div class="detail-item">
                <strong>成立年份:</strong> {{ bioDialogBand?.year }}
              </div>
              <div class="detail-item">
                <strong>音乐类型:</strong> {{ bioDialogBand?.genre || '未分类' }}
              </div>
              <div class="detail-item">
                <strong>成员数量:</strong> {{ bioDialogBand?.member_count || 0 }}人
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="closeBioDialog">关闭</button>
        </div>
      </div>
    </div>

    <!-- 🎯 分页控件 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage <= 1"
        class="btn btn-outline"
      >
        <i class="fa fa-chevron-left"></i>
        上一页
      </button>

      <div class="page-numbers">
        <span class="page-info">
          第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
        </span>
      </div>

      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage >= totalPages"
        class="btn btn-outline"
      >
        下一页
        <i class="fa fa-chevron-right"></i>
      </button>
    </div>

    <!-- 🎵 模态框组件 -->
    <BandModal
      v-if="showCreateModal"
      mode="add"
      @close="closeCreateModal"
      @save="createNewBand"
    />

    <BandModal
      v-if="showEditModal"
      :band="selectedBand"
      mode="edit"
      @close="closeEditModal"
      @save="updateBand"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { BandService } from '@/api/bandService'
import BandModal from '@/components/BandModal.vue'
import BandCard from '@/components/BandCard.vue'

import type { Band } from '@/types'

// 🎵 数据状态
const bands = ref<Band[]>([])
const loading = ref(false)
const error = ref('')

// 🎨 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)

const selectedBand = ref<Band | null>(null)

// 🎯 筛选和搜索状态
const selectedGenre = ref('')
const searchKeyword = ref('')

// 🔄 批量操作状态
const batchMode = ref(false)
const selectedBands = ref<number[]>([])

// 📄 分页状态
const currentPage = ref(1)
const itemsPerPage = 12

// 🌟 简介弹窗状态
const showBioDialog = ref(false)
const bioDialogBand = ref<Band | null>(null)

// 🎨 计算属性
const genreOptions = computed(() => {
  const genres = new Set<string>()
  bands.value.forEach(band => {
    if (band.genre) genres.add(band.genre)
  })
  return Array.from(genres)
})

const filteredBands = computed(() => {
  let result = bands.value

  // 按类型筛选
  if (selectedGenre.value) {
    result = result.filter(band => band.genre === selectedGenre.value)
  }

  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    result = result.filter(band =>
      band.name.toLowerCase().includes(keyword) ||
      (band.genre && band.genre.toLowerCase().includes(keyword))
    )
  }

  return result
})

const paginatedBands = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredBands.value.slice(start, start + itemsPerPage)
})

const totalPages = computed(() => {
  return Math.ceil(filteredBands.value.length / itemsPerPage)
})

// 🎯 事件处理函数
const handleGenreChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  selectedGenre.value = target.value
  currentPage.value = 1
}

const handleSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  searchKeyword.value = target.value
  currentPage.value = 1
}

const resetFilters = () => {
  selectedGenre.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 🔄 API 调用函数
const fetchBands = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await BandService.getBands()
    bands.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    error.value = '获取乐队列表失败: ' + err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 🎵 模态框控制函数
const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}



const closeEditModal = () => {
  showEditModal.value = false
  selectedBand.value = null
}

// 🎨 乐队操作函数
const createNewBand = async (bandData: any) => {
  try {
    await BandService.createBand(bandData)
    await fetchBands()
    closeCreateModal()
  } catch (err) {
    error.value = '创建乐队失败'
    console.error('创建乐队失败:', err)
  }
}

const editBand = (band: Band) => {
  selectedBand.value = band
  showEditModal.value = true
}

const updateBand = async (bandData: any) => {
  try {
    await BandService.updateBand(bandData.id, bandData)
    await fetchBands()
    closeEditModal()
  } catch (err) {
    error.value = '更新乐队失败'
    console.error('更新乐队失败:', err)
  }
}

const deleteBand = async (band: Band) => {
  if (!confirm(`确定删除乐队 "${band.name}" 吗？\n\n⚠️ 此操作将同时删除：\n• 乐队的所有历史图片\n• 乐队成员的所有头像\n• 乐队成员记录\n\n此操作不可撤销！`)) {
    return
  }

  try {
    loading.value = true

    // 清理乐队图片
    try {
      await BandService.cleanupAllBandImages(band.id)
    } catch (cleanupErr) {
      console.warn('清理乐队图片时出现警告:', cleanupErr)
    }

    // 删除乐队
    await BandService.deleteBand(band.id)

    // 强制清理未使用的图片
    try {
      await BandService.forceCleanupAllUnusedImages()
    } catch (forceCleanupErr) {
      console.warn('强制清理未使用图片时出现警告:', forceCleanupErr)
    }

    await fetchBands()
  } catch (err: any) {
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '删除乐队失败: ' + errorMessage
    console.error('删除乐队失败:', err)
  } finally {
    loading.value = false
  }
}



// 🌟 简介弹窗控制
const openBioDialog = (band: Band) => {
  bioDialogBand.value = band
  showBioDialog.value = true
}

const closeBioDialog = () => {
  showBioDialog.value = false
  bioDialogBand.value = null
}

// 🎨 工具函数
const getBandImageUrl = (imageUrl: string) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http')) return imageUrl
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  return API_BASE_URL + imageUrl
}

// 🔄 批量操作函数
const handleBandSelection = (bandId: number, selected: boolean) => {
  if (selected) {
    if (!selectedBands.value.includes(bandId)) {
      selectedBands.value.push(bandId)
    }
  } else {
    selectedBands.value = selectedBands.value.filter(id => id !== bandId)
  }
}

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

  if (!confirm(`确定要删除以下 ${selectedBands.value.length} 个乐队吗？\n${bandNames}\n\n⚠️ 此操作将同时删除所有相关数据，此操作不可撤销！`)) {
    return
  }

  try {
    loading.value = true

    // 批量删除乐队
    for (const bandId of selectedBands.value) {
      try {
        await BandService.cleanupAllBandImages(bandId)
      } catch (err) {
        console.warn(`清理乐队 ${bandId} 图片时出现警告:`, err)
      }
    }

    // 批量删除乐队
    await BandService.batchDeleteBands(selectedBands.value)

    // 强制清理未使用的图片
    try {
      await BandService.forceCleanupAllUnusedImages()
    } catch (forceCleanupErr) {
      console.warn('强制清理未使用图片时出现警告:', forceCleanupErr)
    }

    // 清空选择并刷新列表
    selectedBands.value = []
    await fetchBands()

  } catch (err: any) {
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '批量删除乐队失败: ' + errorMessage
    console.error('批量删除乐队失败:', err)
  } finally {
    loading.value = false
  }
}

// 🔄 组件挂载
onMounted(() => {
  fetchBands()
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.band-management {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 1rem;
  }
}

// 🎨 工具栏样式
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba($darkgray, 0.7);
  backdrop-filter: blur(8px);
  border: $border-light;
  border-radius: $border-radius-xl;

  .toolbar-left {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .toolbar-right {
    display: flex;
    gap: 1rem;
    align-items: center;

    .selection-count {
      color: $primary;
      font-weight: 500;
      font-size: 0.875rem;
    }
  }

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;

    .toolbar-left,
    .toolbar-right {
      width: 100%;
      justify-content: center;
    }
  }
}

// � 乐队网格样式
.bands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .band-item {
    position: relative;

    &.selected {
      transform: scale(0.98);

      &::after {
        content: '';
        position: absolute;
        inset: -4px;
        border: 2px solid $primary;
        border-radius: $border-radius-xl;
        pointer-events: none;
        z-index: 1;
      }
    }

    .batch-checkbox {
      position: absolute;
      top: 1rem;
      left: 1rem;
      z-index: 10;

      .checkbox {
        width: 20px;
        height: 20px;
        cursor: pointer;
        accent-color: $primary;
        border-radius: 4px;
      }
    }
  }
}



// 🎯 分页样式
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-top: 3rem;

  .page-numbers {
    .page-info {
      color: $gray-300;
      font-size: 0.875rem;
    }
  }

  @media (max-width: 480px) {
    flex-direction: column;
    gap: 1rem;
  }
}

// 🔄 加载和错误状态
.loading-section,
.error-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;

  .loading-content,
  .error-content {
    text-align: center;

    .loading-spinner {
      font-size: 3rem;
      color: $primary;
      margin-bottom: 1rem;
    }

    i {
      font-size: 3rem;
      color: #ef4444;
      margin-bottom: 1rem;
    }

    h3 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
    }

    p {
      color: $gray-400;
      margin: 0 0 2rem;
    }
  }
}
</style>

<template>
  <div class="event-management">
    <!-- 🎵 页面头部 -->
    <div class="page-header">
      <h1>
        <span class="gradient-text">演出活动管理</span>
      </h1>
      <p>管理您的演出活动，创造精彩的音乐体验</p>
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
          添加新活动
        </button>

        <button
          v-if="events.length > 0"
          @click="toggleBatchMode"
          class="btn btn-outline"
        >
          <i class="fa fa-check-square"></i>
          {{ batchMode ? '退出批量' : '批量操作' }}
        </button>
      </div>

      <div class="toolbar-right" v-if="batchMode && selectedEvents.length > 0">
        <span class="selection-count">已选择 {{ selectedEvents.length }} 个活动</span>
        <button @click="selectAll" class="btn btn-outline btn-sm">全选</button>
        <button @click="clearSelection" class="btn btn-outline btn-sm">清空</button>
        <button @click="batchDeleteEvents" class="btn btn-danger btn-sm">
          <i class="fa fa-trash"></i>
          批量删除
        </button>
      </div>
    </div>

    <!-- 🎯 筛选区域 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>所属乐队</label>
          <select v-model="selectedBandId" @change="handleBandChange" class="form-control">
            <option value="">全部乐队</option>
            <option v-for="option in bandSelectOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>活动状态</label>
          <select v-model="selectedStatus" @change="handleStatusChange" class="form-control">
            <option value="">全部状态</option>
            <option value="upcoming">即将开始</option>
            <option value="ongoing">进行中</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>

        <div class="filter-group">
          <label>搜索活动</label>
          <input
            v-model="searchKeyword"
            @input="handleSearchInput"
            type="text"
            placeholder="输入活动标题或场地..."
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
        <p>正在加载活动信息...</p>
      </div>
    </div>

    <!-- ⚠️ 错误状态 -->
    <div v-else-if="error" class="error-section">
      <div class="error-content">
        <i class="fa fa-exclamation-triangle"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="fetchEvents" class="btn btn-primary">
          <i class="fa fa-refresh"></i>
          重新加载
        </button>
      </div>
    </div>

    <!-- 🌟 空状态 -->
    <div v-else-if="events.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fa fa-calendar"></i>
      </div>
      <h3>还没有活动</h3>
      <p>开始创建您的第一个演出活动</p>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fa fa-plus"></i>
        创建活动
      </button>
    </div>

    <!-- 🎵 活动网格展示 -->
    <div v-else class="events-grid">
      <div
        v-for="event in paginatedEvents"
        :key="event.id"
        class="event-item"
        :class="{ 'selected': batchMode && selectedEvents.includes(event.id) }"
      >
        <!-- 批量选择复选框 -->
        <div v-if="batchMode" class="batch-checkbox">
          <input
            type="checkbox"
            :value="event.id"
            v-model="selectedEvents"
            class="checkbox"
          />
        </div>

        <!-- 活动卡片 -->
        <div class="event-card card card-interactive">
          <!-- 活动海报 -->
          <div class="event-poster">
            <img
              v-if="event.poster_image_url"
              :src="event.poster_image_url"
              :alt="event.title"
              class="poster-image"
              @error="handlePosterError"
            />
            <div v-else class="poster-placeholder">
              <i class="fa fa-calendar"></i>
              <span>{{ event.title }}</span>
            </div>

            <!-- 状态标签 -->
            <div class="event-status" :class="`status-${event.status}`">
              {{ getStatusText(event.status) }}
            </div>

            <!-- 价格标签 -->
            <div class="event-price">¥{{ event.ticket_price || 120 }}</div>
          </div>

          <!-- 活动信息 -->
          <div class="event-content">
            <h3 class="event-title">{{ event.title }}</h3>
            <div class="event-band">
              <i class="fa fa-music"></i>
              {{ event.band_name }}
            </div>
            <div class="event-venue">
              <i class="fa fa-map-marker"></i>
              {{ event.venue || '待定场地' }}
            </div>
            <div class="event-date">
              <i class="fa fa-clock"></i>
              {{ formatEventDate(event.event_date) }}
            </div>

            <!-- 操作按钮 -->
            <div v-if="!batchMode" class="event-actions">
              <button @click="openEditModal(event)" class="action-btn" title="编辑">
                <i class="fa fa-edit"></i>
              </button>
              <button @click="openUploadModal(event)" class="action-btn" title="上传海报">
                <i class="fa fa-image"></i>
              </button>
              <button @click="deleteEvent(event)" class="action-btn delete" title="删除">
                <i class="fa fa-trash"></i>
              </button>
            </div>
          </div>
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
    <EventModal
      v-if="showCreateModal"
      :event="null"
      mode="add"
      @close="showCreateModal = false"
      @submit="handleCreateEvent"
    />

    <EventModal
      v-if="showEditModal"
      :event="selectedEvent"
      mode="edit"
      @close="showEditModal = false"
      @submit="handleUpdateEvent"
    />

    <!-- 🌟 上传模态框 -->
    <UploadModal
      v-if="showUploadModal"
      title="上传活动海报"
      :upload-api="(file) => EventService.uploadEventPoster(selectedEvent?.id, file)"
      accept="image/*"
      :max-size="5"
      url-field="poster_image_url"
      @close="closeUploadModal"
      @uploaded="handleUploadSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { EventService } from '@/api/eventService'
import { BandService } from '@/api/bandService'
import EventModal from '@/components/EventModal.vue'
import UploadModal from '@/components/UploadModal.vue'
import type { Event } from '@/types'

// 🎵 数据状态
const events = ref<Event[]>([])
const bands = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 🎨 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showUploadModal = ref(false)
const selectedEvent = ref<Event | null>(null)

// 🎯 筛选和搜索状态
const selectedBandId = ref('')
const selectedStatus = ref('')
const searchKeyword = ref('')

// 🔄 批量操作状态
const batchMode = ref(false)
const selectedEvents = ref<number[]>([])

// 📄 分页状态
const currentPage = ref(1)
const itemsPerPage = 12

// 🎨 计算属性
const bandSelectOptions = computed(() => {
  return (bands.value || []).map(band => ({
    value: band.id.toString(),
    label: band.name
  }))
})

const filteredEvents = computed(() => {
  let filtered = events.value

  // 按乐队筛选
  if (selectedBandId.value) {
    filtered = filtered.filter(event => String(event.band_id) === String(selectedBandId.value))
  }

  // 按状态筛选
  if (selectedStatus.value) {
    filtered = filtered.filter(event => String(event.status) === String(selectedStatus.value))
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(event =>
      event.title.toLowerCase().includes(keyword) ||
      (event.venue && event.venue.toLowerCase().includes(keyword)) ||
      (event.band_name && event.band_name.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredEvents.value.slice(start, start + itemsPerPage)
})

const totalPages = computed(() => {
  return Math.ceil(filteredEvents.value.length / itemsPerPage)
})

// 🔄 API 调用函数
const fetchEvents = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await EventService.getAllEvents()

    if (result && result.items && Array.isArray(result.items)) {
      events.value = result.items
    } else {
      events.value = []
    }
  } catch (err: any) {
    error.value = err?.error || err?.message || '获取演出活动列表失败'
    events.value = []
  } finally {
    loading.value = false
  }
}

const fetchBands = async () => {
  try {
    const result = await BandService.getBands()
    if (result && result.items && Array.isArray(result.items)) {
      bands.value = result.items
    } else if (Array.isArray(result)) {
      bands.value = result
    } else {
      bands.value = []
    }
  } catch (err) {
    console.error('获取乐队列表失败:', err)
    bands.value = []
  }
}

// 🎯 事件处理函数
const handleBandChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  selectedBandId.value = target.value
  currentPage.value = 1
}

const handleStatusChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  selectedStatus.value = target.value
  currentPage.value = 1
}

const handleSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  searchKeyword.value = target.value
  currentPage.value = 1
}

const resetFilters = () => {
  selectedBandId.value = ''
  selectedStatus.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 🎵 模态框控制函数
const openCreateModal = () => {
  showCreateModal.value = true
}

const openEditModal = (event: Event) => {
  selectedEvent.value = event
  showEditModal.value = true
}

const openUploadModal = (event: Event) => {
  selectedEvent.value = event
  showUploadModal.value = true
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedEvent.value = null
}

// 🎨 活动操作函数
const handleCreateEvent = async (eventData: any) => {
  try {
    await EventService.createEvent(eventData)
    showCreateModal.value = false
    await fetchEvents()
  } catch (err: any) {
    console.error('创建活动失败:', err)
    error.value = '创建活动失败: ' + (err.message || '未知错误')
  }
}

const handleUpdateEvent = async (eventData: any) => {
  try {
    if (selectedEvent.value) {
      await EventService.updateEvent(selectedEvent.value.id, eventData)
      showEditModal.value = false
      selectedEvent.value = null
      await fetchEvents()
    }
  } catch (err: any) {
    console.error('更新活动失败:', err)
    error.value = '更新活动失败: ' + (err.message || '未知错误')
  }
}

const deleteEvent = async (event: Event) => {
  if (confirm(`确定删除活动 "${event.title}" 吗？此操作不可撤销。`)) {
    try {
      await EventService.deleteEvent(event.id)
      await fetchEvents()
    } catch (err: any) {
      console.error('删除活动失败:', err)
      error.value = '删除活动失败: ' + (err.message || '未知错误')
    }
  }
}

const handleUploadSuccess = () => {
  fetchEvents()
  closeUploadModal()
}

// 🔄 批量操作函数
const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedEvents.value = []
  }
}

const selectAll = () => {
  selectedEvents.value = paginatedEvents.value.map(event => event.id)
}

const clearSelection = () => {
  selectedEvents.value = []
}

const batchDeleteEvents = async () => {
  if (selectedEvents.value.length === 0) return

  const eventNames = selectedEvents.value.map(id => {
    const event = events.value.find(e => e.id === id)
    return event?.title || '未知'
  }).join('、')

  if (confirm(`确定要删除以下 ${selectedEvents.value.length} 个活动吗？\n${eventNames}\n\n此操作不可撤销。`)) {
    try {
      loading.value = true

      const deletePromises = selectedEvents.value.map(id =>
        EventService.deleteEvent(id)
      )

      await Promise.all(deletePromises)

      selectedEvents.value = []
      await fetchEvents()
    } catch (err: any) {
      console.error('批量删除活动失败:', err)
      error.value = '批量删除活动失败: ' + (err.message || '未知错误')
    } finally {
      loading.value = false
    }
  }
}

// 🎨 工具函数
const formatEventDate = (dateString: string) => {
  if (!dateString) return '待定'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    upcoming: '即将开始',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const handlePosterError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  console.warn('海报加载失败:', img.src)
}









// 组件挂载时获取数据
onMounted(async () => {
  console.log('组件挂载，开始获取数据...')
  try {
    await fetchBands()
    console.log('乐队数据获取完成')
    await fetchEvents()
    console.log('活动数据获取完成')
  } catch (error) {
    console.error('数据获取失败:', error)
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.event-management {
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

// 🎵 活动网格样式
.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .event-item {
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

// 🎨 活动卡片样式
.event-card {
  overflow: hidden;

  .event-poster {
    position: relative;
    height: 200px;
    overflow: hidden;

    .poster-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform $transition-slow ease;
    }

    .poster-placeholder {
      width: 100%;
      height: 100%;
      background: rgba($lightgray, 0.3);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: $gray-400;

      i {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: $primary;
      }

      span {
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
      }
    }

    .event-status {
      position: absolute;
      top: 1rem;
      left: 1rem;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;

      &.status-upcoming {
        background: rgba(#10b981, 0.9);
        color: $white;
      }

      &.status-ongoing {
        background: rgba($primary, 0.9);
        color: $white;
      }

      &.status-completed {
        background: rgba($gray-500, 0.9);
        color: $white;
      }

      &.status-cancelled {
        background: rgba(#ef4444, 0.9);
        color: $white;
      }
    }

    .event-price {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba($secondary, 0.9);
      color: $white;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
    }
  }

  .event-content {
    padding: 1.5rem;

    .event-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.75rem;
      color: $white;
      line-height: 1.3;
    }

    .event-band,
    .event-venue,
    .event-date {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: $gray-400;
      font-size: 0.875rem;
      margin-bottom: 0.5rem;

      i {
        color: $primary;
        width: 16px;
        flex-shrink: 0;
      }
    }

    .event-band {
      color: $secondary;
      font-weight: 500;
    }

    .event-actions {
      display: flex;
      justify-content: center;
      gap: 0.5rem;
      margin-top: 1.5rem;

      .action-btn {
        background: none;
        border: none;
        color: $gray-400;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: $border-radius-sm;
        transition: all $transition-fast ease;

        &:hover {
          color: $primary;
          background: rgba($primary, 0.1);
        }

        &.delete:hover {
          color: #ef4444;
          background: rgba(#ef4444, 0.1);
        }
      }
    }
  }

  &:hover {
    .event-poster .poster-image {
      transform: scale(1.1);
    }

    .event-title {
      color: $primary;
    }
  }
}




</style>

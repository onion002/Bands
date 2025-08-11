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
          class="btn btn-primary neon-btn"
        >
          <i class="fa fa-plus"></i>
          添加新活动
        </button>

        <button
          v-if="events.length > 0"
          @click="toggleBatchMode"
          class="btn btn-outline neon-outline-btn"
        >
          <i class="fa fa-check-square"></i>
          {{ batchMode ? '退出批量' : '批量操作' }}
        </button>
      </div>

      <div class="toolbar-right" v-if="batchMode && selectedEvents.length > 0">
        <span class="selection-count">已选择 {{ selectedEvents.length }} 个活动</span>
        <button @click="selectAll" class="btn btn-outline btn-sm neon-outline-btn">全选</button>
        <button @click="clearSelection" class="btn btn-outline btn-sm neon-outline-btn">清空</button>
        <button @click="batchDeleteEvents" class="btn btn-danger btn-sm neon-danger-btn">
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
                          <option value="upcoming">即将售票</option>
              <option value="ongoing">售票中</option>
              <option value="completed">结束售票</option>
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
          <button @click="resetFilters" class="btn btn-outline btn-sm neon-outline-btn">
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
        <button @click="fetchEvents" class="btn btn-primary neon-btn">
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
      <button @click="openCreateModal" class="btn btn-primary neon-btn">
        <i class="fa fa-plus"></i>
        创建活动
      </button>
    </div>

    <!-- 🎵 活动网格展示 -->
    <div v-else class="events-list">
      <EventCard
        v-for="event in paginatedEvents"
        :key="event.id"
        :event="{
          id: event.id,
          title: event.title,
          description: event.description,
          event_date: event.event_date,
          venue: event.venue,
          band_names: event.band_names,
          status: event.status,
          poster_image_url: event.poster_image_url
        }"
        :selected="batchMode && selectedEvents.includes(event.id)"
        :show-batch-checkbox="batchMode"
        :show-actions="!batchMode"
        @selection-change="(selected) => handleEventSelection(event.id, selected)"
        @edit="openEditModal(event)"
        @delete="deleteEvent(event)"
        @view="openEditModal(event)"
      />
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


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { EventService } from '@/api/eventService'
import { BandService } from '@/api/bandService'
import EventModal from '@/components/EventModal.vue'
import EventCard from '@/components/EventCard.vue'

import type { Event as EventItem } from '@/types'

// 🎵 数据状态
const events = ref<EventItem[]>([])
const bands = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 🎨 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)

const selectedEvent = ref<EventItem | null>(null)

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
      filtered = filtered.filter(event => event.band_ids.includes(Number(selectedBandId.value)))
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
        (event.band_names && event.band_names.some(name => name.toLowerCase().includes(keyword)))
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

const openEditModal = (event: EventItem) => {
  selectedEvent.value = event
  showEditModal.value = true
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

const deleteEvent = async (event: EventItem) => {
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





// 🔄 批量操作函数
const handleEventSelection = (eventId: number, selected: boolean) => {
  if (selected) {
    if (!selectedEvents.value.includes(eventId)) {
      selectedEvents.value.push(eventId)
    }
  } else {
    selectedEvents.value = selectedEvents.value.filter(id => id !== eventId)
  }
}

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
    upcoming: '即将售票',
    ongoing: '售票中',
    completed: '结束售票',
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

// 🎨 页面头部样式优化
.page-header {
  text-align: center;

  h1 {
    margin: 0 0 1rem 0;
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;

    .gradient-text {
      background: linear-gradient(135deg, $primary, $secondary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-shadow: 0 4px 20px rgba($primary, 0.3);
    }
  }

  p {
    color: $gray-300;
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
    opacity: 0.9;
    line-height: 1.6;
    text-align: center;
  }
}

// 🎨 工具栏样式
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba($darkgray, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba($white, 0.08);
  border-radius: $border-radius-xl;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  }

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
      font-weight: 600;
      font-size: 0.9rem;
      padding: 0.5rem 1rem;
      background: rgba($primary, 0.1);
      border-radius: $border-radius-md;
      border: 1px solid rgba($primary, 0.2);
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

// 🎨 筛选区域样式优化
.filter-section {
  margin-bottom: 2.5rem;
  padding: 2rem;
  background: rgba($darkgray, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba($white, 0.08);
  border-radius: $border-radius-xl;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);

  .filter-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    align-items: end;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;

    label {
      color: $gray-300;
      font-weight: 600;
      font-size: 0.875rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.25rem;
    }

    .form-control {
      background: rgba($lightgray, 0.6);
      border: 1px solid rgba($white, 0.1);
      border-radius: $border-radius-md;
      color: $white;
      padding: 0.75rem 1rem;
      font-size: 0.95rem;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);

      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba($primary, 0.15);
        background: rgba($lightgray, 0.8);
      }

      &::placeholder {
        color: $gray-400;
        opacity: 0.7;
      }

      option {
        background: $darkgray;
        color: $white;
        padding: 0.5rem;
      }
    }
  }

  .filter-actions {
    display: flex;
    align-items: end;
    height: 100%;

    .btn {
      height: 44px;
      padding: 0 1.5rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }
  }
}

// 🎨 活动网格样式
.events-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3rem;
}







// 🎨 加载和错误状态样式
.loading-section,
.error-section {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba($gray-700, 0.8);
  border-radius: $border-radius-xl;
  margin: 2rem 0;

  .loading-content,
  .error-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;

    i {
      font-size: 3rem;
      color: $primary;
    }

    p {
      color: $gray-300;
      font-size: 1.1rem;
      margin: 0;
    }
  }
}

.error-section {
  .error-content {
    i {
      color: $danger;
    }
  }
}

// 🎨 分页样式
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 3rem 0;
  padding: 1.5rem;
  background: rgba($darkgray, 0.6);
  border-radius: $border-radius-xl;
  backdrop-filter: blur(8px);

  .page-numbers {
    .page-info {
      color: $gray-300;
      font-weight: 500;
      padding: 0.5rem 1rem;
      background: rgba($white, 0.05);
      border-radius: $border-radius-md;
      border: 1px solid rgba($white, 0.1);
    }
  }

  .btn {
    min-width: 100px;
    font-weight: 600;
  }
}

// 🎨 霓虹按钮样式
.neon-btn {
  background: linear-gradient(135deg, #ff2a6d, #05d9e8);
  border: none;
  color: $white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: 0 4px 15px rgba(255, 42, 109, 0.4);
  transition: all 0.3s ease;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(135deg, #ff2a6d, #05d9e8);
    border-radius: inherit;
    z-index: -1;
    opacity: 0.3;
    filter: blur(4px);
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 42, 109, 0.6);
    
    &::before {
      opacity: 0.5;
      filter: blur(6px);
    }
  }
  
  &:active {
    transform: translateY(0);
  }
}

.neon-outline-btn {
  background: transparent;
  border: 2px solid transparent;
  background-clip: padding-box;
  color: $white;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(135deg, #ff2a6d, #05d9e8);
    border-radius: inherit;
    z-index: -1;
    opacity: 0.8;
  }
  
  &:hover {
    color: $white;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 42, 109, 0.4);
    
    &::before {
      opacity: 1;
    }
  }
  
  &:active {
    transform: translateY(0);
  }
}

.neon-danger-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  color: $white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
  transition: all 0.3s ease;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(135deg, #ef4444, #dc2626);
    border-radius: inherit;
    z-index: -1;
    opacity: 0.3;
    filter: blur(4px);
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
    
    &::before {
      opacity: 0.5;
      filter: blur(6px);
    }
  }
  
  &:active {
    transform: translateY(0);
  }
}

// 📱 响应式优化
@media (max-width: 768px) {
  .events-list {
    .event-card {
      flex-direction: column;
      padding: 1rem;
      gap: 1rem;
      
      .event-poster {
        width: 100%;
        height: 200px;
      }
      
      .event-price {
        align-self: center;
        margin: 0.5rem 0;
      }
    }
  }
}

</style>

<template>
  <div class="event-management">
    <div class="content-container">
      <!-- 页面标题和操作按钮区域 -->
      <PageHeader
        title="演出活动管理"
        :batch-mode="batchMode"
        :selected-count="selectedEvents.length"
        item-type="演出活动"
        add-button-text="添加新活动"
        add-button-class="add-event-btn"
        @title-click="goToHome"
        @back-click="goToHome"
        @batch-toggle="toggleBatchMode"
        @add-click="openCreateModal"
        @select-all="selectAll"
        @clear-selection="clearSelection"
        @batch-delete="batchDeleteEvents"
      />

      <!-- 筛选区域 -->
      <FilterSection
        select-label="按乐队筛选"
        :select-value="selectedBandId"
        select-placeholder="全部乐队"
        :select-options="bandSelectOptions"
        search-label="搜索活动"
        :search-value="searchKeyword"
        search-placeholder="输入活动标题或场地"
        @select-change="handleBandChange"
        @search-input="handleSearchInput"
      />

      <!-- 状态筛选区域 -->
      <div class="status-filter-section">
        <div class="status-buttons">
          <button 
            class="status-btn" 
            :class="{ active: selectedStatus === '' }"
            @click="handleStatusChange('')"
          >
            全部状态
          </button>
          <button 
            class="status-btn" 
            :class="{ active: selectedStatus === 'upcoming' }"
            @click="handleStatusChange('upcoming')"
          >
            即将开始
          </button>
          <button 
            class="status-btn" 
            :class="{ active: selectedStatus === 'ongoing' }"
            @click="handleStatusChange('ongoing')"
          >
            进行中
          </button>
          <button 
            class="status-btn" 
            :class="{ active: selectedStatus === 'completed' }"
            @click="handleStatusChange('completed')"
          >
            已完成
          </button>
          <button 
            class="status-btn" 
            :class="{ active: selectedStatus === 'cancelled' }"
            @click="handleStatusChange('cancelled')"
          >
            已取消
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
        <button @click="fetchEvents">重试</button>
      </div>

      <!-- 数据为空时的提示 -->
      <EmptyState
        v-if="!loading && events.length === 0"
        icon-class="fas fa-calendar-alt"
        message="暂无演出活动数据"
        button-text="添加第一个活动"
        button-icon="fas fa-plus"
        @button-click="openCreateModal"
      />

      <!-- 演出活动列表展示 -->
      <div v-if="!loading && filteredEvents.length > 0" class="event-list">
        <div v-for="event in paginatedEvents" :key="event.id" class="event-item">
          <div class="event-card" :class="{ 'batch-mode': batchMode }">
            <!-- 批量删除模式下显示复选框 -->
            <div v-show="batchMode" class="event-checkbox">
              <input
                type="checkbox"
                :value="event.id"
                v-model="selectedEvents"
              >
            </div>

            <!-- 左侧活动海报区域 -->
            <div class="event-image">
              <div class="poster-wrapper">
                <img
                  v-if="event.poster_image_url"
                  :src="event.poster_image_url"
                  class="event-poster-image"
                  :alt="event.title"
                  @error="handlePosterError"
                >
                <div v-else class="poster-placeholder">
                  <i class="fas fa-calendar-alt"></i>
                  <span>活动海报</span>
                </div>
              </div>
            </div>

            <!-- 右侧活动信息区域 -->
            <div class="event-info">
              <div class="event-header">
                <h3 class="event-name">{{ event.title }}</h3>
                <p class="event-band">{{ event.band_name }}</p>
              </div>

              <div class="event-details">
                <p v-if="event.venue" class="event-venue">
                  <i class="fas fa-map-marker-alt"></i>
                  {{ event.venue }}{{ event.address ? ' | ' + event.address : '' }}
                </p>
                <p class="event-date">
                  <i class="fas fa-clock"></i>
                  {{ formatEventDate(event.event_date) }}
                </p>
              </div>

              <div class="event-footer">
                <div class="event-meta">
                  <span class="event-status" :class="`status-${event.status}`">
                    {{ getStatusText(event.status) }}
                  </span>
                  <span class="event-price">¥{{ event.ticket_price || 120 }}</span>
                </div>

                <div class="event-actions" v-if="!batchMode">
                  <button class="action-btn edit" @click="openEditModal(event)">
                    <i class="fas fa-edit"></i>
                    编辑
                  </button>
                  <button class="action-btn delete" @click="deleteEvent(event)">
                    <i class="fas fa-trash"></i>
                    删除
                  </button>
                </div>
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

      <!-- 演出活动模态框 -->
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
  </div>
</template>

<script setup lang="ts">
// 引入 Vue 相关 API
import { ref, onMounted, computed } from 'vue'
// 引入路由
import { useRouter } from 'vue-router'
// 引入演出活动相关 API 服务
import { EventService } from '@/api/eventService'
import { BandService } from '@/api/bandService'
// 引入演出活动信息编辑模态框组件
import EventModal from '@/components/EventModal.vue'
// 引入可复用组件
import PageHeader from '@/components/PageHeader.vue'
import FilterSection from '@/components/FilterSection.vue'
import EmptyState from '@/components/EmptyState.vue'
// 引入类型
import type { Event } from '@/types'

// 路由实例
const router = useRouter()
// 演出活动列表数据
const events = ref<Event[]>([])
// 乐队列表数据
const bands = ref<any[]>([])
// 加载状态
const loading = ref(false)
// 错误信息
const error = ref('')
// 控制添加活动模态框显示
const showCreateModal = ref(false)
// 控制编辑活动模态框显示
const showEditModal = ref(false)

// 当前选中的活动（用于编辑）
const selectedEvent = ref<Event | null>(null)

// 批量操作相关
const batchMode = ref(false)
const selectedEvents = ref<number[]>([])

// 筛选相关
const selectedBandId = ref('')
const selectedStatus = ref('')
const searchKeyword = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const totalEvents = ref(0)

// 计算属性：乐队选择选项
const bandSelectOptions = computed(() => {
  return (bands.value || []).map(band => ({
    value: band.id.toString(),
    label: band.name
  }))
})

// 计算属性：筛选后的活动列表
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

// 计算属性：分页后的活动列表
const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvents.value.slice(start, end)
})

// 计算属性：总页数
const totalPages = computed(() => {
  return Math.ceil(filteredEvents.value.length / pageSize.value)
})

// 获取演出活动列表
const fetchEvents = async () => {
  try {
    loading.value = true
    error.value = ''
    console.log('开始获取演出活动列表...')
    const result = await EventService.getAllEvents()
    console.log('活动API响应:', result)
    console.log('响应类型:', typeof result)
    console.log('响应是否有items:', result && 'items' in result)
    console.log('items是否为数组:', Array.isArray(result?.items))

    if (result && result.items && Array.isArray(result.items)) {
      events.value = result.items
      totalEvents.value = result.total || result.items.length
      console.log('成功设置活动数据，数量:', result.items.length)
    } else {
      console.error('意外的API响应格式:', result)
      events.value = []
      totalEvents.value = 0
    }
  } catch (err: any) {
    console.error('获取演出活动失败:', err)
    error.value = err?.error || err?.message || '获取演出活动列表失败，请检查网络连接'
    events.value = []
    totalEvents.value = 0
  } finally {
    loading.value = false
    console.log('fetchEvents完成，loading:', loading.value, 'events数量:', events.value.length)
  }
}

// 获取乐队列表
const fetchBands = async () => {
  try {
    console.log('开始获取乐队列表...')
    const result = await BandService.getBands()
    console.log('乐队API响应:', result)

    if (result) {
      // BandService使用了axios拦截器，返回的是解包后的数据
      if (result.items && Array.isArray(result.items)) {
        bands.value = result.items
        console.log('成功获取乐队列表，数量:', result.items.length)
      } else if (Array.isArray(result)) {
        bands.value = result
        console.log('成功获取乐队列表（数组格式），数量:', result.length)
      } else {
        console.error('意外的乐队API响应格式:', result)
        console.log('乐队响应类型:', typeof result)
        console.log('乐队响应内容:', JSON.stringify(result, null, 2))
        bands.value = []
      }
    } else {
      console.error('乐队API响应为空:', result)
      bands.value = []
    }
  } catch (err) {
    console.error('获取乐队列表失败:', err)
    bands.value = []
  }
}

// 返回主页
const goToHome = () => {
  router.push('/')
}

// 切换批量模式
const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedEvents.value = []
  }
}

// 全选
const selectAll = () => {
  selectedEvents.value = events.value.map(event => event.id)
}

// 清空选择
const clearSelection = () => {
  selectedEvents.value = []
}

// 切换活动选择状态
const toggleEventSelection = (eventId: number) => {
  const index = selectedEvents.value.indexOf(eventId)
  if (index > -1) {
    selectedEvents.value.splice(index, 1)
  } else {
    selectedEvents.value.push(eventId)
  }
}

// 处理活动点击
const handleEventClick = (event: Event) => {
  if (batchMode.value) {
    toggleEventSelection(event.id)
  } else {
    // 可以添加查看活动详情的逻辑
    console.log('查看活动详情:', event)
  }
}



// 打开创建模态框
const openCreateModal = () => {
  showCreateModal.value = true
}

// 打开编辑模态框
const openEditModal = (event: Event) => {
  selectedEvent.value = event
  showEditModal.value = true
}

// 处理创建活动
const handleCreateEvent = async (eventData: any) => {
  try {
    await EventService.createEvent(eventData)
    showCreateModal.value = false
    await fetchEvents()
    // 可以添加成功提示
  } catch (err: any) {
    console.error('创建活动失败:', err)
    // 可以添加错误提示
  }
}

// 处理更新活动
const handleUpdateEvent = async (eventData: any) => {
  try {
    if (selectedEvent.value) {
      await EventService.updateEvent(selectedEvent.value.id, eventData)
      showEditModal.value = false
      selectedEvent.value = null
      await fetchEvents()
      // 可以添加成功提示
    }
  } catch (err: any) {
    console.error('更新活动失败:', err)
    // 可以添加错误提示
  }
}

// 删除单个活动
const deleteEvent = async (event: Event) => {
  if (confirm(`确定删除活动 "${event.title}" 吗？`)) {
    try {
      await EventService.deleteEvent(event.id)
      await fetchEvents()
      // 可以添加成功提示
    } catch (err: any) {
      console.error('删除活动失败:', err)
      // 可以添加错误提示
    }
  }
}

// 批量删除活动
const batchDeleteEvents = async () => {
  if (selectedEvents.value.length === 0) {
    alert('请选择要删除的活动')
    return
  }

  if (confirm(`确定删除选中的 ${selectedEvents.value.length} 个活动吗？`)) {
    try {
      await EventService.batchDeleteEvents(selectedEvents.value)
      selectedEvents.value = []
      batchMode.value = false
      await fetchEvents()
      // 可以添加成功提示
    } catch (err: any) {
      console.error('批量删除活动失败:', err)
      // 可以添加错误提示
    }
  }
}

// 处理乐队筛选变化
const handleBandChange = (bandId: string | number) => {
  selectedBandId.value = String(bandId)
  currentPage.value = 1
  // 暂时注释掉，使用前端筛选
  // fetchEvents()
}

// 处理状态筛选变化
const handleStatusChange = (status: string) => {
  selectedStatus.value = status
  currentPage.value = 1
  // 暂时注释掉，使用前端筛选
  // fetchEvents()
}

// 处理搜索输入
const handleSearchInput = (keyword: string) => {
  searchKeyword.value = keyword
  // 搜索是在前端进行的，不需要重新请求
}

// 分页切换
const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 格式化活动日期
const formatEventDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    upcoming: '即将开始',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 处理海报图片加载错误
const handlePosterError = (event: any) => {
  // 可以设置默认图片或隐藏图片
  console.log('海报图片加载失败:', event)
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
/* 主容器样式 */
.event-management {
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

/* 页面标题区域 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  h1 {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .button-group {
    display: flex;
    gap: 15px;
  }

  button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;

    &.back-button {
      background: rgba(255, 255, 255, 0.1);
      color: white;

      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }

    &.add-event-btn {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      }
    }
  }
}

/* 加载和错误状态 */
.loading-state, .error-state {
  text-align: center;
  padding: 50px 4px;
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
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(229, 57, 53, 0.3);
    }
  }
}

.error-state {
  button {
    background: #333;
    
    &:hover {
      background: #444;
    }
  }
}

/* 活动列表 */
.event-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0 4px 20px 4px;
}

.event-card {
  background: linear-gradient(135deg, #2a2a2a 0%, #1e1e1e 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  min-height: 160px;

  &:hover {
    box-shadow: 0 8px 30px rgba(229, 57, 53, 0.2);
    transform: translateY(-3px);
    border-color: rgba(229, 57, 53, 0.3);
  }

  &.batch-mode {
    .event-actions {
      display: none;
    }
  }

  .event-checkbox {
    position: absolute;
    top: 15px;
    left: 15px;
    z-index: 10;

    input[type="checkbox"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
      accent-color: #e53935;
    }
  }

  /* 左侧图片区域 */
  .event-image {
    flex-shrink: 0;
    width: 200px;
    height: 205px;
    position: relative;
    overflow: hidden;
    border-radius: 8px 0 0 8px;

    .poster-wrapper {
      width: 100%;
      height: 205px;
      display: flex;
      align-items: center;
      justify-content: center;

      .event-poster-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .poster-placeholder {
        width: 100%;
        height: 205px;
        background: linear-gradient(135deg, #333 0%, #444 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #888;
        font-size: 0.9rem;

        i {
          font-size: 2.5rem;
          margin-bottom: 8px;
          color: #666;
        }
      }
    }
  }

  /* 右侧信息区域 */
  .event-info {
    flex: 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    color: #fff;
    position: relative;

    .event-header {
      .event-name {
        font-size: 1.4rem;
        font-weight: 600;
        color: #fff;
        margin: 0 0 8px 0;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .event-band {
        font-size: 0.95rem;
        color: #ccc;
        margin: 0 0 6px 0;
        
        &::before {
          content: "艺人：";
          color: #999;
        }
      }
    }

    .event-details {
      margin: 8px 0;

      .event-venue {
        font-size: 0.9rem;
        color: #bbb;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;

        i {
          color: #e53935;
          margin-right: 6px;
          width: 14px;
        }
      }

      .event-date {
        font-size: 0.9rem;
        color: #bbb;
        margin: 0;
        display: flex;
        align-items: center;

        i {
          color: #e53935;
          margin-right: 6px;
          width: 14px;
        }
      }
    }

    .event-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: auto;
      padding-top: 12px;

      .event-meta {
        display: flex;
        align-items: center;
        gap: 12px;

        .event-status {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
          border: 1px solid;

          &.status-upcoming {
            background: rgba(82, 196, 26, 0.2);
            color: #52c41a;
            border-color: rgba(82, 196, 26, 0.4);
          }

          &.status-ongoing {
            background: rgba(250, 140, 22, 0.2);
            color: #fa8c16;
            border-color: rgba(250, 140, 22, 0.4);
          }

          &.status-completed {
            background: rgba(140, 140, 140, 0.2);
            color: #8c8c8c;
            border-color: rgba(140, 140, 140, 0.4);
          }

          &.status-cancelled {
            background: rgba(255, 77, 79, 0.2);
            color: #ff4d4f;
            border-color: rgba(255, 77, 79, 0.4);
          }
        }

        .event-price {
          font-size: 1.2rem;
          font-weight: 600;
          color: #ff9800;
          text-shadow: 0 0 10px rgba(255, 152, 0, 0.3);

          &::before {
            content: "¥";
          }

          &::after {
            content: "起";
            font-size: 0.8rem;
            font-weight: normal;
            margin-left: 2px;
          }
        }
      }

      .event-actions {
        display: flex;
        gap: 8px;

        .action-btn {
          padding: 8px 14px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          background: rgba(255, 255, 255, 0.1);
          color: #fff;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 500;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          gap: 4px;
          backdrop-filter: blur(10px);

          &:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
          }

          &.edit {
            &:hover {
              background: linear-gradient(135deg, #2196f3, #1976d2);
              border-color: #2196f3;
              box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
            }
          }

          &.delete {
            &:hover {
              background: linear-gradient(135deg, #f44336, #d32f2f);
              border-color: #f44336;
              box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
            }
          }

          i {
            font-size: 0.8rem;
          }
        }
      }
    }
  }
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 30px 4px;
  margin-top: 20px;

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
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .event-list {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .event-management {
    padding-left: 15px;
    padding-right: 15px;
  }

  .event-list {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .event-card {
    .event-poster {
      height: 150px;
    }

    .event-info {
      padding: 12px;

      .event-title {
        font-size: 1.3rem;
      }
    }

    .event-actions {
      flex-direction: column;
      gap: 8px;

      .action-btn {
        width: 100%;
        justify-content: center;
      }
    }
  }

  .pagination {
    flex-direction: column;
    gap: 10px;

    .page-btn {
      width: 100%;
      justify-content: center;
    }
  }
}

/* 状态筛选区域 */
.status-filter-section {
  margin-bottom: 20px;
  padding: 0 4px;

  .status-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;

    .status-btn {
      padding: 8px 16px;
      border: none;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.1);
      color: rgba(255, 255, 255, 0.7);
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s ease;
      white-space: nowrap;

      &:hover {
        background: rgba(255, 255, 255, 0.15);
        color: rgba(255, 255, 255, 0.9);
      }

      &.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
      }
    }
  }
}

/* 活动状态样式 */
.event-status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid;

  &.status-upcoming {
    background: rgba(82, 196, 26, 0.2);
    color: #52c41a;
    border-color: rgba(82, 196, 26, 0.4);
  }

  &.status-ongoing {
    background: rgba(250, 140, 22, 0.2);
    color: #fa8c16;
    border-color: rgba(250, 140, 22, 0.4);
  }

  &.status-completed {
    background: rgba(140, 140, 140, 0.2);
    color: #8c8c8c;
    border-color: rgba(140, 140, 140, 0.4);
  }

  &.status-cancelled {
    background: rgba(255, 77, 79, 0.2);
    color: #ff4d4f;
    border-color: rgba(255, 77, 79, 0.4);
  }
}
</style>

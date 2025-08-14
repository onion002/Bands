<template>
  <div class="member-management">
    <!-- 🎵 页面头部 -->
    <div class="page-header">
      <h1>
        <span class="gradient-text">成员管理</span>
      </h1>
      <p>管理乐队成员信息，打造完美团队</p>
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
          添加新成员
        </button>

        <button
          v-if="members.length > 0"
          @click="toggleBatchMode"
          class="btn btn-outline"
        >
          <i class="fa fa-check-square"></i>
          {{ batchMode ? '退出批量' : '批量操作' }}
        </button>
      </div>

      <div class="toolbar-right" v-if="batchMode && selectedMembers.length > 0">
        <span class="selection-count">已选择 {{ selectedMembers.length }} 个成员</span>
        <button @click="selectAll" class="btn btn-outline btn-sm">全选</button>
        <button @click="clearSelection" class="btn btn-outline btn-sm">清空</button>
        <button @click="batchDeleteMembers" class="btn btn-danger btn-sm">
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
            <option v-for="band in bands" :key="band.id" :value="band.id">
              {{ band.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>搜索成员</label>
          <input
            v-model="searchKeyword"
            @input="handleSearchInput"
            type="text"
            placeholder="输入成员姓名或角色..."
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
        <p>正在加载成员信息...</p>
      </div>
    </div>

    <!-- ⚠️ 错误状态 -->
    <div v-else-if="error" class="error-section">
      <div class="error-content">
        <i class="fa fa-exclamation-triangle"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="fetchMembers" class="btn btn-primary">
          <i class="fa fa-refresh"></i>
          重新加载
        </button>
      </div>
    </div>

    <!-- 🌟 空状态 -->
    <div v-else-if="filteredMembers.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fa fa-users"></i>
      </div>
      <h3>{{ selectedBandId ? '该乐队暂无成员' : '还没有成员' }}</h3>
      <p>{{ selectedBandId ? '为这个乐队添加第一个成员' : '开始添加您的第一个乐队成员' }}</p>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fa fa-plus"></i>
        添加成员
      </button>
    </div>

    <!-- 🎵 成员网格展示 -->
    <div v-else class="members-grid">
      <MemberCard
        v-for="member in paginatedMembers"
        :key="member.id"
        :member="{
          id: member.id,
          name: member.name,
          role: member.role,
          avatar_url: member.avatar_url,
          band_names: [member.band_name],
          join_date: member.join_date,
          status: 'active'
        }"
        :selected="batchMode && selectedMembers.includes(member.id)"
        :show-batch-checkbox="batchMode"
        :show-actions="!batchMode"
        @selection-change="(selected) => handleMemberSelection(member.id, selected)"
        @edit="editMember(member)"
        @delete="deleteMember(member)"
        @view="editMember(member)"
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
    <MemberModal
      v-if="showCreateModal"
      mode="add"
      @close="closeCreateModal"
      @save="createNewMember"
    />

    <MemberModal
      v-if="showEditModal"
      :member="selectedMember"
      mode="edit"
      @close="closeEditModal"
      @save="updateMember"
    />


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { MemberService } from '@/api/memberService'
import { BandService } from '@/api/bandService'
import MemberModal from '@/components/MemberModal.vue'
import MemberCard from '@/components/MemberCard.vue'

import type { Member, Band } from '@/types'

// 🎵 数据状态
const members = ref<Member[]>([])
const bands = ref<Band[]>([])
const loading = ref(false)
const error = ref('')

// 🎨 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)

const selectedMember = ref<Member | null>(null)

// 🎯 筛选和搜索状态
const selectedBandId = ref('')
const searchKeyword = ref('')

// 🔄 批量操作状态
const batchMode = ref(false)
const selectedMembers = ref<number[]>([])

// 📄 分页状态
const currentPage = ref(1)
const itemsPerPage = 12

// 🎨 计算属性
const filteredMembers = computed(() => {
  let result = members.value

  // 按乐队筛选
  if (selectedBandId.value) {
    result = result.filter(member => member.band_id === parseInt(selectedBandId.value))
  }

  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    result = result.filter(member =>
      member.name.toLowerCase().includes(keyword) ||
      (member.role && member.role.toLowerCase().includes(keyword)) ||
      member.band_name.toLowerCase().includes(keyword)
    )
  }

  return result
})

const paginatedMembers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredMembers.value.slice(start, start + itemsPerPage)
})

const totalPages = computed(() => {
  return Math.ceil(filteredMembers.value.length / itemsPerPage)
})

// 🔄 API 调用函数
const fetchMembers = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await MemberService.getAllMembers(1, 1000)
    members.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    error.value = '获取成员列表失败: ' + err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchBands = async () => {
  try {
    const result = await BandService.getBands()
    bands.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    console.error('获取乐队列表失败:', err)
  }
}

// 🎯 事件处理函数
const handleBandChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  selectedBandId.value = target.value
  currentPage.value = 1
}

const handleSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  searchKeyword.value = target.value
  currentPage.value = 1
}

const resetFilters = () => {
  selectedBandId.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未设置'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const getAvatarUrl = (avatarUrl: string) => {
  if (!avatarUrl) return ''
  if (avatarUrl.startsWith('http')) return avatarUrl
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  return API_BASE_URL + avatarUrl
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 🎵 模态框控制函数
const openCreateModal = () => {
  selectedMember.value = null
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}



const closeEditModal = () => {
  showEditModal.value = false
  selectedMember.value = null
}

// 🎨 成员操作函数
const createNewMember = async (memberData: any) => {
  try {
    const result = await MemberService.createMember({
      name: memberData.name,
      role: memberData.role,
      join_date: memberData.join_date,
      band_id: memberData.band_id,
      avatar_url: memberData.avatar_url
    })

    if (memberData.avatarFile && result.id) {
      try {
        await MemberService.uploadMemberAvatar(result.id, memberData.avatarFile)
      } catch (avatarErr: any) {
        console.error('头像上传失败:', avatarErr)
      }
    }

    await fetchMembers()
    closeCreateModal()

  } catch (err: any) {
    console.error('创建成员失败:', err)
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '创建成员失败: ' + errorMessage
  }
}

const editMember = (member: Member) => {
  selectedMember.value = member
  showEditModal.value = true
}

const updateMember = async (memberData: any) => {
  try {
    if (!selectedMember.value) return

    await MemberService.updateMember(selectedMember.value.id, {
      name: memberData.name,
      role: memberData.role,
      join_date: memberData.join_date,
      band_id: memberData.band_id,
      avatar_url: memberData.avatar_url
    })

    if (memberData.avatarFile) {
      try {
        await MemberService.uploadMemberAvatar(selectedMember.value.id, memberData.avatarFile)
      } catch (avatarErr: any) {
        console.error('头像更新失败:', avatarErr)
      }
    }

    await fetchMembers()
    closeEditModal()
  } catch (err: any) {
    console.error('更新成员失败:', err)
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '更新成员失败: ' + errorMessage
  }
}

const deleteMember = async (member: Member) => {
  if (!confirm(`确定要删除成员 "${member.name}" 吗？此操作不可撤销。`)) {
    return
  }

  try {
    await MemberService.deleteMember(member.id)
    await fetchMembers()
  } catch (err: any) {
    console.error('删除成员失败:', err)
    error.value = '删除成员失败: ' + err.message
  }
}



// 🔄 批量操作函数
const handleMemberSelection = (memberId: number, selected: boolean) => {
  if (selected) {
    if (!selectedMembers.value.includes(memberId)) {
      selectedMembers.value.push(memberId)
    }
  } else {
    selectedMembers.value = selectedMembers.value.filter(id => id !== memberId)
  }
}

const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedMembers.value = []
  }
}

const selectAll = () => {
  selectedMembers.value = paginatedMembers.value.map(member => member.id)
}

const clearSelection = () => {
  selectedMembers.value = []
}

const batchDeleteMembers = async () => {
  if (selectedMembers.value.length === 0) return

  const memberNames = selectedMembers.value.map(id => {
    const member = members.value.find(m => m.id === id)
    return member?.name || '未知'
  }).join('、')

  if (!confirm(`确定要删除以下 ${selectedMembers.value.length} 个成员吗？\n${memberNames}\n\n此操作不可撤销。`)) {
    return
  }

  try {
    loading.value = true

    const deletePromises = selectedMembers.value.map(id =>
      MemberService.deleteMember(id)
    )

    await Promise.all(deletePromises)

    selectedMembers.value = []
    await fetchMembers()
  } catch (err: any) {
    console.error('批量删除成员失败:', err)
    error.value = '批量删除成员失败: ' + err.message
  } finally {
    loading.value = false
  }
}

// 🔄 组件挂载
onMounted(async () => {
  await Promise.all([
    fetchMembers(),
    fetchBands()
  ])
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.member-management {
  min-height: calc(100vh - 4rem);
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

// 🎵 成员网格样式
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .member-item {
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

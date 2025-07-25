<template>
  <!-- 成员管理页面主容器 -->
  <div class="member-management">
    <!-- 页面标题和操作按钮区域 -->
    <PageHeader
      title="成员管理"
      :batch-mode="batchMode"
      :selected-count="selectedMembers.length"
      item-type="成员"
      add-button-text="添加新成员"
      add-button-class="add-member-btn"
      @title-click="goToHome"
      @back-click="goToHome"
      @batch-toggle="toggleBatchMode"
      @add-click="openCreateModal"
      @select-all="selectAll"
      @clear-selection="clearSelection"
      @batch-delete="batchDeleteMembers"
    />

    <!-- 筛选区域 -->
    <FilterSection
      select-label="按乐队筛选"
      :select-value="selectedBandId"
      select-placeholder="全部乐队"
      :select-options="bands.map(band => ({ value: band.id, label: band.name }))"
      search-label="搜索成员"
      :search-value="searchKeyword"
      search-placeholder="输入成员姓名或角色"
      @select-change="handleBandChange"
      @search-input="handleSearchInput"
    />

    <!-- 加载状态指示器 -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> 加载中...
    </div>

    <!-- 错误提示区域 -->
    <div v-if="error" class="error-state">
      {{ error }}
      <button @click="fetchMembers">重试</button>
    </div>

    <!-- 数据为空时的提示 -->
    <EmptyState
      v-if="!loading && filteredMembers.length === 0"
      icon-class="fas fa-users"
      :message="selectedBandId ? '该乐队暂无成员' : '暂无成员数据'"
      button-text="添加第一个成员"
      button-icon="fas fa-plus"
      @button-click="openCreateModal"
    />

    <!-- 成员列表展示 -->
    <div v-if="!loading && filteredMembers.length > 0" class="member-list">
      <div v-for="member in paginatedMembers" :key="member.id" class="member-item">
        <div class="member-card" :class="{ 'batch-mode': batchMode }">
          <!-- 批量删除模式下显示复选框 -->
          <div v-show="batchMode" class="member-checkbox">
            <input 
              type="checkbox" 
              :value="member.id" 
              v-model="selectedMembers"
            >
          </div>
          
          <!-- 成员头像区域 -->
          <div class="member-image">
            <div class="avatar-wrapper">
              <img
                v-if="member.avatar_url"
                :src="getAvatarUrl(member.avatar_url)"
                class="member-avatar-image"
                :alt="member.name"
              >
              <div v-else class="avatar-placeholder">
                <i class="fas fa-user"></i>
                <span>成员头像</span>
              </div>
            </div>
          </div>
          
          <!-- 成员信息区域 -->
          <div class="member-info">
            <h3 class="member-name">{{ member.name }}</h3>
            <p class="member-role">{{ member.role || '未设置角色' }}</p>
            <p class="member-band">所属乐队: {{ member.band_name }}</p>
            <p class="member-date">加入日期: {{ formatDate(member.join_date) }}</p>
            
            <!-- 非批量模式下显示操作按钮 -->
            <div v-if="!batchMode" class="member-actions">
              <div class="action-btn-group">
                <button @click="editMember(member)" class="action-btn edit">
                  <i class="fas fa-edit"></i> 编辑
                </button>
                <button @click="deleteMember(member)" class="action-btn delete">
                  <i class="fas fa-trash"></i> 删除
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

    <!-- 添加成员模态框 -->
    <MemberModal
      v-if="showCreateModal"
      mode="add"
      @close="closeCreateModal"
      @save="createNewMember"
    />

    <!-- 编辑成员模态框 -->
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
// 引入 Vue 相关 API
import { ref, onMounted, computed } from 'vue'
// 引入路由
import { useRouter } from 'vue-router'
// 引入成员相关 API 服务
import { MemberService } from '@/api/memberService'
import { BandService } from '@/api/bandService'
// 引入成员信息编辑模态框组件
import MemberModal from '@/components/MemberModal.vue'
// 引入可复用组件
import PageHeader from '@/components/PageHeader.vue'
import FilterSection from '@/components/FilterSection.vue'
import EmptyState from '@/components/EmptyState.vue'
// 引入类型定义
import type { Member, Band } from '@/types'

// 路由实例
const router = useRouter()

// 数据状态
const members = ref<Member[]>([])
const bands = ref<Band[]>([])
const loading = ref(false)
const error = ref('')

// 筛选和搜索状态
const selectedBandId = ref('')
const searchKeyword = ref('')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

// 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedMember = ref<Member | null>(null)

// 批量删除相关状态
const batchMode = ref(false)
const selectedMembers = ref<number[]>([])

// 计算属性：筛选后的成员列表
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

// 计算属性：分页后的成员列表
const paginatedMembers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMembers.value.slice(start, end)
})

// 计算属性：总页数
const totalPages = computed(() => {
  return Math.ceil(filteredMembers.value.length / pageSize.value)
})

// 获取成员列表数据
const fetchMembers = async () => {
  try {
    loading.value = true
    error.value = ''

    const result = await MemberService.getAllMembers(1, 1000) // 获取所有成员
    members.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    error.value = '获取成员列表失败: ' + err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 获取乐队列表
const fetchBands = async () => {
  try {
    const result = await BandService.getBands()
    bands.value = Array.isArray(result.items) ? result.items : []
  } catch (err: any) {
    console.error('获取乐队列表失败:', err)
  }
}

// 跳转到主页
const goToHome = () => {
  router.push('/')
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未设置'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 处理乐队筛选
const handleBandChange = (value: string | number) => {
  selectedBandId.value = value as string
  currentPage.value = 1 // 重置到第一页
}

// 处理搜索输入
const handleSearchInput = (value: string) => {
  searchKeyword.value = value
  currentPage.value = 1 // 重置到第一页
}

// 分页切换
const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 打开添加成员模态框
const openCreateModal = () => {
  selectedMember.value = null
  showCreateModal.value = true
}

// 关闭添加成员模态框
const closeCreateModal = () => {
  showCreateModal.value = false
}

// 创建新成员
const createNewMember = async (memberData: any) => {
  try {
    // 先创建成员，始终传递 avatar_url 字段
    const result = await MemberService.createMember({
      name: memberData.name,
      role: memberData.role,
      join_date: memberData.join_date,
      band_id: memberData.band_id,
      avatar_url: memberData.avatar_url // 关键：无论有无头像都传递
    })

    // 如果有头像文件，上传头像
    if (memberData.avatarFile && result.id) {
      try {
        await MemberService.uploadMemberAvatar(result.id, memberData.avatarFile)
        console.log('头像上传成功')
      } catch (avatarErr: any) {
        console.error('头像上传失败:', avatarErr)
        // 头像上传失败不影响成员创建
      }
    }

    // 刷新成员列表
    await fetchMembers()

    // 关闭模态框
    closeCreateModal()

    // 显示成功提示
    console.log('成员创建成功')
  } catch (err: any) {
    console.error('创建成员失败:', err)
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '创建成员失败: ' + errorMessage
  }
}

// 编辑成员
const editMember = (member: Member) => {
  selectedMember.value = member
  showEditModal.value = true
}

// 关闭编辑成员模态框
const closeEditModal = () => {
  showEditModal.value = false
  selectedMember.value = null
}

// 更新成员信息
const updateMember = async (memberData: any) => {
  try {
    if (!selectedMember.value) return

    // 先更新成员基本信息，始终传递 avatar_url 字段
    await MemberService.updateMember(selectedMember.value.id, {
      name: memberData.name,
      role: memberData.role,
      join_date: memberData.join_date,
      band_id: memberData.band_id,
      avatar_url: memberData.avatar_url // 关键：无论有无头像都传递
    })

    // 如果有新的头像文件，上传头像
    if (memberData.avatarFile) {
      try {
        await MemberService.uploadMemberAvatar(selectedMember.value.id, memberData.avatarFile)
        console.log('头像更新成功')
      } catch (avatarErr: any) {
        console.error('头像更新失败:', avatarErr)
        // 头像更新失败不影响成员信息更新
      }
    }

    // 刷新成员列表
    await fetchMembers()

    // 关闭模态框
    closeEditModal()

    // 显示成功提示
    console.log('成员信息更新成功')
  } catch (err: any) {
    console.error('更新成员失败:', err)
    const errorMessage = err.response?.data?.error || err.message || '未知错误'
    error.value = '更新成员失败: ' + errorMessage
  }
}

// 删除成员
const deleteMember = async (member: Member) => {
  if (!confirm(`确定要删除成员 "${member.name}" 吗？此操作不可撤销。`)) {
    return
  }

  try {
    await MemberService.deleteMember(member.id)

    // 刷新成员列表
    await fetchMembers()

    // 显示成功提示
    console.log('成员删除成功')
  } catch (err: any) {
    console.error('删除成员失败:', err)
    error.value = '删除成员失败: ' + err.message
  }
}

// 切换批量删除模式
const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    selectedMembers.value = []
  }
}

// 全选
const selectAll = () => {
  selectedMembers.value = paginatedMembers.value.map(member => member.id)
}

// 清空选择
const clearSelection = () => {
  selectedMembers.value = []
}

// 批量删除成员
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
    
    console.log('批量删除成员成功')
  } catch (err: any) {
    console.error('批量删除成员失败:', err)
    error.value = '批量删除成员失败: ' + err.message
  } finally {
    loading.value = false
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

function getAvatarUrl(avatar_url: string | undefined) {
  if (!avatar_url) return '';
  if (avatar_url.startsWith('http')) return avatar_url;
  return API_BASE_URL + avatar_url;
}

// 组件挂载时获取数据
onMounted(async () => {
  await Promise.all([
    fetchMembers(),
    fetchBands()
  ])
})
</script>

<style scoped lang="scss">
/* 主容器样式，参照乐队管理界面 */
.member-management {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); /* 深色渐变背景 */
  color: white; /* 白色文字 */
  min-height: 100vh; /* 页面最小高度撑满视口 */
  width: 100%; /* 铺满整个视口宽度 */
  margin-top: 30px; /* 顶部预留导航栏高度 */
  box-sizing: border-box;
  position: relative;
  overflow-y: auto; /* 允许纵向滚动 */
  padding-left: 32px; /* 页边距 */
  padding-right: 32px; /* 页边距 */
  padding-top: 10px;
}



.member-card {
  background: #222;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
  position: relative;
}

.member-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2);
}

.member-checkbox {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 10;
}

.member-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #ff9800;
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

/* 成员列表区域，内容区加较小左右内边距 */
.member-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* 自适应列宽 */
  gap: 25px; /* 卡片间距 */
  padding: 0 4px 20px 4px; /* 减少底部内边距，减小纵向间距 */
  .member-item {
    /* 单个成员卡片 */
    .member-card {
      background: #222; /* 卡片背景 */
      border-radius: 8px; /* 圆角 */
      overflow: hidden;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); /* 阴影 */
      transition: transform 0.3s ease;
      position: relative; /* 关键：为绝对定位提供上下文 */
      
      &:hover {
        transform: translateY(-5px); /* 悬停上浮 */
        box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2); /* 悬停阴影 */
      }

      &.batch-mode {
        .member-actions {
          display: none; /* 批量模式下隐藏单个操作按钮 */
        }
      }
      
      .member-checkbox {
        position: absolute;
        top: 15px;
        left: 15px;
        z-index: 10;
        
        input[type="checkbox"] {
          width: 20px;
          height: 20px;
          cursor: pointer;
          accent-color: #ff9800;
        }
      }

      /* 成员头像区域 */
      .member-image {
        height: 200px;
        background: #333;
        position: relative;
        overflow: hidden;

        .avatar-wrapper {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;

          .member-avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .avatar-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #888;
            font-size: 0.9rem;

            i {
              font-size: 3rem;
              margin-bottom: 10px;
              color: #666;
            }
          }
        }
      }

      /* 成员信息区域 */
      .member-info {
        padding: 15px 15px 60px 15px; /* 底部多留空间给按钮 */
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;

        .member-name {
          font-size: 1.5rem;
          font-weight: bold;
          color: #e53935;
          margin: 0 0 5px 0;
          text-align: left;
        }

        .member-role {
          font-size: 1rem;
          color: #ccc;
          margin: 0 0 5px 0;
          text-align: left;
        }

        .member-band {
          font-size: 0.9rem;
          color: #aaa;
          margin: 0 0 5px 0;
          text-align: left;
        }

        .member-date {
          font-size: 0.9rem;
          color: #aaa;
          margin: 0;
          text-align: left;
        }

        /* 操作按钮区域 */
        .member-actions {
          /* 保证按钮区和文字区有足够间距 */
          margin-top: 18px;
        }
      }

      .member-actions {
        position: absolute;
        right: 15px;
        bottom: 15px;
        display: flex;
        align-items: center;

        .action-btn-group {
          display: flex;
          gap: 10px;

          .action-btn {
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;

            &.edit {
              background: linear-gradient(to right, #2196f3, #1976d2);
              color: white;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
              }
            }

            &.delete {
              background: linear-gradient(to right, #dc3545, #c82333);
              color: white;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
              }
            }
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
  padding: 30px 4px; /* 减少左右内边距 */
  margin-top: 20px;
}

.page-btn {
  padding: 10px 15px;
  border: 1px solid #555; /* 深色边框 */
  background: #333; /* 深色背景 */
  color: white;
  border-radius: 30px; /* 圆角按钮 */
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  &:hover:not(:disabled) {
    background: linear-gradient(to right, #e53935, #e35d5b); /* 红色渐变悬停 */
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
  color: white; /* 白色文字 */
  font-size: 1rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .member-list {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
}
@media (max-width: 768px) {
  .member-management {
    padding-left: 15px;
    padding-right: 15px;
  }

  .member-list {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  .member-item .member-card .member-image {
    height: 150px;
  }
  .member-item .member-card .member-info {
    padding: 12px;
    .member-name {
      font-size: 1.3rem;
    }
    .member-actions {
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
</style>

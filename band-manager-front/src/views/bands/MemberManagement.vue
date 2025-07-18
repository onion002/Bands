<template>
  <!-- 成员管理页面主容器 -->
  <div class="member-management">
    <!-- 页面标题和操作按钮区域 -->
    <div class="section-header">
      <h1 @click="goToHome" style="cursor:pointer;">成员管理</h1>
      <div class="button-group">
        <!-- 返回主页按钮 -->
        <button class="back-button" @click="goToHome">
          <i class="fas fa-arrow-left"></i> 返回主页
        </button>
        <!-- 添加新成员按钮 -->
        <button class="add-member-btn" @click="openCreateModal">
          <i class="fas fa-plus"></i> 添加新成员
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="filter-group">
        <label>按乐队筛选：</label>
        <select v-model="selectedBandId" @change="handleBandFilter">
          <option value="">全部乐队</option>
          <option
            v-for="band in bands"
            :key="band.id"
            :value="band.id"
          >
            {{ band.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label>搜索成员：</label>
        <input
          type="text"
          v-model="searchKeyword"
          @input="handleSearch"
          placeholder="输入成员姓名或角色"
        >
      </div>
    </div>

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
    <div v-if="!loading && filteredMembers.length === 0" class="empty-state">
      <i class="fas fa-users"></i>
      <p>{{ selectedBandId ? '该乐队暂无成员' : '暂无成员数据' }}</p>
      <button @click="openCreateModal">添加第一个成员</button>
    </div>

    <!-- 成员列表展示 -->
    <div v-if="!loading && filteredMembers.length > 0" class="member-list">
      <div v-for="member in paginatedMembers" :key="member.id" class="member-item">
        <div class="member-card">
          <!-- 成员头像区域 -->
          <div class="member-image">
            <!-- 如果有头像则显示圆形头像，否则显示圆形占位符 -->
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
            <div class="member-actions">
              <button class="upload-avatar-action-btn" @click="openAvatarUpload(member)">
                <i class="fas fa-camera"></i> 上传头像
              </button>
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

    <!-- 头像上传模态框 -->
    <AvatarUploadModal
      v-if="showAvatarUploadModal"
      :member-id="selectedMember?.id || 0"
      :member-name="selectedMember?.name || ''"
      @close="closeAvatarUpload"
      @uploaded="handleAvatarUploaded"
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
// 引入头像上传模态框组件
import AvatarUploadModal from '@/components/AvatarUploadModal.vue'
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
const showAvatarUploadModal = ref(false)
const selectedMember = ref<Member | null>(null)

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
const handleBandFilter = () => {
  currentPage.value = 1 // 重置到第一页
}

// 处理搜索
const handleSearch = () => {
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
    error.value = '创建成员失败: ' + err.message
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
    error.value = '更新成员失败: ' + err.message
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

// 打开头像上传模态框
const openAvatarUpload = (member: Member) => {
  selectedMember.value = member
  showAvatarUploadModal.value = true
}

// 关闭头像上传模态框
const closeAvatarUpload = () => {
  showAvatarUploadModal.value = false
  selectedMember.value = null
}

// 处理头像上传完成后的回调
const handleAvatarUploaded = async (memberId: number, avatarUrl: string) => {
  try {
    // 刷新成员列表，确保头像能显示
    await fetchMembers()
    console.log('头像上传成功')
  } finally {
    closeAvatarUpload()
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

/* 顶部标题和按钮区域，内容区加较小左右内边距，避免双重padding */
.section-header {
  display: flex; /* 横向排列 */
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
  margin-bottom: 30px; /* 与下方内容间距 */
  padding: 30px 4px 15px 4px; /* 减少左右内边距 */
  border-bottom: 1px solid #333; /* 下边框分隔 */
  h1 {
    font-size: 2.2rem; /* 标题字号 */
    color: #e53935; /* 标题高亮色 */
    margin: 0;
  }
  .button-group {
    display: flex;
    gap: 16px; /* 按钮间距 */
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
        background: #444; /* 悬停变色 */
      }
      i {
        margin-right: 5px; /* 图标与文字间距 */
      }
    }
    .add-member-btn {
      background: linear-gradient(to right, #e53935, #e35d5b); /* 渐变背景 */
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 30px;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s ease;
      &:hover {
        transform: translateY(-2px); /* 悬停上浮 */
        box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4); /* 阴影 */
      }
      i {
        margin-right: 8px; /* 图标与文字间距 */
      }
    }
  }
}

/* 筛选区域样式（与乐队管理一致） */
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

/* 状态指示器样式（加载、错误、空），内容区加较小左右内边距 */
.loading-state, .error-state, .empty-state {
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
      &:hover {
        transform: translateY(-5px); /* 悬停上浮 */
        box-shadow: 0 8px 20px rgba(229, 57, 53, 0.2); /* 悬停阴影 */
      }
      /* 成员头像区域 */
      .member-image {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        height: 180px;
        background-color: #444;
        .avatar-wrapper {
          position: relative;
          width: 160px;
          height: 160px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          overflow: hidden;
          background: #222;
        }
        .member-avatar-image {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          object-fit: cover;
          background: #222;
          z-index: 1;
          display: block;
        }
        .avatar-placeholder {
          width: 100%;
          height: 100%;
          border-radius: 50%;
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
        .upload-button {
          position: absolute;
          right: 0;
          bottom: 0;
          background: #222;
          color: #fff;
          border: none;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.1rem;
          box-shadow: 0 2px 6px rgba(0,0,0,0.18);
          cursor: pointer;
          transition: background 0.2s;
          z-index: 2;
          &:hover {
            background: #e53935;
            color: #fff;
          }
        }
      }
      /* 成员信息区域 */
      .member-info {
        padding: 15px; /* 内边距 */
        .member-name {
          font-size: 1.5rem; /* 成员名字号 */
          margin: 0 0 5px;
          color: white;
        }
        .member-role, .member-band, .member-date {
          font-size: 1rem;
          color: #aaa; /* 次要信息色 */
          margin: 5px 0;
        }
        /* 操作按钮区域（编辑、删除） */
        .member-actions {
          display: flex;
          align-items: flex-end;
          margin-top: 18px;
          justify-content: space-between;
          .upload-avatar-action-btn {
            background: #222;
            color: #fff;
            border: none;
            border-radius: 4px;
            padding: 6px 14px;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.10);
            cursor: pointer;
            transition: background 0.2s;
            &:hover {
              background: #e53935;
              color: #fff;
            }
          }
          .action-btn-group {
            display: flex;
            gap: 10px;
          }
          .action-btn {
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            &:hover {
              transform: translateY(-2px); /* 悬停上浮 */
            }
            i {
              margin-right: 5px;
            }
            &.edit {
              background: linear-gradient(to right, #007bff, #0056b3); /* 蓝色渐变 */
              color: white;
              &:hover {
                box-shadow: 0 3px 10px rgba(0, 123, 255, 0.3);
              }
            }
            &.delete {
              background: linear-gradient(to right, #dc3545, #c82333); /* 红色渐变 */
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
  .filter-section {
    flex-direction: column;
    gap: 15px;
  }
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  .filter-group select,
  .filter-group input {
    min-width: 100%;
    width: 100%;
    box-sizing: border-box;
  }
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
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
    padding: 20px 4px 15px 4px;
  }
  .button-group {
    width: 100%;
    justify-content: space-between;
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
  .filter-section {
    flex-direction: column;
    gap: 15px;
  }
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  .filter-group select,
  .filter-group input {
    min-width: 100%;
    width: 100%;
    box-sizing: border-box;
  }
}

@media (max-width: 200px) {
  .filter-section {
    flex-direction: column;
    gap: 15px;
    flex-wrap: wrap;
  }
}
</style>
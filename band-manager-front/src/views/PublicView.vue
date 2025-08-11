<template>
  <div class="public-view">
    <!-- 🎵 页面头部 -->
    <div class="page-header">
      <h1>
        <span class="gradient-text">公开展示</span>
      </h1>
      <p>探索其他管理员的音乐世界</p>
    </div>

    <!-- 🎨 搜索工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="section-title">
          <i class="fa fa-search"></i>
          搜索管理员
        </h2>
        <p class="section-description">输入管理员用户名来查看他们公开的乐队信息</p>
      </div>
      
      <div class="toolbar-right">
        <div class="search-container">
          <div class="input-wrapper">
            <i class="fa fa-user input-icon"></i>
            <input
              v-model="adminUsername"
              type="text"
              placeholder="请输入管理员用户名"
              @keyup.enter="loadAdminData"
              class="search-input"
            />
          </div>
          <button @click="loadAdminData" class="btn btn-primary" :disabled="loading || !adminUsername.trim()">
            <i v-if="loading" class="fa fa-spinner fa-spin"></i>
            <i v-else class="fa fa-search"></i>
            {{ loading ? '搜索中...' : '搜索' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 🎨 主要内容 -->
    <div class="public-content">

    <!-- ⚠️ 错误状态 -->
    <div v-if="error" class="error-section">
      <div class="error-content">
        <i class="fa fa-exclamation-triangle"></i>
        <h3>搜索失败</h3>
        <p>{{ error }}</p>
        <button @click="clearError" class="btn btn-primary">
          <i class="fa fa-refresh"></i>
          重新搜索
        </button>
      </div>
    </div>

      <!-- 管理员信息 -->
      <div v-if="adminInfo" class="admin-info">
        <div class="admin-card">
          <div class="admin-avatar">
            <img 
              v-if="adminInfo.avatar_url" 
              :src="adminInfo.avatar_url" 
              :alt="adminInfo.username"
            />
            <div v-else class="avatar-placeholder">
              <i class="fa fa-user"></i>
            </div>
          </div>
          <div class="admin-details">
            <h3>{{ adminInfo.display_name || adminInfo.username }}</h3>
            <p class="admin-username">@{{ adminInfo.username }}</p>
            <div class="admin-stats">
              <span class="stat-item" v-if="bands.length > 0">
                <i class="fa fa-music"></i>
                {{ bands.length }} 个乐队
              </span>
              <span class="stat-item" v-if="members.length > 0">
                <i class="fa fa-users"></i>
                {{ members.length }} 个成员
              </span>
              <span class="stat-item" v-if="events.length > 0">
                <i class="fa fa-calendar-alt"></i>
                {{ events.length }} 个活动
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 乐队展示 -->
      <div v-if="bands.length > 0" class="content-section">
        <h2 class="section-title">
          <i class="fa fa-music"></i>
          乐队列表
        </h2>
                 <div class="bands-grid">
           <BandCard
             v-for="band in bands"
             :key="band.id"
             :band="band"
             :show-actions="false"
           />
         </div>
      </div>

      <!-- 成员展示 -->
      <div v-if="members.length > 0" class="content-section">
        <h2 class="section-title">
          <i class="fa fa-users"></i>
          成员列表
        </h2>
                 <div class="members-grid">
           <MemberCard
             v-for="member in members"
             :key="member.id"
             :member="member"
             :show-actions="false"
           />
         </div>
      </div>

      <!-- 活动展示 -->
      <div v-if="events.length > 0" class="content-section">
        <h2 class="section-title">
          <i class="fa fa-calendar-alt"></i>
          活动列表
        </h2>
                 <div class="events-list">
           <EventCard
             v-for="event in events"
             :key="event.id"
             :event="event"
             :show-actions="false"
           />
         </div>
      </div>

      <!-- 🌟 空状态 -->
      <div v-if="!loading && !adminInfo && !error" class="empty-state">
        <div class="empty-icon">
          <i class="fa fa-search"></i>
        </div>
        <h3>开始探索</h3>
        <p>输入管理员用户名来查看他们公开的音乐世界</p>
      </div>

      <div v-if="adminInfo && bands.length === 0 && members.length === 0 && events.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fa fa-inbox"></i>
        </div>
        <h3>暂无公开数据</h3>
        <p>该管理员还没有公开任何乐队、成员或活动信息</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BandCard from '@/components/BandCard.vue'
import MemberCard from '@/components/MemberCard.vue'
import EventCard from '@/components/EventCard.vue'

const route = useRoute()

// 界面状态
const loading = ref(false)
const error = ref('')
const adminUsername = ref('')

// 数据
const adminInfo = ref<any>(null)
const bands = ref<any[]>([])
const members = ref<any[]>([])
const events = ref<any[]>([])

// 加载管理员数据
const loadAdminData = async () => {
  if (!adminUsername.value.trim()) {
    error.value = '请输入管理员用户名'
    return
  }

  try {
    loading.value = true
    error.value = ''
    adminInfo.value = null
    bands.value = []
    members.value = []
    events.value = []

    // TODO: 调用API获取公开数据
    // 这里需要实现真实的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 调用后端API
    const response = await fetch(`/api/auth/public/${adminUsername.value}`)
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '管理员不存在或没有公开数据')
    }
    
    const data = await response.json()
    adminInfo.value = data.admin
    bands.value = data.bands || []
    members.value = data.members || []
    events.value = data.events || []
    
  } catch (err: any) {
    error.value = err.message || '加载数据失败'
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatEventDay = (dateStr: string) => {
  return new Date(dateStr).getDate().toString()
}

const formatEventMonth = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short' })
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    upcoming: '即将售票',
    ongoing: '售票中',
    completed: '结束售票',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 清除错误
const clearError = () => {
  error.value = ''
}

onMounted(() => {
  // 如果URL中有用户名参数，自动加载
  if (route.params.username) {
    adminUsername.value = route.params.username as string
    loadAdminData()
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.public-view {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 1rem;
  }
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    font-size: 2.5rem;
    color: $primary;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    
    .gradient-text {
      background: linear-gradient(135deg, $primary, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
  
  p {
    color: $gray-400;
    font-size: 1.1rem;
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
    flex: 1;
    
    .section-title {
      color: $primary;
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      
      i {
        font-size: 1rem;
      }
    }
    
    .section-description {
      color: $gray-400;
      font-size: 0.875rem;
      margin: 0;
    }
  }

  .toolbar-right {
    display: flex;
    gap: 1rem;
    align-items: center;
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

.page-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
}

.public-nav {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.nav-title i {
  color: #667eea;
}

.auth-buttons {
  display: flex;
  gap: 1rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  text-decoration: none;
  color: #4a5568;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.nav-button:hover {
  border-color: #667eea;
  color: #667eea;
}

.nav-button.primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.nav-button.primary:hover {
  background: #5a67d8;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  color: #4a5568;
  font-weight: 500;
}



.admin-selector {
  background: white;
  border-radius: 12px;
  padding: 2.5rem; /* Increased padding */
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.admin-selector h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title i {
  color: #667eea;
}

.section-description {
  color: #718096;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.search-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.input-wrapper {
  position: relative;
  min-width: 300px;
  
  @media (max-width: 768px) {
    min-width: 200px;
  }
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: rgba($lightgray, 0.1);
  border: 1px solid rgba($primary, 0.3);
  border-radius: $border-radius-md;
  font-size: 1rem;
  color: $white;
  transition: all $transition-normal ease;
  
  &::placeholder {
    color: $gray-500;
  }
  
  &:focus {
    outline: none;
    border-color: $primary;
    background: rgba($lightgray, 0.2);
  }
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: $gray-400;
  z-index: 1;
}

// 🔄 加载和错误状态
.error-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  margin-bottom: 2rem;

  .error-content {
    text-align: center;

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

.admin-info {
  margin-bottom: 2rem;
}

.admin-card {
  background: rgba($darkgray, 0.7);
  border: 1px solid rgba($primary, 0.2);
  border-radius: $border-radius-xl;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  backdrop-filter: blur(8px);
  transition: all $transition-normal ease;

  &:hover {
    border-color: rgba($primary, 0.4);
    box-shadow: 0 8px 30px rgba($primary, 0.2);
  }
}

.admin-avatar {
  width: 80px;
  height: 80px;
  background: rgba($primary, 0.8);
  color: $white;
  border: 3px solid rgba($primary, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  overflow: hidden;
  transition: all $transition-normal ease;

  &:hover {
    border-color: rgba($primary, 0.6);
    transform: scale(1.05);
  }
}

.admin-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
}

.admin-details h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: $white;
  margin: 0 0 0.25rem 0;
  transition: color $transition-normal ease;
}

.admin-username {
  color: $primary;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.admin-details p {
  color: $gray-400;
  margin: 0 0 1rem 0;
}

.admin-card:hover {
  .admin-details h3 {
    color: $primary;
  }
}

.admin-stats {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: $gray-300;
  font-size: 0.875rem;
  font-weight: 500;

  i {
    color: $primary;
    font-size: 0.875rem;
  }
}

.content-section {
  background: rgba($darkgray, 0.5);
  border: 1px solid rgba($primary, 0.1);
  border-radius: $border-radius-xl;
  padding: 2rem;
  margin-bottom: 2rem;
  backdrop-filter: blur(8px);
  transition: all $transition-normal ease;

  &:hover {
    border-color: rgba($primary, 0.2);
    box-shadow: 0 4px 20px rgba($primary, 0.1);
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: $primary;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;

    i {
      color: $primary;
      font-size: 1rem;
    }
  }
}

.bands-grid, .members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.band-card {
  overflow: hidden;

  .band-image {
    position: relative;
    height: 200px;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform $transition-slow ease;
    }

    .band-placeholder {
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
      }
    }

    .image-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(to top, rgba($dark, 0.8), transparent);
    }

    .band-genre {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba($primary, 0.9);
      color: $white;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
  }

  .band-info {
    padding: 1.5rem;

    h4 {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
      transition: color $transition-normal ease;
    }

    .band-genre {
      color: $primary;
      font-weight: 500;
      margin-bottom: 0.75rem;
      font-size: 0.875rem;
    }

    .band-year {
      color: $primary;
      font-weight: 500;
      margin-bottom: 0.75rem;
      font-size: 0.875rem;
    }

    .band-bio {
      color: $gray-400;
      font-size: 0.875rem;
      line-height: 1.5;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .band-stats {
      margin-top: 1rem;

      .stat {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: $gray-300;
        font-size: 0.875rem;
        font-weight: 500;

        i {
          color: $primary;
          font-size: 0.875rem;
        }
      }
    }
  }

  &:hover {
    .band-image {
      img {
        transform: scale(1.1);
      }
    }

    .band-info h4 {
      color: $primary;
    }
  }
}

.member-card {
  padding: 2rem;
  text-align: center;

  .member-avatar {
    position: relative;
    width: 100px;
    height: 100px;
    margin: 0 auto 1.5rem;

    img {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid rgba($primary, 0.3);
      transition: all $transition-normal ease;
    }

    .avatar-placeholder {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: rgba($lightgray, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid rgba($primary, 0.3);

      i {
        font-size: 2.5rem;
        color: $gray-400;
      }
    }

    .status-indicator {
      position: absolute;
      bottom: 8px;
      right: 8px;
      width: 16px;
      height: 16px;
      background: #10b981;
      border-radius: 50%;
      border: 2px solid $darkgray;
    }
  }

  .member-info {
    h4 {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
    }

    .member-role {
      color: $primary;
      font-weight: 500;
      margin-bottom: 1rem;
      font-size: 0.875rem;
    }

    .member-band,
    .member-date {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      color: $gray-400;
      font-size: 0.875rem;
      margin-bottom: 0.5rem;

      i {
        color: $primary;
        width: 16px;
      }
    }
  }

  &:hover {
    .member-avatar {
      img {
        border-color: rgba($primary, 0.6);
        transform: scale(1.05);
      }
    }
  }
}

.band-image, .member-avatar {
  height: 150px; /* Adjusted height */
  position: relative;
  overflow: hidden;
}

.band-image img, .member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.band-placeholder, .avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
}

.band-info, .member-info {
  padding: 1.5rem;
}

.band-info h4, .member-info h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: $white;
  margin: 0 0 0.5rem 0;
  transition: color $transition-normal ease;
}

.band-genre, .band-year, .band-bio, .member-role, .member-band, .member-date {
  color: $gray-400;
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.band-card:hover, .member-card:hover {
  .band-info h4, .member-info h4 {
    color: $primary;
  }
}

.band-stats, .member-stats {
  margin-top: 1rem;
}

.stat {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: $gray-300;
  font-size: 0.875rem;
  font-weight: 500;

  i {
    color: $primary;
    font-size: 0.875rem;
  }
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.event-card {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 0;
  color: $white;
  height: 206px;
  background: rgba($darkgray, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: none;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
  }
}

.event-date {
  position: relative;
  width: 206px;
  height: 206px;
  overflow: hidden;
  flex-shrink: 0;
  border-radius: 0;
  box-shadow: none;
  border: none;
  background: linear-gradient(135deg, rgba($primary, 0.8), rgba($secondary, 0.8));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $white;

  .date-day {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .date-month {
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
}

.event-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.2rem;
  gap: 0.6rem;
  min-width: 0;

  .event-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: $white;
    line-height: 1.2;
    margin: 0;
  }

  .event-description {
    color: $gray-300;
    font-size: 0.875rem;
    line-height: 1.4;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.event-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: auto;

  .detail-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: $gray-300;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.25rem 0.75rem;
    background: rgba($white, 0.05);
    border-radius: 9999px;
    border: 1px solid rgba($white, 0.1);

    i {
      color: $primary;
      font-size: 0.75rem;
    }

    &.status {
      &.upcoming { 
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: $white;
        border-color: rgba(245, 158, 11, 0.3);
      }
      &.ongoing { 
        background: linear-gradient(135deg, #10b981, #059669);
        color: $white;
        border-color: rgba(16, 185, 129, 0.3);
      }
      &.completed { 
        background: linear-gradient(135deg, $gray-500, $gray-600);
        color: $white;
        border-color: rgba(107, 114, 128, 0.3);
      }
      &.cancelled { 
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: $white;
        border-color: rgba(239, 68, 68, 0.3);
      }
    }
  }
}

// 🌟 空状态样式
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  padding: 2rem;

  .empty-icon {
    font-size: 4rem;
    color: $primary;
    margin-bottom: 1.5rem;
    opacity: 0.7;
  }

  h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem;
    color: $white;
  }

  p {
    color: $gray-400;
    margin: 0;
    font-size: 1rem;
  }
}

// 📱 响应式设计
@media (max-width: 768px) {
  .public-view {
    padding: 1rem;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 1rem;

    .toolbar-left,
    .toolbar-right {
      width: 100%;
      justify-content: center;
    }
  }
  
  .admin-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .admin-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .event-card {
    flex-direction: column;
    height: auto;
    gap: 0;
    
    .event-date {
      width: 100%;
      height: 120px;
    }
  }
  
  .event-details {
    flex-direction: column;
    gap: 0.5rem;
  }

  .search-container {
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }

  .input-wrapper {
    min-width: 100%;
  }
}
</style>

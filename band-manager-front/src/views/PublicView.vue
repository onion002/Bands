<template>
  <div class="public-view">
    <!-- 顶部导航 -->
    <nav class="public-nav">
      <div class="nav-content">
        <div class="nav-left">
          <h1 class="nav-title">
            <i class="fas fa-music"></i>
            乐队展示
          </h1>
        </div>
        <div class="nav-right">
          <div v-if="!authStore.isAuthenticated" class="auth-buttons">
            <router-link to="/auth/login" class="nav-button">
              <i class="fas fa-sign-in-alt"></i>
              登录
            </router-link>
            <router-link to="/auth/register" class="nav-button primary">
              <i class="fas fa-user-plus"></i>
              注册
            </router-link>
          </div>
          <div v-else class="user-info">
            <span class="welcome-text">{{ authStore.displayName }}</span>
            <button @click="handleLogout" class="nav-button">
              <i class="fas fa-sign-out-alt"></i>
              退出
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="public-content">
      <!-- 管理员选择区域 -->
      <div class="admin-selector">
        <h2>选择要查看的管理员</h2>
        <div class="input-wrapper">
          <i class="fas fa-search input-icon"></i>
          <input
            v-model="adminUsername"
            type="text"
            placeholder="请输入管理员用户名"
            @keyup.enter="loadAdminData"
          />
          <button @click="loadAdminData" class="search-button" :disabled="loading">
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-search"></i>
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>

      <!-- 管理员信息 -->
      <div v-if="adminInfo" class="admin-info">
        <div class="admin-card">
          <div class="admin-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="admin-details">
            <h3>{{ adminInfo.display_name || adminInfo.username }}</h3>
            <p>@{{ adminInfo.username }}</p>
            <div class="admin-stats">
              <span class="stat-item">
                <i class="fas fa-music"></i>
                {{ bands.length }} 个乐队
              </span>
              <span class="stat-item">
                <i class="fas fa-users"></i>
                {{ members.length }} 个成员
              </span>
              <span class="stat-item">
                <i class="fas fa-calendar-alt"></i>
                {{ events.length }} 个活动
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 乐队展示 -->
      <div v-if="bands.length > 0" class="bands-section">
        <h3>乐队列表</h3>
        <div class="bands-grid">
          <div v-for="band in bands" :key="band.id" class="band-card">
            <div class="band-image" :style="{ backgroundColor: band.primary_color }">
              <img v-if="band.banner_image_url" :src="band.banner_image_url" :alt="band.name" />
              <div v-else class="band-placeholder">
                <i class="fas fa-music"></i>
              </div>
            </div>
            <div class="band-info">
              <h4>{{ band.name }}</h4>
              <p v-if="band.genre" class="band-genre">{{ band.genre }}</p>
              <p v-if="band.year" class="band-year">成立于 {{ band.year }}</p>
              <p v-if="band.bio" class="band-bio">{{ band.bio }}</p>
              <div class="band-stats">
                <span class="stat">
                  <i class="fas fa-users"></i>
                  {{ band.member_count }} 成员
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 成员展示 -->
      <div v-if="members.length > 0" class="members-section">
        <h3>成员列表</h3>
        <div class="members-grid">
          <div v-for="member in members" :key="member.id" class="member-card">
            <div class="member-avatar">
              <img v-if="member.avatar_url" :src="member.avatar_url" :alt="member.name" />
              <i v-else class="fas fa-user"></i>
            </div>
            <div class="member-info">
              <h4>{{ member.name }}</h4>
              <p v-if="member.role" class="member-role">{{ member.role }}</p>
              <p v-if="member.band_name" class="member-band">{{ member.band_name }}</p>
              <p v-if="member.join_date" class="member-date">
                加入时间：{{ formatDate(member.join_date) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 活动展示 -->
      <div v-if="events.length > 0" class="events-section">
        <h3>活动列表</h3>
        <div class="events-list">
          <div v-for="event in events" :key="event.id" class="event-card">
            <div class="event-date">
              <div class="date-day">{{ formatEventDay(event.event_date) }}</div>
              <div class="date-month">{{ formatEventMonth(event.event_date) }}</div>
            </div>
            <div class="event-info">
              <h4>{{ event.title }}</h4>
              <p v-if="event.description" class="event-description">{{ event.description }}</p>
              <div class="event-details">
                <span v-if="event.venue" class="detail-item">
                  <i class="fas fa-map-marker-alt"></i>
                  {{ event.venue }}
                </span>
                <span v-if="event.band_name" class="detail-item">
                  <i class="fas fa-music"></i>
                  {{ event.band_name }}
                </span>
                <span class="detail-item status" :class="event.status">
                  <i class="fas fa-circle"></i>
                  {{ getStatusText(event.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !adminInfo && !error" class="empty-state">
        <i class="fas fa-search"></i>
        <h3>搜索管理员</h3>
        <p>输入管理员用户名来查看他们管理的乐队信息</p>
      </div>

      <div v-if="adminInfo && bands.length === 0 && members.length === 0 && events.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>暂无数据</h3>
        <p>该管理员还没有添加任何乐队、成员或活动信息</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

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
    // 这里使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    adminInfo.value = {
      username: adminUsername.value,
      display_name: `管理员 ${adminUsername.value}`
    }
    
    bands.value = [
      {
        id: 1,
        name: '摇滚乐队',
        genre: '摇滚',
        year: 2020,
        bio: '一支充满激情的摇滚乐队',
        member_count: 4,
        primary_color: '#667eea'
      }
    ]
    
    members.value = [
      {
        id: 1,
        name: '张三',
        role: '主唱',
        band_name: '摇滚乐队',
        join_date: '2020-01-15'
      }
    ]
    
    events.value = [
      {
        id: 1,
        title: '音乐节演出',
        description: '参加城市音乐节演出',
        event_date: '2024-08-15T19:00:00',
        venue: '市中心广场',
        band_name: '摇滚乐队',
        status: 'upcoming'
      }
    ]
    
  } catch (err: any) {
    error.value = err.message || '加载数据失败'
  } finally {
    loading.value = false
  }
}

// 处理登出
const handleLogout = () => {
  authStore.logout()
  router.push('/auth/login')
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
    upcoming: '即将开始',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

onMounted(() => {
  // 如果URL中有用户名参数，自动加载
  if (route.params.username) {
    adminUsername.value = route.params.username as string
    loadAdminData()
  }
})
</script>

<style scoped>
.public-view {
  min-height: 100vh;
  background: #f7fafc;
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

.public-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.admin-selector {
  background: white;
  border-radius: 12px;
  padding: 2rem;
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

.input-wrapper {
  position: relative;
  max-width: 400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #a0aec0;
  z-index: 1;
}

.input-wrapper input {
  flex: 1;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px 0 0 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #667eea;
}

.search-button {
  padding: 0.75rem 1rem;
  background: #667eea;
  color: white;
  border: 2px solid #667eea;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: background 0.2s;
}

.search-button:hover:not(:disabled) {
  background: #5a67d8;
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fed7d7;
  color: #c53030;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.admin-info {
  margin-bottom: 2rem;
}

.admin-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.admin-avatar {
  width: 80px;
  height: 80px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.admin-details h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 0.25rem 0;
}

.admin-details p {
  color: #718096;
  margin: 0 0 1rem 0;
}

.admin-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #4a5568;
  font-size: 0.9rem;
}

.bands-section, .members-section, .events-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.bands-section h3, .members-section h3, .events-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.bands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.band-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.band-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.band-image {
  height: 200px;
  position: relative;
  overflow: hidden;
}

.band-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.band-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
}

.band-info {
  padding: 1.5rem;
}

.band-info h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
}

.band-genre, .band-year, .band-bio {
  color: #718096;
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.band-stats {
  margin-top: 1rem;
}

.stat {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #4a5568;
  font-size: 0.9rem;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.member-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  width: 60px;
  height: 60px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 1.5rem;
  color: #a0aec0;
  overflow: hidden;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
}

.member-role, .member-band, .member-date {
  color: #718096;
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.event-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  gap: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.event-date {
  text-align: center;
  min-width: 60px;
}

.date-day {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
}

.date-month {
  font-size: 0.8rem;
  color: #718096;
  text-transform: uppercase;
}

.event-info {
  flex: 1;
}

.event-info h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
}

.event-description {
  color: #718096;
  margin: 0 0 1rem 0;
}

.event-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #4a5568;
  font-size: 0.9rem;
}

.detail-item.status.upcoming { color: #3182ce; }
.detail-item.status.ongoing { color: #38a169; }
.detail-item.status.completed { color: #718096; }
.detail-item.status.cancelled { color: #e53e3e; }

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #a0aec0;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 0 1rem;
  }
  
  .public-content {
    padding: 1rem;
  }
  
  .admin-card {
    flex-direction: column;
    text-align: center;
  }
  
  .admin-stats {
    justify-content: center;
  }
  
  .bands-grid, .members-grid {
    grid-template-columns: 1fr;
  }
  
  .event-card {
    flex-direction: column;
    gap: 1rem;
  }
  
  .event-details {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>

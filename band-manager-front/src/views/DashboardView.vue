<template>
  <div class="dashboard">
    <!-- 顶部导航 -->
    <nav class="dashboard-nav">
      <div class="nav-content">
        <div class="nav-left">
          <h1 class="nav-title">
            <i class="fas fa-music"></i>
            乐队管理系统
          </h1>
        </div>
        <div class="nav-right">
          <div class="user-info">
            <span class="welcome-text">欢迎，{{ authStore.displayName }}</span>
            <div class="user-menu">
              <button class="user-avatar" @click="showUserMenu = !showUserMenu">
                <i class="fas fa-user-circle"></i>
              </button>
              <div v-if="showUserMenu" class="user-dropdown">
                <router-link to="/profile" class="dropdown-item">
                  <i class="fas fa-user"></i>
                  个人资料
                </router-link>
                <button @click="handleLogout" class="dropdown-item">
                  <i class="fas fa-sign-out-alt"></i>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="dashboard-content">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <h2>管理员仪表板</h2>
        <p>管理您的乐队、成员和活动信息</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="loadStats" class="retry-btn">重试</button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card" :class="{ loading }">
          <div class="stat-icon bands">
            <i class="fas fa-music"></i>
          </div>
          <div class="stat-content">
            <h3>{{ loading ? '...' : stats.bands }}</h3>
            <p>乐队数量</p>
          </div>
        </div>

        <div class="stat-card" :class="{ loading }">
          <div class="stat-icon members">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ loading ? '...' : stats.members }}</h3>
            <p>成员总数</p>
          </div>
        </div>

        <div class="stat-card" :class="{ loading }">
          <div class="stat-icon events">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ loading ? '...' : stats.events }}</h3>
            <p>活动数量</p>
          </div>
        </div>

        <div class="stat-card" :class="{ loading }">
          <div class="stat-icon active">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <h3>{{ loading ? '...' : stats.activeEvents }}</h3>
            <p>进行中活动</p>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions">
        <h3>快速操作</h3>
        <div class="action-grid">
          <router-link to="/bands" class="action-card">
            <i class="fas fa-plus-circle"></i>
            <span>添加乐队</span>
          </router-link>
          
          <router-link to="/members" class="action-card">
            <i class="fas fa-user-plus"></i>
            <span>添加成员</span>
          </router-link>
          
          <router-link to="/events" class="action-card">
            <i class="fas fa-calendar-plus"></i>
            <span>创建活动</span>
          </router-link>
          
          <router-link to="/gallery" class="action-card">
            <i class="fas fa-images"></i>
            <span>图片管理</span>
          </router-link>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="recent-section">
        <h3>最近活动</h3>
        <div class="recent-list">
          <div v-if="recentActivities.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>暂无最近活动</p>
          </div>
          <div v-else v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-content">
              <p class="activity-text">{{ activity.text }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { getDashboardStats, getRecentActivities, type DashboardStats, type RecentActivity } from '@/api/statsService'

const router = useRouter()
const authStore = useAuthStore()

// 界面状态
const showUserMenu = ref(false)
const loading = ref(false)
const error = ref('')

// 统计数据
const stats = ref<DashboardStats>({
  bands: 0,
  members: 0,
  events: 0,
  activeEvents: 0
})

// 最近活动
const recentActivities = ref<RecentActivity[]>([])

// 处理登出
const handleLogout = () => {
  authStore.logout()
  router.push('/auth/login')
}

// 加载统计数据
const loadStats = async () => {
  try {
    loading.value = true
    error.value = ''

    // 检查认证状态
    if (!authStore.isAuthenticated) {
      error.value = '请先登录'
      return
    }

    // 获取统计数据
    const statsData = await getDashboardStats()
    stats.value = statsData

    // 获取最近活动
    const activitiesData = await getRecentActivities()
    recentActivities.value = activitiesData

  } catch (err: any) {
    console.error('加载仪表板数据失败:', err)
    error.value = err.error || '加载数据失败'

    // 如果是认证错误，不要自动跳转（避免循环）
    if (err.error && err.error.includes('认证')) {
      console.log('认证错误，但不自动跳转避免循环')
    }
  } finally {
    loading.value = false
  }
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  console.log('Dashboard mounted')
  console.log('Auth status:', authStore.isAuthenticated)
  console.log('User:', authStore.user)
  console.log('Token:', authStore.token)
  console.log('LocalStorage token:', localStorage.getItem('auth_token'))

  loadStats()
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除事件监听
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f7fafc;
}

.dashboard-nav {
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

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  color: #4a5568;
  font-weight: 500;
}

.user-menu {
  position: relative;
}

.user-avatar {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #667eea;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background 0.2s;
}

.user-avatar:hover {
  background: rgba(102, 126, 234, 0.1);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  z-index: 1000;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #4a5568;
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f7fafc;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section {
  margin-bottom: 2rem;
}

.welcome-section h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.welcome-section p {
  color: #718096;
  font-size: 1.1rem;
}

.error-message {
  background: #fed7d7;
  border: 1px solid #fc8181;
  color: #c53030;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-btn {
  background: #c53030;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  margin-left: auto;
}

.retry-btn:hover {
  background: #9c2626;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-card.loading {
  opacity: 0.6;
  pointer-events: none;
}

.stat-card.loading .stat-content h3 {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.bands { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon.members { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.events { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-icon.active { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: #718096;
  margin: 0;
  font-size: 0.9rem;
}

.quick-actions, .recent-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.quick-actions h3, .recent-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  text-decoration: none;
  color: #4a5568;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}

.action-card i {
  font-size: 2rem;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #a0aec0;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f7fafc;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-weight: 500;
}

.activity-time {
  color: #a0aec0;
  font-size: 0.8rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 0 1rem;
  }
  
  .dashboard-content {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

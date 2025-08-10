<template>
  <div class="dashboard">
    <!-- 🎵 页面头部 -->
    <div class="page-header">
      <h1>
        <span class="gradient-text">管理员仪表盘</span>
      </h1>
      <p>欢迎回来，{{ authStore.displayName }}！管理您的音乐世界</p>
    </div>

    <!-- ⚠️ 错误提示 -->
    <div v-if="error" class="error-section">
      <div class="error-content">
        <i class="fa fa-exclamation-triangle"></i>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="loadStats" class="btn btn-primary">
          <i class="fa fa-refresh"></i>
          重新加载
        </button>
      </div>
    </div>

    <!-- 🎨 统计卡片网格 -->
    <div class="stats-grid">
      <div class="stat-card card card-interactive" :class="{ loading }">
        <div class="stat-icon bands">
          <i class="fa fa-music"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ loading ? '...' : stats.bands.count }}</div>
          <div class="stat-label">乐队数量</div>
          <div class="stat-trend" :class="{ positive: stats.bands.change > 0, negative: stats.bands.change < 0 }">
            <i v-if="stats.bands.change > 0" class="fa fa-arrow-up"></i>
            <i v-else-if="stats.bands.change < 0" class="fa fa-arrow-down"></i>
            <i v-else class="fa fa-minus"></i>
            <span>{{ stats.bands.change > 0 ? '+' : '' }}{{ stats.bands.change }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card card card-interactive" :class="{ loading }">
        <div class="stat-icon members">
          <i class="fa fa-users"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ loading ? '...' : stats.members.count }}</div>
          <div class="stat-label">成员总数</div>
          <div class="stat-trend" :class="{ positive: stats.members.change > 0, negative: stats.members.change < 0 }">
            <i v-if="stats.members.change > 0" class="fa fa-arrow-up"></i>
            <i v-else-if="stats.members.change < 0" class="fa fa-arrow-down"></i>
            <i v-else class="fa fa-minus"></i>
            <span>{{ stats.members.change > 0 ? '+' : '' }}{{ stats.members.change }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card card card-interactive" :class="{ loading }">
        <div class="stat-icon events">
          <i class="fa fa-calendar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ loading ? '...' : stats.events.count }}</div>
          <div class="stat-label">活动数量</div>
          <div class="stat-trend" :class="{ positive: stats.events.change > 0, negative: stats.events.change < 0 }">
            <i v-if="stats.events.change > 0" class="fa fa-arrow-up"></i>
            <i v-else-if="stats.events.change < 0" class="fa fa-arrow-down"></i>
            <i v-else class="fa fa-minus"></i>
            <span>{{ stats.events.change > 0 ? '+' : '' }}{{ stats.events.change }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card card card-interactive" :class="{ loading }">
        <div class="stat-icon active">
          <i class="fa fa-chart-line"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ loading ? '...' : stats.activeEvents }}</div>
          <div class="stat-label">进行中活动</div>
          <div class="stat-trend">
            <i class="fa fa-arrow-up"></i>
            <span>+5%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 🚀 快速操作区域 -->
    <div class="quick-actions-section">
      <h2 class="section-title">
        <i class="fa fa-bolt"></i>
        快速操作
      </h2>
      <div class="actions-grid">
        <router-link to="/bands" class="action-card card card-interactive">
          <div class="action-icon bands">
            <i class="fa fa-plus-circle"></i>
          </div>
          <div class="action-content">
            <h3>添加乐队</h3>
            <p>创建新的乐队信息</p>
          </div>
        </router-link>

        <router-link to="/members" class="action-card card card-interactive">
          <div class="action-icon members">
            <i class="fa fa-user-plus"></i>
          </div>
          <div class="action-content">
            <h3>添加成员</h3>
            <p>为乐队添加新成员</p>
          </div>
        </router-link>

        <router-link to="/events" class="action-card card card-interactive">
          <div class="action-icon events">
            <i class="fa fa-calendar-plus"></i>
          </div>
          <div class="action-content">
            <h3>创建活动</h3>
            <p>安排新的演出活动</p>
          </div>
        </router-link>

        <router-link to="/gallery" class="action-card card card-interactive">
          <div class="action-icon gallery">
            <i class="fa fa-images"></i>
          </div>
          <div class="action-content">
            <h3>图片管理</h3>
            <p>管理乐队相关图片</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 📈 最近活动时间线 -->
    <div class="recent-activities-section">
      <h2 class="section-title">
        <i class="fa fa-clock"></i>
        最近活动
      </h2>
      <div class="activities-timeline">
        <div v-if="recentActivities.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fa fa-inbox"></i>
          </div>
          <h3>暂无最近活动</h3>
          <p>开始管理您的乐队，活动记录将在这里显示</p>
        </div>
        <div v-else class="timeline">
          <div v-for="activity in recentActivities" :key="activity.id" class="timeline-item">
            <div class="timeline-marker">
              <i :class="activity.icon"></i>
            </div>
            <div class="timeline-content card">
              <div class="activity-text">{{ activity.text }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { getDashboardStats, getRecentActivities, type DashboardStats, type RecentActivity } from '@/api/statsService'

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

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.dashboard {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 1rem;
  }
}

// 🎨 统计卡片网格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;

  &.loading {
    opacity: 0.6;
    pointer-events: none;
  }

  .stat-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: $white;

    &.bands {
      background: linear-gradient(135deg, $primary, rgba($primary, 0.7));
    }

    &.members {
      background: linear-gradient(135deg, $secondary, rgba($secondary, 0.7));
    }

    &.events {
      background: linear-gradient(135deg, #10b981, rgba(#10b981, 0.7));
    }

    &.active {
      background: linear-gradient(135deg, #f59e0b, rgba(#f59e0b, 0.7));
    }
  }

  .stat-content {
    flex: 1;

    .stat-number {
      font-size: 2.5rem;
      font-weight: 700;
      color: $white;
      line-height: 1;
      margin-bottom: 0.5rem;
    }

    .stat-label {
      color: $gray-400;
      font-size: 0.875rem;
      margin-bottom: 0.75rem;
    }

    .stat-trend {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
      }

      .stat-trend.positive {
        color: $success;
      }

      .stat-trend.negative {
        color: $danger;
      }

      .stat-trend.positive i,
      .stat-trend.negative i {
        font-size: 1rem;
      }
  }
}

// 🚀 快速操作区域
.quick-actions-section {
  margin-bottom: 3rem;

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.5rem;
    font-weight: 600;
    color: $white;
    margin-bottom: 2rem;

    i {
      color: $primary;
    }
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }

  .action-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    text-decoration: none;
    color: inherit;

    .action-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      color: $white;

      &.bands {
        background: rgba($primary, 0.2);
        color: $primary;
      }

      &.members {
        background: rgba($secondary, 0.2);
        color: $secondary;
      }

      &.events {
        background: rgba(#10b981, 0.2);
        color: #10b981;
      }

      &.gallery {
        background: rgba(#f59e0b, 0.2);
        color: #f59e0b;
      }
    }

    .action-content {
      h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: $white;
        margin: 0 0 0.25rem;
      }

      p {
        color: $gray-400;
        font-size: 0.875rem;
        margin: 0;
      }
    }

    &:hover {
      .action-icon {
        transform: scale(1.1);
      }
    }
  }
}

// 📈 最近活动时间线
.recent-activities-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.5rem;
    font-weight: 600;
    color: $white;
    margin-bottom: 2rem;

    i {
      color: $primary;
    }
  }

  .activities-timeline {
    .timeline {
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 20px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: rgba($primary, 0.3);
      }

      .timeline-item {
        position: relative;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.5rem;

        .timeline-marker {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: $primary;
          display: flex;
          align-items: center;
          justify-content: center;
          color: $white;
          font-size: 1rem;
          z-index: 1;
          flex-shrink: 0;
        }

        .timeline-content {
          flex: 1;
          padding: 1rem;

          .activity-text {
            color: $white;
            font-weight: 500;
            margin-bottom: 0.5rem;
          }

          .activity-time {
            color: $gray-400;
            font-size: 0.875rem;
          }
        }
      }
    }
  }
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


</style>

<template>
  <header class="nav-header">
    <div class="nav-container">
      <!-- 🎵 品牌Logo -->
      <router-link to="/" class="nav-brand">
        <div class="brand-icon">
          <i class="fa fa-music"></i>
        </div>
        <span class="brand-text">SOUNDWAVE</span>
      </router-link>

      <!-- 🎯 桌面导航菜单 -->
      <nav class="nav-menu">
        <!-- 管理员专用导航 -->
        <template v-if="authStore.isAuthenticated && authStore.isAdmin">
          <router-link to="/dashboard" class="nav-link">仪表盘</router-link>
          <router-link to="/bands" class="nav-link">乐队管理</router-link>
          <router-link to="/members" class="nav-link">成员管理</router-link>
          <router-link to="/events" class="nav-link">演出活动</router-link>
          <router-link to="/gallery" class="nav-link">照片墙</router-link>
          <router-link to="/public" class="nav-link">公开展示</router-link>
        </template>

        <!-- 普通用户导航 -->
        <template v-else-if="authStore.isAuthenticated && !authStore.isAdmin">
          <router-link to="/public" class="nav-link">我的主页</router-link>
        </template>

        <!-- 未登录用户导航 -->
        <template v-else>
          <router-link to="/public" class="nav-link">公开展示</router-link>
          <router-link to="/auth/login" class="nav-link">登录</router-link>
          <router-link to="/auth/register" class="nav-link">注册</router-link>
        </template>

        <!-- 大麦网链接始终显示 -->
        <a href="https://www.damai.cn/" target="_blank" class="nav-link">大麦网</a>
      </nav>

      <!-- 🎨 用户操作区域 -->
      <div class="nav-actions">
        <template v-if="authStore.isAuthenticated">
          <div class="user-info">
            <span class="user-name">{{ authStore.user?.username }}</span>
            <span class="user-type" :class="{ 'admin': authStore.isAdmin }">
              {{ authStore.isAdmin ? '管理员' : '用户' }}
            </span>
          </div>
          <button @click="handleLogout" class="btn btn-outline btn-sm">
            <i class="fa fa-sign-out"></i>
            退出
          </button>
        </template>
      </div>

      <!-- 📱 移动端菜单按钮 -->
      <button class="mobile-menu-btn" @click="toggleMobileMenu">
        <i class="fa fa-bars"></i>
      </button>
    </div>

    <!-- 📱 移动端菜单 -->
    <div v-if="showMobileMenu" class="mobile-menu">
      <div class="mobile-menu-content">
        <!-- 移动端导航项 -->
        <template v-if="authStore.isAuthenticated && authStore.isAdmin">
          <router-link to="/dashboard" class="mobile-nav-link" @click="closeMobileMenu">仪表盘</router-link>
          <router-link to="/bands" class="mobile-nav-link" @click="closeMobileMenu">乐队管理</router-link>
          <router-link to="/members" class="mobile-nav-link" @click="closeMobileMenu">成员管理</router-link>
          <router-link to="/events" class="mobile-nav-link" @click="closeMobileMenu">演出活动</router-link>
          <router-link to="/gallery" class="mobile-nav-link" @click="closeMobileMenu">照片墙</router-link>
          <router-link to="/public" class="mobile-nav-link" @click="closeMobileMenu">公开展示</router-link>
        </template>

        <template v-else-if="authStore.isAuthenticated && !authStore.isAdmin">
          <router-link to="/public" class="mobile-nav-link" @click="closeMobileMenu">我的主页</router-link>
        </template>

        <template v-else>
          <router-link to="/public" class="mobile-nav-link" @click="closeMobileMenu">公开展示</router-link>
          <router-link to="/auth/login" class="mobile-nav-link" @click="closeMobileMenu">登录</router-link>
          <router-link to="/auth/register" class="mobile-nav-link" @click="closeMobileMenu">注册</router-link>
        </template>

        <a href="https://www.damai.cn/" target="_blank" class="mobile-nav-link">大麦网</a>

        <template v-if="authStore.isAuthenticated">
          <div class="mobile-user-info">
            <span>{{ authStore.user?.username }} ({{ authStore.isAdmin ? '管理员' : '用户' }})</span>
          </div>
          <button @click="handleLogout" class="mobile-nav-link logout-btn">退出登录</button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// 移动端菜单状态
const showMobileMenu = ref(false)

// 切换移动端菜单
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  showMobileMenu.value = false
}

// 处理退出登录
const handleLogout = () => {
  authStore.logout()
  router.push('/')
  closeMobileMenu()
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

// 🎨 用户信息样式
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;

  .user-name {
    font-weight: 600;
    color: $white;
    font-size: 0.875rem;
  }

  .user-type {
    font-size: 0.75rem;
    color: $gray-400;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    background: rgba($lightgray, 0.3);

    &.admin {
      color: $primary;
      background: rgba($primary, 0.1);
    }
  }
}

// 📱 移动端菜单样式
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba($darkgray, 0.95);
  backdrop-filter: blur(8px);
  border-top: 1px solid rgba($primary, 0.2);

  .mobile-menu-content {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    .mobile-nav-link {
      color: $gray-300;
      text-decoration: none;
      padding: 0.75rem 1rem;
      border-radius: $border-radius-md;
      transition: all $transition-normal ease;
      font-weight: 500;

      &:hover {
        color: $primary;
        background: rgba($primary, 0.1);
      }

      &.router-link-active {
        color: $primary;
        background: rgba($primary, 0.1);
      }

      &.logout-btn {
        background: rgba(#ef4444, 0.1);
        color: #ef4444;
        border: 1px solid rgba(#ef4444, 0.3);
        text-align: center;

        &:hover {
          background: rgba(#ef4444, 0.2);
        }
      }
    }

    .mobile-user-info {
      padding: 0.75rem 1rem;
      background: rgba($lightgray, 0.2);
      border-radius: $border-radius-md;
      color: $gray-300;
      font-size: 0.875rem;
      text-align: center;
    }
  }
}

// 🎯 活跃链接样式
.nav-link.router-link-active {
  color: $primary !important;

  &::after {
    content: '';
    position: absolute;
    bottom: -0.5rem;
    left: 0;
    right: 0;
    height: 2px;
    background: $primary;
    border-radius: 1px;
  }
}

.mobile-nav-link.router-link-active {
  color: $primary !important;
  background: rgba($primary, 0.1) !important;
}

// 🌟 响应式调整
@media (max-width: 768px) {
  .nav-container {
    padding: 1rem 1rem !important;
  }

  .user-info {
    display: none;
  }
}

@media (max-width: 480px) {
  .brand-text {
    display: none;
  }

  .brand-icon {
    width: 2rem !important;
    height: 2rem !important;
    font-size: 1rem !important;
  }
}
</style>

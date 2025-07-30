import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import HomeView from '@/views/HomeView.vue'

const routes = [
  // 首页路由 - 根据认证状态显示不同内容
  {
    path: '/',
    name: 'home',
    component: HomeView
  },

  // 认证路由
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true }
  },

  // 管理员仪表板
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  // 管理员专用路由
  {
    path: '/bands',
    name: 'BandManagement',
    component: () => import('@/views/bands/BandManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/members',
    name: 'MemberManagement',
    component: () => import('@/views/bands/MemberManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/events',
    name: 'EventManagement',
    component: () => import('@/views/bands/EventManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/bands/GalleryView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  // 公开展示路由
  {
    path: '/public/:username?',
    name: 'PublicView',
    component: () => import('@/views/PublicView.vue'),
    props: true
  },

  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 初始化认证状态（如果还没有初始化）
  if (!authStore.isAuthenticated) {
    authStore.initAuth()

    // 如果初始化后有token，验证其有效性
    if (authStore.token) {
      try {
        const isValid = await authStore.verifyToken()
        if (!isValid) {
          authStore.logout()
        }
      } catch (error) {
        console.error('Token验证失败:', error)
        authStore.logout()
      }
    }
  }

  // 如果访问首页且已登录，根据用户类型重定向
  if (to.name === 'home' && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      next({ name: 'Dashboard' })
      return
    } else {
      next({ name: 'PublicView' })
      return
    }
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // 不是管理员，跳转到公开页面
      next({ name: 'PublicView' })
      return
    }
  }

  // 检查是否需要游客状态（已登录用户不能访问登录/注册页）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 已登录，根据用户类型跳转
    if (authStore.isAdmin) {
      next({ name: 'Dashboard' })
    } else {
      next({ name: 'PublicView' })
    }
    return
  }

  next()
})

export default router
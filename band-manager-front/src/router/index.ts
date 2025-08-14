import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import HomeView from '@/views/HomeView.vue'

// 🚀 优化的路由懒加载函数
const lazyLoad = (component: string) => {
  return () => import(/* webpackChunkName: "[request]" */ `@/views/${component}.vue`)
}

// 🚀 优化的模块懒加载函数
const lazyLoadModule = (modulePath: string, componentName: string) => {
  return () => import(/* webpackChunkName: "poster-girl" */ modulePath).then(module => ({ 
    default: module[componentName] 
  }))
}

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
    component: lazyLoad('auth/LoginView'),
    meta: { requiresGuest: true }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: lazyLoad('auth/RegisterView'),
    meta: { requiresGuest: true }
  },

  // 图标测试页面（已移除）

  // 管理员仪表板
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: lazyLoad('DashboardView'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  // 超级管理员：用户管理、举报管理
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: lazyLoad('admin/AdminUsersView'),
    meta: { requiresAuth: true, requiresSuperadmin: true }
  },
  {
    path: '/admin/reports',
    name: 'AdminReports',
    component: lazyLoad('admin/AdminReportsView'),
    meta: { requiresAuth: true, requiresSuperadmin: true }
  },

  // 管理员专用路由
  {
    path: '/bands',
    name: 'BandManagement',
    component: lazyLoad('bands/BandManagement'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/members',
    name: 'MemberManagement',
    component: lazyLoad('bands/MemberManagement'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/events',
    name: 'EventManagement',
    component: lazyLoad('bands/EventManagement'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: lazyLoad('bands/CommunityView'),
    // 社区对所有用户可浏览，发帖/评论在接口层做鉴权
  },

  // 公开展示路由
  {
    path: '/public/:username?',
    name: 'PublicView',
    component: lazyLoad('PublicView'),
    props: true
  },

  // AI乐队顾问（所有用户可用）
  {
    path: '/music-teacher',
    name: 'MusicTeacher',
    component: lazyLoad('MusicTeacherView')
  },

  // 音乐盒演示页面（所有用户可用）
  {
    path: '/music-box-demo',
    name: 'MusicBoxDemo',
    component: lazyLoad('MusicBoxDemo')
  },

  // 看板娘设置页面（所有用户可用）
  {
    path: '/poster-girl-settings',
    name: 'PosterGirlSettings', 
    component: lazyLoadModule('@/modules/poster-girl', 'PosterGirlSettings')
  },

  // 用户资料页面
  {
    path: '/profile',
    name: 'Profile',
    component: lazyLoad('ProfileView'),
    meta: { requiresAuth: true }
  },

  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: lazyLoad('NotFoundView')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 🚀 优化的路由守卫 - 减少不必要的认证检查
let authInitialized = false

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 只在第一次路由跳转时初始化认证状态
  if (!authInitialized) {
    authStore.initAuth()
    authInitialized = true

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

    // 检查是否需要超级管理员
    if ((to.meta as any).requiresSuperadmin && authStore.user?.user_type !== ('superadmin' as any)) {
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
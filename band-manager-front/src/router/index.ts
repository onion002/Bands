import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/bands',
    name: 'BandManagement',
    component: () => import('@/views/bands/BandManagement.vue')
  },
  // 添加其他页面的占位路由（必须匹配导航栏中的链接）
  {
    path: '/members',
    name: 'MemberManagement',
    component: () => import('@/views/bands/MemberManagement.vue')
  },
  {
    path: '/events',
    name: 'EventManagement',
    component: () => import('@/views/bands/EventManagement.vue')
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/bands/GalleryView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
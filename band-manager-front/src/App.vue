<template>
  <div id="app" class="bg-noise">
    <!-- 🎵 导航头部 - 完全独立，固定在顶部 -->
    <NavHeader />

    <!-- 🎨 主内容区域 - 在导航栏下方，有适当的上边距 -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 🚀 返回顶部按钮 - 全局组件 -->
    <BackToTop />
  </div>
</template>

<script setup lang="ts">
import NavHeader from '@/components/NavHeader.vue'
import BackToTop from '@/components/BackToTop.vue'
</script>

<style lang="scss">
@use '@/assets/scss/variables' as *;

#app {
  min-height: 100vh;
  background: $dark;
  color: $white;
  font-family: $font-family-base;
  padding-top: 0; // 移除顶部内边距，让导航栏完全独立
}

.main-content {
  padding-top: 4rem; // 为固定导航栏留出空间
  min-height: calc(100vh - 4rem);
  width: 100%;
  position: relative;
  z-index: 1; // 确保主内容在导航栏下方
}

// 🌟 Font Awesome 图标支持 - 升级到6.4.0版本
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
</style>
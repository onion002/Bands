<template>
  <div id="app" class="bg-noise">
    <!-- 🎵 导航头部 -->
    <NavHeader />

    <!-- 🎨 主内容区域 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import NavHeader from '@/components/NavHeader.vue'
</script>

<style lang="scss">
@use '@/assets/scss/variables' as *;

#app {
  min-height: 100vh;
  background: $dark;
  color: $white;
  font-family: $font-family-base;
}

.main-content {
  padding-top: 80px; // 为固定导航栏留出空间
  min-height: calc(100vh - 80px);
}

// 🌟 Font Awesome 图标支持
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css');
</style>
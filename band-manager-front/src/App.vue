<template>
  <div id="app">
    <!-- 导航栏容器 -->
    <div class="nav-container">
      <NavHeader />
    </div>
    
    <!-- 主内容区 -->
    <main>
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import NavHeader from '@/components/NavHeader.vue'
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  width: 100%;
}

.nav-container {
  position: relative;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}

main {
  width: 100%;
}
</style>
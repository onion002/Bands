<template>
  <div class="home-view">
    <!-- 智能导航栏 -->
    <NavHeader />
    
    <!-- 乐队展示区 -->
    <BandShowcase />
  </div>
</template>

<script setup lang="ts">
import NavHeader from '@/components/NavHeader.vue';
import BandShowcase from '@/components/BandShowcase.vue';
</script>

<style scoped>
.home-view {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
}
</style>
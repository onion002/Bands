<template>
  <div class="nav-header-wrapper">
    <div class="nav-header">
      <!-- Logo - B为红色，ANDS为黑色 -->
      <div class="logo">
        <span class="letter-b">B</span><span class="other-letters">ANDS</span>
      </div>
      
      <!-- 导航链接 - 黑色背景 -->
      <div class="nav-boxes">
        <router-link to="/bands" class="nav-box">乐队管理</router-link>
        <router-link to="/members" class="nav-box">成员管理</router-link>
        <router-link to="/events" class="nav-box">演出活动</router-link>
        <router-link to="/gallery" class="nav-box">照片墙</router-link>
      </div>
    </div>
    
    <!-- 隐藏的鼠标感应区域 -->
    <div class="nav-trigger-area"></div>
  </div>
</template>

<script setup lang="ts">
// 不再需要isExpanded和相关方法
</script>

<style scoped lang="scss">
.nav-header-wrapper,
.nav-header {
  box-sizing: border-box;
}

.nav-header-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  height: 60px;
  
  .nav-trigger-area {
    display: none;
  }
  
  .nav-header {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background: linear-gradient(90deg, #1b1a1a, #a32321);
    display: flex;
    align-items: center;
    padding: 0 20px;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    
    .logo {
      font-family: 'Arial Black', sans-serif;
      font-size: 32px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      letter-spacing: 2px;
      
      .letter-b {
        color: #ff0000; /* 红色B */
      }
      
      .other-letters {
        color: #ffffff; /* 黑色ANDS */
      }
    }
    
    .nav-boxes {
      display: flex;
      gap: 15px;
      margin-left: auto;
      opacity: 1;
      
      .nav-box {
        padding: 10px 20px;
        background: #131212; /* 黑色背景 */
        color: white;
        border-radius: 8px;
        font-weight: bold;
        text-decoration: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        min-width: 120px;
        text-align: center;
        
        &:hover {
          transform: translateY(-3px);
          box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
          background: #333333; /* 深灰色悬停效果 */
        }
      }
    }
  }
}
</style>
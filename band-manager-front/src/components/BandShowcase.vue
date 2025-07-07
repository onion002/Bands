<template>
  <div class="band-showcase">
    <!-- 左箭头 -->
    <button class="nav-arrow prev" @click="prevSlide" aria-label="上一组乐队">
      <svg width="24" height="24" viewBox="0 0 24 24">
        <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
      </svg>
    </button>
    
    <!-- 乐队展示区 -->
    <div class="showcase-container">
      <div class="slide-group">
        <div 
          v-for="(band, index) in visibleBands" 
          :key="band.id" 
          class="band-card"
          :class="{ active: activeBandIndex === index }"
          @mouseenter="pauseAutoSlide"
          @mouseleave="resumeAutoSlide"
          @click="selectBand(band)"
          @mouseover="hoverCard(index)"
          @mouseout="unhoverCard"
        >
          <div class="image-container">
            <div class="placeholder-image" :style="{ backgroundColor: band.color }">
              <div v-if="!band.imageUrl" class="placeholder-text">
                <!-- 使用原生音乐符号 -->
                <div class="music-symbol">♪</div>
                <span>乐队图片</span>
              </div>
            </div>
          </div>
          <div class="band-info">
            <h3 class="band-name">{{ band.name }}</h3>
            <p class="band-genre">{{ band.genre }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右箭头 -->
    <button class="nav-arrow next" @click="nextSlide" aria-label="下一组乐队">
      <svg width="24" height="24" viewBox="0 0 24 24">
        <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

// 乐队数据 - 使用黑白灰三种纯色作为默认背景
const bands = ref([
  { 
    id: 1, 
    name: "霓虹狂想曲", 
    genre: "电子摇滚", 
    color: "#333333", // 深灰色
    imageUrl: "" 
  },
  { 
    id: 2, 
    name: "金属意志", 
    genre: "重金属", 
    color: "#666666", // 中灰色
    imageUrl: "" 
  },
  { 
    id: 3, 
    name: "城市之声", 
    genre: "流行摇滚", 
    color: "#999999", // 浅灰色
    imageUrl: "" 
  },
  { 
    id: 4, 
    name: "荒野节奏", 
    genre: "民谣摇滚", 
    color: "#333333", // 深灰色
    imageUrl: "" 
  },
  { 
    id: 5, 
    name: "幻影和弦", 
    genre: "前卫摇滚", 
    color: "#666666", // 中灰色
    imageUrl: "" 
  },
  { 
    id: 6, 
    name: "街头回响", 
    genre: "朋克摇滚", 
    color: "#999999", // 浅灰色
    imageUrl: "" 
  },
]);

const activeBandIndex = ref(0);
const currentGroup = ref(0);
const autoSlideInterval = ref<number | null>(null);
const hoveredCardIndex = ref(-1);

// 每页显示3个乐队
const visibleBands = computed(() => {
  const start = currentGroup.value * 3;
  return bands.value.slice(start, start + 3);
});

const nextSlide = () => {
  if (currentGroup.value >= Math.ceil(bands.value.length / 3) - 1) {
    currentGroup.value = 0;
  } else {
    currentGroup.value++;
  }
};

const prevSlide = () => {
  if (currentGroup.value <= 0) {
    currentGroup.value = Math.ceil(bands.value.length / 3) - 1;
  } else {
    currentGroup.value--;
  }
};

const startAutoSlide = () => {
  if (autoSlideInterval.value) return;
  
  autoSlideInterval.value = window.setInterval(() => {
    nextSlide();
  }, 5000);
};

const pauseAutoSlide = () => {
  if (autoSlideInterval.value) {
    clearInterval(autoSlideInterval.value);
    autoSlideInterval.value = null;
  }
};

const resumeAutoSlide = () => {
  if (!autoSlideInterval.value) {
    startAutoSlide();
  }
};

const selectBand = (band: any) => {
  console.log('Selected band:', band);
};

const hoverCard = (index: number) => {
  hoveredCardIndex.value = index;
};

const unhoverCard = () => {
  hoveredCardIndex.value = -1;
};

onMounted(() => {
  startAutoSlide();
});

onUnmounted(() => {
  pauseAutoSlide();
});
</script>

<style scoped lang="scss">
.band-showcase {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #000;

  .nav-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    cursor: pointer;
    z-index: 10;
    backdrop-filter: blur(10px);
    
    svg {
      width: 32px;
      height: 32px;
      fill: white;
    }
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
      transform: translateY(-50%) scale(1.1);
    }
    
    &.prev {
      left: 30px;
    }
    
    &.next {
      right: 30px;
    }
  }
  
  .showcase-container {
    width: 100%;
    height: 100%;
    padding: 0 5px; /* 小幅度内边距 */
    
    .slide-group {
      display: flex;
      width: 100%;
      height: 100%;
      gap: 2px; /* 极小的间隙 */
      
      .band-card {
        flex: 1;
        height: 100%;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
        cursor: pointer;
        transition: 
          transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275),
          z-index 0.5s;
        
        /* 悬停放大效果 - 刚好填满间隙 */
        &:hover {
          transform: scale(1.01);
          z-index: 5;
          box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }
        
        .image-container {
          width: 100%;
          height: 100%;
          
          .placeholder-image {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            
            .placeholder-text {
              display: flex;
              flex-direction: column;
              align-items: center;
              color: rgba(255, 255, 255, 0.7);
              font-size: 1.5rem;
              text-align: center;
              
              .music-symbol {
                font-size: 4rem;
                margin-bottom: 10px;
                animation: pulse 2s infinite;
              }
              
              span {
                font-size: 1.2rem;
                font-weight: 500;
              }
            }
          }
        }
        
        .band-info {
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          padding: 20px;
          background: rgba(0, 0, 0, 0.6);
          color: white;
          backdrop-filter: blur(5px);
          transform: translateY(0);
          transition: transform 0.4s ease;
          
          .band-name {
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
          }
          
          .band-genre {
            margin: 10px 0 0;
            font-size: 1.3rem;
            opacity: 0.9;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
          }
        }
      }
    }
  }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
}
</style>
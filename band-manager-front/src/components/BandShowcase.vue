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
            <template v-if="band.banner_image_url">
              <img :src="band.banner_image_url" alt="乐队图片" style="width:100%;height:100%;object-fit:cover;display:block;" />
            </template>
            <template v-else>
              <div class="placeholder-image" :style="{ backgroundColor: band.color || '#222' }">
                <div class="placeholder-text">
                <div class="music-symbol">♪</div>
                <span>乐队图片</span>
              </div>
            </div>
            </template>
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
import { BandService } from '@/api/bandService';

const bands = ref<any[]>([]);
const activeBandIndex = ref(0);
const autoSlideInterval = ref<number | null>(null);
const hoveredCardIndex = ref(-1);

// 只展示1个乐队
const visibleBands = computed(() => {
  if (bands.value.length === 0) return [];
  return [bands.value[activeBandIndex.value]];
});

const nextSlide = () => {
  if (bands.value.length === 0) return;
  activeBandIndex.value = (activeBandIndex.value + 1) % bands.value.length;
};

const prevSlide = () => {
  if (bands.value.length === 0) return;
  activeBandIndex.value = (activeBandIndex.value - 1 + bands.value.length) % bands.value.length;
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
  // 可扩展点击事件
};

const hoverCard = (index: number) => {
  hoveredCardIndex.value = index;
};

const unhoverCard = () => {
  hoveredCardIndex.value = -1;
};

onMounted(async () => {
  // 获取真实乐队数据
  try {
    const result = await BandService.getBands();
    bands.value = Array.isArray(result.items) ? result.items : [];
  } catch (e) {
    bands.value = [];
  }
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
        // 性能优化的过渡效果
        transition:
          transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275),
          z-index 0.5s,
          box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        will-change: transform;
        // 启用硬件加速
        transform: translateZ(0);
        backface-visibility: hidden;

        /* 优化的悬停效果 */
        &:hover {
          transform: scale(1.01) translateZ(0);
          z-index: 5;
          box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }

        &:not(:hover) {
          will-change: auto;
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
                // 使用优化的脉冲动画
                animation: optimized-pulse 2s ease-in-out infinite;
                will-change: transform;
                transform: translateZ(0);
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

// 优化的脉冲动画 - 使用 transform3d 和硬件加速
@keyframes optimized-pulse {
  0% {
    transform: scale3d(1, 1, 1);
    opacity: 0.8;
  }
  50% {
    transform: scale3d(1.1, 1.1, 1.1);
    opacity: 1;
  }
  100% {
    transform: scale3d(1, 1, 1);
    opacity: 0.8;
  }
}
</style>
<template>
    <div class="band-card" :style="cardStyle" @click="console.log('card clicked')">
      <div class="card-overlay"></div>
      
      <div class="card-content" @click="console.log('content clicked')">
        <div class="image-container" @click="console.log('clicked'); showBioDialog = true" style="cursor: pointer;">
          <div v-if="band.banner_image_url" class="band-image" :style="{ backgroundImage: `url(${band.banner_image_url})` }">
            <img
              :src="band.banner_image_url"
              class="band-image-content"
              @click="showBioDialog = true"
              style="cursor: pointer;"
            />
          </div>
          <div v-else class="placeholder-image">
            <div class="placeholder-content">
              <i class="fas fa-music"></i>
              <span>乐队图片</span>
            </div>
          </div>
        </div>
        
        <div class="band-info">
          <div class="band-header">
            <h3 class="band-name">{{ band.name }}</h3>
            <p class="band-genre">{{ band.genre }}</p>
          </div>
          <p class="band-year">成立年份: {{ band.year }}</p>
          <p class="band-members">成员数量: {{ band.member_count || 0 }}</p>
          
          <div class="band-actions">
            <button @click.stop="$emit('edit', band)" class="action-btn edit-btn">
              <i class="fas fa-edit"></i> 编辑
            </button>
            <button @click.stop="$emit('upload', band)" class="action-btn upload-btn">
              <i class="fas fa-upload"></i> 上传
            </button>
            <button @click.stop="$emit('delete', band)" class="action-btn delete-btn">
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
      </div>
      <!-- 乐队简介弹窗 -->
      <div v-if="showBioDialog" class="bio-dialog-overlay" @click.self="showBioDialog = false">
        <div class="bio-dialog">
          <h3>乐队简介</h3>
          <div class="bio-content">{{ band.bio || '暂无简介' }}</div>
          <button class="close-bio-btn" @click="showBioDialog = false">关闭</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed, ref } from 'vue';
  import type { PropType } from 'vue';
  import type { Band } from '@/types';
  
  const props = defineProps({
    band: {
      type: Object as PropType<Band>,
      required: true
    }
  });
  
  const showBioDialog = ref(false);
  
  // 随机生成灰色背景
  const cardBackground = computed(() => {
    const grays = ['#222', '#333', '#444', '#555'];
    return grays[Math.floor(Math.random() * grays.length)];
  });
  
  // 卡片整体样式
  const cardStyle = computed(() => ({
    background: cardBackground.value,
    border: `1px solid ${cardBackground.value === '#222' ? '#444' : '#666'}`
  }));
  </script>
  
  <style scoped lang="scss">
  .band-card {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    
    &:hover {
      transform: translateY(-10px) scale(1.02);
      box-shadow: 0 12px 40px rgba(229, 57, 53, 0.4);
    }
    
    .card-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.8) 100%);
      z-index: 1;
      pointer-events: none;
    }
    
    .card-content {
      position: relative;
      z-index: 2;
      padding: 20px;
    }
    
    .image-container {
      height: 200px;
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      margin-bottom: 15px;
      
      .band-image {
        width: 100%;
        height: 100%;
        background-size: cover;
        background-position: center;
      }
      
      .placeholder-image {
        width: 100%;
        height: 100%;
        background-color: #222;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .placeholder-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          color: rgba(255, 255, 255, 0.5);
          font-size: 1.5rem;
          
          i {
            font-size: 3rem;
            margin-bottom: 10px;
            color: rgba(229, 57, 53, 0.7);
          }
          
          span {
            font-size: 1.2rem;
          }
        }
      }
    }
    
    .band-info {
      color: white;
      
      .band-header {
        margin-bottom: 15px;
        
        .band-name {
          font-size: 1.8rem;
          margin: 0 0 5px;
          color: #fff;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .band-genre {
          font-size: 1.1rem;
          color: #ccc;
          margin: 0;
        }
      }
      
      .band-year, .band-members {
        font-size: 0.95rem;
        color: #aaa;
        margin: 5px 0;
      }
    }
    
    .band-actions {
      display: flex;
      gap: 10px;
      margin-top: 20px;
      
      .action-btn {
        flex: 1;
        padding: 8px 12px;
        border: none;
        border-radius: 5px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        
        i {
          margin-right: 5px;
        }
        
        &:hover {
          transform: translateY(-2px);
        }
      }
      
      .edit-btn {
        background: rgba(41, 121, 255, 0.8);
        color: white;
      }
      
      .upload-btn {
        background: rgba(106, 176, 76, 0.8);
        color: white;
      }
      
      .delete-btn {
        background: rgba(229, 57, 53, 0.8);
        color: white;
      }
    }
  }
  
  .bio-dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }
  .bio-dialog {
    background: #222;
    color: #fff;
    border-radius: 10px;
    padding: 30px 30px 20px 30px;
    min-width: 300px;
    max-width: 90vw;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    text-align: left;
    position: relative;
  }
  .bio-dialog h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #e53935;
  }
  .bio-content {
    margin-bottom: 20px;
    white-space: pre-wrap;
    word-break: break-all;
  }
  .close-bio-btn {
    background: #e53935;
    color: #fff;
    border: none;
    border-radius: 20px;
    padding: 8px 24px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  .close-bio-btn:hover {
    background: #b71c1c;
  }
  .band-image-content {
    pointer-events: auto !important;
    cursor: pointer;
  }
  </style>
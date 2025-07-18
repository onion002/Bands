<template>
    <div class="modal-overlay" @click.self="close">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ mode === 'edit' ? '编辑乐队信息' : '添加新乐队' }}</h2>
          <button class="close-btn" @click="close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="save">
            <!-- 在表单顶部添加上传图片按钮 -->
            <div class="form-group band-image-upload-section">
              <label>乐队图片</label>
              <div class="band-image-upload-area">
                <div class="band-image-preview">
                  <img v-if="formData.banner_image_url" :src="formData.banner_image_url" alt="乐队图片" class="band-image-preview-img">
                  <div v-else class="band-image-placeholder">
                    <i class="fas fa-image"></i>
                  </div>
                </div>
                <div class="band-image-actions">
                  <input
                    type="file"
                    ref="bandImageInput"
                    accept="image/*"
                    @change="handleBandImageChange"
                    style="display: none;"
                  >
                  <button type="button" class="upload-band-image-btn" @click="triggerBandImageUpload">
                    <i class="fas fa-camera"></i> 上传图片
                  </button>
                  <button v-if="formData.banner_image_url" type="button" class="remove-band-image-btn" @click="removeBandImage">
                    <i class="fas fa-trash"></i> 移除
                  </button>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>乐队名称</label>
              <input type="text" v-model="formData.name" required>
            </div>
            
            <div class="form-group">
              <label>音乐流派</label>
              <input type="text" v-model="formData.genre" required>
            </div>
            
            <!-- 成立年份和成员数量各自单独一行 -->
            <div class="form-group">
              <label>成立年份</label>
              <input type="number" v-model="formData.formedYear" min="1900" :max="new Date().getFullYear()" required>
            </div>
            <div class="form-group">
              <label>成员数量</label>
              <input type="number" v-model="formData.memberCount" min="1" max="20" required>
            </div>
            
            <div class="form-group">
              <label>乐队简介</label>
              <textarea v-model="formData.description" rows="4"></textarea>
            </div>
            
            <div class="form-buttons">
              <button type="button" class="cancel-btn" @click="close">取消</button>
              <button type="submit" class="save-btn">{{ mode === 'edit' ? '更新' : '创建' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch, onMounted } from 'vue';
  import type { Band } from '@/types';
  
  const props = defineProps({
    band: {
      type: Object as () => Band | null,
      default: null
    },
    mode: {
      type: String,
      default: 'add'
    }
  });
  
  const formData = ref({
    id: '',
    name: '',
    genre: '',
    formedYear: new Date().getFullYear(),
    description: '',
    memberCount: 4,
    banner_image_url: '' // 新增用于存储图片URL的字段
  });
  
  const emit = defineEmits(['close', 'save']);
  
  // 当传入的band发生变化时更新表单数据
  watch(() => props.band, (newBand) => {
    if (newBand) {
      formData.value = {
        id: String(newBand.id),
        name: newBand.name,
        genre: newBand.genre,
        formedYear: newBand.year,
        description: newBand.bio,
        memberCount: newBand.member_count,
        banner_image_url: newBand.banner_image_url // 更新图片URL
      };
    }
  }, { immediate: true });
  
  // 关闭模态框
  const close = () => {
    emit('close');
  };
  
  // 保存乐队信息
  const save = () => {
    emit('save', {
      id: formData.value.id,
      name: formData.value.name,
      genre: formData.value.genre,
      year: formData.value.formedYear,
      bio: formData.value.description,
      member_count: formData.value.memberCount,
      banner_image_url: formData.value.banner_image_url // 传递图片URL
    });
  };

  // 图片上传相关
  const bandImageInput = ref<HTMLInputElement | null>(null);

  const triggerBandImageUpload = () => {
    bandImageInput.value?.click();
  };

  const handleBandImageChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const file = target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          formData.value.banner_image_url = e.target.result as string;
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const removeBandImage = () => {
    formData.value.banner_image_url = '';
  };
  </script>
  
  <style scoped lang="scss">
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    
    .modal-container {
      background: linear-gradient(135deg, #1e1e2e, #2c2c3e);
      border-radius: 12px;
      width: 500px;
      max-width: 90vw;
      box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(229, 57, 53, 0.3);
      overflow: hidden;
      
      .modal-header {
        background: rgba(229, 57, 53, 0.8);
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        h2 {
          margin: 0;
          color: white;
          font-size: 1.6rem;
        }
        
        .close-btn {
          background: none;
          border: none;
          color: white;
          font-size: 1.5rem;
          cursor: pointer;
          transition: transform 0.3s ease;
          
          &:hover {
            transform: rotate(90deg);
          }
        }
      }
      
      .modal-body {
        padding: 25px;
        
        .form-group {
          margin-bottom: 20px;
          
          label {
            display: block;
            margin-bottom: 8px;
            color: #ccc;
            font-weight: 500;
          }
          
          input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: none;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
            
            &:focus {
              outline: none;
              background: rgba(255, 255, 255, 0.15);
              box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.5);
            }
          }
          
          textarea {
            resize: vertical;
          }
        }
        
        .form-row {
          display: flex;
          gap: 20px;
        }
        .form-row .form-group {
          flex: 1;
          max-width: calc(50% - 10px);
        }
        
        .form-buttons {
          display: flex;
          justify-content: flex-end;
          gap: 15px;
          margin-top: 20px;
          
          button {
            padding: 12px 30px;
            border: none;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
          }
          
          .cancel-btn {
            background: rgba(255, 255, 255, 0.1);
            color: #ccc;
            
            &:hover {
              background: rgba(255, 255, 255, 0.2);
            }
          }
          
          .save-btn {
            background: linear-gradient(to right, #e53935, #e35d5b);
            color: white;
            
            &:hover {
              box-shadow: 0 5px 15px rgba(229, 57, 53, 0.4);
              transform: translateY(-2px);
            }
          }
        }
      }
    }
  }
  .form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  background: #23232e;
  color: #fff;
  border: none;
  width: 100%;
  max-width: 400px;
  min-width: 200px;
  margin-left: auto;
  margin-right: auto;
  display: block;
  box-sizing: border-box;
  padding: 12px 15px;
  font-size: 1rem;
  height: 43px;
  border-radius: 6px;
}
.form-group textarea {
  min-height: 80px;
  resize: vertical;
}
.form-group label {
  color: #ccc;
}
.form-group select option {
  background: #23232e;
  color: #fff;
}
/* 样式：乐队图片上传区、按钮、预览等 */
.band-image-upload-section {
  text-align: center;
  margin-bottom: 25px;
}
.band-image-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
.band-image-preview {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 3px solid #444;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #23232e;
}
.band-image-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.band-image-placeholder {
  color: #888;
  font-size: 2rem;
}
.band-image-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
.upload-band-image-btn,
.remove-band-image-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}
.upload-band-image-btn {
  background: linear-gradient(to right, #1976d2, #2196f3);
  color: white;
}
.upload-band-image-btn:hover {
  background: #1565c0;
}
.remove-band-image-btn {
  background: rgba(229, 57, 53, 0.8);
  color: white;
}
.remove-band-image-btn:hover {
  background: #b71c1c;
}
  </style>
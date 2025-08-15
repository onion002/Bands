<template>
  <div class="profile-view">
    <div class="page-header">
      <h1 class="page-title">
        <i class="fa fa-user-circle"></i>
        个人资料
      </h1>
      <p class="page-subtitle">管理您的个人信息和账户设置</p>
    </div>

    <div class="profile-container">
      <div class="avatar-section">
        <div class="avatar-container">
          <img 
            v-if="user?.avatar_url" 
            :src="user.avatar_url" 
            :alt="user?.username"
            class="current-avatar"
          />
          <div v-else class="avatar-placeholder">
            <i class="fa fa-user"></i>
          </div>
          
          <div class="avatar-overlay">
            <label for="avatar-upload" class="avatar-upload-btn">
              <i class="fa fa-camera"></i>
              更换头像
            </label>
            <input 
              id="avatar-upload" 
              type="file" 
              accept="image/*" 
              @change="handleAvatarChange"
              style="display: none;"
            />
          </div>
        </div>
        
        <div class="avatar-info">
          <h3>{{ user?.username }}</h3>
          <p>{{ 
            user?.user_type === 'superadmin' ? '超级管理员' : 
            user?.user_type === 'admin' ? '管理员' : '用户' 
          }}</p>
          <p class="join-date">加入时间：{{ formatDate(user?.created_at) }}</p>
          
          <!-- 快捷跳转按钮 -->
          <div class="quick-nav-buttons">
            <button 
              @click="scrollToSection('basic-info')" 
              class="quick-nav-btn"
              title="跳转到基本信息"
            >
              <i class="fa fa-edit"></i>
              基本信息
            </button>
            <button 
              @click="scrollToSection('password-change')" 
              class="quick-nav-btn"
              title="跳转到修改密码"
            >
              <i class="fa fa-lock"></i>
              修改密码
            </button>
            <button 
              v-if="user?.user_type === 'admin'"
              @click="scrollToSection('privacy-settings')" 
              class="quick-nav-btn"
              title="跳转到公开设置"
            >
              <i class="fa fa-globe"></i>
              公开设置
            </button>
            <button
              @click="scrollToSection('favorites')"
              class="quick-nav-btn"
              title="跳转到我的收藏"
            >
              <i class="fa fa-heart"></i>
              我的收藏
            </button>
          </div>
        </div>
      </div>

      <div id="basic-info" class="profile-section">
        <h2 class="section-title">
          <i class="fa fa-edit"></i>
          基本信息
        </h2>
        
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              id="username" 
              v-model="profileForm.username" 
              type="text" 
              required
              :disabled="true"
              class="form-input"
            />
            <small class="form-help">用户名不可修改</small>
          </div>
          
          <div class="form-group">
            <label for="display_name">显示名称</label>
            <input 
              id="display_name" 
              v-model="profileForm.display_name" 
              type="text" 
              required
              class="form-input"
              placeholder="请输入显示名称"
            />
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input 
              id="email" 
              v-model="profileForm.email" 
              type="email" 
              class="form-input"
              placeholder="请输入邮箱地址"
            />
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="profileLoading"
            >
              <i v-if="profileLoading" class="fa fa-spinner fa-spin"></i>
              <i v-else class="fa fa-save"></i>
              {{ profileLoading ? '保存中...' : '保存更改' }}
            </button>
          </div>
        </form>
      </div>

      <div id="favorites" class="profile-section">
        <h2 class="section-title">
          <i class="fa fa-heart"></i>
          我的收藏
        </h2>
        <div class="favorites-list">
          <div v-if="favLoading" class="loading"><i class="fa fa-spinner fa-spin"></i> 加载中…</div>
          <div v-else-if="favorites.length === 0" class="empty">暂无收藏</div>
          <ul v-else>
            <li v-for="p in favorites" :key="p.id" class="favorite-item">
              <div class="title" @click="goToPost(p.id)">{{ p.title || (p.content?.slice(0, 40) + '...') }}</div>
              <div class="meta"><i class="fa fa-user"></i> {{ p.author?.display_name || p.author?.username || '匿名' }} · <i class="fa fa-clock-o"></i> {{ formatDateTime(p.created_at) }}</div>
            </li>
          </ul>
          <div v-if="favPages > 1" class="pagination">
            <button class="btn btn-outline btn-sm" :disabled="favPage<=1" @click="loadFavorites(favPage-1)"><i class="fa fa-chevron-left"></i>上一页</button>
            <span>第 {{ favPage }} / {{ favPages }} 页</span>
            <button class="btn btn-outline btn-sm" :disabled="favPage>=favPages" @click="loadFavorites(favPage+1)">下一页<i class="fa fa-chevron-right"></i></button>
          </div>
        </div>
      </div>

      <div id="password-change" class="profile-section">
        <h2 class="section-title">
          <i class="fa fa-lock"></i>
          修改密码
        </h2>
        
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label for="old_password">当前密码</label>
            <input 
              id="old_password" 
              v-model="passwordForm.old_password" 
              type="password" 
              required
              class="form-input"
              placeholder="请输入当前密码"
            />
          </div>
          
          <div class="form-group">
            <label for="new_password">新密码</label>
            <input 
              id="new_password" 
              v-model="passwordForm.new_password" 
              type="password" 
              required
              class="form-input"
              placeholder="请输入新密码"
              minlength="6"
            />
            <small class="form-help">密码长度至少6位</small>
          </div>
          
          <div class="form-group">
            <label for="confirm_password">确认新密码</label>
            <input 
              id="confirm_password" 
              v-model="passwordForm.confirm_password" 
              type="password" 
              required
              class="form-input"
              placeholder="请再次输入新密码"
            />
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="passwordLoading || !isPasswordValid"
            >
              <i v-if="passwordLoading" class="fa fa-spinner fa-spin"></i>
              <i v-else class="fa fa-key"></i>
              {{ passwordLoading ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 公开设置 -->
      <div v-if="user?.user_type === 'admin'" id="privacy-settings" class="profile-section">
        <h2 class="section-title">
          <i class="fa fa-globe"></i>
          公开设置
        </h2>
        
        <div class="privacy-settings">
          <div class="privacy-item">
            <div class="privacy-info">
              <h4>乐队信息</h4>
              <p>允许其他用户查看您管理的乐队信息</p>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="privacySettings.bands_public"
                @change="updatePrivacySettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          
          <div class="privacy-item">
            <div class="privacy-info">
              <h4>成员信息</h4>
              <p>允许其他用户查看您管理的成员信息</p>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="privacySettings.members_public"
                @change="updatePrivacySettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          
          <div class="privacy-item">
            <div class="privacy-info">
              <h4>活动信息</h4>
              <p>允许其他用户查看您管理的活动信息</p>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="privacySettings.events_public"
                @change="updatePrivacySettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
        
        <div class="privacy-note">
          <i class="fa fa-info-circle"></i>
          <span>公开设置将影响其他用户在公开展示页面中能看到的内容</span>
        </div>
      </div>

      
    </div>

    <div v-if="successMessage" class="success-message">
      <i class="fa fa-check-circle"></i>
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="error-message">
      <i class="fa fa-exclamation-circle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'
import type { User } from '@/api/authService'
import { CommunityService, type CommunityPost } from '@/api/communityService'

const authStore = useAuthStore()
const router = useRouter()

const user = ref<User | null>(null)
const profileLoading = ref(false)
const passwordLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const profileForm = reactive({
  username: '',
  display_name: '',
  email: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const privacySettings = reactive({
  bands_public: false,
  members_public: false,
  events_public: false
})

// 收藏（点赞）
const favorites = ref<CommunityPost[]>([])
const favPage = ref(1)
const favPages = ref(1)
const favLoading = ref(false)

const isPasswordValid = computed(() => {
  return passwordForm.new_password.length >= 6 && 
         passwordForm.new_password === passwordForm.confirm_password
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}
const formatDateTime = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const initUserData = () => {
  user.value = authStore.user
  if (user.value) {
    profileForm.username = user.value.username
    profileForm.display_name = user.value.display_name
    profileForm.email = user.value.email || ''
    
    // 初始化公开设置
    privacySettings.bands_public = user.value.bands_public || false
    privacySettings.members_public = user.value.members_public || false
    privacySettings.events_public = user.value.events_public || false
  }
}

const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    showError('请选择图片文件')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    showError('图片大小不能超过5MB')
    return
  }
  
  try {
    await authStore.uploadAvatar(file)
    user.value = authStore.user
    showSuccess('头像上传成功')
  } catch (error: any) {
    showError(error.error || '头像上传失败')
  }
}

const updateProfile = async () => {
  try {
    profileLoading.value = true
    clearMessages()
    
    const updateData = {
      display_name: profileForm.display_name,
      email: profileForm.email
    }
    
    await authStore.updateProfile(updateData)
    user.value = authStore.user
    showSuccess('个人资料更新成功')
  } catch (error: any) {
    showError(error.error || '更新失败')
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  if (!isPasswordValid.value) {
    showError('请检查密码输入')
    return
  }
  
  try {
    passwordLoading.value = true
    clearMessages()
    
    await authStore.changePassword(
      passwordForm.old_password,
      passwordForm.new_password
    )
    
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    
    showSuccess('密码修改成功')
  } catch (error: any) {
    showError(error.error || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

const showSuccess = (message: string) => {
  successMessage.value = message
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const showError = (message: string) => {
  errorMessage.value = message
  setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
}

const clearMessages = () => {
  successMessage.value = ''
  errorMessage.value = ''
}

const updatePrivacySettings = async () => {
  try {
    await authStore.updateProfile({
      bands_public: privacySettings.bands_public,
      members_public: privacySettings.members_public,
      events_public: privacySettings.events_public
    })
    showSuccess('公开设置更新成功')
  } catch (error: any) {
    showError(error.error || '公开设置更新失败')
  }
}

const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    })
  }
}

const loadFavorites = async (page: number = 1) => {
  try {
    favLoading.value = true
    const res = await CommunityService.listMyLikedPosts({ page, page_size: 10 })
    favorites.value = res.items
    favPage.value = res.page
    favPages.value = res.pages
  } finally {
    favLoading.value = false
  }
}

const goToPost = (postId: number) => {
  // 暂用跳转到社区页并依靠 UI 展开（后续可做单帖路由）
  router.push('/community')
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/auth/login')
    return
  }
  
  initUserData()
  loadFavorites(1)
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.profile-view {
  max-width: 800px;
  margin: 0 auto;
  margin-top: 4rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  
  .page-title {
    font-size: 2.5rem;
    color: $primary;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    
    i {
      font-size: 2rem;
    }
  }
  
  .page-subtitle {
    color: $gray-400;
    font-size: 1.1rem;
  }
}

.profile-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: rgba($darkgray, 0.5);
  border-radius: $border-radius-lg;
  border: 1px solid rgba($primary, 0.2);
  
  .avatar-container {
    position: relative;
    width: 120px;
    height: 120px;
    
    .current-avatar,
    .avatar-placeholder {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
    }
    
    .avatar-placeholder {
      background: rgba($primary, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      color: $primary;
      font-size: 3rem;
    }
    
    .avatar-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(0, 0, 0, 0.7);
      padding: 0.5rem;
      border-radius: 0 0 50% 50%;
      opacity: 0;
      transition: opacity $transition-normal ease;
      
      .avatar-upload-btn {
        color: $white;
        cursor: pointer;
        font-size: 0.875rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        
        &:hover {
          color: $primary;
        }
      }
    }
    
    &:hover .avatar-overlay {
      opacity: 1;
    }
  }
  
  .avatar-info {
    flex: 1;
    
    h3 {
      color: $white;
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: $gray-300;
      margin-bottom: 0.25rem;
      
      &.join-date {
        color: $gray-400;
        font-size: 0.875rem;
      }
    }
    
    .quick-nav-buttons {
      display: flex;
      gap: 0.75rem;
      margin-top: 1.5rem;
      flex-wrap: wrap;
      
      .quick-nav-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba($primary, 0.1);
        border: 1px solid rgba($primary, 0.3);
        border-radius: $border-radius-md;
        color: $primary;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba($primary, 0.2);
          border-color: rgba($primary, 0.5);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba($primary, 0.2);
        }
        
        &:active {
          transform: translateY(0);
        }
        
        i {
          font-size: 0.8rem;
        }
      }
    }
  }
}

.profile-section {
  background: rgba($darkgray, 0.5);
  border-radius: $border-radius-lg;
  padding: 2rem;
  border: 1px solid rgba($primary, 0.2);
  
  .section-title {
    color: $primary;
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    
    i {
      font-size: 1.25rem;
    }
  }
}

.favorites-list {
  .favorite-item { padding: .5rem 0; border-bottom: 1px dashed rgba($primary,.2); }
  .favorite-item .title { color: $white; cursor: pointer; }
  .favorite-item .title:hover { color: $primary; }
  .favorite-item .meta { color: $gray-400; font-size: .9rem; margin-top: .2rem; display:flex; align-items:center; gap:.35rem; }
  .loading { color:$gray-300; }
  .empty { color:$gray-400; }
  .pagination { display:flex; align-items:center; gap:.75rem; margin-top:.75rem; }
}

.profile-form,
.password-form {
  .form-group {
    margin-bottom: 1.5rem;
    
    label {
      display: block;
      color: $white;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
    
    .form-input {
      width: 100%;
      padding: 0.75rem 1rem;
      background: rgba($lightgray, 0.1);
      border: 1px solid rgba($primary, 0.3);
      border-radius: $border-radius-md;
      color: $white;
      font-size: 1rem;
      transition: all $transition-normal ease;
      
      &:focus {
        outline: none;
        border-color: $primary;
        background: rgba($lightgray, 0.2);
      }
      
      &:disabled {
        background: rgba($gray-600, 0.3);
        color: $gray-400;
        cursor: not-allowed;
      }
      
      &::placeholder {
        color: $gray-500;
      }
    }
    
    .form-help {
      display: block;
      color: $gray-400;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  }
  
  .form-actions {
    margin-top: 2rem;
    
    .btn {
      padding: 0.75rem 2rem;
      font-size: 1rem;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
  }
}

.privacy-settings {
  .privacy-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
    border-bottom: 1px solid rgba($primary, 0.1);
    
    &:last-child {
      border-bottom: none;
    }
    
    .privacy-info {
      flex: 1;
      
      h4 {
        color: $white;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
      }
      
      p {
        color: $gray-400;
        font-size: 0.875rem;
        margin: 0;
      }
    }
  }
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 3rem;
  height: 1.5rem;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
    
    &:checked + .toggle-slider {
      background-color: $primary;
      
      &:before {
        transform: translateX(1.5rem);
      }
    }
    
    &:focus + .toggle-slider {
      box-shadow: 0 0 1px $primary;
    }
  }
  
  .toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba($gray-600, 0.5);
    transition: 0.3s;
    border-radius: 1.5rem;
    
    &:before {
      position: absolute;
      content: "";
      height: 1.25rem;
      width: 1.25rem;
      left: 0.125rem;
      bottom: 0.125rem;
      background-color: white;
      transition: 0.3s;
      border-radius: 50%;
    }
  }
}

.privacy-note {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba($primary, 0.1);
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: $gray-300;
  font-size: 0.875rem;
  
  i {
    color: $primary;
    font-size: 1rem;
  }
}

.success-message,
.error-message {
  position: fixed;
  top: 5rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: $border-radius-md;
  color: $white;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 10000;
  animation: slideInRight 0.3s ease;
  
  &.success-message {
    background: #10b981;
  }
  
  &.error-message {
    background: #ef4444;
  }
  
  i {
    font-size: 1.25rem;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .profile-view {
    padding: 1rem;
    margin-top: 4rem;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
    
    .avatar-container {
      width: 100px;
      height: 100px;
    }
    
    .avatar-info {
      .quick-nav-buttons {
        justify-content: center;
        gap: 0.5rem;
        
        .quick-nav-btn {
          padding: 0.4rem 0.8rem;
          font-size: 0.8rem;
          
          i {
            font-size: 0.7rem;
          }
        }
      }
    }
  }
  
  .page-title {
    font-size: 2rem !important;
    
    i {
      font-size: 1.5rem !important;
    }
  }
}
</style>

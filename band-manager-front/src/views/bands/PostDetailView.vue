<template>
  <div class="post-detail-view">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <i class="fa fa-arrow-left"></i> 返回
      </button>
      <h1 class="gradient-text">帖子详情</h1>
    </div>

    <div class="post-detail-container" v-if="post">
      <!-- 主帖内容 -->
      <article class="main-post">
        <div class="post-header">
          <div class="author-info">
            <img v-if="post.author.avatar_url" :src="post.author.avatar_url" :alt="post.author.username" class="avatar" />
            <div v-else class="avatar-placeholder">
              <i class="fa fa-user"></i>
            </div>
            <div class="author-details">
              <h3 class="author-name">{{ post.author.display_name || post.author.username }}</h3>
              <span class="author-username">@{{ post.author.username }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
          <div class="post-actions" v-if="canDeletePost">
            <button class="btn btn-danger btn-sm" @click="deletePost">
              <i class="fa fa-trash"></i> 删除
            </button>
          </div>
        </div>

        <div class="post-content">
          <div v-if="post.content" class="content-text" v-html="renderedContent"></div>

          <!-- 图片展示 -->
          <div v-if="post.image_urls && post.image_urls.length" class="images-grid">
            <div 
              v-for="(url, idx) in post.image_urls" 
              :key="idx" 
              class="image-item"
              :class="{ 'single': post.image_urls.length === 1 }"
              @click="openImageViewer(url, idx)"
            >
              <img :src="url" :alt="`图片 ${idx + 1}`" />
            </div>
          </div>

          <!-- 链接展示 -->
          <div v-if="post.link_urls && post.link_urls.length" class="links-list">
            <a 
              v-for="(url, idx) in post.link_urls" 
              :key="idx" 
              :href="url" 
              target="_blank" 
              class="link-item"
            >
              <i class="fa fa-external-link-alt"></i>
              {{ url }}
            </a>
          </div>

          <!-- 标签 -->
          <div v-if="post.tags && post.tags.length" class="tags-list">
            <span v-for="tag in post.tags" :key="tag.id" class="tag">
              #{{ tag.name }}
            </span>
          </div>
        </div>

        <div class="post-footer">
          <div class="stats">
            <button 
              class="stat-btn like-btn" 
              :class="{ liked: likedPostIds.has(post.id) }"
              @click="toggleLike('post', post.id)"
            >
              <i class="fa fa-heart" :class="likedPostIds.has(post.id) ? 'fa-solid' : 'fa-regular'"></i>
              {{ post.like_count || 0 }}
            </button>
            <span class="stat-item">
              <i class="fa fa-comment"></i>
              {{ post.comment_count || 0 }}
            </span>
          </div>
          <button class="btn btn-outline btn-sm" @click="reportContent('post', post.id)">
            <i class="fa fa-flag"></i> 举报
          </button>
        </div>
      </article>

      <!-- 评论区 -->
      <section class="comments-section">
        <h3 class="section-title">
          <i class="fa fa-comments"></i>
          评论 ({{ comments.length }})
        </h3>

        <!-- 发表评论 -->
        <div v-if="isAuthenticated" class="comment-composer">
          <textarea
            v-model="newComment"
            placeholder="发表你的看法..."
            class="comment-input"
            rows="3"
          ></textarea>
          <div class="comment-actions">
            <button
              class="btn btn-primary"
              :disabled="!newComment.trim() || submittingComment"
              @click="submitComment"
            >
              <i v-if="submittingComment" class="fa fa-spinner fa-spin"></i>
              {{ submittingComment ? '发布中...' : '发布评论' }}
            </button>
          </div>
        </div>
        <div v-else class="login-prompt">
          <p>登录后即可评论</p>
          <router-link to="/auth/login" class="btn btn-primary btn-sm">去登录</router-link>
        </div>

        <!-- 评论列表 -->
        <div class="comments-list">
          <div
            v-for="comment in comments"
            :key="comment.id"
            class="comment-item"
            :class="{ highlighted: highlightedCommentId === comment.id }"
          >
            <div class="comment-header">
              <div class="author-info">
                <img v-if="comment.author.avatar_url" :src="comment.author.avatar_url" :alt="comment.author.username" class="avatar" />
                <div v-else class="avatar-placeholder">
                  <i class="fa fa-user"></i>
                </div>
                <div class="author-details">
                  <span class="author-name">{{ comment.author.display_name || comment.author.username }}</span>
                  <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                </div>
              </div>
              <div class="comment-actions" v-if="canDeleteComment(comment)">
                <button class="btn btn-danger btn-sm" @click="deleteComment(comment.id)">
                  <i class="fa fa-trash"></i>
                </button>
              </div>
            </div>

            <div class="comment-content" v-html="renderMarkdown(comment.content)"></div>

            <div class="comment-footer">
              <button 
                class="stat-btn like-btn" 
                :class="{ liked: likedCommentIds.has(comment.id) }"
                @click="toggleLike('comment', comment.id)"
              >
                <i class="fa fa-heart" :class="likedCommentIds.has(comment.id) ? 'fa-solid' : 'fa-regular'"></i>
                {{ comment.like_count || 0 }}
              </button>
              <button class="btn btn-outline btn-sm" @click="reportContent('comment', comment.id)">
                <i class="fa fa-flag"></i> 举报
              </button>
            </div>
          </div>
        </div>

        <!-- 加载更多评论 -->
        <div v-if="hasMoreComments" class="load-more-section">
          <button class="btn btn-outline" @click="loadMoreComments" :disabled="loadingComments">
            <i v-if="loadingComments" class="fa fa-spinner fa-spin"></i>
            {{ loadingComments ? '加载中...' : '加载更多评论' }}
          </button>
        </div>
      </section>
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <i class="fa fa-spinner fa-spin"></i>
      <span>加载中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <i class="fa fa-exclamation-triangle"></i>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="loadPost">重试</button>
    </div>

    <!-- 图片查看器模态框 -->
    <div v-if="imageViewerVisible" class="image-viewer" @click="closeImageViewer">
      <div class="image-viewer-content">
        <button class="close-btn" @click="closeImageViewer">
          <i class="fa fa-times"></i>
        </button>
        <img :src="currentImageUrl" alt="查看图片" />
        <div v-if="post?.image_urls && post.image_urls.length > 1" class="image-nav">
          <button class="nav-btn prev" @click.stop="prevImage" :disabled="currentImageIndex === 0">
            <i class="fa fa-chevron-left"></i>
          </button>
          <span class="image-counter">{{ currentImageIndex + 1 }} / {{ post.image_urls.length }}</span>
          <button class="nav-btn next" @click.stop="nextImage" :disabled="currentImageIndex === post.image_urls.length - 1">
            <i class="fa fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { CommunityService } from '@/api/communityService'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const newComment = ref('')
const submittingComment = ref(false)
const loadingComments = ref(false)
const hasMoreComments = ref(false)
const commentsPage = ref(1)
const likedPostIds = ref(new Set())
const likedCommentIds = ref(new Set())
const highlightedCommentId = ref(null)

// 图片查看器
const imageViewerVisible = ref(false)
const currentImageUrl = ref('')
const currentImageIndex = ref(0)

// 计算属性
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)
const isSuperAdmin = computed(() => authStore.isSuperAdmin)

const canDeletePost = computed(() => {
  if (!post.value || !authStore.user) return false
  return isSuperAdmin.value || post.value.author_id === authStore.user.id
})

const canDeleteComment = computed(() => (comment) => {
  if (!authStore.user) return false
  return isSuperAdmin.value || comment.author_id === authStore.user.id
})

const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  return renderMarkdown(post.value.content)
})

// 方法
const renderMarkdown = (text) => {
  if (!text) return ''
  return marked(text)
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  
  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  if (diff < 7 * day) return `${Math.floor(diff / day)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const loadPost = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const postId = parseInt(route.params.id as string)
    const response = await CommunityService.getPost(postId)
    post.value = response
    
    // 初始化点赞状态
    if (response.liked_by_me) {
      likedPostIds.value.add(response.id)
    }
    
    // 加载评论
    await loadComments()
    
  } catch (err) {
    error.value = err.error || '加载帖子失败'
  } finally {
    loading.value = false
  }
}

const loadComments = async (page = 1) => {
  try {
    loadingComments.value = page > 1
    
    const postId = parseInt(route.params.id as string)
    const response = await CommunityService.listComments({ post_id: postId, page, page_size: 20 })
    
    if (page === 1) {
      comments.value = response.items
      commentsPage.value = 1
    } else {
      comments.value.push(...response.items)
    }
    
    hasMoreComments.value = response.page < response.pages
    commentsPage.value = response.page
    
    // 初始化评论点赞状态
    response.items.forEach(comment => {
      if (comment.liked_by_me) {
        likedCommentIds.value.add(comment.id)
      }
    })
    
    // 检查是否需要高亮特定评论
    const highlight = route.query.highlight as string
    if (highlight && highlight.startsWith('comment_')) {
      const commentId = parseInt(highlight.replace('comment_', ''))
      highlightedCommentId.value = commentId
      
      // 滚动到高亮的评论
      setTimeout(() => {
        const element = document.querySelector(`.comment-item.highlighted`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 100)
    }
    
  } catch (err) {
    console.error('加载评论失败:', err)
  } finally {
    loadingComments.value = false
  }
}

const loadMoreComments = () => {
  if (hasMoreComments.value && !loadingComments.value) {
    loadComments(commentsPage.value + 1)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    submittingComment.value = true
    
    const postId = parseInt(route.params.id as string)
    await CommunityService.createComment({
      post_id: postId,
      content: newComment.value
    })
    
    newComment.value = ''
    // 重新加载评论
    await loadComments(1)
    
  } catch (err) {
    alert(err.error || '发布评论失败')
  } finally {
    submittingComment.value = false
  }
}

const toggleLike = async (type, id) => {
  if (!isAuthenticated.value) {
    alert('请先登录')
    return
  }
  
  try {
    if (type === 'post') {
      await CommunityService.likePost(id)
      
      // 更新本地状态
      if (likedPostIds.value.has(id)) {
        likedPostIds.value.delete(id)
        post.value.like_count = Math.max(0, (post.value.like_count || 0) - 1)
      } else {
        likedPostIds.value.add(id)
        post.value.like_count = (post.value.like_count || 0) + 1
      }
    } else {
      await CommunityService.likeComment(id)
      
      // 更新本地状态
      const comment = comments.value.find(c => c.id === id)
      if (comment) {
        if (likedCommentIds.value.has(id)) {
          likedCommentIds.value.delete(id)
          comment.like_count = Math.max(0, (comment.like_count || 0) - 1)
        } else {
          likedCommentIds.value.add(id)
          comment.like_count = (comment.like_count || 0) + 1
        }
      }
    }
  } catch (err) {
    alert(err.error || '操作失败')
  }
}

const deletePost = async () => {
  if (!confirm('确定删除这个帖子吗？')) return
  
  try {
    await CommunityService.deletePost(post.value.id)
    router.push('/community')
  } catch (err) {
    alert(err.error || '删除失败')
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('确定删除这个评论吗？')) return
  
  try {
    await CommunityService.deleteComment(commentId)
    // 重新加载评论
    await loadComments(1)
  } catch (err) {
    alert(err.error || '删除失败')
  }
}

const reportContent = async (type, id) => {
  const reason = prompt(`举报这个${type === 'post' ? '帖子' : '评论'}的原因：`)
  if (!reason) return
  
  try {
    await CommunityService.reportContent({ target_type: type, target_id: id, reason })
    alert('举报成功，感谢您的反馈')
  } catch (err) {
    alert(err.error || '举报失败')
  }
}

const goBack = () => {
  router.back()
}

// 图片查看器相关方法
const openImageViewer = (url, index) => {
  currentImageUrl.value = url
  currentImageIndex.value = index
  imageViewerVisible.value = true
  document.body.style.overflow = 'hidden'
}

const closeImageViewer = () => {
  imageViewerVisible.value = false
  document.body.style.overflow = ''
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    currentImageUrl.value = post.value.image_urls[currentImageIndex.value]
  }
}

const nextImage = () => {
  if (currentImageIndex.value < post.value.image_urls.length - 1) {
    currentImageIndex.value++
    currentImageUrl.value = post.value.image_urls[currentImageIndex.value]
  }
}

// 生命周期
onMounted(() => {
  loadPost()
})

// 监听路由变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadPost()
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.post-detail-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  
  .back-btn {
    background: rgba($primary, 0.1);
    border: 1px solid rgba($primary, 0.3);
    color: $primary;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba($primary, 0.2);
    }
  }
  
  h1 {
    margin: 0;
  }
}

.post-detail-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.main-post {
  background: rgba($darkgray, 0.6);
  border: 1px solid rgba($primary, 0.2);
  border-radius: $border-radius-lg;
  padding: 1.5rem;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.author-info {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  
  .avatar, .avatar-placeholder {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    overflow: hidden;
    background: rgba($lightgray, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    i {
      color: $gray-400;
      font-size: 1.5rem;
    }
  }
  
  .author-details {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    
    .author-name {
      font-weight: 600;
      color: $white;
      margin: 0;
    }
    
    .author-username {
      color: $gray-400;
      font-size: 0.9rem;
    }
    
    .post-time {
      color: $gray-500;
      font-size: 0.85rem;
    }
  }
}

.post-content {
  margin-bottom: 1rem;
  
  .content-text {
    color: $gray-200;
    line-height: 1.6;
    margin-bottom: 1rem;
    
    // Markdown样式
    :deep(h1), :deep(h2), :deep(h3) {
      color: $primary;
      margin: 1rem 0 0.5rem 0;
    }
    
    :deep(p) {
      margin: 0.5rem 0;
    }
    
    :deep(code) {
      background: rgba($lightgray, 0.2);
      padding: 0.2rem 0.4rem;
      border-radius: 0.3rem;
      font-family: 'Courier New', monospace;
    }
    
    :deep(pre) {
      background: rgba($lightgray, 0.1);
      padding: 1rem;
      border-radius: 0.5rem;
      overflow-x: auto;
    }
    
    :deep(blockquote) {
      border-left: 3px solid $primary;
      padding-left: 1rem;
      margin: 1rem 0;
      color: $gray-300;
    }
  }
}

.images-grid {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
  
  .image-item {
    border-radius: 0.5rem;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.02);
    }
    
    &.single {
      max-width: 500px;
    }
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  // 网格布局逻辑
  &:has(.image-item:nth-child(1):nth-last-child(1)) {
    grid-template-columns: 1fr;
  }
  
  &:has(.image-item:nth-child(2):nth-last-child(1)) {
    grid-template-columns: 1fr 1fr;
  }
  
  &:has(.image-item:nth-child(3):nth-last-child(1)) {
    grid-template-columns: 1fr 1fr 1fr;
  }
  
  &:has(.image-item:nth-child(4):nth-last-child(1)) {
    grid-template-columns: 1fr 1fr;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  &:has(.image-item:nth-child(5)) {
    grid-template-columns: repeat(3, 1fr);
    
    .image-item {
      aspect-ratio: 1;
    }
  }
}

.links-list {
  margin-bottom: 1rem;
  
  .link-item {
    display: block;
    color: $primary;
    text-decoration: none;
    padding: 0.5rem;
    background: rgba($primary, 0.1);
    border-radius: 0.4rem;
    margin-bottom: 0.5rem;
    transition: background 0.2s ease;
    
    &:hover {
      background: rgba($primary, 0.2);
    }
    
    i {
      margin-right: 0.5rem;
    }
  }
}

.tags-list {
  margin-bottom: 1rem;
  
  .tag {
    display: inline-block;
    background: rgba($primary, 0.2);
    color: $primary;
    padding: 0.25rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.85rem;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid rgba($primary, 0.2);
}

.stats {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stat-btn, .stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: $gray-400;
  font-size: 0.9rem;
}

.stat-btn {
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  
  &:hover {
    color: $gray-300;
  }
  
  &.like-btn.liked {
    color: #ef4444;
  }
}

.comments-section {
  background: rgba($darkgray, 0.4);
  border: 1px solid rgba($primary, 0.2);
  border-radius: $border-radius-lg;
  padding: 1.5rem;
}

.section-title {
  color: $primary;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comment-composer {
  margin-bottom: 2rem;
  
  .comment-input {
    width: 100%;
    background: rgba($lightgray, 0.1);
    border: 1px solid rgba($primary, 0.3);
    color: $white;
    border-radius: 0.5rem;
    padding: 0.75rem;
    resize: vertical;
    min-height: 80px;
    
    &::placeholder {
      color: $gray-400;
    }
  }
  
  .comment-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.75rem;
  }
}

.login-prompt {
  text-align: center;
  padding: 2rem;
  color: $gray-400;
  
  p {
    margin-bottom: 1rem;
  }
}

.comments-list {
  .comment-item {
    background: rgba($lightgray, 0.05);
    border: 1px solid rgba($primary, 0.1);
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    
    &.highlighted {
      border-color: $primary;
      background: rgba($primary, 0.1);
    }
  }
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  
  .author-info {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    
    .avatar, .avatar-placeholder {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      overflow: hidden;
      background: rgba($lightgray, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      i {
        color: $gray-400;
        font-size: 1rem;
      }
    }
    
    .author-details {
      display: flex;
      flex-direction: column;
      gap: 0.1rem;
      
      .author-name {
        font-weight: 500;
        color: $white;
      }
      
      .comment-time {
        color: $gray-500;
        font-size: 0.8rem;
      }
    }
  }
}

.comment-content {
  color: $gray-200;
  line-height: 1.5;
  margin-bottom: 0.75rem;
  
  :deep(p) {
    margin: 0.25rem 0;
  }
  
  :deep(code) {
    background: rgba($lightgray, 0.2);
    padding: 0.1rem 0.3rem;
    border-radius: 0.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
  }
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
}

.load-more-section {
  text-align: center;
  margin-top: 1.5rem;
}

.loading-container, .error-container {
  text-align: center;
  padding: 4rem 2rem;
  color: $gray-400;
  
  i {
    font-size: 2rem;
    margin-bottom: 1rem;
    display: block;
  }
  
  h3 {
    color: $white;
    margin-bottom: 0.5rem;
  }
}

.image-viewer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  
  .image-viewer-content {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    
    img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
    
    .close-btn {
      position: absolute;
      top: -40px;
      right: 0;
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
      }
    }
    
    .image-nav {
      position: absolute;
      bottom: -50px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 1rem;
      color: white;
      
      .nav-btn {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.3);
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
      
      .image-counter {
        font-size: 0.9rem;
        min-width: 80px;
        text-align: center;
      }
    }
  }
}

.btn {
  cursor: pointer;
  border-radius: 0.5rem;
  border: 1px solid rgba($primary, 0.4);
  background: transparent;
  color: $primary;
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  &:hover:not(:disabled) {
    background: rgba($primary, 0.1);
  }
  
  &.btn-primary {
    background: $primary;
    color: $white;
    border-color: $primary;
    
    &:hover:not(:disabled) {
      background: #e6246b;
    }
  }
  
  &.btn-danger {
    border-color: rgba(#ef4444, 0.5);
    color: #ef4444;
    
    &:hover:not(:disabled) {
      background: rgba(#ef4444, 0.1);
    }
  }
  
  &.btn-outline {
    background: transparent;
  }
  
  &.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.85rem;
  }
}

.gradient-text {
  background: linear-gradient(135deg, $primary 0%, #ff5a88 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .post-detail-view {
    padding: 1rem;
  }
  
  .images-grid {
    &:has(.image-item:nth-child(3):nth-last-child(1)) {
      grid-template-columns: 1fr 1fr;
      
      .image-item:first-child {
        grid-column: 1 / -1;
      }
    }
    
    &:has(.image-item:nth-child(5)) {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  .post-header, .comment-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>

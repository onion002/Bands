<template>
  <div class="community-view">
    <div class="page-header" ref="pageHeaderRef" :class="{ pushed: searchExpanded }">
      <h1>
        <span class="gradient-text">音乐社区</span>
      </h1>
      <p class="page-subtitle">发布音乐动态、分享灵感，与乐友交流</p>
    </div>

    <div class="community-layout">
      <section class="composer-section composer-fixed">
        <div class="fixed-inner">
          <div class="composer-card">
          <div v-if="!isAuthenticated" class="composer-overlay">
            <p>登录后即可发布帖子与评论</p>
            <router-link to="/auth/login" class="btn btn-primary btn-sm">去登录</router-link>
          </div>

          <textarea v-model="composer.content" class="composer-input" :placeholder="isAuthenticated ? '分享你的音乐想法、作品或问题…' : '请登录后发布'" :disabled="!isAuthenticated || submitting"></textarea>

          <div class="composer-actions">
            <div class="left">
              <label class="icon-btn" title="上传图片">
                <input type="file" multiple accept="image/*" @change="onPickImages" :disabled="!isAuthenticated || submitting" hidden />
                <i class="fa fa-image"></i>
              </label>
              <button class="icon-btn" title="添加链接" @click="addLink" :disabled="!isAuthenticated || submitting">
                <i class="fa fa-link"></i>
              </button>
              <input v-model="tagInput" @keydown.enter.prevent="addTag" class="tag-input" placeholder="# 添加标签" :disabled="!isAuthenticated || submitting" />
              <button class="btn btn-outline btn-sm" @click="addTag" :disabled="!isAuthenticated || submitting || !tagInput.trim()" type="button">
                <i class="fa fa-plus"></i>
              </button>
            </div>
            <div class="right">
              <button class="btn btn-primary" :disabled="!isAuthenticated || submitting || !canSubmit" @click="submitPost">
                <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
                {{ submitting ? '发布中…' : '发布' }}
              </button>
            </div>
          </div>

          <div v-if="composer.previewImages.length" class="image-preview">
            <div v-for="(url, idx) in composer.previewImages" :key="idx" class="image-item">
              <img :src="url" />
              <button class="remove" @click="removeImage(idx)"><i class="fa fa-times"></i></button>
            </div>
          </div>

          <div v-if="composer.link_urls.length" class="links-preview">
            <div v-for="(url, idx) in composer.link_urls" :key="idx" class="link-item">
              <i class="fa fa-link"></i>
              <a :href="url" target="_blank">{{ url }}</a>
              <button class="remove" @click="removeLink(idx)"><i class="fa fa-times"></i></button>
            </div>
          </div>

          <div v-if="composer.tags.length" class="tags-preview">
            <span v-for="(t, idx) in composer.tags" :key="t + idx" class="tag" @click="removeTag(idx)">#{{ t }}</span>
          </div>
          </div>
        </div>
      </section>

      <section class="feed-section">
        <div class="search-fixed" :class="{ collapsed: !searchExpanded }">
          <div class="fixed-inner">
            <div class="feed-toolbar">
              <div class="search-box">
                <button class="icon-btn search-trigger" @click="toggleSearch" aria-label="展开搜索"><i class="fa" :class="[searchExpanded ? 'fa-times' : 'fa-search']"></i></button>
                <input ref="searchInputRef" v-model="query.search" placeholder="搜索帖子内容或标题" @input="debouncedFetch" @blur="onSearchBlur" />
              </div>
              <div class="sort-tabs" v-show="searchExpanded">
                <button :class="['tab', query.sort === 'latest' && 'active']" @click="changeSort('latest')">最新</button>
                <button :class="['tab', query.sort === 'hot' && 'active']" @click="changeSort('hot')">热度</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading"><i class="fa fa-spinner fa-spin"></i> 加载中…</div>
        <div v-else-if="error" class="error"><i class="fa fa-exclamation-circle"></i> {{ error }}</div>
        <div v-else class="post-list with-fixed">
          <div v-if="posts.length === 0" class="empty">
            <i class="fa fa-inbox"></i>
            暂无帖子
          </div>

          <article v-for="post in posts" :key="post.id" class="post-card">
            <header class="post-header">
              <div class="author">
                <img v-if="post.author?.avatar_url" :src="post.author.avatar_url" class="avatar" />
                <div v-else class="avatar placeholder"><i class="fa fa-user"></i></div>
                <div class="meta">
                  <strong>{{ post.author?.display_name || post.author?.username || '匿名' }}</strong>
                </div>
              </div>
              <div class="tags">
                <span v-for="tag in post.tags" :key="tag.id" class="tag" @click="filterByTag(tag.name)">#{{ tag.name }}</span>
              </div>
            </header>

            <!-- 编辑模式 -->
            <div v-if="editingPostId === post.id" class="edit-mode">
              <div class="edit-form">
                <textarea v-model="editContent" placeholder="编辑帖子内容..." class="edit-textarea"></textarea>
                
                <div class="edit-tags">
                  <label>标签：</label>
                  <div class="tag-input-container">
                    <span v-for="(tag, idx) in editTags" :key="idx" class="edit-tag">
                      #{{ tag }}
                      <button @click="editTags.splice(idx, 1)" class="remove-tag">&times;</button>
                    </span>
                    <input v-model="newTag" @keydown.enter.prevent="addEditTag" placeholder="添加标签" class="tag-input" />
                    <button @click="addEditTag" class="add-tag-btn">+</button>
                  </div>
                </div>
                
                <div class="edit-images">
                  <label>图片：</label>
                  
                  <!-- 现有图片 -->
                  <div v-if="editImages.length > 0" class="current-images">
                    <div class="image-grid">
                      <div v-for="(imageUrl, idx) in editImages" :key="idx" class="edit-image-item">
                        <img :src="imageUrl" :alt="`图片 ${idx + 1}`" />
                        <button @click="removeEditImage(idx)" class="remove-image">&times;</button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 待上传的新图片 -->
                  <div v-if="editImageFiles.length > 0" class="new-images">
                    <div class="image-grid">
                      <div v-for="(file, idx) in editImageFiles" :key="idx" class="edit-image-item">
                        <img :src="createObjectURL(file)" :alt="`新图片 ${idx + 1}`" />
                        <button @click="removeEditImageFile(idx)" class="remove-image">&times;</button>
                        <div class="new-image-badge">新</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 图片上传 -->
                  <div class="image-upload">
                    <input 
                      type="file" 
                      multiple 
                      accept="image/*" 
                      @change="handleEditImageSelect" 
                      class="file-input" 
                      id="edit-image-input"
                    />
                    <label for="edit-image-input" class="upload-btn">
                      <i class="fa fa-plus"></i> 添加图片
                    </label>
                  </div>
                </div>

                <div class="edit-links">
                  <label>链接：</label>
                  <div v-for="(link, idx) in editLinks" :key="idx" class="link-input-container">
                    <input v-model="editLinks[idx]" placeholder="链接URL" class="link-input" />
                    <button @click="editLinks.splice(idx, 1)" class="remove-link">&times;</button>
                  </div>
                  <button @click="editLinks.push('')" class="add-link-btn">+ 添加链接</button>
                </div>
                
                <div class="edit-actions">
                  <button @click="saveEditPost" :disabled="updating || uploading" class="btn btn-primary">
                    <i v-if="updating || uploading" class="fa fa-spinner fa-spin"></i>
                    {{ uploading ? '上传图片中...' : updating ? '保存中...' : '保存' }}
                  </button>
                  <button @click="cancelEditPost" class="btn btn-outline">取消</button>
                </div>
              </div>
            </div>
            
            <!-- 普通显示模式 -->
            <div v-else>
              <div class="post-content" v-html="renderMarkdown(post.content)"></div>

              <div v-if="post.image_urls?.length" class="gallery" :class="getImageDisplayClass(post.image_urls.length)">
                <div 
                  v-for="(url, idx) in post.image_urls" 
                  :key="idx" 
                  class="image-item"
                  @click="openImageViewer(url, idx, post.image_urls)"
                >
                  <img 
                    :src="url" 
                    :alt="`图片 ${idx + 1}`" 
                    loading="lazy"
                    @load="onImageLoad"
                    @error="onImageError"
                  />
                  <div v-if="post.image_urls.length > 9 && idx === 8" class="more-overlay">
                    <span>+{{ post.image_urls.length - 9 }}</span>
                  </div>
                </div>
              </div>

              <div v-if="post.link_urls?.length" class="links">
                <div v-for="(url, idx) in post.link_urls" :key="idx" class="link">
                  <i class="fa fa-link"></i>
                  <a :href="url" target="_blank">{{ url }}</a>
                </div>
              </div>
            </div>

            <footer class="post-actions">
              <div class="actions-left">
                <button class="action like" @click="toggleLikePost(post)" :disabled="liking">
                  <i :class="[isPostLiked(post.id) ? 'fa-solid fa-heart' : 'fa-regular fa-heart']"></i>
                  <span class="count" :class="{ liked: isPostLiked(post.id) }">{{ post.like_count }}</span>
                </button>
                <button class="action" @click="openComments(post)">
                  <i class="fa fa-comment"></i>
                  {{ post.comment_count }}
                </button>
                <router-link :to="`/community/post/${post.id}`" class="action detail">
                  <i class="fa fa-eye"></i> 详情
                </router-link>
                <button class="action" @click="reportTarget('post', post.id)"><i class="fa fa-flag"></i> 举报</button>
                <button v-if="canEditPost(post)" class="action edit" @click="startEditPost(post)"><i class="fa fa-edit"></i> 编辑</button>
                <button v-if="canDeletePost(post)" class="action danger" @click="deletePost(post)"><i class="fa fa-trash"></i> 删除</button>
              </div>
              <div class="post-time">
                {{ formatTime(post.created_at) }}
              </div>
            </footer>

            <!-- 默认显示前3条评论 -->
            <div v-if="getPostComments(post.id).length > 0 && expandedPostId !== post.id" class="default-comments">
              <div class="comment-list">
                <div v-for="c in getPostComments(post.id).slice(0, 3)" :key="c.id" class="comment-item" :class="{ 'pinned-comment': c.is_pinned }">
                  <div class="c-author">
                    <img v-if="c.author?.avatar_url" :src="c.author.avatar_url" class="avatar" />
                    <div v-else class="avatar placeholder"><i class="fa fa-user"></i></div>
                    <div class="meta">
                      <strong>{{ c.author?.display_name || c.author?.username || '匿名' }}</strong>
                    </div>
                    <div class="c-actions">
                      <button class="action like" @click="toggleLikeComment(c)" :disabled="liking"><i :class="[isCommentLiked(c.id) ? 'fa-solid fa-heart' : 'fa-regular fa-heart']"></i> <span class="count" :class="{ liked: isCommentLiked(c.id) }">{{ c.like_count }}</span></button>
                      <button v-if="canPinComment(c)" class="action pin" @click="togglePinComment(c)" :disabled="pinning">
                        <i :class="[c.is_pinned ? 'fa fa-thumbtack' : 'fa fa-thumbtack']"></i> 
                        {{ c.is_pinned ? '取消置顶' : '置顶' }}
                      </button>
                      <button class="action" @click="reportTarget('comment', c.id)"><i class="fa fa-flag"></i> 举报</button>
                    </div>
                  </div>
                  <div class="c-content">
                    <div v-if="c.is_pinned" class="pinned-badge">
                      <i class="fa fa-thumbtack"></i> 置顶
                    </div>
                    <div class="comment-text">{{ c.content }}</div>
                    <div class="comment-time">{{ formatTime(c.created_at) }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 查看更多评论按钮 -->
              <div v-if="getPostComments(post.id).length > 3 || post.comment_count > 3" class="more-comments">
                <button class="btn btn-outline btn-sm" @click="expandComments(post)">
                  查看全部 {{ post.comment_count }} 条评论
                </button>
              </div>
            </div>

            <!-- 展开的评论区（点击查看更多后显示） -->
            <div v-if="expandedPostId === post.id" class="comments">
              <div class="comment-composer" v-if="isAuthenticated">
                <input v-model="commentContent" placeholder="写下你的评论…" @keydown.enter.prevent="submitComment(post)" />
                <button class="btn btn-outline btn-sm" :disabled="!commentContent.trim() || commenting" @click="submitComment(post)">
                  <i v-if="commenting" class="fa fa-spinner fa-spin"></i>
                  发送
                </button>
              </div>
              <div v-else class="comment-hint">登录后可参与评论</div>

              <div v-if="commentsLoading" class="loading small"><i class="fa fa-spinner fa-spin"></i> 加载评论…</div>
              <div v-else>
                <div v-if="comments.length === 0" class="empty small">暂无评论</div>
                <div v-else class="comment-list">
                  <div v-for="c in comments" :key="c.id" class="comment-item" :class="{ 'pinned-comment': c.is_pinned }">
                    <div class="c-author">
                      <img v-if="c.author?.avatar_url" :src="c.author.avatar_url" class="avatar" />
                      <div v-else class="avatar placeholder"><i class="fa fa-user"></i></div>
                      <div class="meta">
                        <strong>{{ c.author?.display_name || c.author?.username || '匿名' }}</strong>
                      </div>
                      <div class="c-actions">
                        <button class="action like" @click="toggleLikeComment(c)" :disabled="liking"><i :class="[isCommentLiked(c.id) ? 'fa-solid fa-heart' : 'fa-regular fa-heart']"></i> <span class="count" :class="{ liked: isCommentLiked(c.id) }">{{ c.like_count }}</span></button>
                        <button v-if="canPinComment(c)" class="action pin" @click="togglePinComment(c)" :disabled="pinning">
                          <i :class="[c.is_pinned ? 'fa fa-thumbtack' : 'fa fa-thumbtack']"></i> 
                          {{ c.is_pinned ? '取消置顶' : '置顶' }}
                        </button>
                        <button class="action" @click="reportTarget('comment', c.id)"><i class="fa fa-flag"></i> 举报</button>
                      </div>
                    </div>
                    <div class="c-content">
                      <div v-if="c.is_pinned" class="pinned-badge">
                        <i class="fa fa-thumbtack"></i> 置顶
                      </div>
                      <div class="comment-text">{{ c.content }}</div>
                      <div class="comment-time">{{ formatTime(c.created_at) }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- 收起评论按钮 -->
                <div class="more-comments">
                  <button class="btn btn-outline btn-sm" @click="collapseComments()">
                    收起评论
                  </button>
                </div>
              </div>
            </div>
          </article>

          <!-- 无限滚动加载指示器 -->
          <div v-if="loadingMore" class="loading-more">
            <i class="fa fa-spinner fa-spin"></i>
            <span>加载更多中...</span>
          </div>
          
          <div v-else-if="hasMore && posts.length > 0" class="load-more-trigger" ref="loadMoreTrigger">
            <div class="load-more-hint">滚动到底部自动加载更多</div>
          </div>
          
          <div v-else-if="posts.length > 0 && !hasMore" class="no-more">
            <span>已加载全部内容</span>
          </div>
        </div>
      </section>
    </div>

    <!-- 图片查看器模态框 -->
    <div v-if="imageViewerVisible" class="image-viewer" @click="closeImageViewer">
      <div class="image-viewer-content">
        <button class="close-btn" @click="closeImageViewer">
          <i class="fa fa-times"></i>
        </button>
        <img :src="currentImageUrl" alt="查看图片" />
        <div v-if="currentImageList.length > 1" class="image-nav">
          <button class="nav-btn prev" @click.stop="prevImage" :disabled="currentImageIndex === 0">
            <i class="fa fa-chevron-left"></i>
          </button>
          <span class="image-counter">{{ currentImageIndex + 1 }} / {{ currentImageList.length }}</span>
          <button class="nav-btn next" @click.stop="nextImage" :disabled="currentImageIndex === currentImageList.length - 1">
            <i class="fa fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { CommunityService, type CommunityPost, type CommunityComment } from '@/api/communityService'
import { marked } from 'marked'
import hljs from 'highlight.js'

const auth = useAuthStore()
const isAuthenticated = computed(() => auth.isAuthenticated)
const isAdmin = computed(() => auth.isAdmin)
const isSuperadmin = computed(() => auth.user?.user_type === 'superadmin')

const loading = ref(false)
const loadingMore = ref(false)
const error = ref('')
const posts = ref<CommunityPost[]>([])
const page = ref(1)
const pages = ref(1)
const total = ref(0)
const hasMore = computed(() => page.value < pages.value)
const loadMoreTrigger = ref<HTMLElement | null>(null)

// 图片查看器
const imageViewerVisible = ref(false)
const currentImageUrl = ref('')
const currentImageIndex = ref(0)
const currentImageList = ref<string[]>([])

const query = reactive({ search: '', sort: 'latest' as 'latest'|'hot', tag: '' })
let debounceTimer: any = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    fetchPosts().then(() => {
      // 重新设置无限滚动观察器
      nextTick(() => {
        cleanupInfiniteScroll()
        setupInfiniteScroll()
      })
    })
  }, 300)
}

// composer
const composer = reactive({ content: '', previewImages: [] as string[], imageFiles: [] as File[], link_urls: [] as string[], tags: [] as string[] })
const tagInput = ref('')
const submitting = ref(false)
const canSubmit = computed(() => composer.content.trim().length > 0)

function onPickImages(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (!files.length) return
  files.forEach(async (file) => {
    try {
      const { url } = await CommunityService.uploadImage(file)
      composer.previewImages.push(url)
    } catch (err) {
      // ignore single failure
    }
  })
  input.value = ''
}

function addLink() {
  const url = prompt('输入链接（例如歌曲/新闻地址）')?.trim()
  if (url) composer.link_urls.push(url)
}

function removeImage(idx: number) { composer.previewImages.splice(idx, 1) }
function removeLink(idx: number) { composer.link_urls.splice(idx, 1) }

function addTag() {
  const t = tagInput.value.replace(/^#/, '').trim()
  if (t && !composer.tags.includes(t)) {
    composer.tags.push(t)
  }
  tagInput.value = ''
}

function removeTag(idx: number) { composer.tags.splice(idx, 1) }

async function submitPost() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    await CommunityService.createPost({ content: composer.content, image_urls: composer.previewImages, link_urls: composer.link_urls, tags: composer.tags })
    composer.content = ''
    composer.previewImages = []
    composer.link_urls = []
    composer.tags = []
    await fetchPosts()
  } catch (err: any) {
    error.value = err?.error || '发布失败'
  } finally {
    submitting.value = false
  }
}

function changeSort(s: 'latest'|'hot') {
  if (query.sort !== s) {
    query.sort = s
    page.value = 1
    fetchPosts()
  }
}

function filterByTag(name: string) {
  query.tag = name
  page.value = 1
  fetchPosts()
}

async function fetchPosts(append = false) {
  try {
    if (append) {
      loadingMore.value = true
    } else {
      loading.value = true
      page.value = 1
    }
    error.value = ''
    
    const res = await CommunityService.listPosts({ 
      page: page.value, 
      page_size: 10, 
      search: query.search || undefined, 
      sort: query.sort, 
      tag: query.tag || undefined 
    })
    
    if (append) {
      // 追加模式：添加到现有列表
      posts.value.push(...res.items)
      // 合并点赞状态
      const newLikedIds = new Set([...likedPostIds.value, ...res.items.filter(p => p.liked_by_me).map(p => p.id)])
      likedPostIds.value = newLikedIds
    } else {
      // 替换模式：重置列表
      posts.value = res.items
      likedPostIds.value = new Set(res.items.filter(p => p.liked_by_me).map(p => p.id))
    }
    
    total.value = res.total
    page.value = res.page
    pages.value = res.pages
    
    // 为每个帖子获取前3条评论
    await Promise.all(res.items.map(async (post) => {
      try {
        const commentsRes = await CommunityService.listComments({ 
          post_id: post.id, 
          page_size: 3 
        })
        postComments.value.set(post.id, commentsRes.items)
      } catch (error) {
        console.warn(`Failed to load comments for post ${post.id}:`, error)
      }
    }))
  } catch (err: any) {
    error.value = err?.error || '加载失败'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多帖子
async function loadMorePosts() {
  if (loadingMore.value || !hasMore.value) return
  page.value += 1
  await fetchPosts(true)
}

// likes local cache
const likedPostIds = ref<Set<number>>(new Set())
const likedCommentIds = ref<Set<number>>(new Set())
const liking = ref(false)

function isPostLiked(id: number) { return likedPostIds.value.has(id) }
function isCommentLiked(id: number) { return likedCommentIds.value.has(id) }

function canDeletePost(post: CommunityPost) {
  // 超级管理员可删全部，普通/管理员只能删自己发的
  if (isSuperadmin.value) return true
  return auth.user?.username && post.author?.username === auth.user.username
}

function canEditPost(post: CommunityPost) {
  // 只有帖子作者可以编辑
  return auth.user?.username && post.author?.username === auth.user.username
}

async function toggleLikePost(post: CommunityPost) {
  try {
    liking.value = true
    const res = await CommunityService.likePost(post.id)
    post.like_count = res.like_count
    if (res.action === 'liked') likedPostIds.value.add(post.id)
    else likedPostIds.value.delete(post.id)
  } finally {
    liking.value = false
  }
}

// comments
const expandedPostId = ref<number | null>(null)
const comments = ref<CommunityComment[]>([])
const commentsLoading = ref(false)
const commentContent = ref('')
const commenting = ref(false)
const pinning = ref(false)
const showAllComments = ref<Set<number>>(new Set()) // 记录哪些帖子显示了全部评论
const postComments = ref<Map<number, CommunityComment[]>>(new Map()) // 存储每个帖子的评论

// 编辑帖子相关状态
const editingPostId = ref<number | null>(null)
const editContent = ref('')
const editTags = ref<string[]>([])
const editLinks = ref<string[]>([])
const editImages = ref<string[]>([])
const editImageFiles = ref<File[]>([])
const newTag = ref('')
const updating = ref(false)
const uploading = ref(false)

// 计算属性：显示的评论（默认显示3条热门评论）
const displayedComments = computed(() => {
  if (expandedPostId.value && showAllComments.value.has(expandedPostId.value)) {
    return comments.value // 显示全部评论
  }
  return comments.value.slice(0, 3) // 只显示前3条热门评论
})

async function openComments(post: CommunityPost) {
  if (expandedPostId.value === post.id) {
    expandedPostId.value = null
    return
  }
  expandedPostId.value = post.id
  showAllComments.value.delete(post.id) // 重置为显示热门评论
  await fetchComments(post)
}

// 判断是否有更多评论
function hasMoreComments(post: CommunityPost): boolean {
  if (!expandedPostId.value || expandedPostId.value !== post.id) return false
  return comments.value.length > 3 && !showAllComments.value.has(post.id)
}

// 加载更多评论
async function loadMoreComments(post: CommunityPost) {
  showAllComments.value.add(post.id)
}

// 获取帖子的评论
function getPostComments(postId: number): CommunityComment[] {
  return postComments.value.get(postId) || []
}

// 展开评论区
async function expandComments(post: CommunityPost) {
  expandedPostId.value = post.id
  await fetchComments(post)
}

// 收起评论区
function collapseComments() {
  expandedPostId.value = null
  comments.value = []
}

// 判断是否可以置顶评论（只有帖子作者可以置顶）
function canPinComment(comment: CommunityComment): boolean {
  const authStore = useAuthStore()
  if (!isAuthenticated.value || !authStore.user) return false
  
  // 找到对应的帖子
  const post = posts.value.find(p => p.id === comment.post_id)
  if (!post) return false
  
  // 只有帖子作者可以置顶评论
  return post.author?.id === authStore.user.id
}

// 切换评论置顶状态
async function togglePinComment(comment: CommunityComment) {
  if (pinning.value) return
  
  try {
    pinning.value = true
    const res = await CommunityService.pinComment(comment.id)
    
    // 更新评论状态
    comment.is_pinned = res.is_pinned
    
    // 更新postComments中的数据
    const currentComments = postComments.value.get(comment.post_id)
    if (currentComments) {
      const commentIndex = currentComments.findIndex(c => c.id === comment.id)
      if (commentIndex !== -1) {
        currentComments[commentIndex].is_pinned = res.is_pinned
        // 重新排序评论（置顶的排在前面）
        currentComments.sort((a, b) => {
          if (a.is_pinned && !b.is_pinned) return -1
          if (!a.is_pinned && b.is_pinned) return 1
          return b.like_count - a.like_count
        })
        postComments.value.set(comment.post_id, [...currentComments])
      }
    }
    
    // 更新展开评论区的数据
    if (expandedPostId.value === comment.post_id) {
      const expandedCommentIndex = comments.value.findIndex(c => c.id === comment.id)
      if (expandedCommentIndex !== -1) {
        comments.value[expandedCommentIndex].is_pinned = res.is_pinned
        // 重新排序评论
        comments.value.sort((a, b) => {
          if (a.is_pinned && !b.is_pinned) return -1
          if (!a.is_pinned && b.is_pinned) return 1
          return b.like_count - a.like_count
        })
      }
    }
    
    // 显示成功消息
    console.log(res.message)
  } catch (err: any) {
    console.error('置顶操作失败:', err)
  } finally {
    pinning.value = false
  }
}

// 开始编辑帖子
function startEditPost(post: CommunityPost) {
  editingPostId.value = post.id
  editContent.value = post.content
  editTags.value = post.tags ? post.tags.map(tag => tag.name) : []
  editLinks.value = post.link_urls || []
  editImages.value = post.image_urls || []
  editImageFiles.value = []
}

// 取消编辑帖子
function cancelEditPost() {
  editingPostId.value = null
  editContent.value = ''
  editTags.value = []
  editLinks.value = []
  editImages.value = []
  editImageFiles.value = []
  newTag.value = ''
}

// 添加编辑标签
function addEditTag() {
  const tag = newTag.value.trim()
  if (tag && !editTags.value.includes(tag)) {
    editTags.value.push(tag)
    newTag.value = ''
  }
}

// 删除编辑图片
function removeEditImage(index: number) {
  editImages.value.splice(index, 1)
}

// 处理图片文件选择
function handleEditImageSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    editImageFiles.value.push(...Array.from(files))
  }
}

// 删除待上传的图片文件
function removeEditImageFile(index: number) {
  editImageFiles.value.splice(index, 1)
}

// 上传编辑图片
async function uploadEditImages() {
  if (editImageFiles.value.length === 0) return []
  
  uploading.value = true
  const uploadPromises = editImageFiles.value.map(file => CommunityService.uploadImage(file))
  
  try {
    const results = await Promise.all(uploadPromises)
    return results.map(result => result.url)
  } catch (error) {
    console.error('图片上传失败:', error)
    throw error
  } finally {
    uploading.value = false
  }
}

// 创建对象URL预览
function createObjectURL(file: File): string {
  return URL.createObjectURL(file)
}

// 图片加载事件处理
function onImageLoad(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.opacity = '1'
  
  // 启动性能监控
  monitorImagePerformance(img)
  
  // 为单张图片应用智能比例检测
  const imageItem = img.closest('.image-item')
  const gallery = img.closest('.gallery')
  
  if (gallery?.classList.contains('images-1') && imageItem) {
    const aspectRatio = img.naturalWidth / img.naturalHeight
    const width = img.naturalWidth
    const height = img.naturalHeight
    
    // 获取图片质量分析
    const analysis = analyzeImageQuality(img)
    
    // 移除所有样式类
    imageItem.classList.remove(
      'fixed-size', 'normal-ratio', 'long-image', 'ultra-long', 
      'panorama', 'square', 'portrait', 'high-quality', 'low-quality'
    )
    
    // 添加质量标识
    imageItem.classList.add(analysis.quality === 'high' ? 'high-quality' : 'low-quality')
    
    // 智能分类逻辑 - 结合质量分析
    if (aspectRatio > 4) {
      // 超长图 (宽高比 > 4:1)
      imageItem.classList.add('ultra-long')
    } else if (aspectRatio > 2.5) {
      // 长图 (宽高比 > 2.5:1)
      imageItem.classList.add('long-image')
    } else if (aspectRatio >= 1.2) {
      // 横图，根据图片质量和尺寸决定显示模式
      if (analysis.quality === 'high' && analysis.size === 'large') {
        // 高质量大图使用等比缩放
        imageItem.classList.add('normal-ratio')
      } else {
        // 普通图片使用固定尺寸
        imageItem.classList.add('fixed-size')
      }
    } else if (aspectRatio >= 0.8) {
      // 方形图片 (宽高比 0.8-1.2:1)
      imageItem.classList.add('square')
    } else if (aspectRatio < 0.6) {
      // 全景图 (宽高比 < 0.6:1)
      imageItem.classList.add('panorama')
    } else {
      // 竖图 (宽高比 < 0.8:1)
      imageItem.classList.add('portrait')
    }
    
    // 根据质量调整显示策略
    const imgElement = imageItem.querySelector('img')
    if (imgElement && analysis.recommendedDisplay) {
      imgElement.style.objectFit = analysis.recommendedDisplay
    }
  }
}

function onImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.opacity = '0.5'
  img.alt = '图片加载失败'
}

// 获取图片显示类名 - 智能布局选择
function getImageDisplayClass(imageCount: number): string {
  const count = Math.min(imageCount, 9)
  
  // 根据图片数量选择最优布局
  if (count === 1) {
    return 'images-1'
  } else if (count === 2) {
    return 'images-2'
  } else if (count === 3) {
    return 'images-3'
  } else if (count === 4) {
    return 'images-4'
  } else if (count >= 5 && count <= 6) {
    return 'images-multi-small'  // 5-6张图片使用紧凑布局
  } else {
    return 'images-multi-grid'   // 7-9张图片使用标准网格
  }
}

// 多图布局优化：根据图片数量和内容智能选择布局
function getOptimalGridLayout(imageCount: number, images?: string[]): string {
  if (imageCount <= 4) {
    return getImageDisplayClass(imageCount)
  }
  
  // 5+张图片时，可以根据具体需求选择布局策略
  // 这里预留接口，future可以根据图片内容（人物、风景等）智能选择
  if (imageCount <= 6) {
    return 'images-multi-small'
  } else {
    return 'images-multi-grid'
  }
}

// 图片质量检测和优化建议
function analyzeImageQuality(img: HTMLImageElement): {
  quality: 'high' | 'medium' | 'low',
  recommendedDisplay: 'contain' | 'cover',
  size: 'large' | 'medium' | 'small'
} {
  const width = img.naturalWidth
  const height = img.naturalHeight
  const pixels = width * height
  
  let quality: 'high' | 'medium' | 'low'
  let size: 'large' | 'medium' | 'small'
  
  // 判断图片质量
  if (pixels > 2000000) { // 2MP+
    quality = 'high'
    size = 'large'
  } else if (pixels > 500000) { // 0.5MP+
    quality = 'medium'
    size = 'medium'
  } else {
    quality = 'low'
    size = 'small'
  }
  
  // 根据质量推荐显示方式
  const recommendedDisplay = quality === 'high' ? 'contain' : 'cover'
  
  return { quality, recommendedDisplay, size }
}

// 添加图片加载性能监控
function monitorImagePerformance(img: HTMLImageElement) {
  const startTime = performance.now()
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const loadTime = performance.now() - startTime
        
        // 记录加载时间（可用于后续优化）
        if (loadTime > 1000) {
          console.warn(`图片加载较慢: ${loadTime}ms`, img.src)
        }
        
        observer.unobserve(img)
      }
    })
  })
  
  observer.observe(img)
}

// 保存编辑帖子
async function saveEditPost() {
  if (!editingPostId.value || updating.value) return
  
  try {
    updating.value = true
    
    // 上传新图片
    let newImageUrls: string[] = []
    if (editImageFiles.value.length > 0) {
      newImageUrls = await uploadEditImages()
    }
    
    // 合并现有图片和新图片
    const allImageUrls = [...editImages.value, ...newImageUrls]
    
    const res = await CommunityService.updatePost(editingPostId.value, {
      content: editContent.value,
      tags: editTags.value,
      link_urls: editLinks.value,
      image_urls: allImageUrls
    })
    
    // 更新帖子列表中的数据
    const postIndex = posts.value.findIndex(p => p.id === editingPostId.value)
    if (postIndex !== -1) {
      posts.value[postIndex] = res.post
    }
    
    // 取消编辑状态
    cancelEditPost()
    
    console.log(res.message)
  } catch (err: any) {
    console.error('更新帖子失败:', err)
  } finally {
    updating.value = false
  }
}

async function fetchComments(post: CommunityPost) {
  try {
    commentsLoading.value = true
    const res = await CommunityService.listComments({ post_id: post.id })
    comments.value = res.items
    likedCommentIds.value = new Set(res.items.filter(c => c.liked_by_me).map(c => c.id))
  } catch (err) {
    // ignore
  } finally {
    commentsLoading.value = false
  }
}

async function submitComment(post: CommunityPost) {
  const text = commentContent.value.trim()
  if (!text) return
  commenting.value = true
  try {
    const res = await CommunityService.createComment({ post_id: post.id, content: text })
    commentContent.value = ''
    post.comment_count = res.comment_count
    await fetchComments(post)
  } finally {
    commenting.value = false
  }
}

async function toggleLikeComment(c: CommunityComment) {
  try {
    liking.value = true
    const res = await CommunityService.likeComment(c.id)
    c.like_count = res.like_count
    if (res.action === 'liked') likedCommentIds.value.add(c.id)
    else likedCommentIds.value.delete(c.id)
  } finally {
    liking.value = false
  }
}

async function deletePost(post: CommunityPost) {
  if (!confirm('确定删除该帖子吗？')) return
  try {
    await CommunityService.deletePost(post.id)
    await fetchPosts()
  } catch (err) {
    // ignore
  }
}

// 图片查看器相关方法
function openImageViewer(url: string, index: number, imageList: string[]) {
  currentImageUrl.value = url
  currentImageIndex.value = index
  currentImageList.value = imageList
  imageViewerVisible.value = true
  document.body.style.overflow = 'hidden'
}

function closeImageViewer() {
  imageViewerVisible.value = false
  document.body.style.overflow = ''
}

function prevImage() {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    currentImageUrl.value = currentImageList.value[currentImageIndex.value]
  }
}

function nextImage() {
  if (currentImageIndex.value < currentImageList.value.length - 1) {
    currentImageIndex.value++
    currentImageUrl.value = currentImageList.value[currentImageIndex.value]
  }
}

async function reportTarget(type: 'post'|'comment', id: number) {
  const reason = prompt('请输入举报理由：')?.trim()
  if (!reason) return
  try {
    await CommunityService.reportContent({ target_type: type, target_id: id, reason })
    alert('举报已提交')
  } catch (err) {
    alert('提交失败')
  }
}

// markdown render
marked.setOptions({})
function renderMarkdown(text: string) { return marked.parse(text || '') as string }

function formatTime(iso: string) {
  try { return new Date(iso).toLocaleString() } catch { return '' }
}

fetchPosts()

// 计算并设置搜索栏相对标题的固定偏移
const pageHeaderRef = ref<HTMLElement | null>(null)
const setHeaderVar = () => {
  const h = pageHeaderRef.value?.offsetHeight || 72
  document.documentElement.style.setProperty('--community-page-header-h', `${h}px`)
}
// Intersection Observer for infinite scroll
let observer: IntersectionObserver | null = null

const setupInfiniteScroll = () => {
  if (!loadMoreTrigger.value) return
  
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && hasMore.value && !loadingMore.value) {
          loadMorePosts()
        }
      })
    },
    {
      root: null,
      rootMargin: '100px',
      threshold: 0.1
    }
  )
  
  observer.observe(loadMoreTrigger.value)
}

const cleanupInfiniteScroll = () => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
}

onMounted(() => {
  setHeaderVar()
  window.addEventListener('resize', setHeaderVar)
  
  // 设置无限滚动
  nextTick(() => {
    setupInfiniteScroll()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', setHeaderVar)
  cleanupInfiniteScroll()
})

// 搜索栏展开/收起
const searchExpanded = ref(false)
const searchInputRef = ref<HTMLInputElement | null>(null)
const toggleSearch = async () => {
  searchExpanded.value = !searchExpanded.value
  if (searchExpanded.value) {
    await nextTick()
    searchInputRef.value?.focus()
  }
}
const onSearchBlur = () => {
  if (!query.search.trim()) {
    searchExpanded.value = false
  }
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.community-view { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
.page-title { display:flex; align-items:center; gap:.75rem; color: $primary; font-size: 2rem; margin: 0; }
.page-header { transition: transform .2s ease; }
.page-header.pushed { transform: translateY(18px); }
.page-header h1{
  margin-bottom:0px;
}
.gradient-text { background: linear-gradient(135deg, $white 0%, rgba($primary, 0.9) 50%, $white 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 0 4px 20px rgba($primary, 0.3); font-weight: 800; letter-spacing: .5px; }
.page-subtitle { color: $gray-400; }

.community-layout { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }

.composer-card { position: relative; background: rgba($darkgray, .6); border: 1px solid rgba($primary, .2); border-radius: $border-radius-lg; padding: 1rem; }
.composer-fixed { position: fixed; left: 0; right: 0; bottom: 8px; z-index: 6; padding: 0 1rem; }
.fixed-inner { max-width: 1068px; margin: 0 auto; }
.composer-fixed .composer-card { background: rgba($darkgray,.95); backdrop-filter: blur(8px); border:1px solid rgba($primary,.25); border-radius: $border-radius-xl; }
.composer-overlay { position:absolute; inset:0; background: rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; gap:1rem; border-radius: $border-radius-lg; z-index:2; }
.composer-input { width: 100%; min-height: 90px; background: rgba($lightgray, .08); border: 1px solid rgba($primary, .3); border-radius: $border-radius-md; color: $white; padding: .75rem; }
.composer-actions { display:flex; align-items:center; justify-content:space-between; margin-top:.5rem; }
.composer-actions .left { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.icon-btn { background: transparent; border: 1px solid rgba($primary,.3); color: $gray-300; padding:.4rem .6rem; border-radius: .5rem; cursor:pointer; }
.icon-btn:hover { color: $primary; border-color: $primary; }
.tag-input { background: rgba($lightgray,.08); border:1px solid rgba($primary,.3); color:$white; border-radius:.5rem; padding:.4rem .6rem; width: 140px; }
.btn { cursor:pointer; border:none; border-radius:.6rem; padding:.5rem .9rem; color:$white; }
.btn-primary { background: linear-gradient(135deg, $primary 0%, $secondary 100%); }
.btn-outline { background: transparent; border:1px solid rgba($primary,.4); color:$primary; }
.btn-sm { padding: .35rem .6rem; font-size: .9rem; }
.danger { color: #ef4444; }

.image-preview { display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem; }
.image-item { position:relative; width: 120px; height: 120px; border-radius:.5rem; overflow:hidden; border:1px solid rgba($primary,.3); }
.image-item img { width:100%; height:100%; object-fit:cover; }
.image-item .remove { position:absolute; top:.25rem; right:.25rem; background: rgba(0,0,0,.5); color:#fff; border:none; border-radius:.35rem; padding:.2rem .35rem; cursor:pointer; }

.links-preview { display:flex; flex-direction:column; gap:.25rem; margin-top:.5rem; }
.link-item { display:flex; align-items:center; gap:.5rem; color:$gray-300; }
.link-item .remove { margin-left:auto; background:transparent; border:none; color:$gray-400; cursor:pointer; }

.tags-preview { display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem; }
.tag { color:$primary; background: rgba($primary,.12); border:1px solid rgba($primary,.25); padding:.15rem .5rem; border-radius:999px; cursor:pointer; }

.feed-toolbar { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin: .5rem 0 1rem; }
.search-fixed { position: fixed; left: 0; right: 0; top: 4rem; z-index: 6; padding: .6rem 1rem; }
.search-fixed.collapsed { padding-top: .4rem; padding-bottom: .4rem; }
.search-box { position:relative; flex:1; display:flex; align-items:center; gap:.5rem; }
.search-trigger { border:1px solid rgba($primary,.35); background:transparent; color:$gray-300; padding:.4rem .6rem; border-radius:.5rem; }
.search-trigger:hover { color:$primary; border-color:$primary; }
.search-box i { color:$gray-400; }
.search-box input { flex:1; min-width: 0; padding:.5rem .6rem; border-radius:.6rem; background: transparent; color:$white; border:1px solid rgba($primary,.3); transition: width .2s ease, opacity .2s ease; }
.collapsed .search-box input { width: 0; opacity: 0; padding-left: 0; padding-right: 0; border-color: transparent; pointer-events: none; }
.sort-tabs { display:flex; gap:.5rem; }
.tab { background:transparent; color:$gray-300; border:1px solid rgba($primary,.3); border-radius:.6rem; padding:.45rem .8rem; cursor:pointer; }
.tab.active, .tab:hover { color:$primary; border-color:$primary; }

.post-card { 
  background: rgba($darkgray,.6); 
  border:1px solid rgba($primary,.2); 
  border-radius:$border-radius-lg; 
  padding:1rem; 
  margin-bottom:1rem; 
  transition: all 0.3s ease;
  animation: slideInUp 0.5s ease-out;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba($primary, 0.15);
    border-color: rgba($primary, 0.4);
  }
}
.post-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; }
.author { display:flex; align-items:center; gap:.75rem; }
.avatar { width:36px; height:36px; border-radius:50%; object-fit:cover; }
.avatar.placeholder { display:flex; align-items:center; justify-content:center; background: rgba($primary,.2); color:$primary; }
.tags { display:flex; gap:.5rem; flex-wrap:wrap; }
.post-content { 
  color:$white; 
  padding:.25rem 0 .25rem; // 减小底部padding
  
  p {
    margin: 8px 0; // 减小p标签的margin到8px
  }
}
.gallery {
  display: grid;
  gap: 0.25rem; // 间距 b
  margin-top: 0.4rem;
  border-radius: 0.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
  width: 100%;
  
  .image-item {
    position: relative;
    overflow: hidden;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
    background: rgba($darkgray, 0.3);
    
    &:hover {
      transform: scale(1.02);
      box-shadow: 0 4px 15px rgba($primary, 0.2);
    }
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: all 0.3s ease;
      opacity: 0;
    }
    
    .more-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, rgba(0, 0, 0, 0.6), rgba($primary, 0.3));
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 1.2rem;
      font-weight: 600;
      backdrop-filter: blur(2px);
      border-radius: 0.25rem;
    }
  }
  

  
  // 响应式设计 - 移动端优化
  @media (max-width: 768px) {
    gap: 0.2rem;
    
    // 单张图片在移动端的响应式
    &.images-1 {
      max-width: 100% !important;
      
      .image-item {
        &.normal-ratio {
          max-height: 250px;
        }
        
        &.long-image {
          width: 240px;
          height: 200px;
        }
        
        &.panorama {
          max-width: 100%;
          height: 120px;
        }
      }
    }
    
    // 2-3张图片保持原布局，但缩小尺寸
    &.images-2 {
      grid-template-columns: repeat(2, 100px);
      grid-template-rows: 100px;
    }
    
    &.images-3 {
      grid-template-columns: repeat(3, 100px);
      grid-template-rows: 100px;
    }
    
    // 4张及以上显示为3列布局
    &.images-4, &.images-5, &.images-6, &.images-7, &.images-8, &.images-9,
    &.images-multi-small, &.images-multi-grid, &.images-magazine {
      grid-template-columns: repeat(3, 100px) !important;
      grid-template-rows: repeat(auto, 100px) !important;
      gap: 0.15rem !important;
      
      .image-item {
        width: 100px !important;
        height: 100px !important;
        aspect-ratio: 1 !important;
        grid-column: unset !important;
        grid-row: unset !important;
      }
    }
    
    // 移动端9+张图片的更多提示
    &.images-9 {
      .image-item:nth-child(7) .more-overlay {
        display: flex;
      }
      
      .image-item:nth-child(9) .more-overlay {
        display: none;
      }
      
      .image-item:nth-child(n+8) {
        display: none;
      }
    }
  }
  
  @media (max-width: 480px) {
    gap: 0.15rem;
    
    // 小屏手机进一步缩小尺寸
    &.images-2 {
      grid-template-columns: repeat(2, 85px);
      grid-template-rows: 85px;
    }
    
    &.images-3 {
      grid-template-columns: repeat(3, 85px);
      grid-template-rows: 85px;
    }
    
    &.images-4, &.images-5, &.images-6, &.images-7, &.images-8, &.images-9,
    &.images-multi-small, &.images-multi-grid, &.images-magazine {
      grid-template-columns: repeat(3, 85px) !important;
      
      .image-item {
        width: 85px !important;
        height: 85px !important;
        grid-column: unset !important;
        grid-row: unset !important;
      }
    }
  }
  
  // 单张图片 - 智能适配显示
  &.images-1 {
    grid-template-columns: 1fr;
    
    .image-item {
      border-radius: 0.5rem;
      overflow: hidden;
      
      // 默认样式：固定尺寸展示模式
      &.fixed-size {
        width: 300px;
        height: 300px;
        img {
          object-fit: cover;
          object-position: center;
        }
      }
      
      // 正常比例图片 - 随比例变化模式
      &.normal-ratio {
        max-width: 400px;
        min-width: 200px;
        img {
          width: 100%;
          height: auto;
          max-height: 350px;
          min-height: 150px;
          object-fit: contain;
        }
      }
      
      // 长图 (宽高比 > 2.5:1) - 固定宽度，限制高度
      &.long-image {
        width: 300px;
        height: 200px;
        img {
          object-fit: cover;
          object-position: center top;
        }
      }
      
      // 超长图 (宽高比 > 4:1) - 极端长图处理
      &.ultra-long {
        width: 350px;
        height: 150px;
        img {
          object-fit: cover;
          object-position: center top;
        }
      }
      
      // 全景图 (宽高比 < 0.6:1) - 宽容器，限制高度
      &.panorama {
        width: 100%;
        max-width: 500px;
        height: 180px;
        img {
          object-fit: cover;
          object-position: center;
        }
      }
      
      // 方形图片 (宽高比 0.8-1.2:1) - 正方形显示
      &.square {
        width: 280px;
        height: 280px;
        img {
          object-fit: cover;
          object-position: center;
        }
      }
      
      // 竖图 (宽高比 < 0.8:1) - 固定宽度
      &.portrait {
        width: 250px;
        height: 350px;
        img {
          object-fit: cover;
          object-position: center;
        }
      }
      
      // 高质量图片优化显示
      &.high-quality {
        box-shadow: 0 2px 12px rgba($primary, 0.1);
        
        img {
          filter: contrast(1.05) saturate(1.1);
        }
        
        &:hover {
          box-shadow: 0 4px 20px rgba($primary, 0.2);
        }
      }
      
      // 低质量图片适配
      &.low-quality {
        img {
          filter: brightness(1.05) contrast(1.1);
        }
      }
    }
  }
  
  // 2张图片 - 方形容器并排
  &.images-2 {
    grid-template-columns: repeat(2, 120px); // a²方形容器
    grid-template-rows: 120px;
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 3张图片 - 方形容器排列
  &.images-3 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: 120px;
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 4张图片 - 特殊布局避免视觉失衡 (2+1+1)
  &.images-4 {
    grid-template-columns: repeat(2, 120px);
    grid-template-rows: repeat(2, 120px);
    gap: 0.25rem;
    width: fit-content; // (2a + b)²容器
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 5张图片 - 方形容器排列 (3+2)
  &.images-5 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: repeat(2, 120px);
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 6张图片 - 方形容器排列 (3+3)
  &.images-6 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: repeat(2, 120px);
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 7张图片 - 方形容器排列 (3+3+1)
  &.images-7 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: repeat(3, 120px);
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 8张图片 - 方形容器排列 (3+3+2)
  &.images-8 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: repeat(3, 120px);
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
    }
  }
  
  // 9张图片 - 方形容器排列 (3+3+3)，最多显示9张
  &.images-9 {
    grid-template-columns: repeat(3, 120px);
    grid-template-rows: repeat(3, 120px);
    gap: 0.25rem;
    
    .image-item {
      aspect-ratio: 1;
      
      &:nth-child(n+10) {
        display: none;
      }
    }
    
    .image-item:nth-child(9) .more-overlay {
      display: flex;
    }
  }
  
  // 5-6张图片紧凑布局
  &.images-multi-small {
    grid-template-columns: repeat(3, 115px);
    grid-template-rows: repeat(2, 115px);
    gap: 0.2rem;
    
    .image-item {
      aspect-ratio: 1;
      border-radius: 0.3rem;
      
      // 5张图片时第3个位置留空
      &:nth-child(3) {
        grid-column: 1;
        grid-row: 2;
      }
      
      &:nth-child(4) {
        grid-column: 2;
        grid-row: 2;
      }
      
      &:nth-child(5) {
        grid-column: 3;
        grid-row: 2;
      }
    }
    
    // 6张图片完美填充
    &.images-6 .image-item {
      &:nth-child(4) {
        grid-column: 1;
        grid-row: 2;
      }
      
      &:nth-child(5) {
        grid-column: 2;
        grid-row: 2;
      }
      
      &:nth-child(6) {
        grid-column: 3;
        grid-row: 2;
      }
    }
  }
  
  // 7-9张图片标准网格布局
  &.images-multi-grid {
    grid-template-columns: repeat(3, 110px);
    grid-template-rows: repeat(3, 110px);
    gap: 0.2rem;
    
    .image-item {
      aspect-ratio: 1;
      border-radius: 0.3rem;
      
      &:nth-child(n+10) {
        display: none;
      }
    }
    
    // 显示更多图片提示
    &.has-more .image-item:nth-child(9) .more-overlay {
      display: flex;
    }
  }
  
  // 拼图布局模式（实验性）
  &.images-magazine {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(3, 100px);
    gap: 0.15rem;
    max-width: 480px;
    
    .image-item {
      border-radius: 0.2rem;
      
      // 主图占据更大空间
      &:first-child {
        grid-column: 1 / 3;
        grid-row: 1 / 3;
      }
      
      // 其他图片填充剩余空间
      &:nth-child(2) {
        grid-column: 3 / 5;
        grid-row: 1;
      }
      
      &:nth-child(3) {
        grid-column: 3;
        grid-row: 2;
      }
      
      &:nth-child(4) {
        grid-column: 4;
        grid-row: 2;
      }
      
      &:nth-child(5) {
        grid-column: 1;
        grid-row: 3;
      }
      
      &:nth-child(6) {
        grid-column: 2;
        grid-row: 3;
      }
      
      &:nth-child(7) {
        grid-column: 3;
        grid-row: 3;
      }
      
      &:nth-child(8) {
        grid-column: 4;
        grid-row: 3;
      }
    }
  }
}
.links { display:flex; flex-direction:column; gap:.25rem; color:$gray-300; margin-top:.25rem; } // 减小与上方内容的间距
.post-actions { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-top: .35rem; // 减小顶部间距 
  
  .actions-left { 
    display: flex; 
    align-items: center; 
    gap: 1rem; 
  }
  
  .post-time { 
    color: $gray-500; 
    font-size: 0.85rem; 
    margin-left: auto; 
  }
}
.action { 
  background:transparent; 
  border:none; 
  color:$gray-300; 
  cursor:pointer; 
  display:inline-flex; 
  align-items:center; 
  gap:.35rem; 
  text-decoration:none; 
  padding:.25rem .5rem; 
  border-radius:.3rem; 
  transition:all .3s ease; 
  position: relative;
  
  &:hover { 
    color:$primary; 
    background:rgba($primary,.1); 
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.action.like {
  i { 
    transition: all .3s ease; 
    
    &.fa-heart { 
      color:#ef4444; 
      
      &:hover {
        transform: scale(1.2);
      }
    }
  }
  
  .count { 
    transition: all .3s ease; 
    
    &.liked { 
      color:#ef4444; 
      animation: bounce 0.6s ease;
    }
  }
  
  &:hover i:not(.fa-heart) {
    color: #ef4444;
    transform: scale(1.1);
  }
}

.action.detail:hover { color:#10b981; background:rgba(#10b981,.1); }
.action.edit:hover { color:#f59e0b; background:rgba(#f59e0b,.1); }
.action.danger:hover { color:#ef4444; background:rgba(#ef4444,.1); }

.default-comments,
.comments { 
  margin-top:.5rem; // 减小与帖子内容的间距
  border-top:1px dashed rgba($primary,.25); 
  padding-top:.4rem; // 减小顶部padding 
  animation: slideInDown 0.4s ease-out;
}

.default-comments {
  border-color: rgba($primary,.15);
  background: rgba($lightgray,.02);
  border-radius: .5rem;
  padding: .75rem;
}

.comment-composer { 
  display:flex; 
  align-items:center; 
  gap:.5rem; 
  
  input { 
    flex:1; 
    background: rgba($lightgray,.08); 
    border:1px solid rgba($primary,.3); 
    border-radius:.5rem; 
    color:$white; 
    padding:.45rem .6rem; 
    transition: all 0.3s ease;
    
    &:focus {
      border-color: $primary;
      box-shadow: 0 0 0 2px rgba($primary, 0.2);
      transform: translateY(-1px);
    }
  }
}

.comment-list { 
  display:flex; 
  flex-direction:column; 
  gap:.5rem; 
  margin-top:.5rem; 
}

.more-comments { 
  margin-top: .75rem; 
  text-align: center; 
  padding-top: .5rem; 
  border-top: 1px dashed rgba($primary, .2); 
  animation: fadeInUp 0.4s ease-out;
}

.comment-item { 
  background: rgba($lightgray,.05); 
  border:1px solid rgba($primary,.2); 
  border-radius:.5rem; 
  padding:.5rem .6rem; 
  transition: all 0.3s ease;
  animation: fadeInLeft 0.4s ease-out;
  position: relative;
  
  &:hover {
    background: rgba($lightgray,.08);
    border-color: rgba($primary,.3);
    transform: translateX(4px);
  }
  
  // 置顶评论特殊样式 - 通过类名而不是:has()来避免兼容性问题
  &.pinned-comment {
    background: rgba($primary, 0.08);
    border-color: rgba($primary, 0.3);
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: linear-gradient(to bottom, $primary, rgba($primary, 0.6));
      border-radius: .5rem 0 0 .5rem;
    }
  }
}

.pinned-badge {
  display: inline-flex;
  align-items: center;
  gap: .25rem;
  background: rgba($primary, 0.15);
  color: $primary;
  font-size: 0.75rem;
  padding: .2rem .4rem;
  border-radius: .3rem;
  margin-bottom: .5rem;
  font-weight: 600;
  
  i {
    font-size: 0.7rem;
  }
}

.action.pin {
  &:hover {
    color: $primary;
    background: rgba($primary, 0.1);
  }
  
  i {
    color: inherit;
  }
}
.c-author { display:flex; align-items:center; gap:.6rem; }
.c-content { 
  color:$gray-200; 
  margin-top:.25rem; 
  position: relative;
  
  .comment-text {
    margin-bottom: .75rem; // 为时间留出空间
  }
  
  .comment-time {
    position: absolute;
    bottom: 0;
    right: 0;
    color: $gray-500;
    font-size: 0.75rem;
    opacity: 0.8;
  }
}
.c-actions { margin-left:auto; display:flex; align-items:center; gap:.5rem; }

.loading { color:$gray-300; padding: 1rem 0; }
.loading.small { font-size:.9rem; }
.error { color:#ef4444; padding: 1rem 0; }
.empty { color:$gray-400; text-align:center; padding: 1rem 0; }
.empty.small { font-size:.9rem; }

.post-list.with-fixed { padding-top: 20px; padding-bottom: 160px; }
.loading-more, .load-more-trigger, .no-more {
  text-align: center;
  padding: 2rem 1rem;
  color: $gray-400;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  
  i {
    color: $primary;
  }
}

.load-more-trigger {
  opacity: 0.7;
  
  .load-more-hint {
    font-size: 0.9rem;
    color: $gray-500;
  }
}

.no-more {
  border-top: 1px solid rgba($primary, 0.2);
  margin-top: 1rem;
  
  span {
    display: inline-block;
    background: rgba($darkgray, 0.8);
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    font-size: 0.9rem;
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

@media (max-width: 768px) {
  .gallery {
    // 在移动端简化布局
    &.images-3 {
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      
      .image-item:first-child {
        grid-row: 1;
        grid-column: 1 / 3;
        aspect-ratio: 16/9;
      }
    }
  }
}

// 动画关键帧
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: scale(1);
  }
  40%, 43% {
    transform: scale(1.1);
  }
  70% {
    transform: scale(1.05);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

// 组合器动画
.composer-fixed .composer-card {
  animation: slideInUp 0.6s ease-out;
  
  &:hover {
    animation: pulse 2s infinite;
  }
}

// 图片悬停效果
.gallery .image-item {
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.02) rotate(0.5deg);
    filter: brightness(1.1);
  }
}

// 标签动画
.tag {
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
    background: rgba($primary, 0.25);
    cursor: pointer;
  }
}

// 加载动画增强
.loading-more, .load-more-trigger {
  animation: fadeInUp 0.5s ease-out;
}

// 编辑模式样式
.edit-mode {
  background: rgba($lightgray, 0.03);
  border: 1px solid rgba($primary, 0.2);
  border-radius: .5rem;
  padding: 1rem;
  margin: .5rem 0;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.edit-textarea {
  background: rgba($darkgray, 0.6);
  border: 1px solid rgba($primary, 0.3);
  border-radius: .5rem;
  color: $white;
  padding: .75rem;
  min-height: 120px;
  resize: vertical;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: $primary;
    box-shadow: 0 0 0 2px rgba($primary, 0.2);
  }
}

.edit-tags,
.edit-links,
.edit-images {
  label {
    display: block;
    color: $gray-300;
    font-weight: 600;
    margin-bottom: .5rem;
  }
}

.tag-input-container {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  align-items: center;
  padding: .5rem;
  background: rgba($darkgray, 0.4);
  border: 1px solid rgba($primary, 0.2);
  border-radius: .5rem;
  
  .edit-tag {
    display: inline-flex;
    align-items: center;
    gap: .25rem;
    background: rgba($primary, 0.2);
    color: $primary;
    padding: .25rem .5rem;
    border-radius: .3rem;
    font-size: 0.85rem;
    
    .remove-tag {
      background: none;
      border: none;
      color: $primary;
      cursor: pointer;
      font-size: 1rem;
      line-height: 1;
      
      &:hover {
        color: #ef4444;
      }
    }
  }
  
  .tag-input {
    background: transparent;
    border: none;
    color: $white;
    outline: none;
    flex: 1;
    min-width: 120px;
    padding: .25rem;
  }
  
  .add-tag-btn {
    background: rgba($primary, 0.2);
    border: 1px solid rgba($primary, 0.4);
    color: $primary;
    border-radius: .3rem;
    padding: .25rem .5rem;
    cursor: pointer;
    
    &:hover {
      background: rgba($primary, 0.3);
    }
  }
}

.link-input-container {
  display: flex;
  gap: .5rem;
  margin-bottom: .5rem;
  
  .link-input {
    flex: 1;
    background: rgba($darkgray, 0.6);
    border: 1px solid rgba($primary, 0.3);
    border-radius: .3rem;
    color: $white;
    padding: .5rem;
    
    &:focus {
      outline: none;
      border-color: $primary;
    }
  }
  
  .remove-link {
    background: #ef4444;
    border: none;
    color: white;
    border-radius: .3rem;
    padding: .5rem .75rem;
    cursor: pointer;
    
    &:hover {
      background: #dc2626;
    }
  }
}

.add-link-btn {
  background: rgba($primary, 0.1);
  border: 1px dashed rgba($primary, 0.4);
  color: $primary;
  border-radius: .3rem;
  padding: .5rem 1rem;
  cursor: pointer;
  
  &:hover {
    background: rgba($primary, 0.2);
  }
}

.edit-actions {
  display: flex;
  gap: .75rem;
  justify-content: flex-end;
  padding-top: .5rem;
  border-top: 1px solid rgba($primary, 0.2);
}

// 图片编辑相关样式
.edit-images {
  .current-images,
  .new-images {
    margin-bottom: 1rem;
  }
  
  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: .75rem;
    margin-bottom: .75rem;
  }
  
  .edit-image-item {
    position: relative;
    aspect-ratio: 1;
    border-radius: .5rem;
    overflow: hidden;
    border: 2px solid rgba($primary, 0.2);
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .remove-image {
      position: absolute;
      top: .25rem;
      right: .25rem;
      background: rgba(#ef4444, 0.9);
      color: white;
      border: none;
      border-radius: 50%;
      width: 24px;
      height: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: .875rem;
      
      &:hover {
        background: #ef4444;
      }
    }
    
    .new-image-badge {
      position: absolute;
      top: .25rem;
      left: .25rem;
      background: rgba($primary, 0.9);
      color: white;
      padding: .125rem .375rem;
      border-radius: .25rem;
      font-size: .75rem;
      font-weight: 600;
    }
  }
  
  .image-upload {
    .file-input {
      display: none;
    }
    
    .upload-btn {
      display: inline-flex;
      align-items: center;
      gap: .5rem;
      background: rgba($primary, 0.1);
      border: 2px dashed rgba($primary, 0.4);
      color: $primary;
      border-radius: .5rem;
      padding: .75rem 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba($primary, 0.2);
        border-color: rgba($primary, 0.6);
      }
      
      i {
        font-size: 1rem;
      }
    }
  }
}

@media (min-width: 992px) { .community-layout { grid-template-columns: 1fr; } }
</style>



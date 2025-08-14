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
                  <span class="time">{{ formatTime(post.created_at) }}</span>
                </div>
              </div>
              <div class="tags">
                <span v-for="tag in post.tags" :key="tag.id" class="tag" @click="filterByTag(tag.name)">#{{ tag.name }}</span>
              </div>
            </header>

            <div class="post-content" v-html="renderMarkdown(post.content)"></div>

            <div v-if="post.image_urls?.length" class="gallery">
              <img v-for="(url, idx) in post.image_urls" :key="idx" :src="url" />
            </div>

            <div v-if="post.link_urls?.length" class="links">
              <div v-for="(url, idx) in post.link_urls" :key="idx" class="link">
                <i class="fa fa-link"></i>
                <a :href="url" target="_blank">{{ url }}</a>
              </div>
            </div>

            <footer class="post-actions">
              <button class="action like" @click="toggleLikePost(post)" :disabled="liking">
                <i :class="[isPostLiked(post.id) ? 'fa-solid fa-heart' : 'fa-regular fa-heart']"></i>
                <span class="count" :class="{ liked: isPostLiked(post.id) }">{{ post.like_count }}</span>
              </button>
              <button class="action" @click="openComments(post)">
                <i class="fa fa-comment"></i>
                {{ post.comment_count }}
              </button>
              <button class="action" @click="reportTarget('post', post.id)"><i class="fa fa-flag"></i> 举报</button>
              <button v-if="isAdmin" class="action danger" @click="deletePost(post)"><i class="fa fa-trash"></i> 删除</button>
            </footer>

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
                  <div v-for="c in comments" :key="c.id" class="comment-item">
                    <div class="c-author">
                      <img v-if="c.author?.avatar_url" :src="c.author.avatar_url" class="avatar" />
                      <div v-else class="avatar placeholder"><i class="fa fa-user"></i></div>
                      <div class="meta">
                        <strong>{{ c.author?.display_name || c.author?.username || '匿名' }}</strong>
                        <span class="time">{{ formatTime(c.created_at) }}</span>
                      </div>
                      <div class="c-actions">
                        <button class="action like" @click="toggleLikeComment(c)" :disabled="liking"><i :class="[isCommentLiked(c.id) ? 'fa-solid fa-heart' : 'fa-regular fa-heart']"></i> <span class="count" :class="{ liked: isCommentLiked(c.id) }">{{ c.like_count }}</span></button>
                        <button class="action" @click="reportTarget('comment', c.id)"><i class="fa fa-flag"></i> 举报</button>
                      </div>
                    </div>
                    <div class="c-content">{{ c.content }}</div>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <div v-if="pages > 1" class="pagination">
            <button class="btn btn-outline" :disabled="page<=1" @click="page = page - 1; fetchPosts()"><i class="fa fa-chevron-left"></i> 上一页</button>
            <span>第 {{ page }} / {{ pages }} 页</span>
            <button class="btn btn-outline" :disabled="page>=pages" @click="page = page + 1; fetchPosts()">下一页 <i class="fa fa-chevron-right"></i></button>
          </div>
        </div>
      </section>
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

const loading = ref(false)
const error = ref('')
const posts = ref<CommunityPost[]>([])
const page = ref(1)
const pages = ref(1)
const total = ref(0)

const query = reactive({ search: '', sort: 'latest' as 'latest'|'hot', tag: '' })
let debounceTimer: any = null
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    fetchPosts()
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
  if (t && !composer.tags.includes(t)) composer.tags.push(t)
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

async function fetchPosts() {
  try {
    loading.value = true
    error.value = ''
    const res = await CommunityService.listPosts({ page: page.value, page_size: 10, search: query.search || undefined, sort: query.sort, tag: query.tag || undefined })
    posts.value = res.items
    likedPostIds.value = new Set(res.items.filter(p => p.liked_by_me).map(p => p.id))
    total.value = res.total
    page.value = res.page
    pages.value = res.pages
  } catch (err: any) {
    error.value = err?.error || '加载失败'
  } finally {
    loading.value = false
  }
}

// likes local cache
const likedPostIds = ref<Set<number>>(new Set())
const likedCommentIds = ref<Set<number>>(new Set())
const liking = ref(false)

function isPostLiked(id: number) { return likedPostIds.value.has(id) }
function isCommentLiked(id: number) { return likedCommentIds.value.has(id) }

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

async function openComments(post: CommunityPost) {
  if (expandedPostId.value === post.id) {
    expandedPostId.value = null
    return
  }
  expandedPostId.value = post.id
  await fetchComments(post)
}

async function fetchComments(post: CommunityPost) {
  try {
    commentsLoading.value = true
    const res = await CommunityService.listComments(post.id)
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
    const res = await CommunityService.createComment(post.id, { content: text })
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

async function reportTarget(type: 'post'|'comment', id: number) {
  const reason = prompt('请输入举报理由：')?.trim()
  if (!reason) return
  try {
    await CommunityService.report({ target_type: type, target_id: id, reason })
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
onMounted(() => {
  setHeaderVar()
  window.addEventListener('resize', setHeaderVar)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', setHeaderVar)
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
.composer-actions .left { display:flex; align-items:center; gap:.5rem; }
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

.post-card { background: rgba($darkgray,.6); border:1px solid rgba($primary,.2); border-radius:$border-radius-lg; padding:1rem; margin-bottom:1rem; }
.post-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; }
.author { display:flex; align-items:center; gap:.75rem; }
.avatar { width:36px; height:36px; border-radius:50%; object-fit:cover; }
.avatar.placeholder { display:flex; align-items:center; justify-content:center; background: rgba($primary,.2); color:$primary; }
.post-content { color:$white; padding:.25rem 0 .5rem; }
.gallery { display:grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap:.5rem; margin-top:.5rem; }
.gallery img { width:100%; border-radius:.5rem; border:1px solid rgba($primary,.3); }
.links { display:flex; flex-direction:column; gap:.25rem; color:$gray-300; margin-top:.5rem; }
.post-actions { display:flex; align-items:center; gap:1rem; margin-top:.5rem; }
.action { background:transparent; border:none; color:$gray-300; cursor:pointer; display:inline-flex; align-items:center; gap:.35rem; }
.action:hover { color:$primary; }
.action.like i { transition: color .2s ease; }
.action.like .count { transition: color .2s ease; }
.action.like i.fa-heart { color:#ef4444; }
.action.like .count.liked { color:#ef4444; }

.comments { margin-top:.75rem; border-top:1px dashed rgba($primary,.25); padding-top:.5rem; }
.comment-composer { display:flex; align-items:center; gap:.5rem; }
.comment-composer input { flex:1; background: rgba($lightgray,.08); border:1px solid rgba($primary,.3); border-radius:.5rem; color:$white; padding:.45rem .6rem; }
.comment-list { display:flex; flex-direction:column; gap:.5rem; margin-top:.5rem; }
.comment-item { background: rgba($lightgray,.05); border:1px solid rgba($primary,.2); border-radius:.5rem; padding:.5rem .6rem; }
.c-author { display:flex; align-items:center; gap:.6rem; }
.c-content { color:$gray-200; margin-top:.25rem; }
.c-actions { margin-left:auto; display:flex; align-items:center; gap:.5rem; }

.loading { color:$gray-300; padding: 1rem 0; }
.loading.small { font-size:.9rem; }
.error { color:#ef4444; padding: 1rem 0; }
.empty { color:$gray-400; text-align:center; padding: 1rem 0; }
.empty.small { font-size:.9rem; }

.post-list.with-fixed { padding-top: 20px; padding-bottom: 160px; }
.pagination { display:flex; align-items:center; justify-content:center; gap:1rem; padding-top:.5rem; }

@media (min-width: 992px) { .community-layout { grid-template-columns: 1fr; } }
</style>



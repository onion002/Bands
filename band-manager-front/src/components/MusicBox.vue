<template>
  <div class="music-box" :class="{ 'expanded': isExpanded }">
    <!-- 🎵 旋转的黑色胶片 -->
    <div class="vinyl-disc" @click="toggleMusicBox">
      <div class="vinyl-center">
        <i class="fa fa-music"></i>
      </div>
      <div class="vinyl-grooves"></div>
    </div>

    <!-- 迷你播放器 - 放在黑胶唱片下方 -->
    <div v-if="!isExpanded && currentSong && isPlaying" class="mini-player">
      <div class="mini-info">
        <div class="mini-title">{{ currentSong.song }}</div>
        <div class="mini-artist">{{ currentSong.singer }}</div>
      </div>
      <div class="mini-controls">
        <button @click="togglePlay" class="mini-btn" :title="isPlaying ? '暂停' : '播放'">
          <i :class="isPlaying ? 'fa fa-pause' : 'fa fa-play'"></i>
        </button>
        <button @click="stopPlay" class="mini-btn" title="停止">
          <i class="fa fa-stop"></i>
        </button>
      </div>
    </div>

    <!-- 🎶 点歌功能面板 -->
    <div v-if="isExpanded" class="music-panel">
      <div class="panel-header">
        <h3>🎵 点歌台</h3>
        <button class="close-btn" @click="collapseMusicBox">
          <i class="fa fa-times"></i>
        </button>
      </div>

      <!-- 标签页导航 -->
      <div class="tab-navigation">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
        >
          {{ tab.label }}
          <span v-if="tab.key === 'favorites'" class="badge">{{ favoriteCount }}</span>
        </button>
      </div>

      <!-- 搜索标签页 -->
      <div v-if="activeTab === 'search'" class="tab-content">
        <!-- 搜索区域 -->
        <div class="search-section">
          <div class="search-input-group">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="输入歌名、歌手或专辑..."
              class="search-input"
              @keyup.enter="searchMusic"
            />
            <button @click="searchMusic" class="search-btn">
              <i class="fa fa-search"></i>
            </button>
          </div>
          
          <!-- 音质选择 -->
          <div class="quality-selector">
            <label>音质选择:</label>
            <select v-model="selectedQuality" class="quality-select">
              <option v-for="option in qualityOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" class="results-section">
          <h4>搜索结果 ({{ searchResults.length }})</h4>
          <div class="results-list">
            <div 
              v-for="song in searchResults" 
              :key="song.id" 
              class="song-item"
              @click="playSong(song)"
            >
              <div class="song-cover">
                <img :src="song.cover" :alt="song.song" />
              </div>
              <div class="song-info">
                <div class="song-title">{{ song.song }}</div>
                <div class="song-artist">{{ song.singer }}</div>
                <div class="song-album">{{ song.album }}</div>
                <div class="song-details">
                  <span class="song-duration">{{ formatDuration(song.interval) }}</span>
                  <span class="song-size">{{ formatFileSize(song.size) }}</span>
                </div>
              </div>
              <div class="song-quality">{{ song.quality }}</div>
              <div class="song-actions">
                <button 
                  @click.stop="toggleFavorite(song)"
                  :class="['favorite-btn', { active: isFavorite(song.id) }]"
                  :title="isFavorite(song.id) ? '取消收藏' : '收藏'"
                >
                  <i :class="isFavorite(song.id) ? 'fa fa-heart' : 'fa fa-heart-o'"></i>
                </button>
                <button class="play-btn">
                  <i class="fa fa-play"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史记录标签页 -->
      <div v-if="activeTab === 'history'" class="tab-content">
        <div class="tab-header">
          <h4>播放历史</h4>
          <div class="tab-actions">
            <button @click="clearHistory" class="clear-btn" title="清空历史">
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>
        
        <div v-if="playHistory.length > 0" class="history-list">
          <div 
            v-for="item in recentPlayed" 
            :key="`${item.id}-${item.playedAt}`"
            class="history-item"
            @click="playSong(item)"
          >
            <div class="history-cover">
              <img :src="item.cover" :alt="item.song" />
            </div>
            <div class="history-info">
              <div class="history-title">{{ item.song }}</div>
              <div class="history-artist">{{ item.singer }}</div>
              <div class="history-meta">
                <span class="play-count">播放 {{ item.playCount }} 次</span>
                <span class="play-time">{{ formatTimeAgo(item.playedAt) }}</span>
              </div>
            </div>
            <div class="history-actions">
              <button 
                @click.stop="toggleFavorite(item)"
                :class="['favorite-btn', { active: isFavorite(item.id) }]"
              >
                <i :class="isFavorite(item.id) ? 'fa fa-heart' : 'fa fa-heart-o'"></i>
              </button>
              <button class="play-btn">
                <i class="fa fa-play"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <i class="fa fa-history"></i>
          <p>暂无播放历史</p>
        </div>
      </div>

      <!-- 收藏标签页 -->
      <div v-if="activeTab === 'favorites'" class="tab-content">
        <div class="tab-header">
          <h4>我的收藏 ({{ favoriteCount }})</h4>
          <div class="tab-actions">
            <label class="auto-play-toggle">
              <input 
                type="checkbox" 
                v-model="autoPlayHistory"
                @change="toggleAutoPlayHistory"
              />
              <span>自动播放收藏</span>
            </label>
            <button @click="clearFavorites" class="clear-btn" title="清空收藏">
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>
        
        <div v-if="favorites.length > 0" class="favorites-list">
          <div 
            v-for="item in favorites" 
            :key="`${item.id}-${item.addedAt}`"
            class="favorite-item"
            @click="playSong(item)"
          >
            <div class="favorite-cover">
              <img :src="item.cover" :alt="item.song" />
            </div>
            <div class="favorite-info">
              <div class="favorite-title">{{ item.song }}</div>
              <div class="favorite-artist">{{ item.singer }}</div>
              <div class="favorite-meta">
                <span class="added-time">收藏于 {{ formatTimeAgo(item.addedAt) }}</span>
              </div>
            </div>
            <div class="favorite-actions">
              <button 
                @click.stop="removeFromFavorites(item.id)"
                class="remove-btn"
                title="取消收藏"
              >
                <i class="fa fa-heart-broken"></i>
              </button>
              <button class="play-btn">
                <i class="fa fa-play"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <i class="fa fa-heart"></i>
          <p>暂无收藏歌曲</p>
        </div>
      </div>

      <!-- 播放器 -->
      <div v-if="currentSong" class="player-section">
        <h4>正在播放</h4>
        <div class="now-playing">
          <div class="playing-cover">
            <img :src="currentSong.cover" :alt="currentSong.song" />
          </div>
          <div class="playing-info">
            <div class="playing-title">{{ currentSong.song }}</div>
            <div class="playing-artist">{{ currentSong.singer }}</div>
            <div class="playing-album">{{ currentSong.album }}</div>
          </div>
          <div class="playing-controls">
            <button @click="togglePlay" class="control-btn">
              <i :class="isPlaying ? 'fa fa-pause' : 'fa fa-play'"></i>
            </button>
            <button @click="stopPlay" class="control-btn">
              <i class="fa fa-stop"></i>
            </button>
          </div>
        </div>
        
        <!-- 播放进度条 -->
        <div class="progress-container">
          <div class="progress-bar" @click="handleProgressClick" ref="progressBar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            <div 
              class="progress-handle" 
              :style="{ left: progressPercent + '%' }"
              @mousedown="startDragging"
              @touchstart="startDragging"
            ></div>
          </div>
          <div class="time-display">
            <span class="current-time">{{ formatTime(currentTime) }}</span>
            <span class="total-time">{{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <span>搜索中...</span>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <div class="error-content">
          <span>{{ error }}</span>
          <button @click="searchMusic" class="retry-btn" :disabled="isLoading">
            {{ isLoading ? '重试中...' : '重试' }}
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!isLoading && searchResults.length === 0 && searchQuery && !error" class="empty-state">
        <i class="fa fa-music"></i>
        <p>没有找到相关音乐</p>
        <p class="empty-tip">试试其他关键词或检查网络连接</p>
      </div>
    </div>

    <!-- 音频元素 -->
    <audio 
      ref="audioPlayer" 
      @ended="onAudioEnded"
      @timeupdate="onTimeUpdate"
      @loadeddata="onAudioLoaded"
      @canplay="onCanPlay"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { musicService, type SongInfo } from '@/api/musicService'
import { useMusicBoxStore } from '@/stores/musicBoxStore'
import { useAuthStore } from '@/stores/authStore'

// 状态管理
const isExpanded = ref(false)
const searchQuery = ref('')
const searchResults = ref<SongInfo[]>([])
const currentSong = ref<SongInfo | null>(null)
const isPlaying = ref(false)
const isLoading = ref(false)
const error = ref('')
const audioPlayer = ref<HTMLAudioElement>()

// 标签页管理
const activeTab = ref('search')
const tabs = [
  { key: 'search', label: '🔍 搜索' },
  { key: 'history', label: '📚 历史' },
  { key: 'favorites', label: '❤️ 收藏' }
]

// 音质选择
const selectedQuality = ref(9)
const qualityOptions = computed(() => musicService.getQualityOptions())

// 音乐盒存储
const musicBoxStore = useMusicBoxStore()
const authStore = useAuthStore()

// 计算属性
const playHistory = computed(() => musicBoxStore.playHistory)
const favorites = computed(() => musicBoxStore.favorites)
const recentPlayed = computed(() => musicBoxStore.recentPlayed)
const favoriteCount = computed(() => musicBoxStore.favoriteCount)
const autoPlayHistory = computed(() => musicBoxStore.autoPlayHistory)

// 监听认证状态变化
watch(() => authStore.isAuthenticated, (newValue, oldValue) => {
  if (newValue && !oldValue) {
    // 用户刚登录
    console.log('🎵 用户已登录，检查自动播放收藏')
    setTimeout(() => {
      checkAndAutoPlayFavorites()
    }, 500)
  }
}, { immediate: true })

// 播放进度
const currentTime = ref(0)
const duration = ref(0)
const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// 切换展开状态
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
  if (!isExpanded.value) {
    // 关闭时停止播放
    stopPlay()
  }
}

// 收起音乐盒
const collapseMusicBox = () => {
  isExpanded.value = false
  // 不停止音乐播放，让音乐继续在后台播放
  console.log('🎵 音乐盒已收起，音乐继续在后台播放')
}

// 展开音乐盒
const expandMusicBox = () => {
  isExpanded.value = true
  // 展开时不停止播放，让音乐继续播放
  console.log('🎵 音乐盒已展开，音乐继续播放')
}

// 切换音乐盒展开状态
const toggleMusicBox = () => {
  if (isExpanded.value) {
    collapseMusicBox()
  } else {
    expandMusicBox()
  }
}

// 搜索音乐
const searchMusic = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '请输入搜索关键词'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const results = await musicService.searchMusic(
      searchQuery.value, 
      1, 
      10, 
      selectedQuality.value
    )
    
    searchResults.value = results
  } catch (err: any) {
    console.error('搜索音乐失败:', err)
    
    // 提供更友好的错误提示
    if (err.message.includes('服务器暂时繁忙')) {
      error.value = '服务器暂时繁忙，请稍后重试'
    } else if (err.message.includes('请求过于频繁')) {
      error.value = '请求过于频繁，请稍等片刻再试'
    } else if (err.message.includes('网络连接失败')) {
      error.value = '网络连接失败，请检查网络后重试'
    } else {
      error.value = err.message || '搜索失败，请稍后重试'
    }
    
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

// 检查音频URL的CORS状态
const checkAudioCors = async (url: string): Promise<{ cors: boolean, accessible: boolean }> => {
  try {
    // 尝试预加载音频
    const audio = new Audio()
    audio.crossOrigin = 'anonymous'
    
    return new Promise((resolve) => {
      audio.addEventListener('canplay', () => {
        resolve({ cors: true, accessible: true })
      })
      
      audio.addEventListener('error', (e) => {
        resolve({ cors: false, accessible: false })
      })
      
      // 设置超时
      setTimeout(() => {
        resolve({ cors: false, accessible: false })
      }, 5000)
      
      audio.src = url
      audio.load()
    })
  } catch (error: any) {
    return { cors: false, accessible: false }
  }
}

// 获取最佳音频URL
const getBestAudioUrl = (song: SongInfo): string | null => {
  // 优先使用url字段，如果没有则使用link字段
  if (song.url && song.url.trim()) {
    return song.url
  }
  if (song.link && song.link.trim()) {
    return song.link
  }
  
  return null
}

// 测试音频URL是否可访问
const testAudioUrl = async (url: string): Promise<boolean> => {
  try {
    const response = await fetch(url, { method: 'HEAD' })
    return response.ok
  } catch (error: any) {
    return false
  }
}

// 播放歌曲时添加到历史记录
const playSong = async (song: SongInfo) => {
  try {
    // 获取最佳音频URL
    const audioUrl = getBestAudioUrl(song)
    if (!audioUrl) {
      error.value = '播放链接无效，请选择其他歌曲'
      return
    }
    
    // 添加到播放历史
    musicBoxStore.addToHistory(song)
    
    // 测试URL是否可访问
    const isUrlAccessible = await testAudioUrl(audioUrl)
    
    // 检查CORS状态
    const corsCheck = await checkAudioCors(audioUrl)
    
    if (!corsCheck.accessible) {
      console.warn('⚠️ 音频可能存在CORS问题，但仍尝试播放')
    }
    
    currentSong.value = song
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    
    if (audioPlayer.value) {
      // 先停止当前播放
      audioPlayer.value.pause()
      audioPlayer.value.currentTime = 0
      
      // 设置新的音频源
      audioPlayer.value.src = audioUrl
      
      // 加载音频
      audioPlayer.value.load()
      
      // 等待音频可以播放
      audioPlayer.value.addEventListener('canplay', () => {
        const playPromise = audioPlayer.value!.play()
        if (playPromise !== undefined) {
          playPromise.then(() => {
            isPlaying.value = true
            error.value = ''
            console.log('🎵 播放成功:', song.song)
          }).catch((err) => {
            console.error('❌ 播放失败:', err)
            error.value = `播放失败: ${err.message || '可能是版权限制或网络问题'}`
            isPlaying.value = false
            
            // 尝试使用备用方法
            tryFallbackPlayback(audioUrl)
          })
        }
      }, { once: true })
      
      // 添加错误处理
      audioPlayer.value.addEventListener('error', (e) => {
        console.error('❌ 音频加载错误:', e)
        
        // 根据错误类型提供更具体的错误信息
        let errorMessage = '音频加载失败'
        if (audioPlayer.value?.error) {
          switch (audioPlayer.value.error.code) {
            case MediaError.MEDIA_ERR_ABORTED:
              errorMessage = '音频播放被中断'
              break
            case MediaError.MEDIA_ERR_NETWORK:
              errorMessage = '网络错误，无法加载音频'
              break
            case MediaError.MEDIA_ERR_DECODE:
              errorMessage = '音频格式不支持或损坏'
              break
            case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
              errorMessage = '音频源不支持或无法访问'
              break
            default:
              errorMessage = '音频播放失败，请检查网络连接或选择其他歌曲'
          }
        }
        
        error.value = errorMessage
        isPlaying.value = false
        
        // 尝试使用备用方法
        tryFallbackPlayback(audioUrl)
      })
      
      // 添加加载状态处理
      audioPlayer.value.addEventListener('loadstart', () => {
        isLoading.value = true
      })
      
      audioPlayer.value.addEventListener('canplaythrough', () => {
        isLoading.value = false
      })
      
    } else {
      console.error('❌ 音频播放器未找到')
      error.value = '音频播放器初始化失败'
      
      // 尝试使用备用方法
      tryFallbackPlayback(audioUrl)
    }
  } catch (err) {
    console.error('❌ 播放歌曲失败:', err)
    error.value = `播放失败: ${err instanceof Error ? err.message : '未知错误'}`
  }
}

// 切换播放/暂停
const togglePlay = () => {
  if (!audioPlayer.value) return
  
  if (isPlaying.value) {
    audioPlayer.value.pause()
    isPlaying.value = false
  } else {
    audioPlayer.value.play()
    isPlaying.value = true
  }
}

// 停止播放
const stopPlay = () => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value.currentTime = 0
    isPlaying.value = false
    currentTime.value = 0
  }
}

// 音频事件处理
const onAudioEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
}

const onTimeUpdate = () => {
  if (audioPlayer.value) {
    currentTime.value = audioPlayer.value.currentTime
  }
}

const onAudioLoaded = () => {
  // 音频加载完成
}

const onCanPlay = () => {
  if (audioPlayer.value) {
    duration.value = audioPlayer.value.duration
  }
}

// 备用播放方法
const tryFallbackPlayback = async (url: string) => {
  try {
    const audio = new Audio()
    audio.crossOrigin = 'anonymous'
    audio.src = url
    audio.load()

    audio.addEventListener('canplay', () => {
      const playPromise = audio.play()
      if (playPromise !== undefined) {
        playPromise.then(() => {
          isPlaying.value = true
          error.value = ''
        }).catch((err) => {
          error.value = `备用播放失败: ${err.message || '可能是版权限制或网络问题'}`
          isPlaying.value = false
        })
      }
    }, { once: true })

    audio.addEventListener('error', (e) => {
      error.value = '备用播放失败，请检查网络连接'
      isPlaying.value = false
    })

  } catch (err) {
    error.value = `备用播放失败: ${err instanceof Error ? err.message : '未知错误'}`
    isPlaying.value = false
  }
}

// 收藏相关方法
const toggleFavorite = (song: SongInfo) => {
  if (musicBoxStore.isFavorite(song.id)) {
    musicBoxStore.removeFromFavorites(song.id)
  } else {
    musicBoxStore.addToFavorites(song)
  }
}

const isFavorite = (songId: number) => {
  return musicBoxStore.isFavorite(songId)
}

const clearFavorites = () => {
  if (confirm('确定要清空所有收藏吗？')) {
    musicBoxStore.clearFavorites()
  }
}

// 历史记录相关方法
const clearHistory = () => {
  if (confirm('确定要清空播放历史吗？')) {
    musicBoxStore.clearHistory()
  }
}

const toggleAutoPlayHistory = () => {
  musicBoxStore.toggleAutoPlayHistory()
}

// 拖拽进度条
const progressBar = ref<HTMLDivElement | null>(null)
const isDragging = ref(false)

const startDragging = (event: MouseEvent | TouchEvent) => {
  event.preventDefault()
  isDragging.value = true
  
  if (event instanceof MouseEvent) {
    document.addEventListener('mousemove', handleDragMove)
    document.addEventListener('mouseup', stopDragging)
  } else if (event instanceof TouchEvent) {
    document.addEventListener('touchmove', handleDragMove)
    document.addEventListener('touchend', stopDragging)
  }
}

const handleDragMove = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value || !progressBar.value) return
  
  const rect = progressBar.value.getBoundingClientRect()
  let offsetX = 0
  
  if (event instanceof MouseEvent) {
    offsetX = event.clientX - rect.left
  } else if (event instanceof TouchEvent) {
    offsetX = event.touches[0].clientX - rect.left
  }
  
  const newPercent = Math.max(0, Math.min(100, (offsetX / rect.width) * 100))
  seekToPosition(newPercent)
}

const seekToPosition = (percent: number) => {
  if (!audioPlayer.value) return
  
  const newTime = (percent / 100) * duration.value
  audioPlayer.value.currentTime = newTime
  currentTime.value = newTime
}

const stopDragging = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', stopDragging)
  document.removeEventListener('touchmove', handleDragMove)
  document.removeEventListener('touchend', stopDragging)
}

// 处理进度条点击
const handleProgressClick = (event: MouseEvent) => {
  if (!progressBar.value) return

  const rect = progressBar.value.getBoundingClientRect()
  const offsetX = event.clientX - rect.left
  const newPercent = (offsetX / rect.width) * 100
  seekToPosition(newPercent)
}

// 工具函数
const formatDuration = (interval: string) => {
  return musicService.formatDuration(interval)
}

const formatFileSize = (size: string) => {
  return musicService.formatFileSize(size)
}

const formatTime = (seconds: number) => {
  if (isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 时间格式化
const formatTimeAgo = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`
  
  return new Date(timestamp).toLocaleDateString()
}

// 从收藏中移除歌曲
const removeFromFavorites = (songId: number) => {
  musicBoxStore.removeFromFavorites(songId)
}

// 生命周期
onMounted(() => {
  // 确保音频元素存在
  if (audioPlayer.value) {
    // 添加音频事件监听器
    audioPlayer.value.addEventListener('loadstart', () => {})
    audioPlayer.value.addEventListener('durationchange', () => {})
    audioPlayer.value.addEventListener('loadedmetadata', () => {})
    audioPlayer.value.addEventListener('canplay', () => {})
    audioPlayer.value.addEventListener('canplaythrough', () => {})
    audioPlayer.value.addEventListener('playing', () => {})
    audioPlayer.value.addEventListener('waiting', () => {})
    audioPlayer.value.addEventListener('seeking', () => {})
    audioPlayer.value.addEventListener('seeked', () => {})
    audioPlayer.value.addEventListener('ended', () => {})
    audioPlayer.value.addEventListener('error', (e) => {})
    audioPlayer.value.addEventListener('abort', () => {})
    audioPlayer.value.addEventListener('emptied', () => {})
    audioPlayer.value.addEventListener('stalled', () => {})
    audioPlayer.value.addEventListener('suspend', () => {})
  }
  
  // 延迟检查自动播放，确保认证状态已更新
  setTimeout(() => {
    checkAndAutoPlayFavorites()
  }, 1000)
})

// 检查并自动播放收藏列表
const checkAndAutoPlayFavorites = () => {
  if (authStore.isAuthenticated && autoPlayHistory.value) {
    // 改为播放收藏列表中的第一首歌
    const firstFavorite = favorites.value[0]
    if (firstFavorite) {
      console.log('🎵 自动播放收藏列表:', firstFavorite.song)
      // 直接尝试播放，不做任何限制
      setTimeout(() => {
        playSong(firstFavorite)
      }, 2000)
    } else {
      console.log('🎵 收藏列表为空，无法自动播放')
    }
  }
}

onUnmounted(() => {
  // 清理拖拽事件监听器
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', stopDragging)
  document.removeEventListener('touchmove', handleDragMove)
  document.removeEventListener('touchend', stopDragging)
  
  // 清理音频事件监听器
  if (audioPlayer.value) {
    audioPlayer.value.removeEventListener('loadstart', () => {})
    audioPlayer.value.removeEventListener('durationchange', () => {})
    audioPlayer.value.removeEventListener('loadedmetadata', () => {})
    audioPlayer.value.removeEventListener('canplay', () => {})
    audioPlayer.value.removeEventListener('canplaythrough', () => {})
    audioPlayer.value.removeEventListener('playing', () => {})
    audioPlayer.value.removeEventListener('waiting', () => {})
    audioPlayer.value.removeEventListener('seeking', () => {})
    audioPlayer.value.removeEventListener('seeked', () => {})
    audioPlayer.value.removeEventListener('ended', () => {})
    audioPlayer.value.removeEventListener('error', () => {})
    audioPlayer.value.removeEventListener('abort', () => {})
    audioPlayer.value.removeEventListener('emptied', () => {})
    audioPlayer.value.removeEventListener('stalled', () => {})
    audioPlayer.value.removeEventListener('suspend', () => {})
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/scss/variables' as *;

.music-box {
  position: fixed;
  top: 5rem;
  left: 2rem;
  z-index: 1000;
  transition: all $transition-normal ease;
}

// 🎵 旋转的黑色胶片
.vinyl-disc {
  width: 80px;
  height: 80px;
  background: $black;
  border-radius: 50%;
  position: relative;
  cursor: pointer;
  box-shadow: $shadow-dark;
  transition: all $transition-normal ease;
  animation: rotate 3s linear infinite;
  border: 3px solid $primary;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: $shadow-primary;
    animation-play-state: paused;
  }
  
  &:active {
    transform: scale(0.95);
  }
}

.vinyl-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: $primary;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $white;
  font-size: 10px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}

.vinyl-grooves {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 50px;
    height: 50px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }
}

// 旋转动画
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 🎶 点歌功能面板
.music-panel {
  position: absolute;
  top: 100px;
  left: 0;
  width: 450px;
  max-height: 100vh;
  background: $darkgray;
  border: $border-primary;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-primary;
  backdrop-filter: blur(10px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: linear-gradient(135deg, $primary, $secondary);
    color: $white;
    
    h3 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
    }
    
    .close-btn {
      background: none;
      border: none;
      color: $white;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: $border-radius-sm;
      transition: all $transition-fast ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }

  // 标签页导航
  .tab-navigation {
    display: flex;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 1rem;
    
    .tab-btn {
      flex: 1;
      padding: 0.75rem 1rem;
      background: none;
      border: none;
      color: $gray-400;
      cursor: pointer;
      transition: all $transition-fast ease;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      
      &:hover {
        color: $white;
        background: rgba(255, 255, 255, 0.05);
      }
      
      &.active {
        color: $primary;
        border-bottom: 2px solid $primary;
      }
      
      .badge {
        background: $secondary;
        color: $white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        min-width: 20px;
        text-align: center;
      }
    }
  }
  
  // 标签页内容
  .tab-content {
    flex: 1;
    
    &:first-child {
      padding-top: 1rem;
    }
  }
  
  // 标签页头部
  .tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    
    h4 {
      margin: 0;
      color: $secondary;
      font-size: 1rem;
    }
    
    .tab-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
      
      .clear-btn {
        padding: 0.5rem;
        background: $danger;
        border: none;
        border-radius: $border-radius-sm;
        color: $white;
        cursor: pointer;
        transition: all $transition-fast ease;
        
        &:hover {
          background: darken($danger, 10%);
        }
      }
      
      .auto-play-toggle {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: $gray-400;
        font-size: 0.9rem;
        cursor: pointer;
        
        input[type="checkbox"] {
          accent-color: $primary;
        }
      }
    }
  }
}

// 搜索区域
.search-section {
  padding: 1rem;
  
  .search-input-group {
    display: flex;
    gap: 0.5rem;
    
    .search-input {
      flex: 1;
      padding: 0.75rem;
      background: $lightgray;
      border: $border-light;
      border-radius: $border-radius-md;
      color: $white;
      font-size: 0.9rem;
      
      &::placeholder {
        color: $gray-400;
      }
      
      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 2px rgba(255, 42, 109, 0.2);
      }
    }
    
    .search-btn {
      padding: 0.75rem 1rem;
      background: $primary;
      border: none;
      border-radius: $border-radius-md;
      color: $white;
      cursor: pointer;
      transition: all $transition-fast ease;
      
      &:hover {
        background: darken($primary, 10%);
        transform: translateY(-1px);
      }
    }
  }

  .quality-selector {
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: $gray-400;
    font-size: 0.9rem;

    label {
      margin-right: 0.5rem;
    }

    .quality-select {
      padding: 0.5rem 1rem;
      background: $lightgray;
      border: $border-light;
      border-radius: $border-radius-md;
      color: $white;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all $transition-fast ease;

      &:hover {
        background: $gray-700;
      }

      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 2px rgba(255, 42, 109, 0.2);
      }
    }
  }
}

// 搜索结果
.results-section {
  padding: 0 1rem 1rem;
  
  h4 {
    margin: 0 0 1rem 0;
    color: $secondary;
    font-size: 1rem;
  }
  
  .results-list {
    max-height: 256px;
    overflow-y: auto;
    
    .song-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: $lightgray;
      border-radius: $border-radius-md;
      margin-bottom: 0.5rem;
      cursor: pointer;
      transition: all $transition-fast ease;
      border: 1px solid transparent;
      height: 80px;
      
      &:hover {
        background: $gray-700;
        border-color: $primary;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(255, 42, 109, 0.2);
      }
      
      .song-cover {
        width: 50px;
        height: 50px;
        border-radius: $border-radius-sm;
        overflow: hidden;
        flex-shrink: 0;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
      
      .song-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        
        .song-title {
          font-weight: 600;
          color: $white;
          margin-bottom: 0.2rem;
          font-size: 0.9rem;
          line-height: 1.2;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .song-artist {
          font-size: 0.8rem;
          color: $secondary;
          margin-bottom: 0.2rem;
          line-height: 1.2;
        }
        
        .song-album {
          font-size: 0.75rem;
          color: $gray-400;
          margin-bottom: 0.2rem;
          line-height: 1.2;
        }

        .song-details {
          font-size: 0.7rem;
          color: $gray-400;
          display: flex;
          gap: 0.8rem;
          line-height: 1.2;
          
          .song-duration, .song-size {
            white-space: nowrap;
          }
        }
      }
      
      .song-quality {
        font-size: 0.7rem;
        color: $primary;
        background: rgba(255, 42, 109, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: $border-radius-sm;
        white-space: nowrap;
        flex-shrink: 0;
        max-width: 120px;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .song-actions {
        display: flex;
        gap: 0.5rem;
        flex-shrink: 0;
        margin-left: auto;
        
        .favorite-btn {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.3);
          color: $white;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          transition: all $transition-fast ease;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;

          &:hover {
            color: $danger;
            background: rgba(239, 68, 68, 0.2);
            border-color: $danger;
            transform: scale(1.1);
          }

          &.active {
            color: $danger;
            background: rgba(239, 68, 68, 0.2);
            border-color: $danger;
          }
        }
        
        .play-btn {
          background: $secondary;
          border: none;
          border-radius: 50%;
          width: 32px;
          height: 32px;
          color: $white;
          cursor: pointer;
          transition: all $transition-fast ease;
          
          &:hover {
            background: darken($secondary, 10%);
            transform: scale(1.1);
          }
        }
      }
    }
  }
}

// 历史记录
.history-list {
  max-height: 256px;
  overflow-y: auto;
  margin-top: 1rem;

  .history-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: $lightgray;
    border-radius: $border-radius-md;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all $transition-fast ease;
    border: 1px solid transparent;
    height: 80px;

    &:hover {
      background: $gray-700;
      border-color: $primary;
      transform: translateX(5px);
    }

    .history-cover {
      width: 50px;
      height: 50px;
      border-radius: $border-radius-sm;
      overflow: hidden;
      flex-shrink: 0;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .history-info {
      flex: 1;
      min-width: 0;
      
      .history-title {
        font-weight: 600;
        color: $white;
        margin-bottom: 0.2rem;
        font-size: 0.9rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .history-artist {
        font-size: 0.8rem;
        color: $secondary;
        margin-bottom: 0.2rem;
        line-height: 1.2;
      }

      .history-meta {
        font-size: 0.7rem;
        color: $gray-400;
        display: flex;
        gap: 0.8rem;
        line-height: 1.2;
      }
    }

    .history-actions {
      display: flex;
      gap: 0.5rem;
      margin-left: auto;
    }

    .favorite-btn {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: $white;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 50%;
      transition: all $transition-fast ease;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        color: $danger;
        background: rgba(239, 68, 68, 0.2);
        border-color: $danger;
        transform: scale(1.1);
      }

      &.active {
        color: $danger;
        background: rgba(239, 68, 68, 0.2);
        border-color: $danger;
      }
    }

    .play-btn {
      background: $secondary;
      border: none;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      color: $white;
      cursor: pointer;
      transition: all $transition-fast ease;
      
      &:hover {
        background: darken($secondary, 10%);
        transform: scale(1.1);
      }
    }
  }
}

// 收藏
.favorites-list {
  max-height: 256px;
  overflow-y: auto;
  margin-top: 1rem;

  .favorite-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: $lightgray;
    border-radius: $border-radius-md;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all $transition-fast ease;
    border: 1px solid transparent;
    height: 80px;

    &:hover {
      background: $gray-700;
      border-color: $primary;
      transform: translateX(5px);
    }

    .favorite-cover {
      width: 50px;
      height: 50px;
      border-radius: $border-radius-sm;
      overflow: hidden;
      flex-shrink: 0;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .favorite-info {
      flex: 1;
      min-width: 0;
      
      .favorite-title {
        font-weight: 600;
        color: $white;
        margin-bottom: 0.2rem;
        font-size: 0.9rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .favorite-artist {
        font-size: 0.8rem;
        color: $secondary;
        margin-bottom: 0.2rem;
        line-height: 1.2;
      }

      .favorite-meta {
        font-size: 0.7rem;
        color: $gray-400;
        display: flex;
        gap: 0.8rem;
        line-height: 1.2;
      }
    }

    .favorite-actions {
      display: flex;
      gap: 0.5rem;
      margin-left: auto;
    }

    .remove-btn {
      background: none;
      border: none;
      color: $gray-400;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 50%;
      transition: all $transition-fast ease;

      &:hover {
        color: $danger;
      }
    }

    .play-btn {
      background: $secondary;
      border: none;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      color: $white;
      cursor: pointer;
      transition: all $transition-fast ease;
      
      &:hover {
        background: darken($secondary, 10%);
        transform: scale(1.1);
      }
    }
  }
}

// 播放器区域
.player-section {
  padding: 1rem;
  border-top: $border-light;
  
  h4 {
    margin: 0 0 1rem 0;
    color: $secondary;
    font-size: 1rem;
  }
  
  .now-playing {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: $lightgray;
    border-radius: $border-radius-md;
    
    .playing-cover {
      width: 60px;
      height: 60px;
      border-radius: $border-radius-sm;
      overflow: hidden;
      flex-shrink: 0;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
    
    .playing-info {
      flex: 1;
      
      .playing-title {
        font-weight: 600;
        color: $white;
        margin-bottom: 0.25rem;
      }
      
      .playing-artist {
        font-size: 0.9rem;
        color: $secondary;
      }

      .playing-album {
        font-size: 0.8rem;
        color: $gray-400;
      }
    }
    
    .playing-controls {
      display: flex;
      gap: 0.5rem;
      
      .control-btn {
        background: $primary;
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        color: $white;
        cursor: pointer;
        transition: all $transition-fast ease;
        
        &:hover {
          background: darken($primary, 10%);
          transform: scale(1.1);
        }
      }
    }
  }

  .progress-container {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: $gray-400;
    font-size: 0.8rem;

    .progress-bar {
      flex: 1;
      height: 5px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 2.5px;
      overflow: visible;
      position: relative;
      cursor: pointer;
      
      &:hover .progress-handle {
        transform: translateY(-50%) scale(1.2);
      }
      
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, $primary, $secondary);
        border-radius: 2.5px;
        transition: width $transition-fast ease;
      }

      .progress-handle {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        background: $white;
        border: 3px solid $primary;
        border-radius: 50%;
        cursor: grab;
        user-select: none;
        z-index: 2;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: transform $transition-fast ease;
        
        &:active {
          cursor: grabbing;
          transform: translateY(-50%) scale(1.1);
        }
      }
    }

    .time-display {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.8rem;
      color: $gray-400;
      
      .current-time, .total-time {
        font-family: 'Courier New', monospace;
        font-weight: 500;
      }
      
      .current-time {
        color: $primary;
      }
      
      .total-time {
        color: $gray-500;
      }
    }
  }
}

// 加载状态
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: $gray-400;
  
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid $gray-600;
    border-top: 2px solid $primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 错误提示
.error-message {
  padding: 1rem;
  color: $danger;
  text-align: center;
  background: rgba(239, 68, 68, 0.1);
  border-radius: $border-radius-md;
  margin: 1rem;

  .error-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .retry-btn {
    padding: 0.5rem 1rem;
    background: $primary;
    border: none;
    border-radius: $border-radius-md;
    color: $white;
    cursor: pointer;
    transition: all $transition-fast ease;

    &:hover {
      background: darken($primary, 10%);
    }

    &:disabled {
      background: $gray-600;
      cursor: not-allowed;
      color: $gray-400;
    }
  }
}

// 空状态
.empty-state {
  text-align: center;
  padding: 2rem;
  color: $gray-400;
  font-size: 1rem;

  i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  p {
    margin-bottom: 0.25rem;
  }

  .empty-tip {
    font-size: 0.8rem;
    color: $gray-500;
  }
}

// 迷你播放器
.mini-player {
  position: absolute;
  top: 100px;
  left: 0;
  width: 160px;
  padding: 2px;
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  z-index: 998;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
  transform: translateY(0);

  .mini-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;

    .mini-title {
      font-weight: 600;
      color: $white;
      font-size: 0.95rem;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 0.25rem;
    }

    .mini-artist {
      font-size: 0.8rem;
      color: $secondary;
      line-height: 1.2;
    }
  }

  .mini-controls {
    display: flex;
    gap: 0.75rem;
    flex-shrink: 0;
  }

  .mini-btn {
    background: $primary;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    color: $white;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(255, 42, 109, 0.3);

    &:hover {
      background: darken($primary, 10%);
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(255, 42, 109, 0.4);
    }

    &:active {
      transform: translateY(0);
      box-shadow: 0 2px 8px rgba(255, 42, 109, 0.3);
    }

    i {
      font-size: 0.9rem;
    }
  }
}

// 歌曲操作按钮
.song-actions {
  display: flex;
  gap: 0.5rem;
  
  .favorite-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: $white;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: $border-radius-sm;
    transition: all $transition-fast ease;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      color: $danger;
      background: rgba(239, 68, 68, 0.2);
      border-color: $danger;
      transform: scale(1.1);
    }
    
    &.active {
      color: $danger;
      background: rgba(239, 68, 68, 0.2);
      border-color: $danger;
    }
  }
}
</style>

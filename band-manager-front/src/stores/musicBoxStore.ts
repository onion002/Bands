import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SongInfo } from '@/api/musicService'

export interface PlayHistoryItem extends SongInfo {
  playedAt: number // 播放时间戳
  playCount: number // 播放次数
}

export interface FavoriteItem extends SongInfo {
  addedAt: number // 收藏时间戳
}

export const useMusicBoxStore = defineStore('musicBox', () => {
  // 状态
  const playHistory = ref<PlayHistoryItem[]>([])
  const favorites = ref<FavoriteItem[]>([])
  const currentUser = ref<string | null>(null)
  const autoPlayHistory = ref(true) // 是否自动播放历史记录

  // 计算属性
  const recentPlayed = computed(() => {
    return [...playHistory.value]
      .sort((a, b) => b.playedAt - a.playedAt)
      .slice(0, 10) // 最近播放的10首
  })

  const mostPlayed = computed(() => {
    return [...playHistory.value]
      .sort((a, b) => b.playCount - a.playCount)
      .slice(0, 10) // 播放次数最多的10首
  })

  const favoriteCount = computed(() => favorites.value.length)

  // 方法
  const addToHistory = (song: SongInfo) => {
    const existingIndex = playHistory.value.findIndex(item => item.id === song.id)
    
    if (existingIndex >= 0) {
      // 更新现有记录
      playHistory.value[existingIndex].playedAt = Date.now()
      playHistory.value[existingIndex].playCount += 1
    } else {
      // 添加新记录
      playHistory.value.unshift({
        ...song,
        playedAt: Date.now(),
        playCount: 1
      })
    }

    // 限制历史记录数量
    if (playHistory.value.length > 100) {
      playHistory.value = playHistory.value.slice(0, 100)
    }

    // 保存到本地存储
    saveToLocalStorage()
  }

  const addToFavorites = (song: SongInfo) => {
    const existingIndex = favorites.value.findIndex(item => item.id === song.id)
    
    if (existingIndex === -1) {
      favorites.value.unshift({
        ...song,
        addedAt: Date.now()
      })
      saveToLocalStorage()
      return true
    }
    return false
  }

  const removeFromFavorites = (songId: number) => {
    const index = favorites.value.findIndex(item => item.id === songId)
    if (index >= 0) {
      favorites.value.splice(index, 1)
      saveToLocalStorage()
      return true
    }
    return false
  }

  const isFavorite = (songId: number) => {
    return favorites.value.some(item => item.id === songId)
  }

  const clearHistory = () => {
    playHistory.value = []
    saveToLocalStorage()
  }

  const clearFavorites = () => {
    favorites.value = []
    saveToLocalStorage()
  }

  const getLastPlayedSong = () => {
    return playHistory.value.length > 0 ? playHistory.value[0] : null
  }

  const setUser = (username: string) => {
    currentUser.value = username
    loadFromLocalStorage()
  }

  const clearUser = () => {
    currentUser.value = null
    playHistory.value = []
    favorites.value = []
  }

  // 本地存储
  const saveToLocalStorage = () => {
    if (!currentUser.value) return
    
    const key = `musicBox_${currentUser.value}`
    const data = {
      playHistory: playHistory.value,
      favorites: favorites.value,
      autoPlayHistory: autoPlayHistory.value
    }
    
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (error) {
      console.error('保存音乐盒数据失败:', error)
    }
  }

  const loadFromLocalStorage = () => {
    if (!currentUser.value) return
    
    const key = `musicBox_${currentUser.value}`
    
    try {
      const data = localStorage.getItem(key)
      if (data) {
        const parsed = JSON.parse(data)
        playHistory.value = parsed.playHistory || []
        favorites.value = parsed.favorites || []
        autoPlayHistory.value = parsed.autoPlayHistory !== undefined ? parsed.autoPlayHistory : true
      }
    } catch (error) {
      console.error('加载音乐盒数据失败:', error)
    }
  }

  const toggleAutoPlayHistory = () => {
    autoPlayHistory.value = !autoPlayHistory.value
    saveToLocalStorage()
  }

  return {
    // 状态
    playHistory,
    favorites,
    currentUser,
    autoPlayHistory,
    
    // 计算属性
    recentPlayed,
    mostPlayed,
    favoriteCount,
    
    // 方法
    addToHistory,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
    clearHistory,
    clearFavorites,
    getLastPlayedSong,
    setUser,
    clearUser,
    toggleAutoPlayHistory
  }
})

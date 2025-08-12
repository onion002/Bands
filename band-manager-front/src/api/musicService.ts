// 音乐服务 - 网易云音乐API
export interface SongInfo {
  id: number
  song: string
  singer: string
  album: string
  time: string
  quality: string
  cover: string
  interval: string
  link: string
  size: string
  kbps: string
  url: string
}

export interface SearchResponse {
  code: number
  message: string
  data: SongInfo | SongInfo[]
  time: string
  pid: number
  tips: string
}

class MusicService {
  private baseUrl = 'https://api.vkeys.cn/v2/music/netease'

  /**
   * 搜索音乐
   * @param keyword 搜索关键词
   * @param page 页码，默认1
   * @param num 每页数量，默认10
   * @param quality 最大音质，默认最大
   * @returns Promise<SongInfo[]>
   */
  async searchMusic(
    keyword: string, 
    page: number = 1, 
    num: number = 10, 
    quality: number = 9
  ): Promise<SongInfo[]> {
    const maxRetries = 3
    let lastError: Error | null = null

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const params = new URLSearchParams({
          word: keyword,
          page: page.toString(),
          num: num.toString(),
          quality: quality.toString()
        })

        const url = `${this.baseUrl}?${params}`
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data: SearchResponse = await response.json()
        
        if (data.code === 200 && data.data) {
          // 如果返回的是单个歌曲，包装成数组
          const results = Array.isArray(data.data) ? data.data : [data.data]
          
          // 如果搜索结果没有URL字段，尝试获取播放链接
          if (results.length > 0 && !results[0].url && !results[0].link) {
            const songsWithUrls = await Promise.all(
              results.map(async (song) => {
                try {
                  const songWithUrl = await this.getMusicById(song.id, quality)
                  return songWithUrl
                } catch (error) {
                  console.warn(`获取歌曲 ${song.song} 播放链接失败:`, error)
                  return song // 返回原始歌曲信息
                }
              })
            )
            return songsWithUrls
          }
          
          return results
        } else {
          // 处理API返回的错误
          let errorMessage = data.message || '搜索失败'
          
          // 根据错误类型提供更友好的提示
          if (errorMessage.includes('系统运行错误')) {
            errorMessage = '服务器暂时繁忙，请稍后重试'
          } else if (errorMessage.includes('请求过于频繁')) {
            errorMessage = '请求过于频繁，请稍等片刻再试'
          } else if (errorMessage.includes('网络错误')) {
            errorMessage = '网络连接异常，请检查网络后重试'
          }
          
          throw new Error(errorMessage)
        }
      } catch (error) {
        lastError = error as Error
        
        // 如果不是最后一次尝试，等待后重试
        if (attempt < maxRetries) {
          const waitTime = attempt * 1000 // 递增等待时间：1秒、2秒、3秒
          console.log(`搜索失败，${waitTime}ms后重试 (${attempt}/${maxRetries})`)
          await new Promise(resolve => setTimeout(resolve, waitTime))
          continue
        }
        
        // 最后一次尝试失败，抛出错误
        if (lastError.message.includes('系统运行错误')) {
          throw new Error('服务器暂时繁忙，请稍后重试')
        } else if (lastError.message.includes('fetch')) {
          throw new Error('网络连接失败，请检查网络后重试')
        } else {
          throw lastError
        }
      }
    }
    
    // 这里不应该到达，但为了类型安全
    throw lastError || new Error('搜索失败')
  }

  /**
   * 根据音乐ID获取音乐信息
   * @param id 音乐ID
   * @param quality 最大音质，默认最大
   * @returns Promise<SongInfo>
   */
  async getMusicById(id: number, quality: number = 9): Promise<SongInfo> {
    const maxRetries = 2
    let lastError: Error | null = null

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const params = new URLSearchParams({
          id: id.toString(),
          quality: quality.toString()
        })

        const url = `${this.baseUrl}?${params}`
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data: SearchResponse = await response.json()
        
        if (data.code === 200 && data.data) {
          // 确保返回的是单个歌曲
          const songData = Array.isArray(data.data) ? data.data[0] : data.data
          return songData
        } else {
          // 处理API返回的错误
          let errorMessage = data.message || '获取音乐信息失败'
          
          if (errorMessage.includes('系统运行错误')) {
            errorMessage = '服务器暂时繁忙，请稍后重试'
          }
          
          throw new Error(errorMessage)
        }
      } catch (error) {
        lastError = error as Error
        
        // 如果不是最后一次尝试，等待后重试
        if (attempt < maxRetries) {
          const waitTime = attempt * 500 // 较短的重试间隔
          console.log(`获取音乐信息失败，${waitTime}ms后重试 (${attempt}/${maxRetries})`)
          await new Promise(resolve => setTimeout(resolve, waitTime))
          continue
        }
        
        // 最后一次尝试失败，抛出错误
        if (lastError.message.includes('系统运行错误')) {
          throw new Error('服务器暂时繁忙，请稍后重试')
        } else if (lastError.message.includes('fetch')) {
          throw new Error('网络连接失败，请检查网络后重试')
        } else {
          throw lastError
        }
      }
    }
    
    throw lastError || new Error('获取音乐信息失败')
  }

  /**
   * 获取音质选项
   * @returns 音质选项数组
   */
  getQualityOptions() {
    return [
      { value: 1, label: '标准（64k）' },
      { value: 2, label: '标准（128k）' },
      { value: 3, label: 'HQ极高（192k）' },
      { value: 4, label: 'HQ极高（320k）' },
      { value: 5, label: 'SQ无损' },
      { value: 6, label: '高解析度无损（Hi-Res）' },
      { value: 7, label: '高清臻音（Spatial Audio）' },
      { value: 8, label: '沉浸环绕声（Surround Audio）' },
      { value: 9, label: '超清母带（Master）' }
    ]
  }

  /**
   * 格式化文件大小
   * @param size 文件大小字符串
   * @returns 格式化后的大小
   */
  formatFileSize(size: string): string {
    return size || '未知'
  }

  /**
   * 格式化时长
   * @param interval 时长字符串
   * @returns 格式化后的时长
   */
  formatDuration(interval: string): string {
    return interval || '未知'
  }
}

// 创建单例实例
export const musicService = new MusicService()
export default musicService

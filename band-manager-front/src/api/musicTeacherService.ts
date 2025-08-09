import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/music-teacher`,
  headers: { 'Content-Type': 'application/json' }
})

// 如果登录了就带上 token（该功能所有用户可用，不要求必须登录）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (error) => {
    const msg = error?.response?.data?.error || error.message || '请求失败'
    return Promise.reject({ error: msg })
  }
)

export interface TeacherRequest {
  message: string
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface TeacherResponse {
  answer: string
  model: string
}

export const MusicTeacherService = {
  async ask(data: TeacherRequest): Promise<TeacherResponse> {
    return api.post('/chat', data)
  },

  // 流式请求（SSE）
  async askStream(data: TeacherRequest, onToken: (chunk: string) => void, onEnd?: () => void, signal?: AbortSignal): Promise<void> {
    const url = `${API_BASE_URL}/api/music-teacher/chat?stream=1`
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
      body: JSON.stringify(data),
      signal
    })
    if (!res.ok || !res.body) throw new Error('网络错误')

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buf = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const parts = buf.split('\n\n')
      buf = parts.pop() || ''
      for (const part of parts) {
        if (!part.startsWith('data:')) continue
        const payload = part.slice(5).trim()
        if (payload === '[DONE]') { onEnd && onEnd(); return }
        try {
          const json = JSON.parse(payload)
          if (json.token) onToken(json.token)
        } catch {}
      }
    }
    onEnd && onEnd()
  }
}



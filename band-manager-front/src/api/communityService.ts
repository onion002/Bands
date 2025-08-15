import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const communityApi = axios.create({
  baseURL: `${API_BASE_URL}/api/community`,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true
})

communityApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers = config.headers || {}
    ;(config.headers as any).Authorization = `Bearer ${token}`
  }
  return config
})

communityApi.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error?.response?.data || error?.message)
)

export interface CommunityTag {
  id: number
  name: string
}

export interface CommunityUserRef {
  id: number
  username: string
  display_name?: string
  avatar_url?: string
}

export interface CommunityPost {
  id: number
  title?: string
  content: string
  image_urls: string[]
  link_urls: string[]
  like_count: number
  comment_count: number
  created_at: string
  updated_at?: string
  author?: CommunityUserRef
  tags: CommunityTag[]
  liked_by_me?: boolean
}

export interface CommunityComment {
  id: number
  content: string
  like_count: number
  is_pinned: boolean
  created_at: string
  updated_at?: string
  post_id: number
  author?: CommunityUserRef
  parent_id?: number
  liked_by_me?: boolean
}

export const CommunityService = {
  async listPosts(params?: { page?: number; page_size?: number; search?: string; sort?: 'latest' | 'hot'; tag?: string }): Promise<{ items: CommunityPost[]; total: number; page: number; pages: number }> {
    return communityApi.get('/posts', { params })
  },

  async getPost(postId: number): Promise<CommunityPost> {
    return communityApi.get(`/posts/${postId}`)
  },

  async createPost(data: { title?: string; content: string; image_urls?: string[]; link_urls?: string[]; tags?: string[] }): Promise<{ message: string; post: CommunityPost }> {
    return communityApi.post('/posts', data)
  },

  async updatePost(postId: number, data: { content: string; tags?: string[]; link_urls?: string[]; image_urls?: string[] }): Promise<{ message: string; post: CommunityPost }> {
    return communityApi.put(`/posts/${postId}`, data)
  },

  async deletePost(postId: number): Promise<{ message: string }> {
    return communityApi.delete(`/posts/${postId}`)
  },

  async likePost(postId: number): Promise<{ message: string; action: 'liked' | 'unliked'; like_count: number }> {
    return communityApi.post(`/posts/${postId}/like`)
  },

  async listComments(params: { post_id?: number; page?: number; page_size?: number } = {}): Promise<{ items: CommunityComment[]; total: number; page: number; pages: number }> {
    return communityApi.get('/comments', { params })
  },

  async createComment(data: { post_id: number; content: string; parent_id?: number }): Promise<{ message: string; comment: CommunityComment; comment_count: number }> {
    return communityApi.post('/comments', data)
  },

  async deleteComment(commentId: number): Promise<{ message: string }> {
    return communityApi.delete(`/comments/${commentId}`)
  },

  async pinComment(commentId: number): Promise<{ message: string; is_pinned: boolean }> {
    return communityApi.patch(`/comments/${commentId}/pin`)
  },

  async likeComment(commentId: number): Promise<{ message: string; action: 'liked' | 'unliked'; like_count: number }> {
    return communityApi.post(`/comments/${commentId}/like`)
  },

  async uploadImage(file: File): Promise<{ message: string; url: string }> {
    const formData = new FormData()
    formData.append('image', file)
    return communityApi.post('/upload-image', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },

  async reportContent(data: { target_type: 'post' | 'comment'; target_id: number; reason: string }): Promise<{ message: string }> {
    return communityApi.post('/reports', data)
  },

  async listReports(): Promise<{ items: any[]; total: number }> {
    return communityApi.get('/reports')
  },

  async updateReport(reportId: number, status: 'pending' | 'resolved' | 'dismissed'): Promise<{ message: string }> {
    return communityApi.patch(`/reports/${reportId}`, { status })
  },

  async listMyLikedPosts(params?: { page?: number; page_size?: number }): Promise<{ items: CommunityPost[]; total: number; page: number; pages: number }>{
    return communityApi.get('/me/likes', { params })
  }
}



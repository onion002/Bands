import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 创建axios实例
const bandApi = axios.create({
  baseURL: `${API_BASE_URL}/api/bands`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器 - 自动添加认证token
bandApi.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 添加响应拦截器
bandApi.interceptors.response.use(response => {
  return response.data;
}, error => {
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
    // 如果是401错误，可能需要重新登录
    if (error.response.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      // 可以在这里触发登出事件
    }
    return Promise.reject(error.response.data);
  } else {
    console.error('Network Error:', error.message);
    return Promise.reject({ error: '网络错误，请检查连接' });
  }
});

// 定义类型
export interface Band {
  id: number;
  name: string;
  year: number;
  genre: string;
  member_count: number;
  bio: string;
  banner_image_url?: string;
  primary_color?: string;
}

export interface GetBandsResponse {
  items: Band[];
  total: number;
}

export const BandService = {
  // 获取当前管理员的乐队（需要认证）
  async getBands(): Promise<GetBandsResponse> {
    return bandApi.get('/');
  },

  // 获取公开乐队列表
  async getPublicBands(username: string): Promise<GetBandsResponse> {
    return bandApi.get(`/public/${username}`);
  },

  // 创建乐队（需要管理员权限）
  async createBand(bandData: any) {
    return bandApi.post('/', bandData);
  },

  // 更新乐队信息
  async updateBand(id: string | number, bandData: any) {
    return bandApi.put(`/${id}`, bandData);
  },

  // 删除乐队
  async deleteBand(id: string | number) {
    return bandApi.delete(`/${id}`);
  },

  // 批量删除乐队
  async batchDeleteBands(bandIds: number[]) {
    return bandApi.post('/batch_delete', {
      band_ids: bandIds
    });
  },

  // 强制清理乐队的所有图片
  async cleanupAllBandImages(bandId: number) {
    return bandApi.post(`/${bandId}/cleanup_all_images`);
  },

  // 清理孤立图片
  async cleanupOrphanedImages() {
    return bandApi.post('/cleanup_orphaned_images');
  },

  // 强制清理所有未使用的图片
  async forceCleanupAllUnusedImages() {
    return bandApi.post('/force_cleanup_all_unused_images');
  },

  // 上传乐队图片
  async uploadBandImage(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return bandApi.post('/upload_image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};
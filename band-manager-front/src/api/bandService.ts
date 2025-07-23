import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 添加请求拦截器
axios.interceptors.request.use(config => {
  // 如果需要，可以在这里添加认证头部
  return config;
}, error => {
  return Promise.reject(error);
});

// 添加响应拦截器
axios.interceptors.response.use(response => {
  return response.data;
}, error => {
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
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
  // 获取所有乐队（分页）
  async getBands(): Promise<GetBandsResponse> {
    return axios.get(`${API_BASE_URL}/api/bands/`);
  },
  
  // 创建乐队
  async createBand(bandData: any) {
    return axios.post(`${API_BASE_URL}/api/bands/`, bandData);
  },
  
  // 更新乐队信息
  async updateBand(id: string | number, bandData: any) {
    return axios.put(`${API_BASE_URL}/api/bands/${id}`, bandData);
  },
  
  // 删除乐队
  async deleteBand(id: string | number) {
    return axios.delete(`${API_BASE_URL}/api/bands/${id}`);
  },
  
  // 上传乐队图片
  async uploadBandImage(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    return axios.post(`${API_BASE_URL}/api/bands/upload_image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};
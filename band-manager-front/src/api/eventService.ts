import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 创建axios实例
const eventApi = axios.create({
  baseURL: `${API_BASE_URL}/api/events`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器 - 自动添加认证token
eventApi.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('EventService 请求:', config.method?.toUpperCase(), config.url);
  return config;
}, error => {
  console.error('EventService 请求错误:', error);
  return Promise.reject(error);
});

// 添加响应拦截器
eventApi.interceptors.response.use(response => {
  console.log('EventService 响应:', response.status, response.data);
  return response.data;
}, error => {
  console.error('EventService 响应错误:', error);
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
    if (error.response.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
    }
    return Promise.reject(error.response.data);
  } else {
    console.error('Network Error:', error.message);
    return Promise.reject({ error: '网络错误，请检查连接' });
  }
});

// 定义API响应类型
interface EventsResponse {
  items: any[];
  total: number;
  pages: number;
  current_page: number;
}

export class EventService {
  // 获取所有演出活动（需要认证）
  static async getEvents(): Promise<EventsResponse> {
    try {
      return await eventApi.get('/');
    } catch (error) {
      console.error('获取演出活动失败:', error)
      throw error
    }
  }

  // 获取所有演出活动 (别名方法)
  static async getAllEvents(): Promise<EventsResponse> {
    return this.getEvents()
  }

  // 获取公开活动列表
  static async getPublicEvents(username: string): Promise<EventsResponse> {
    try {
      return await eventApi.get(`/public/${username}`);
    } catch (error) {
      console.error('获取公开演出活动失败:', error)
      throw error
    }
  }

  // 创建演出活动
  static async createEvent(eventData: any) {
    try {
      return await eventApi.post('/', eventData);
    } catch (error) {
      console.error('创建演出活动失败:', error)
      throw error
    }
  }

  // 更新演出活动
  static async updateEvent(id: number, eventData: any) {
    try {
      return await eventApi.put(`/${id}`, eventData);
    } catch (error) {
      console.error('更新演出活动失败:', error)
      throw error
    }
  }

  // 删除演出活动
  static async deleteEvent(id: number) {
    try {
      return await eventApi.delete(`/${id}`);
    } catch (error) {
      console.error('删除演出活动失败:', error)
      throw error
    }
  }

  // 批量删除演出活动
  static async batchDeleteEvents(eventIds: number[]) {
    try {
      return await eventApi.post('/batch_delete', {
        event_ids: eventIds
      });
    } catch (error) {
      console.error('批量删除演出活动失败:', error)
      throw error
    }
  }

  // 上传演出活动海报
  static async uploadPoster(formData: FormData) {
    try {
      console.log('EventService.uploadPoster 被调用')
      const result = await eventApi.post('/upload_poster', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('EventService.uploadPoster 响应:', result)
      return result;
    } catch (error: any) {
      console.error('EventService.uploadPoster 错误:', error)
      throw error
    }
  }
}



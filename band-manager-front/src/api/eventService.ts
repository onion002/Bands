import axios from 'axios'

// 使用相对路径，让Vite代理处理
const eventAxios = axios.create();

// 添加请求拦截器
eventAxios.interceptors.request.use(config => {
  console.log('EventService 请求:', config.method?.toUpperCase(), config.url);
  return config;
}, error => {
  console.error('EventService 请求错误:', error);
  return Promise.reject(error);
});

// 添加响应拦截器
eventAxios.interceptors.response.use(response => {
  console.log('EventService 响应:', response.status, response.data);
  return response.data;
}, error => {
  console.error('EventService 响应错误:', error);
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
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
  // 获取所有演出活动
  static async getEvents(): Promise<EventsResponse> {
    try {
      return await eventAxios.get('/api/events/');
    } catch (error) {
      console.error('获取演出活动失败:', error)
      throw error
    }
  }

  // 获取所有演出活动 (别名方法)
  static async getAllEvents(): Promise<EventsResponse> {
    return this.getEvents()
  }

  // 创建演出活动
  static async createEvent(eventData: any) {
    try {
      return await eventAxios.post('/api/events/', eventData);
    } catch (error) {
      console.error('创建演出活动失败:', error)
      throw error
    }
  }

  // 更新演出活动
  static async updateEvent(id: number, eventData: any) {
    try {
      return await eventAxios.put(`/api/events/${id}`, eventData);
    } catch (error) {
      console.error('更新演出活动失败:', error)
      throw error
    }
  }

  // 删除演出活动
  static async deleteEvent(id: number) {
    try {
      return await eventAxios.delete(`/api/events/${id}`);
    } catch (error) {
      console.error('删除演出活动失败:', error)
      throw error
    }
  }

  // 批量删除演出活动
  static async batchDeleteEvents(eventIds: number[]) {
    try {
      return await eventAxios.post('/api/events/batch_delete', {
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
      const result = await eventAxios.post('/api/events/upload_poster', formData, {
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



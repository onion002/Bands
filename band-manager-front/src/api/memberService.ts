import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 创建axios实例
const memberApi = axios.create({
  baseURL: `${API_BASE_URL}/api/members`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器 - 自动添加认证token
memberApi.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 添加响应拦截器
memberApi.interceptors.response.use(response => {
  return response.data;
}, error => {
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

// 定义成员类型
export interface Member {
  id: number;
  name: string;
  role: string;
  join_date: string;
  band_id: number;
  band_name: string;
  avatar_url?: string;
}

export interface GetMembersResponse {
  items: Member[];
  total: number;
  pages: number;
  current_page: number;
}

export interface CreateMemberData {
  name: string;
  role?: string;
  join_date: string;
  band_id: number;
  avatar_url?: string;
}

export interface UpdateMemberData {
  name?: string;
  role?: string;
  join_date?: string;
  band_id?: number;
  avatar_url?: string;
}

export const MemberService = {
  // 获取指定乐队的成员列表（分页）- 需要认证
  async getBandMembers(bandId: number, page: number = 1, perPage: number = 10): Promise<GetMembersResponse> {
    return memberApi.get(`/band/${bandId}?page=${page}&per_page=${perPage}`);
  },

  // 获取所有成员列表（用于成员管理页面）- 需要认证
  async getAllMembers(page: number = 1, perPage: number = 10): Promise<GetMembersResponse> {
    return memberApi.get(`/?page=${page}&per_page=${perPage}`);
  },

  // 获取公开成员列表
  async getPublicMembers(username: string, page: number = 1, perPage: number = 10): Promise<GetMembersResponse> {
    return memberApi.get(`/public/${username}?page=${page}&per_page=${perPage}`);
  },

  // 创建新成员
  async createMember(memberData: CreateMemberData): Promise<Member> {
    return memberApi.post('/', memberData);
  },

  // 获取成员详情
  async getMember(id: number): Promise<Member> {
    return memberApi.get(`/${id}`);
  },

  // 更新成员信息
  async updateMember(id: number, memberData: UpdateMemberData): Promise<Member> {
    return memberApi.put(`/${id}`, memberData);
  },

  // 删除成员
  async deleteMember(id: number): Promise<{ message: string }> {
    return memberApi.delete(`/${id}`);
  },

  // 上传成员头像
  async uploadMemberAvatar(memberId: number, file: File): Promise<{ success: boolean; message: string; avatar_url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    return memberApi.post(`/${memberId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

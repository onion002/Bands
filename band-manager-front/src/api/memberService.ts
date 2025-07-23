import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

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
  // 获取指定乐队的成员列表（分页）
  async getBandMembers(bandId: number, page: number = 1, perPage: number = 10): Promise<GetMembersResponse> {
    return axios.get(`${API_BASE_URL}/api/members/band/${bandId}?page=${page}&per_page=${perPage}`);
  },

  // 获取所有成员列表（用于成员管理页面）
  async getAllMembers(page: number = 1, perPage: number = 10): Promise<GetMembersResponse> {
    return axios.get(`${API_BASE_URL}/api/members/?page=${page}&per_page=${perPage}`);
  },

  // 创建新成员
  async createMember(memberData: CreateMemberData): Promise<Member> {
    return axios.post(`${API_BASE_URL}/api/members/`, memberData);
  },

  // 获取成员详情
  async getMember(id: number): Promise<Member> {
    return axios.get(`${API_BASE_URL}/api/members/${id}`);
  },

  // 更新成员信息
  async updateMember(id: number, memberData: UpdateMemberData): Promise<Member> {
    return axios.put(`${API_BASE_URL}/api/members/${id}`, memberData);
  },

  // 删除成员
  async deleteMember(id: number): Promise<{ message: string }> {
    return axios.delete(`${API_BASE_URL}/api/members/${id}`);
  },

  // 上传成员头像
  async uploadMemberAvatar(memberId: number, file: File): Promise<{ success: boolean; message: string; avatar_url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    return axios.post(`${API_BASE_URL}/api/members/${memberId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

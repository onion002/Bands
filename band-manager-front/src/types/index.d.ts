// 乐队类型定义
export interface Band {
  id: number;
  name: string;
  genre: string;
  year: number;
  member_count: number;
  banner_image_url?: string;
  bio: string;
  primary_color?: string;
}

// 成员类型定义
export interface Member {
  id: number;
  name: string;
  role: string;
  join_date: string;
  band_id: number;
  band_name: string;
  avatar_url?: string;
}

// 创建成员数据类型
export interface CreateMemberData {
  name: string;
  role?: string;
  join_date: string;
  band_id: number;
  avatar_url?: string; // 新增，允许传递头像移除信号
}

// 更新成员数据类型
export interface UpdateMemberData {
  name?: string;
  role?: string;
  join_date?: string;
  band_id?: number;
  avatar_url?: string; // 新增，允许传递头像移除信号
}

// 获取成员响应类型
export interface GetMembersResponse {
  items: Member[];
  total: number;
  pages: number;
  current_page: number;
}

// 演出活动类型定义
export interface Event {
  id: number;
  title: string;
  description?: string;
  event_date: string;
  venue?: string;
  address?: string;
  ticket_price?: number;
  capacity?: number;
  status: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  band_id: number;
  band_name: string;
  poster_image_url?: string;
}

// 创建演出活动数据类型
export interface CreateEventData {
  title: string;
  description?: string;
  event_date: string;
  venue?: string;
  address?: string;
  ticket_price?: number;
  capacity?: number;
  status?: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  band_id: number;
  poster_image_url?: string;
}

// 更新演出活动数据类型
export interface UpdateEventData {
  title?: string;
  description?: string;
  event_date?: string;
  venue?: string;
  address?: string;
  ticket_price?: number;
  capacity?: number;
  status?: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  band_id?: number;
  poster_image_url?: string;
}

// 获取演出活动响应类型
export interface GetEventsResponse {
  items: Event[];
  total: number;
  pages: number;
  current_page: number;
}

// 粒子类型定义
export interface Particle {
  size: number;
  top: number;
  left: number;
  duration: number;
  delay: number;
}
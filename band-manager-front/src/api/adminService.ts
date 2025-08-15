import { request } from './request';

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  user_type: 'user' | 'admin' | 'superadmin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AdminReport {
  id: number;
  target_type: 'post' | 'comment';
  target_id: number;
  reason: string;
  status: 'pending' | 'resolved' | 'dismissed';
  reporter_id: number;
  reporter_name?: string;
  created_at: string;
  target_content?: {
    id: number;
    author: string;
    content: string;
    post_id?: number;
    created_at?: string;
  };
}

// 用户管理
export const listUsers = (params: {
  q?: string;
  page?: number;
  page_size?: number;
  role?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  export?: string;
}) => {
  if (params.export === 'csv') {
    // CSV导出
    return request.get('/api/admin/users', {
      params,
      responseType: 'blob',
    }) as Promise<Blob>;
  }
  
  return request.get<{
    items: AdminUser[];
    total: number;
    page: number;
    pages: number;
  }>('/api/admin/users', { params });
};

export const updateUser = (id: number, data: Partial<AdminUser>) => {
  return request.patch<{ message: string; user: AdminUser }>(`/api/admin/users/${id}`, data);
};

export const deleteUser = (id: number) => {
  return request.delete<{ message: string }>(`/api/admin/users/${id}`);
};

export const resetUserPassword = (id: number, password: string) => {
  return request.patch<{ message: string }>(`/api/admin/users/${id}`, { password });
};

export const batchUpdateUsers = (user_ids: number[], data: { is_active?: boolean; user_type?: string }) => {
  return request.post<{ message: string; count: number }>('/api/admin/users/batch_update', {
    user_ids,
    ...data
  });
};

export const batchDeleteUsers = (user_ids: number[]) => {
  return request.post<{ message: string; count: number }>('/api/admin/users/batch_delete', {
    user_ids
  });
};

// 举报管理
export const listReports = (params: {
  page?: number;
  page_size?: number;
  status?: string;
}) => {
  return request.get<{
    items: AdminReport[];
    total: number;
    page: number;
    pages: number;
  }>('/api/admin/reports', { params });
};

export const updateReportStatus = (id: number, status: string) => {
  return request.patch<{ message: string; report: AdminReport }>(`/api/admin/reports/${id}`, { status });
};

// 帖子强删
export const forceDeletePost = (id: number) => {
  return request.delete<{ message: string }>(`/api/admin/posts/${id}`);
};

<template>
  <div class="admin-reports">
    <div class="page-header">
      <h1 class="page-title"><i class="fa fa-flag"></i> 举报信息</h1>
      <p class="page-subtitle">仅超级管理员可访问</p>
    </div>

    <div class="table-card">
      <div class="toolbar">
        <div class="left">
          <select v-model="statusFilter" @change="fetchReports(1)">
            <option value="">所有状态</option>
            <option value="pending">待处理</option>
            <option value="resolved">已解决</option>
            <option value="dismissed">已驳回</option>
          </select>
        </div>
        <div class="right">
          <button class="btn btn-outline" @click="fetchReports()"><i class="fa fa-sync"></i> 刷新</button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>类型</th><th>目标内容</th><th>状态</th><th>原因</th><th>举报人</th><th>时间</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.target_type === 'post' ? '帖子' : '评论' }}</td>
            <td class="target-content">
              <div v-if="r.target_content" class="content-preview">
                <div class="author">{{ r.target_content.author }}</div>
                <div class="content-text">{{ r.target_content.content }}</div>
                <div class="content-actions">
                  <button class="btn btn-sm btn-primary" @click="viewTargetContent(r)">
                    <i class="fa fa-eye"></i> 查看
                  </button>
                  <button class="btn btn-sm btn-danger" @click="deleteTargetContent(r)">
                    <i class="fa fa-trash"></i> 删除
                  </button>
                </div>
              </div>
              <div v-else class="content-deleted">内容已删除</div>
            </td>
            <td>
              <select v-model="r.status" @change="updateStatus(r)">
                <option value="pending">待处理</option>
                <option value="resolved">已解决</option>
                <option value="dismissed">已驳回</option>
              </select>
            </td>
            <td class="reason">{{ r.reason }}</td>
            <td>{{ r.reporter_name || '匿名' }}</td>
            <td>{{ formatTime(r.created_at) }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-success" v-if="r.status === 'pending'" @click="quickResolve(r)">
                <i class="fa fa-check"></i> 解决
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="pages > 1">
        <button class="btn btn-outline" :disabled="page <= 1" @click="fetchReports(page - 1)">
          <i class="fa fa-chevron-left"></i> 上一页
        </button>
        <span>第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 条</span>
        <button class="btn btn-outline" :disabled="page >= pages" @click="fetchReports(page + 1)">
          下一页 <i class="fa fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
const api = axios.create({ baseURL: `${API_BASE_URL}/api/admin`, withCredentials: true })
api.interceptors.request.use((c) => { const t = localStorage.getItem('auth_token'); if (t) { c.headers = c.headers || {}; (c.headers as any).Authorization = `Bearer ${t}` } return c })
api.interceptors.response.use(r => r.data, e => Promise.reject(e?.response?.data || e.message))

const reports = ref<any[]>([])
const page = ref(1)
const pages = ref(1)
const total = ref(0)
const statusFilter = ref('')

async function fetchReports(targetPage?: number) {
  if (targetPage) page.value = targetPage
  const params: any = {
    page: page.value,
    page_size: 20
  }
  if (statusFilter.value) params.status = statusFilter.value
  
  const res = await api.get('/reports', { params })
  reports.value = res.items
  pages.value = res.pages
  total.value = res.total
}

async function updateStatus(r: any) {
  await api.patch(`/reports/${r.id}`, { status: r.status })
}

async function quickResolve(r: any) {
  r.status = 'resolved'
  await updateStatus(r)
}

async function viewTargetContent(r: any) {
  // 跳转到社区页面查看具体内容
  if (r.target_type === 'post') {
    // 跳转到社区页面并高亮该帖子
    window.open(`/community?highlight=post_${r.target_id}`, '_blank')
  } else if (r.target_type === 'comment') {
    // 跳转到社区页面并高亮该评论
    window.open(`/community?highlight=comment_${r.target_id}&post=${r.target_content?.post_id}`, '_blank')
  }
}

async function deleteTargetContent(r: any) {
  if (!confirm(`确定删除这个${r.target_type === 'post' ? '帖子' : '评论'}吗？`)) return
  
  try {
    if (r.target_type === 'post') {
      await api.delete(`/posts/${r.target_id}`)
    } else {
      // 需要添加删除评论的API
      await axios.delete(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/community/comments/${r.target_id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` }
      })
    }
    
    // 删除成功后，将举报状态设为已解决
    await quickResolve(r)
    await fetchReports()
    alert('删除成功')
  } catch (error) {
    alert('删除失败')
  }
}

function formatTime(iso: string){ try { return new Date(iso).toLocaleString() } catch { return '' } }

onMounted(fetchReports)
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
.admin-reports { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.page-title { display:flex; align-items:center; gap:.5rem; color:$primary }
.table-card { background: rgba($darkgray,.6); border:1px solid rgba($primary,.2); border-radius:$border-radius-lg; padding:1rem; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:.75rem }
.toolbar .left { display:flex; gap:.5rem; align-items:center }
table { width:100%; border-collapse: collapse; }
th, td { padding:.5rem .75rem; border-bottom:1px solid rgba($primary,.2); vertical-align: top; }
.reason { max-width: 200px; white-space: pre-wrap; font-size: .9em; }
.target-content { max-width: 250px; }
.content-preview { 
  background: rgba($lightgray,.1); 
  border-radius: .4rem; 
  padding: .5rem; 
  margin-bottom: .25rem;
  .author { font-weight: bold; color: $primary; font-size: .85em; margin-bottom: .25rem; }
  .content-text { font-size: .9em; margin-bottom: .5rem; max-height: 60px; overflow: hidden; }
  .content-actions { display: flex; gap: .25rem; }
}
.content-deleted { color: $gray-400; font-style: italic; }
.pagination { display:flex; justify-content:center; gap:1rem; padding-top: .75rem; margin-top: .75rem; border-top: 1px solid rgba($primary,.2); }
input, select { background: rgba($lightgray,.08); border:1px solid rgba($primary,.3); color:$white; border-radius:.4rem; padding:.25rem .4rem; }
.btn { cursor:pointer; border-radius:.5rem; border:1px solid rgba($primary,.4); background:transparent; color:$primary; padding:.35rem .6rem; }
.btn-sm { padding: .2rem .4rem; font-size: .85em; }
.btn-primary { border-color: rgba($primary,.6); background: rgba($primary,.1); }
.btn-success { border-color: rgba(#10b981,.6); color: #10b981; background: rgba(#10b981,.1); }
.btn-danger { border-color: rgba(#ef4444,.5); color:#ef4444; background: rgba(#ef4444,.1); }
</style>



<template>
  <div class="admin-reports">
    <div class="page-header">
      <h1 class="page-title"><i class="fa fa-flag"></i> 举报信息</h1>
      <p class="page-subtitle">仅超级管理员可访问</p>
    </div>

    <div class="table-card">
      <div class="toolbar">
        <button class="btn btn-outline" @click="fetchReports"><i class="fa fa-sync"></i> 刷新</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>类型</th><th>对象ID</th><th>状态</th><th>原因</th><th>时间</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.target_type }}</td>
            <td>{{ r.target_id }}</td>
            <td>{{ r.status }}</td>
            <td class="reason">{{ r.reason }}</td>
            <td>{{ formatTime(r.created_at) }}</td>
            <td class="actions">
              <select v-model="r.status" @change="updateStatus(r)">
                <option value="pending">pending</option>
                <option value="resolved">resolved</option>
                <option value="dismissed">dismissed</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
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

async function fetchReports(){
  const res = await api.get('/reports')
  reports.value = res.items
}

async function updateStatus(r: any){
  await api.patch(`/reports/${r.id}`, { status: r.status })
}

function formatTime(iso: string){ try { return new Date(iso).toLocaleString() } catch { return '' } }

onMounted(fetchReports)
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
.admin-reports { max-width: 1000px; margin: 0 auto; padding: 2rem 1rem; }
.page-title { display:flex; align-items:center; gap:.5rem; color:$primary }
.table-card { background: rgba($darkgray,.6); border:1px solid rgba($primary,.2); border-radius:$border-radius-lg; padding:1rem; }
.toolbar { display:flex; justify-content:flex-end; margin-bottom:.75rem }
table { width:100%; border-collapse: collapse; }
th, td { padding:.5rem .75rem; border-bottom:1px solid rgba($primary,.2); vertical-align: top; }
.reason { max-width: 380px; white-space: pre-wrap; }
input, select { background: rgba($lightgray,.08); border:1px solid rgba($primary,.3); color:$white; border-radius:.4rem; padding:.25rem .4rem; }
.btn { cursor:pointer; border-radius:.5rem; border:1px solid rgba($primary,.4); background:transparent; color:$primary; padding:.35rem .6rem; }
</style>



<template>
  <div class="admin-users">
    <div class="page-header">
      <h1 class="page-title"><i class="fa fa-users-cog"></i> 用户管理</h1>
      <p class="page-subtitle">仅超级管理员可访问</p>
    </div>

    <div class="table-card">
      <div class="toolbar">
        <div class="left">
          <input v-model="q" placeholder="搜索用户名/邮箱/显示名" @keyup.enter="fetchUsers(1)" />
          <button class="btn btn-outline" @click="fetchUsers(1)"><i class="fa fa-search"></i> 搜索</button>
        </div>
        <div class="right">
          <button class="btn btn-outline" @click="fetchUsers()"><i class="fa fa-sync"></i> 刷新</button>
        </div>
      </div>
      <div class="bulk-bar">
        <label><input type="checkbox" :checked="allChecked" @change="toggleAll($event)" /> 全选</label>
        <button class="btn btn-outline btn-sm" :disabled="selectedIds.length===0" @click="bulkSetActive(true)">启用</button>
        <button class="btn btn-outline btn-sm" :disabled="selectedIds.length===0" @click="bulkSetActive(false)">禁用</button>
        <button class="btn btn-outline btn-sm" :disabled="selectedIds.length===0" @click="bulkSetRole('user')">设为用户</button>
        <button class="btn btn-outline btn-sm" :disabled="selectedIds.length===0" @click="bulkSetRole('admin')">设为管理员</button>
        <button class="btn btn-danger btn-sm" :disabled="selectedIds.length===0" @click="bulkDelete()"><i class="fa fa-trash"></i> 批量删除</button>
      </div>
      <table>
        <thead>
          <tr>
            <th width="36"></th><th>ID</th><th>用户名</th><th>类型</th><th>显示名</th><th>邮箱</th><th>状态</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td><input type="checkbox" :value="u.id" v-model="selectedIds" /></td>
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>
              <select v-model="u.user_type" @change="saveUser(u)">
                <option value="user">user</option>
                <option value="admin">admin</option>
                <option value="superadmin">superadmin</option>
              </select>
            </td>
            <td><input v-model="u.display_name" @blur="saveUser(u)" /></td>
            <td>{{ u.email }}</td>
            <td>
              <label><input type="checkbox" v-model="u.is_active" @change="saveUser(u)" /> 活跃</label>
            </td>
            <td>
              <div class="row-actions">
                <button class="btn btn-outline btn-sm" @click="promptResetPassword(u)"><i class="fa fa-key"></i> 重置密码</button>
                <button class="btn btn-danger btn-sm" @click="removeUser(u)"><i class="fa fa-trash"></i> 删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="pages>1">
        <button class="btn btn-outline" :disabled="page<=1" @click="fetchUsers(page-1)"><i class="fa fa-chevron-left"></i> 上一页</button>
        <span>第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 条</span>
        <button class="btn btn-outline" :disabled="page>=pages" @click="fetchUsers(page+1)">下一页 <i class="fa fa-chevron-right"></i></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
const api = axios.create({ baseURL: `${API_BASE_URL}/api/admin`, withCredentials: true })
api.interceptors.request.use((c) => { const t = localStorage.getItem('auth_token'); if (t) { c.headers = c.headers || {}; (c.headers as any).Authorization = `Bearer ${t}` } return c })
api.interceptors.response.use(r => r.data, e => Promise.reject(e?.response?.data || e.message))

const users = ref<any[]>([])
const q = ref('')
const page = ref(1)
const pages = ref(1)
const total = ref(0)
const selectedIds = ref<number[]>([])
const allChecked = computed(() => users.value.length>0 && selectedIds.value.length === users.value.length)

async function fetchUsers(targetPage?: number){
  if (targetPage) page.value = targetPage
  const res = await api.get('/users', { params: { q: q.value, page: page.value, page_size: 20 } })
  users.value = res.items
  pages.value = res.pages
  total.value = res.total
  // 校正选择框
  selectedIds.value = selectedIds.value.filter(id => users.value.some(u => u.id === id))
}

async function saveUser(u: any){
  await api.patch(`/users/${u.id}`, { user_type: u.user_type, display_name: u.display_name, is_active: u.is_active })
}

async function removeUser(u: any){
  if (!confirm(`确定删除用户 ${u.username} 吗？`)) return
  await api.delete(`/users/${u.id}`)
  await fetchUsers()
}

onMounted(fetchUsers)

function promptResetPassword(u: any){
  const pwd = prompt(`给用户 ${u.username} 设置新密码：`)
  if (!pwd) return
  api.patch(`/users/${u.id}`, { password: pwd }).then(fetchUsers)
}

function toggleAll(e: Event){
  const checked = (e.target as HTMLInputElement).checked
  if (checked) selectedIds.value = users.value.map(u => u.id)
  else selectedIds.value = []
}

function bulkSetActive(active: boolean){
  if (selectedIds.value.length===0) return
  api.post('/users/batch_update', { user_ids: selectedIds.value, is_active: active }).then(() => fetchUsers())
}

function bulkSetRole(role: 'user'|'admin'|'superadmin'){
  if (selectedIds.value.length===0) return
  if (role === 'superadmin' && !confirm('将用户设为超级管理员会使其获得最高权限，且系统只能有一个超级管理员。确认继续？')) return
  api.post('/users/batch_update', { user_ids: selectedIds.value, user_type: role }).then(() => fetchUsers())
}

function bulkDelete(){
  if (selectedIds.value.length===0) return
  if (!confirm(`确定删除选中的 ${selectedIds.value.length} 个用户吗？`)) return
  api.post('/users/batch_delete', { user_ids: selectedIds.value }).then(() => fetchUsers())
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
.admin-users { max-width: 1000px; margin: 0 auto; padding: 2rem 1rem; }
.page-title { display:flex; align-items:center; gap:.5rem; color:$primary }
.table-card { background: rgba($darkgray,.6); border:1px solid rgba($primary,.2); border-radius:$border-radius-lg; padding:1rem; }
.toolbar { display:flex; justify-content:space-between; align-items:center; gap:.75rem; margin-bottom:.75rem }
.toolbar .left { display:flex; gap:.5rem; align-items:center }
.bulk-bar { display:flex; align-items:center; gap:.5rem; margin-bottom:.5rem; color:$gray-300 }
table { width:100%; border-collapse: collapse; }
th, td { padding:.5rem .75rem; border-bottom:1px solid rgba($primary,.2); }
input, select { background: rgba($lightgray,.08); border:1px solid rgba($primary,.3); color:$white; border-radius:.4rem; padding:.25rem .4rem; }
.btn { cursor:pointer; border-radius:.5rem; border:1px solid rgba($primary,.4); background:transparent; color:$primary; padding:.35rem .6rem; }
.btn-danger { border-color: rgba(#ef4444,.5); color:#ef4444 }
.pagination { display:flex; justify-content:center; gap:1rem; padding-top: .75rem; }
.row-actions { display:flex; gap:.5rem; }
</style>



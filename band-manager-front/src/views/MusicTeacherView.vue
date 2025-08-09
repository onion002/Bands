<template>
  <div class="teacher-management">
    <!-- 主布局外壳：左侧会话盒子 + 右侧内容盒子 -->
    <div class="shell" :class="{ collapsed: sidebarCollapsed }">
      <!-- 侧边栏（会话盒子） -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="title">
            <i class="fa fa-comments"></i>
            <span v-if="!sidebarCollapsed">会话列表</span>
          </div>
          <button class="collapse-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '展开' : '收起'">
            <i :class="sidebarCollapsed ? 'fa fa-angles-right' : 'fa fa-angles-left'"></i>
          </button>
        </div>

        <div v-if="!sidebarCollapsed" class="search-box">
          <input v-model="sessionSearch" class="form-control search-input" placeholder="搜索会话..." />
        </div>

        <button class="new-chat-btn" @click="newChat" :title="sidebarCollapsed ? '新建对话' : ''">
          <i class="fa fa-plus"></i>
          <span v-if="!sidebarCollapsed">新建对话</span>
        </button>

        <ul class="session-list scrollbar-hide" :class="{ compact: sidebarCollapsed }">
          <li v-for="s in visibleSessions" :key="s.id" :class="{ active: s.id === activeSessionId }">
            <button class="session-item" @click="selectSession(s.id)" :title="sidebarCollapsed ? (s.title || '未命名对话') : ''">
              <i class="fa fa-message"></i>
              <span v-if="!sidebarCollapsed" class="text">{{ s.title || '未命名对话' }}</span>
            </button>
            <div v-if="!sidebarCollapsed" class="item-actions">
              <button class="icon-btn" @click.stop="renameSession(s.id)" title="重命名"><i class="fa fa-pen"></i></button>
              <button class="icon-btn" @click.stop="togglePin(s.id)" :title="s.pinned ? '取消置顶' : '置顶'">
                <i :class="s.pinned ? 'fa fa-thumbtack' : 'fa fa-thumbtack'" style="transform: rotate(45deg);"></i>
              </button>
              <button class="icon-btn delete" @click.stop="deleteSession(s.id)" title="删除"><i class="fa fa-trash"></i></button>
            </div>
          </li>
        </ul>
      </aside>

      <!-- 右侧内容盒子 -->
      <div class="content-box">
        <!-- 页头：与乐队管理一致的结构与层级 -->
        <div class="page-header">
          <h1>
            <span class="gradient-text">音乐老师</span>
          </h1>
          <p>灵感 · 编曲 · 练习 · 演出 · 运营 —— 为你的乐队提供专业建议</p>
        </div>

        <!-- 操作工具栏（风格对齐乐队管理） -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button class="btn btn-primary" @click="newChat">
              <i class="fa fa-plus"></i>
              新建对话
            </button>
            <button class="btn btn-outline" :disabled="messages.length === 0" @click="clearChat">
              <i class="fa fa-trash"></i>
              清空对话
            </button>
          </div>

          <div class="toolbar-right">
            <div class="model-select">
              <label>模型</label>
              <select v-model="model" class="form-control">
                <option value="deepseek-chat">DeepSeek Chat</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 会话区 -->
        <section class="conversation-panel">
        <!-- 欢迎建议：仿 Deepseek 底部建议卡片，但使用本站深色风格 -->
        <div v-if="messages.length === 0" class="suggestions">
          <button v-for="s in suggestionChips" :key="s" class="chip" @click="useSuggestion(s)">
            {{ s }}
          </button>
        </div>

        <!-- 会话卡片（深色卡片 + 边框 + 阴影） -->
        <div class="chat-card card card-dark">
          <!-- 错误条 -->
          <div v-if="errorMsg" class="error-bar">
            <i class="fa fa-exclamation-triangle"></i>
            <span>{{ errorMsg }}</span>
            <button class="btn btn-outline btn-sm" @click="retryLast">重试</button>
            <button class="icon-btn" @click="errorMsg=''" title="关闭"><i class="fa fa-times"></i></button>
          </div>
          <div ref="chatWindowRef" class="chat-window scrollbar-hide">
            <div v-if="messages.length === 0 && !loading" class="welcome-screen">
              <h1 class="hi">Hi, {{ displayName || 'Musician' }}</h1>
            </div>

            <div
              v-for="(m, idx) in messages"
              :key="idx"
              class="msg"
              :class="m.role"
            >
              <div class="avatar">
                <i :class="m.role === 'user' ? 'fa fa-user' : 'fa fa-music'"></i>
              </div>
              <div class="bubble">
                <div class="bubble-toolbar" v-if="m.role==='assistant'">
                  <button class="icon-btn" title="复制"
                          @click="copyText(m.content)"><i class="fa fa-copy"></i></button>
                </div>
                <div class="bubble-content" v-html="renderMarkdown(m.content)"></div>
              </div>
            </div>

            <div v-if="loading" class="msg assistant loading">
              <div class="avatar"><i class="fa fa-music"></i></div>
              <div class="bubble"><i class="fa fa-spinner fa-spin"></i> 正在思考…</div>
            </div>
          </div>

          <!-- 作文区（底部工具条与发送按钮） -->
          <div class="composer">
            <textarea
              v-model="composer"
              class="composer-input form-control"
              placeholder="描述你的问题… Enter 发送 / Shift+Enter 换行"
              rows="3"
              @keydown.enter.exact.prevent="send"
              @keydown.shift.enter.stop
            />
            <div class="composer-actions">
              <div class="knobs">
                <label>
                  温度
                  <input type="range" min="0" max="1" step="0.1" v-model.number="temperature" />
                  <span class="value">{{ temperature.toFixed(1) }}</span>
                </label>
                <label>
                  最大字数
                  <input type="number" min="200" max="4000" step="100" v-model.number="maxTokens" />
                </label>
              </div>
              <button v-if="!isStreaming" class="btn btn-primary" :disabled="loading || !composer.trim()" @click="send">
                <i :class="loading ? 'fa fa-spinner fa-spin' : 'fa fa-paper-plane'"></i>
                发送
              </button>
              <button v-else class="btn btn-danger" @click="stopGenerating">
                <i class="fa fa-stop"></i>
                停止
              </button>
            </div>
          </div>
        </div>
      </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed, watch } from 'vue'
import { MusicTeacherService } from '@/api/musicTeacherService'
// @ts-ignore - 使用运行时渲染，无需类型
import { marked } from 'marked'
// @ts-ignore
import hljs from 'highlight.js'

type Role = 'user' | 'assistant'
interface ChatMessage { role: Role; content: string }

const chatWindowRef = ref<HTMLDivElement | null>(null)
const messages = ref<ChatMessage[]>([])
const composer = ref('')
const loading = ref(false)
const model = ref('deepseek-chat')
const temperature = ref(0.7)
const maxTokens = ref(1200)
// 流式状态
// 注意：isStreaming 已在上方声明，这里避免重复声明

// 侧边栏会话列表
interface Session { id: string; title: string; messages: ChatMessage[]; pinned?: boolean }
const sessions = ref<Session[]>([])
const activeSessionId = ref<string>('')
const sidebarCollapsed = ref(false)

const suggestionChips = [
  '如何为摇滚歌曲设计更有力量的鼓点？',
  '帮我制定一周吉他练习计划（进阶）',
  '我们要办校园演出，给出舞台流程与注意事项',
  '写一段电子/流行混合风格的主歌和弦走向',
]

// 显示名（从本地用户信息或匿名）
const storedUser = localStorage.getItem('user_info')
const displayName = storedUser ? (JSON.parse(storedUser).display_name || JSON.parse(storedUser).username) : ''

// 搜索与排序（置顶优先）
const sessionSearch = ref('')
const visibleSessions = computed(() => {
  const keyword = sessionSearch.value.trim().toLowerCase()
  const list = sessions.value
    .slice()
    .sort((a: any, b: any) => (Number(!!b.pinned) - Number(!!a.pinned)))
  if (!keyword) return list
  return list.filter(s => (s.title || '').toLowerCase().includes(keyword))
})

function toHtml(text: string) {
  return (text || '').replace(/\n/g, '<br/>')
}

// Markdown 渲染器
marked.setOptions({
  // @ts-ignore
  highlight(code: any, lang: any) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

function renderMarkdown(md: string) {
  try { return marked.parse(md || '') as string } catch { return md }
}

function scrollToBottom() {
  nextTick(() => {
    const el = chatWindowRef.value
    if (!el) return
    el.scrollTop = el.scrollHeight
  })
}

function newChat() {
  const id = `${Date.now()}`
  const session: Session = { id, title: '新对话', messages: [], pinned: false as any }
  sessions.value.unshift(session)
  activeSessionId.value = id
  messages.value = session.messages
  composer.value = ''
  persist()
}

function clearChat() {
  messages.value.splice(0, messages.value.length)
  const session = sessions.value.find(s => s.id === activeSessionId.value)
  if (session) session.messages = messages.value
  persist()
}

function useSuggestion(s: string) {
  composer.value = s
}

const isStreaming = ref(false)
const abortController = ref<AbortController | null>(null)
const errorMsg = ref('')
let lastMsgSnapshot = ''
async function send() {
  const content = composer.value.trim()
  if (!content || loading.value) return
  messages.value.push({ role: 'user', content })
  // 更新会话标题（首条消息时）
  const session = sessions.value.find(s => s.id === activeSessionId.value)
  if (session && session.title === '新对话') session.title = content.slice(0, 18)
  composer.value = ''
  scrollToBottom()

  try {
    loading.value = true
    isStreaming.value = true
    messages.value.push({ role: 'assistant', content: '' })
    const idx = messages.value.length - 1
    lastMsgSnapshot = content
    const controller = new AbortController()
    abortController.value = controller
    await MusicTeacherService.askStream(
      { message: content, model: model.value, temperature: temperature.value, max_tokens: maxTokens.value },
      (chunk) => { messages.value[idx].content += chunk; scrollToBottom() },
      () => { isStreaming.value = false; abortController.value = null; errorMsg.value = '' },
      controller.signal
    )
  } catch (e: any) {
    const msg = e?.error || e?.message || '请求失败'
    errorMsg.value = msg
    messages.value.push({ role: 'assistant', content: msg })
  } finally {
    loading.value = false
    scrollToBottom()
    persist()
  }
}

function stopGenerating() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
    isStreaming.value = false
  }
}

async function retryLast() {
  if (!lastMsgSnapshot) return
  composer.value = lastMsgSnapshot
  errorMsg.value = ''
  await send()
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text || '')
  } catch {
    // ignore
  }
}

function selectSession(id: string) {
  activeSessionId.value = id
  const session = sessions.value.find(s => s.id === id)
  messages.value = session ? session.messages : []
}

function deleteSession(id: string) {
  const idx = sessions.value.findIndex(s => s.id === id)
  if (idx === -1) return
  sessions.value.splice(idx, 1)
  if (activeSessionId.value === id) {
    if (sessions.value.length) {
      activeSessionId.value = sessions.value[0].id
      messages.value = sessions.value[0].messages
    } else {
      activeSessionId.value = ''
      messages.value = []
    }
  }
  persist()
}

function toggleSidebar() { sidebarCollapsed.value = !sidebarCollapsed.value }

function renameSession(id: string) {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  const name = prompt('重命名会话', s.title || '')
  if (name !== null) {
    s.title = name.trim() || '未命名对话'
    persist()
  }
}

function togglePin(id: string) {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  ;(s as any).pinned = !(s as any).pinned
  // 调整顺序：置顶到列表前
  sessions.value = sessions.value
    .slice()
    .sort((a: any, b: any) => (Number(!!b.pinned) - Number(!!a.pinned)))
  persist()
}

// 本地持久化
const STORAGE_KEY = 'music_teacher_sessions_v1'
function persist() {
  const data = {
    sessions: sessions.value,
    activeId: activeSessionId.value
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

function restore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return false
    const data = JSON.parse(raw)
    if (!data || !Array.isArray(data.sessions)) return false
    sessions.value = data.sessions
    activeSessionId.value = data.activeId || (sessions.value[0]?.id || '')
    const session = sessions.value.find(s => s.id === activeSessionId.value)
    messages.value = session ? session.messages : []
    return true
  } catch { return false }
}

if (!restore()) {
  // 初始化默认会话
  newChat()
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.teacher-management {
  min-height: 100vh;
  padding: 0; // 外壳负责内边距
}

.page-header {
  margin-bottom: 1.25rem;
  h1 { margin: 0 0 .25rem 0; }
  p { color: $gray-400; margin: 0; }
}

.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.25rem; padding: 1rem; background: rgba($darkgray, 0.7);
  border: $border-light; border-radius: $border-radius-xl; backdrop-filter: blur(8px);
  .toolbar-left { display: flex; gap: 1rem; align-items: center; }
  .toolbar-right { display: flex; gap: 1rem; align-items: center; }
  .model-select { display: flex; align-items: center; gap: .5rem; label { color: $gray-300; font-size: .875rem; } }
  @media (max-width: 768px) { flex-direction: column; gap: 1rem; }
}

.suggestions {
  display: flex; flex-wrap: wrap; gap: .75rem; margin-bottom: 1rem;
  .chip {
    background: rgba($lightgray, .35);
    border: 1px solid rgba($white, .1);
    color: $gray-300;
    padding: .6rem .9rem; border-radius: 12px; cursor: pointer; transition: all $transition-fast ease;
    &:hover { color: $white; border-color: rgba($primary, .5); box-shadow: $shadow-primary; }
  }
}

.shell { display: grid; grid-template-columns: 260px 1fr; gap: 0; }
.shell.collapsed { grid-template-columns: 72px 1fr; }

.sidebar { background: #101010; border-right: 1px solid #2a2a2a; min-height: 100vh; position: sticky; top: 0; }
.sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: .75rem .75rem; border-bottom: 1px solid #2a2a2a; 
  .title { display: flex; align-items: center; gap: .5rem; color: $white; font-weight: 600; }
  .collapse-btn { background: transparent; border: none; color: #bbb; cursor: pointer; }
}
.search-box { display: flex; align-items: center; gap: .5rem; padding: .5rem .75rem .25rem;
  .search-input { width: 100%; }
}
.new-chat-btn { margin: .75rem; width: calc(100% - 1.5rem); display: flex; align-items: center; gap: .5rem; justify-content: center; background: linear-gradient(to right, #e53935, #e35d5b); color: white; border: none; padding: .55rem .75rem; border-radius: 10px; font-weight: 600; cursor: pointer; }
.session-list { list-style: none; margin: 0 .5rem .75rem .5rem; padding: 0; display: flex; flex-direction: column; gap: .35rem; max-height: calc(100vh - 240px); overflow-y: auto; }
.session-list.compact { margin: .5rem; gap: .5rem; 
  li { grid-template-columns: 1fr; }
  .delete-btn { display: none; }
  .session-item { justify-content: center; }
}
.session-list li { display: grid; grid-template-columns: 1fr auto; align-items: center; border-radius: 8px; }
.session-list li.active { background: rgba(229,57,53,0.08); }
.session-item { text-align: left; background: transparent; border: none; color: #ddd; padding: .5rem .5rem; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: .5rem; width: 100%; }
.item-actions { display: flex; gap: .25rem; padding-right: .25rem; }
.icon-btn { background: transparent; border: none; color: #888; cursor: pointer; padding: .25rem .35rem; border-radius: 6px; transition: all $transition-fast ease; &:hover { color: $primary; background: rgba($primary, .08);} }

.welcome-screen { display: grid; place-items: center; min-height: 360px; 
  .hi { font-weight: 800; font-size: 2.2rem; letter-spacing: .3px; color: $white; }
  :deep(pre code) { display: block; padding: 1rem; border-radius: 10px; background: #0f111a; border: 1px solid #222; }
}

.content-box { padding: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; }
.conversation-panel { min-width: 0; }

.chat-card { padding: 0; }
.chat-window { padding: 1rem; max-height: calc(100vh - 340px); overflow-y: auto; }
/* 滚动锚点优化：用户向上滚动浏览时不强制跟随到底部 */
.chat-window:hover { scroll-behavior: smooth; }

/* 错误条 */
.error-bar { display: flex; align-items: center; gap: .5rem; padding: .6rem .75rem; border: 1px solid rgba(#ef4444, .4); border-radius: 10px; background: rgba(#ef4444, .1); color: #ffb4b4; margin: .5rem 1rem 0; }
.error-bar .icon-btn { margin-left: auto; }

.empty { text-align: center; color: $gray-400; padding: 2rem 0;
  .empty-icon { font-size: 2.2rem; color: $primary; margin-bottom: .5rem; }
}

.msg { display: flex; gap: 12px; margin-bottom: 12px; &.user { flex-direction: row-reverse; } }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: #222; color: #eee; display: flex; align-items: center; justify-content: center; }
.bubble { max-width: 75%; padding: 10px 12px; border-radius: 12px; line-height: 1.6; color: #e5e5e5; background: #1b1b1b; border: 1px solid #2a2a2a; box-shadow: inset 0 1px 0 rgba(255,255,255,.04); }
.bubble { position: relative; }
.bubble .bubble-toolbar { position: absolute; top: 6px; right: 6px; opacity: 0.6; }
.bubble .bubble-content { margin-top: 20px; }
.assistant .bubble { background: #121212; border-color: #2a2a2a; }
.user .bubble { background: rgba($primary, .15); border-color: rgba($primary, .35); }

.composer { border-top: 1px solid #2a2a2a; padding: .75rem; background: rgba(255,255,255,.02); }
.composer-input { width: 100%; resize: vertical; min-height: 120px; }
.composer-actions { display: flex; align-items: center; gap: .75rem; margin-top: .5rem; }
.knobs { display: flex; align-items: center; gap: 14px; color: $gray-400; label { display: flex; align-items: center; gap: 6px; } }

/* 深色主题输入样式（仅作用于本组件） */
.content-box .form-control,
.sidebar .search-input,
.composer-input {
  background: rgba($lightgray, 0.25);
  border: 1px solid rgba($lightgray, 0.5);
  color: $white;
  border-radius: $border-radius-md;
  transition: all $transition-normal ease;
}

.content-box .form-control:focus,
.sidebar .search-input:focus,
.composer-input:focus {
  outline: none;
  border-color: $primary;
  box-shadow: 0 0 0 3px rgba($primary, 0.15);
  background: rgba($lightgray, 0.35);
}

.content-box .form-control::placeholder,
.sidebar .search-input::placeholder,
.composer-input::placeholder { color: $gray-400; }

/* select 和 number 输入的适配色 */
.content-box select.form-control,
.content-box input[type='number'].form-control {
  background: rgba($lightgray, 0.25);
  color: $white;
  border: 1px solid rgba($lightgray, 0.5);
}

.content-box select.form-control:focus,
.content-box input[type='number'].form-control:focus { border-color: $primary; box-shadow: 0 0 0 3px rgba($primary, 0.15); }

</style>

 
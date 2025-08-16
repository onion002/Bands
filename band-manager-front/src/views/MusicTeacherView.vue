<template>
  <div class="teacher-management" @keydown="handleKeydown" tabindex="0">
    <!-- 主布局外壳：左侧会话盒子 + 右侧内容盒子 -->
    <div class="shell" :class="{ collapsed: sidebarCollapsed }">
      <!-- 侧边栏（会话盒子） -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="title">
            <i class="fa fa-comments"></i>
            <span v-if="!sidebarCollapsed">会话列表</span>
          </div>
          <div v-if="!sidebarCollapsed" class="user-info">
            <span class="user-name">{{ displayName }}</span>
            <span class="session-count">({{ sessions.length }}个会话)</span>
          </div>
          <button class="collapse-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '展开' : '收起'">
            <i :class="sidebarCollapsed ? 'fa fa-angles-right' : 'fa fa-angles-left'"></i>
          </button>
          <!-- 移动端侧边栏切换按钮 -->
          <button class="mobile-toggle-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '显示会话列表' : '隐藏会话列表'">
            <i class="fa fa-bars"></i>
          </button>
        </div>

        <div v-if="!sidebarCollapsed" class="search-box">
          <input v-model="sessionSearch" class="form-control search-input" placeholder="搜索会话..." />
        </div>

        <button class="new-chat-btn" @click="newChat" :title="sidebarCollapsed ? '新建对话' : ''">
          <i class="fa fa-plus"></i>
          <span v-if="!sidebarCollapsed">新建对话</span>
        </button>

        <ul class="session-list" :class="{ compact: sidebarCollapsed }">
          <li v-for="s in visibleSessions" :key="s.id" :class="{ active: s.id === activeSessionId }">
            <button class="session-item" @click="selectSession(s.id)" :title="sidebarCollapsed ? (s.title || '未命名对话') : ''">
              <i class="fa fa-message"></i>
              <div v-if="!sidebarCollapsed" class="session-info">
                <span class="text">{{ s.title || '未命名对话' }}</span>
                <span class="time">{{ formatSessionTime(s.lastUpdated) }}</span>
              </div>
            </button>
            <div v-if="!sidebarCollapsed" class="item-actions">
              <button class="icon-btn" @click.stop="renameSession(s.id)" title="重命名"><i class="fa fa-pen"></i></button>
              <button class="icon-btn" @click.stop="togglePin(s.id)" :title="s.pinned ? '取消置顶' : '置顶'">
                <i :class="s.pinned ? 'fa fa-thumbtack' : 'fa fa-thumbtack'" style="transform: rotate(45deg);"></i>
              </button>
              <button class="icon-btn delete" @click.stop="deleteSession(s.id)" title="删除"><i class="fa fa-trash"></i></button>
            </div>
          </li>
          <!-- 空状态提示 -->
          <li v-if="visibleSessions.length === 0" class="empty-sessions">
            <div class="empty-sessions-content">
              <i class="fa fa-comments-o"></i>
              <span v-if="!sidebarCollapsed">暂无会话</span>
            </div>
          </li>
        </ul>
      </aside>

      <!-- 右侧内容盒子 -->
      <div class="content-box">
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
            
            <!-- 聊天消息容器 -->
            <div class="chat-messages-container">
              <div ref="chatWindowRef" class="chat-window" @scroll="checkScrollPosition">
                <div v-if="messages.length === 0 && !loading" class="welcome-screen">
                  <div class="welcome-avatar">
                    <i class="fa fa-music"></i>
                  </div>
                  <h1 class="welcome-title">Hi, {{ displayName || 'Musician' }} 🎵</h1>
                  <p class="welcome-subtitle">我是你的AI音乐顾问，专精于音乐理论、演奏技巧和创作指导</p>
                  <div class="welcome-features">
                    <div class="feature-item">
                      <i class="fa fa-guitar"></i>
                      <span>乐器演奏指导</span>
                    </div>
                    <div class="feature-item">
                      <i class="fa fa-music"></i>
                      <span>音乐理论解析</span>
                    </div>
                    <div class="feature-item">
                      <i class="fa fa-users"></i>
                      <span>乐队合作建议</span>
                    </div>
                    <div class="feature-item">
                      <i class="fa fa-lightbulb"></i>
                      <span>创作灵感启发</span>
                    </div>
                  </div>
                  <div class="welcome-prompt">
                    <i class="fa fa-arrow-down bounce"></i>
                    <span>从下方的建议问题开始，或直接输入你的音乐疑问</span>
                  </div>
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
                      <button class="icon-btn" title="重新生成"
                              @click="regenerateResponse(idx)"><i class="fa fa-refresh"></i></button>
                      <button class="icon-btn" title="导出对话"
                              @click="exportConversation"><i class="fa fa-download"></i></button>
                    </div>
                    <div class="bubble-content" v-html="renderMarkdown(m.content)"></div>
                    
                    <!-- AI回答后的建议问题 -->
                    <div v-if="m.role === 'assistant' && m.suggestions && m.suggestions.length > 0" class="follow-up-suggestions">
                      <div class="suggestions-header">
                        <i class="fa fa-lightbulb"></i>
                        <span>相关问题</span>
                      </div>
                      <div class="suggestions-list">
                        <button 
                          v-for="suggestion in m.suggestions" 
                          :key="suggestion"
                          class="suggestion-chip"
                          @click="useSuggestion(suggestion)"
                        >
                          {{ suggestion }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="loading" class="msg assistant loading">
                  <div class="avatar"><i class="fa fa-music"></i></div>
                  <div class="bubble">
                    <div class="loading-content">
                      <i class="fa fa-spinner fa-spin"></i> 
                      <span>正在思考…</span>
                      <div class="loading-dots">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Toast 提示 -->
            <div v-if="toast.show" class="toast" :class="toast.type">
              <i :class="toast.icon"></i>
              <span>{{ toast.message }}</span>
            </div>

            <!-- 固定的输入区域 -->
            <div class="composer-container">
              <div class="composer">
                <!-- 快速操作栏 -->
                <div class="quick-actions-bar" v-if="messages.length > 0">
                  <button class="quick-action-btn" @click="clearChat" title="清空对话">
                    <i class="fa fa-trash"></i>
                  </button>
                  <button class="quick-action-btn" @click="exportConversation" title="导出对话">
                    <i class="fa fa-download"></i>
                  </button>
                  <button class="quick-action-btn" @click="toggleSettings" title="显示/隐藏设置">
                    <i class="fa fa-cog"></i>
                  </button>
                </div>
                
                <!-- 输入区域 -->
                <div class="input-area">
                  <textarea
                    v-model="composer"
                    class="composer-input form-control"
                    :placeholder="inputPlaceholder"
                    rows="3"
                    @keydown.enter.exact.prevent="send"
                    @keydown.shift.enter.stop
                    @focus="onInputFocus"
                    @blur="onInputBlur"
                  />
                  <!-- 字符计数提示 -->
                  <div class="char-counter" v-if="composer.length > 0">
                    <span :class="{ 'warning': composer.length > 1000, 'danger': composer.length > 2000 }">
                      {{ composer.length }} 字符
                    </span>
                  </div>
                </div>
                
                <div class="composer-actions">
                  <div class="knobs" :class="{ collapsed: !showSettings }">
                    <label>
                      温度
                      <input type="range" min="0" max="1" step="0.1" v-model.number="temperature" />
                      <span class="value">{{ temperature.toFixed(1) }}</span>
                    </label>
                    <label>
                      最大字数
                      <input type="number" min="200" max="4000" step="100" v-model.number="maxTokens" class="max-tokens-input" />
                    </label>
                    <label>
                      Top P
                      <input type="range" min="0" max="1" step="0.1" v-model.number="topP" />
                      <span class="value">{{ topP.toFixed(1) }}</span>
                    </label>
                    <!-- 模型选择 -->
                    <label class="model-select-label">
                      模型
                      <select v-model="model" class="form-control model-select">
                        <option v-for="option in modelOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                      <div class="model-description">{{ getCurrentModelDescription() }}</div>
                    </label>
                  </div>
                  <button v-if="!isStreaming" class="btn btn-primary send-btn" :disabled="loading || !composer.trim()" @click="send">
                    <i :class="loading ? 'fa fa-spinner fa-spin' : 'fa fa-paper-plane'"></i>
                    发送
                  </button>
                  <button v-else class="btn btn-danger send-btn" @click="stopGenerating">
                    <i class="fa fa-stop"></i>
                    停止
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <!-- 页脚 - AI生成提示 -->
        <footer class="page-footer" v-if="messages.length > 0">
          <div class="ai-disclaimer">
            <span class="non-selectable">内容由AI生成，仅供参考</span>
          </div>
        </footer>
        
        <!-- 移动端快速操作工具栏 -->
        <div class="mobile-quick-actions" v-if="showMobileQuickActions">
          <button class="quick-action-btn" @click="newChat" title="新建对话">
            <i class="fa fa-plus"></i>
          </button>
          <button class="quick-action-btn" @click="clearChat" title="清空对话" v-if="messages.length > 0">
            <i class="fa fa-trash"></i>
          </button>
          <button class="quick-action-btn" @click="exportConversation" title="导出对话" v-if="messages.length > 0">
            <i class="fa fa-download"></i>
          </button>
          <button class="quick-action-btn" @click="toggleSidebar" title="切换侧边栏">
            <i class="fa fa-bars"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed, watch, onMounted, onUnmounted } from 'vue'
import { MusicTeacherService } from '@/api/musicTeacherService'
// @ts-ignore - 使用运行时渲染，无需类型
import { marked } from 'marked'
// @ts-ignore
import hljs from 'highlight.js'

type Role = 'user' | 'assistant' | 'system'
interface ChatMessage { 
  role: Role; 
  content: string;
  suggestions?: string[];
  timestamp?: number;
}

const chatWindowRef = ref<HTMLDivElement | null>(null)
const messages = ref<ChatMessage[]>([])
const composer = ref('')
const loading = ref(false)
const model = ref('deepseek-chat')
const temperature = ref(0.7)
const maxTokens = ref(1200)
const topP = ref(0.9)



// 侧边栏会话列表
interface Session { 
  id: string; 
  title: string; 
  messages: ChatMessage[]; 
  pinned?: boolean;
  lastUpdated?: number;
  createdAt?: number;
}
const sessions = ref<Session[]>([])
const activeSessionId = ref<string>('')
const sidebarCollapsed = ref(true)

// 移动端快速操作工具栏显示状态
const showMobileQuickActions = ref(false)

// 设置显示状态
const showSettings = ref(true)

// 模型选项配置
const modelOptions = [
  { value: 'deepseek-chat', label: 'DeepSeek Chat', description: '通用对话，适合日常音乐咨询' },
  { value: 'deepseek-reasoner', label: 'DeepSeek Reasoner', description: '推理增强，适合复杂音乐理论分析' }
]

const suggestionChips = [
  '如何为摇滚歌曲设计更有力量的鼓点？',
  '帮我制定一周吉他练习计划（进阶）',
  '我们要办校园演出，给出舞台流程与注意事项',
  '写一段电子/流行混合风格的主歌和弦走向',
  '分析一下爵士乐和蓝调的区别',
  '如何选择适合新手的第一把吉他？',
  '请推荐一些适合练习指弹的经典曲目',
  '乐队排练时如何协调各声部的音量平衡？'
]

// 用户信息管理
const storedUser = localStorage.getItem('user_info')
const currentUser = storedUser ? JSON.parse(storedUser) : null
const userId = currentUser?.id || currentUser?.user_id || 'anonymous'
const displayName = currentUser?.display_name || currentUser?.username || '匿名用户'

// 获取当前模型描述
function getCurrentModelDescription() {
  const currentModel = modelOptions.find(option => option.value === model.value)
  return currentModel ? currentModel.description : ''
}

// 系统提示词
const systemPrompt = `你是一位专业的音乐教师和音乐理论专家，具备以下专长：
- 音乐理论分析与教学
- 乐器演奏技巧指导
- 作曲与编曲建议
- 音乐风格分析
- 演出策划与舞台指导

请用专业、易懂的方式回答用户问题，必要时提供具体的音乐示例和练习建议。`

// DeepSeek 错误处理
function handleDeepSeekError(error: any) {
  const errorMap: Record<string, string> = {
    'rate_limit_exceeded': '请求频率过高，请稍后再试',
    'insufficient_quota': 'API配额不足，请联系管理员',
    'invalid_api_key': 'API密钥无效，请联系管理员',
    'model_not_found': '模型不存在或不可用',
    'context_length_exceeded': '对话内容过长，请开始新对话',
    'invalid_request': '请求参数错误，请检查输入',
    'server_error': '服务器内部错误，请稍后重试'
  }
  
  const errorCode = error?.error?.code || error?.code || error?.status
  const defaultMessage = '请求失败，请稍后重试'
  
  return {
    code: errorCode,
    message: errorMap[errorCode] || defaultMessage,
    original: error
  }
}

// 上下文管理
const MAX_CONTEXT_LENGTH = 20 // 最大对话轮数
const MAX_MESSAGE_LENGTH = 2000 // 单条消息最大字符数

function truncateContext(messages: ChatMessage[]): ChatMessage[] {
  if (messages.length <= MAX_CONTEXT_LENGTH) {
    return messages
  }
  
  // 保留系统提示词和最近的对话
  const truncated = messages.slice(-MAX_CONTEXT_LENGTH)
  
  // 如果第一条不是系统提示词，添加系统提示词
  if (truncated[0]?.role !== 'system') {
    truncated.unshift({ role: 'assistant', content: '由于对话内容较长，已自动截取最近的对话内容。' })
  }
  
  return truncated
}

function getContextLength(): number {
  return messages.value.reduce((total, msg) => total + msg.content.length, 0)
}

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

function onInputFocus() {
  inputFocused.value = true
}

function onInputBlur() {
  inputFocused.value = false
  placeholderIndex = (placeholderIndex + 1) % inputPlaceholders.length
}

function generateFollowUpSuggestions(originalQuestion: string, aiResponse: string): string[] {
  const suggestions: string[] = []
  const question = originalQuestion.toLowerCase()
  const response = aiResponse.toLowerCase()
  
  if (question.includes('吉他') || response.includes('吉他')) {
    suggestions.push('吉他的不同演奏技巧有哪些？', '如何选择吉他的音效器？')
  }
  if (question.includes('鼓') || response.includes('鼓')) {
    suggestions.push('不同鼓点风格的特点是什么？', '如何设置鼓的录音？')
  }
  if (question.includes('乐队') || response.includes('乐队')) {
    suggestions.push('乐队成员之间如何配合？', '乐队演出前需要准备什么？')
  }
  if (question.includes('练习') || response.includes('练习')) {
    suggestions.push('制定有效的练习计划', '如何克服练习中的困难？')
  }
  if (question.includes('和弦') || response.includes('和弦')) {
    suggestions.push('常用和弦进行有哪些？', '如何快速转换和弦？')
  }
  if (question.includes('节奏') || response.includes('节奏')) {
    suggestions.push('复杂节奏的练习方法', '不同音乐风格的节奏特点')
  }
  
  const generalSuggestions = [
    '推荐一些音乐理论入门书籍',
    '如何提高音乐听力？',
    '音乐创作的灵感来源',
    '现代音乐制作软件推荐'
  ]
  
  if (suggestions.length === 0) {
    const randomSuggestions = generalSuggestions.sort(() => 0.5 - Math.random()).slice(0, 2)
    suggestions.push(...randomSuggestions)
  }
  
  return suggestions.slice(0, 3)
}

function regenerateResponse(messageIndex: number) {
  if (messageIndex <= 0 || messageIndex >= messages.value.length) return
  
  const userMessage = messages.value[messageIndex - 1]
  if (userMessage.role !== 'user') return
  
  messages.value = messages.value.slice(0, messageIndex)
  composer.value = userMessage.content
  send()
}

function scrollToBottom() {
  nextTick(() => {
    const el = chatWindowRef.value
    if (!el) return
    // 只有当用户接近底部时才自动滚动
    if (isNearBottom) {
      el.scrollTop = el.scrollHeight
    }
  })
}

// 检测是否接近底部
function checkScrollPosition() {
  const el = chatWindowRef.value
  if (!el) return
  const { scrollTop, scrollHeight, clientHeight } = el
  // 如果距离底部小于 100px，认为接近底部
  isNearBottom = (scrollHeight - scrollTop - clientHeight) < 100
}

// 显示 Toast 提示
function showToast(message: string, type: 'success' | 'error' | 'info' = 'success') {
  const icons = {
    success: 'fa fa-check',
    error: 'fa fa-exclamation-triangle',
    info: 'fa fa-info-circle'
  }
  toast.value = {
    show: true,
    message,
    type,
    icon: icons[type]
  }
  // 3秒后自动隐藏
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

function newChat() {
  const now = Date.now()
  const id = `${now}`
  const session: Session = { 
    id, 
    title: '新对话', 
    messages: [], 
    pinned: false,
    createdAt: now,
    lastUpdated: now
  }
  sessions.value.unshift(session)
  activeSessionId.value = id
  messages.value = session.messages
  composer.value = ''
  persist()
  showToast('已创建新对话', 'info')
}

function clearChat() {
  if (messages.value.length === 0) {
    showToast('当前没有对话内容', 'info')
    return
  }
  messages.value.splice(0, messages.value.length)
  const session = sessions.value.find(s => s.id === activeSessionId.value)
  if (session) session.messages = messages.value
  persist()
  showToast('对话已清空', 'success')
}

function useSuggestion(s: string) {
  composer.value = s
  showToast('建议已填入输入框', 'info')
}

// Toast 提示状态
const toast = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'info',
  icon: 'fa fa-check'
})

// 滚动位置检测
let isNearBottom = true

// 流式状态
const isStreaming = ref(false)
const abortController = ref<AbortController | null>(null)
const errorMsg = ref('')
let lastMsgSnapshot = ''

// 输入框状态
const inputFocused = ref(false)
const inputPlaceholders = [
  '问我任何音乐相关的问题... 💭',
  '比如：如何提升吉他演奏技巧？',
  '例如：分析一下爵士乐的和声特点',
  '试试：为我推荐适合新手的练习曲目',
  '询问：如何组建一个乐队？'
]
let placeholderIndex = 0

const inputPlaceholder = computed(() => {
  if (inputFocused.value) {
    return 'Enter 发送 / Shift+Enter 换行 / Ctrl+Enter 快速发送'
  }
  return inputPlaceholders[placeholderIndex] || inputPlaceholders[0]
})
async function send() {
  const content = composer.value.trim()
      if (!content) return
  if (loading.value) return
  
  // 构建消息内容
  let messageContent = content
  const originalQuestion = content
  
  messages.value.push({ role: 'user', content: messageContent, timestamp: Date.now() })
  
  // 更新会话标题和时间戳（首条消息时）
  const session = sessions.value.find(s => s.id === activeSessionId.value)
  if (session) {
    if (session.title === '新对话') {
      session.title = content.slice(0, 18) || '新对话'
    }
    session.lastUpdated = Date.now()
  }
  
  // 清空输入
  composer.value = ''
  scrollToBottom()

  try {
    loading.value = true
    isStreaming.value = true
    messages.value.push({ role: 'assistant', content: '', timestamp: Date.now() })
    const idx = messages.value.length - 1
    lastMsgSnapshot = content
    
    // 应用上下文截断
    const truncatedMessages = truncateContext(messages.value)
    
    const controller = new AbortController()
    abortController.value = controller
    await MusicTeacherService.askStream(
      { 
        message: messageContent, 
        model: model.value, 
        temperature: temperature.value, 
        max_tokens: maxTokens.value,
        top_p: topP.value
      },
      (chunk) => { messages.value[idx].content += chunk; scrollToBottom() },
      () => { 
        isStreaming.value = false; 
        abortController.value = null; 
        errorMsg.value = '';
        
        // 生成建议问题
        const aiResponse = messages.value[idx].content
        const suggestions = generateFollowUpSuggestions(originalQuestion, aiResponse)
        messages.value[idx].suggestions = suggestions
      },
      controller.signal
    )
  } catch (e: any) {
    const errorInfo = handleDeepSeekError(e)
    errorMsg.value = errorInfo.message
    messages.value.push({ role: 'assistant', content: errorInfo.message, timestamp: Date.now() })
    handleError(e, 'AI对话')
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
    showToast('生成已停止', 'info')
  }
}

async function retryLast() {
  if (!lastMsgSnapshot) return
  composer.value = lastMsgSnapshot
  errorMsg.value = ''
  showToast('正在重试...', 'info')
  await send()
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text || '')
    showToast('复制成功！', 'success')
  } catch {
    showToast('复制失败，请手动复制', 'error')
  }
}

function selectSession(id: string) {
  if (activeSessionId.value === id) return
  activeSessionId.value = id
  const session = sessions.value.find(s => s.id === id)
  messages.value = session ? session.messages : []
  
  // 更新会话的最后访问时间
  if (session) {
    session.lastUpdated = Date.now()
  }
  
  const sessionTitle = session?.title || '未命名对话'
  showToast(`已切换到：${sessionTitle}`, 'info')
  persist()
}

function deleteSession(id: string) {
  const idx = sessions.value.findIndex(s => s.id === id)
  if (idx === -1) return
  const sessionTitle = sessions.value[idx].title || '未命名对话'
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
  showToast(`已删除会话：${sessionTitle}`, 'success')
}

function toggleSidebar() { sidebarCollapsed.value = !sidebarCollapsed.value }

function toggleSettings() { 
  showSettings.value = !showSettings.value
  showToast(showSettings.value ? '设置已显示' : '设置已隐藏', 'info')
}



function renameSession(id: string) {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  const oldName = s.title || '未命名对话'
  const name = prompt('重命名会话', oldName)
  if (name !== null) {
    const newName = name.trim() || '未命名对话'
    s.title = newName
    persist()
    if (newName !== oldName) {
      showToast(`会话已重命名为：${newName}`, 'success')
    }
  }
}

function togglePin(id: string) {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  const wasPinned = (s as any).pinned
  ;(s as any).pinned = !wasPinned
  // 调整顺序：置顶到列表前
  sessions.value = sessions.value
    .slice()
    .sort((a: any, b: any) => (Number(!!b.pinned) - Number(!!a.pinned)))
  persist()
  const action = (s as any).pinned ? '置顶' : '取消置顶'
  showToast(`会话已${action}`, 'success')
}

// 本地持久化
// 动态生成存储键，支持用户切换
const getStorageKey = () => `music_teacher_sessions_${userId}_v1`

// 会话存储管理
const MAX_SESSIONS_PER_USER = 50 // 每个用户最大会话数
const MAX_STORAGE_SIZE = 10 * 1024 * 1024 // 最大存储大小 10MB

// 清理过期和过多的会话
function cleanupSessions() {
  if (sessions.value.length > MAX_SESSIONS_PER_USER) {
    // 按最后更新时间排序，保留最新的会话
    sessions.value.sort((a, b) => (b.lastUpdated || 0) - (a.lastUpdated || 0))
    sessions.value = sessions.value.slice(0, MAX_SESSIONS_PER_USER)
    
    // 如果当前活动会话被删除，选择第一个会话
    if (!sessions.value.find(s => s.id === activeSessionId.value)) {
      activeSessionId.value = sessions.value[0]?.id || ''
      messages.value = sessions.value[0]?.messages || []
    }
  }
}

// 清理旧会话数据
function cleanupOldSessions() {
  // 删除30天前的会话
  const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000)
  sessions.value = sessions.value.filter(session => {
    return (session.lastUpdated || 0) > thirtyDaysAgo
  })
  
  // 如果所有会话都被清理，创建新会话
  if (sessions.value.length === 0) {
    newChat()
  }
}

// 格式化会话时间
function formatSessionTime(timestamp?: number): string {
  if (!timestamp) return ''
  
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
  
  const date = new Date(timestamp)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function persist() {
  try {
    // 清理过期和过多的会话
    cleanupSessions()
    
    const data = {
      sessions: sessions.value,
      activeId: activeSessionId.value,
      userId: userId,
      lastUpdated: Date.now()
    }
    
    // 检查存储空间
    const dataString = JSON.stringify(data)
    if (dataString.length > MAX_STORAGE_SIZE) {
      console.warn('会话数据过大，清理旧数据')
      cleanupOldSessions()
      // 重新生成数据
      const cleanedData = {
        sessions: sessions.value,
        activeId: activeSessionId.value,
        userId: userId,
        lastUpdated: Date.now()
      }
      localStorage.setItem(getStorageKey(), JSON.stringify(cleanedData))
    } else {
      localStorage.setItem(getStorageKey(), dataString)
    }
  } catch (e) {
    console.error('保存会话失败:', e)
    showToast('保存会话失败', 'error')
  }
}

function restore() {
  try {
    const raw = localStorage.getItem(getStorageKey())
    if (!raw) return false
    const data = JSON.parse(raw)
    if (!data || !Array.isArray(data.sessions)) return false
    
    // 验证用户ID匹配
    if (data.userId && data.userId !== userId) {
      console.warn('用户ID不匹配，清除旧会话数据')
      return false
    }
    
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

// 用户切换检测
function checkUserChange() {
  const newStoredUser = localStorage.getItem('user_info')
  const newUser = newStoredUser ? JSON.parse(newStoredUser) : null
  const newUserId = newUser?.id || newUser?.user_id || 'anonymous'
  
  if (newUserId !== userId) {
    console.log('检测到用户切换，清理当前会话')
    // 清理当前会话
    sessions.value = []
    activeSessionId.value = ''
    messages.value = []
    // 重新加载新用户的会话
    if (newUserId !== 'anonymous') {
      restore()
    } else {
      newChat()
    }
  }
}

// 监听localStorage变化，检测用户切换
function setupUserChangeListener() {
  window.addEventListener('storage', (e) => {
    if (e.key === 'user_info') {
      checkUserChange()
    }
  })
  
  // 定期检查用户信息变化（处理同标签页内的变化）
  setInterval(checkUserChange, 5000)
}

// 组件挂载时的设置
onMounted(() => {
  setupMobileOptimizations()
  setupUserChangeListener()
  window.addEventListener('resize', handleResize)
  
  // 设置焦点到主容器以启用键盘快捷键
  nextTick(() => {
    const container = document.querySelector('.teacher-management') as HTMLElement
    if (container) {
      container.focus()
    }
  })
})

// 组件卸载时清理事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 键盘快捷键支持
function handleKeydown(event: KeyboardEvent) {
  // Ctrl/Cmd + Enter 发送消息
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    if (!loading.value && composer.value.trim()) {
      send()
    }
  }
  
  // Ctrl/Cmd + N 新建对话
  if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
    event.preventDefault()
    newChat()
  }
  
  // Ctrl/Cmd + K 清空对话
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    clearChat()
  }
  
  // Ctrl/Cmd + / 切换侧边栏
  if ((event.ctrlKey || event.metaKey) && event.key === '/') {
    event.preventDefault()
    toggleSidebar()
  }
}

// 移动端检测
function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 移动端适配
function setupMobileOptimizations() {
  if (isMobileDevice()) {
    // 移动端默认收起侧边栏（已经是默认状态）
    // 显示移动端快速操作工具栏
    showMobileQuickActions.value = true
  }
}

// 监听窗口大小变化
function handleResize() {
  if (window.innerWidth <= 768) {
    showMobileQuickActions.value = true
    if (!sidebarCollapsed.value) {
      sidebarCollapsed.value = true
    }
  } else {
    showMobileQuickActions.value = false
  }
}

// 导出对话功能
function exportConversation() {
  if (messages.value.length === 0) {
    showToast('当前没有对话内容可导出', 'info')
    return
  }
  
  try {
    const session = sessions.value.find(s => s.id === activeSessionId.value)
    const sessionTitle = session?.title || '未命名对话'
    const timestamp = new Date().toLocaleString('zh-CN')
    
    let exportContent = `# ${sessionTitle}\n\n`
    exportContent += `导出时间: ${timestamp}\n\n`
    exportContent += `---\n\n`
    
    messages.value.forEach((msg, index) => {
      const role = msg.role === 'user' ? '👤 用户' : '🤖 AI助手'
      exportContent += `## ${role} (第${index + 1}轮)\n\n`
      exportContent += `${msg.content}\n\n`
      exportContent += `---\n\n`
    })
    
    // 创建并下载文件
    const blob = new Blob([exportContent], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${sessionTitle}_${Date.now()}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    showToast('对话已导出为Markdown文件', 'success')
  } catch (error) {
    console.error('导出失败:', error)
    showToast('导出失败，请重试', 'error')
  }
}

// 更好的错误处理
function handleError(error: any, context: string = '操作') {
  console.error(`${context}失败:`, error)
  
  let errorMessage = '操作失败，请重试'
  
  if (typeof error === 'string') {
    errorMessage = error
  } else if (error?.message) {
    errorMessage = error.message
  } else if (error?.error) {
    errorMessage = error.error
  }
  
  showToast(errorMessage, 'error')
  return errorMessage
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;

.teacher-management {
  /* 减去固定导航栏4rem的高度，避免出现页面滚动条 */
  min-height: calc(100vh - 4rem);
  height: calc(100vh - 4rem);
  padding: 0; // 外壳负责内边距
  overflow: hidden; // 防止页面滚动
}

.page-header {
  
  h1 { margin: 0 0 .25rem 0; }
  p { color: $gray-400; margin: 0; }
}

.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem; padding: 0.75rem; background: rgba($darkgray, 0.7);
  border: $border-light; border-radius: $border-radius-xl; backdrop-filter: blur(8px);
  .toolbar-left { display: flex; gap: 0.75rem; align-items: center; }
  .toolbar-right { display: flex; gap: 0.75rem; align-items: center; }
  .model-select { display: flex; align-items: center; gap: .5rem; label { color: $gray-300; font-size: .875rem; } }
  @media (max-width: 768px) { flex-direction: column; gap: 0.75rem; }
}

.suggestions {
  display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 0.75rem;
  .chip {
    background: rgba($lightgray, .35);
    border: 1px solid rgba($white, .1);
    color: $gray-300;
    padding: .5rem .75rem; border-radius: 10px; cursor: pointer; transition: all $transition-fast ease;
    &:hover { color: $white; border-color: rgba($primary, .5); box-shadow: $shadow-primary; }
    
    /* 移动端优化 */
    @media (max-width: 768px) {
      flex: 1;
      min-width: 140px;
      text-align: center;
      justify-content: center;
    }
  }
}

/* AI回答后的建议问题样式 */
.follow-up-suggestions {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba($darkgray, 0.3);
  border-radius: 8px;
  border: 1px solid rgba($lightgray, 0.15);
  
  .suggestions-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    color: $gray-300;
    font-size: 0.875rem;
    font-weight: 500;
    
    i {
      color: $warning;
      font-size: 0.875rem;
    }
  }
  
  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .suggestion-chip {
    background: rgba($lightgray, 0.2);
    border: 1px solid rgba($white, 0.1);
    color: $gray-300;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all $transition-fast ease;
    text-align: left;
    font-size: 0.875rem;
    
    &:hover {
      color: $white;
      background: rgba($primary, 0.15);
      border-color: rgba($primary, 0.4);
      transform: translateX(4px);
    }
    
    &:active {
      transform: translateX(2px);
    }
  }
}

.shell { display: grid; grid-template-columns: 260px 1fr; gap: 0; height: 100%; }
.shell.collapsed { grid-template-columns: 72px 1fr; }

.sidebar { background: #101010; border-right: 1px solid #2a2a2a; height: 100%; position: sticky; top: 0; }
.sidebar-header { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  padding: .75rem .75rem; 
  border-bottom: 1px solid #2a2a2a; 
  
  .title { 
    display: flex; 
    align-items: center; 
    gap: .5rem; 
    color: $white; 
    font-weight: 600; 
  }
  
  .user-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.2rem;
    
    .user-name {
      color: $primary;
      font-size: 0.875rem;
      font-weight: 500;
    }
    
    .session-count {
      color: $gray-400;
      font-size: 0.75rem;
    }
  }
  
  .collapse-btn { background: transparent; border: none; color: #bbb; cursor: pointer; }
  .mobile-toggle-btn { display: none; background: transparent; border: none; color: #bbb; cursor: pointer; padding: 0.25rem; }
}
.search-box { display: flex; align-items: center; gap: .5rem; padding: .5rem .75rem .25rem;
  .search-input { width: 100%; }
}
.new-chat-btn { 
  margin: .75rem; 
  width: calc(100% - 1.5rem); 
  display: flex; 
  align-items: center; 
  gap: .5rem; 
  justify-content: center; 
  background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%); 
  color: white; 
  border: none; 
  padding: .55rem .75rem; 
  border-radius: 10px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.4), 0 8px 25px rgba(78, 205, 196, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}
.session-list { 
  list-style: none; 
  margin: 0 .5rem .75rem .5rem; 
  padding: 0; 
  display: flex; 
  flex-direction: column; 
  gap: .35rem; 
  max-height: calc(100vh - 240px); 
  overflow-y: auto;
  
  /* 自定义滚动条样式 */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba($darkgray, 0.2);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba($primary, 0.5);
    border-radius: 3px;
    
    &:hover {
      background: rgba($primary, 0.7);
    }
  }
  
  /* Firefox 滚动条 */
  scrollbar-width: thin;
  scrollbar-color: rgba($primary, 0.5) rgba($darkgray, 0.2);
}
.session-list.compact { margin: .5rem; gap: .5rem; 
  li { grid-template-columns: 1fr; }
  .delete-btn { display: none; }
  .session-item { justify-content: center; }
}
.session-list li { display: grid; grid-template-columns: 1fr auto; align-items: center; border-radius: 8px; }
.session-list li.active { background: rgba(229,57,53,0.08); }
.session-item { 
  text-align: left; 
  background: transparent; 
  border: none; 
  color: #ddd; 
  padding: .5rem .5rem; 
  border-radius: 8px; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  gap: .5rem; 
  width: 100%; 
  
  .session-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    flex: 1;
    
    .text {
      color: #ddd;
      font-weight: 500;
    }
    
    .time {
      color: $gray-400;
      font-size: 0.75rem;
    }
  }
}
.item-actions { display: flex; gap: .25rem; padding-right: .25rem; }
.icon-btn { background: transparent; border: none; color: #888; cursor: pointer; padding: .25rem .35rem; border-radius: 6px; transition: all $transition-fast ease; &:hover { color: $primary; background: rgba($primary, .08);} }

.empty-sessions {
  padding: 1rem 0.5rem;
  text-align: center;
  
  .empty-sessions-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    color: $gray-400;
    
    i {
      font-size: 1.5rem;
      opacity: 0.6;
    }
    
    span {
      font-size: 0.875rem;
    }
  }
}

.welcome-screen { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  min-height: 400px; 
  padding: 2rem 1rem;
  text-align: center;
  
  .welcome-avatar {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
    animation: welcomePulse 2s ease-in-out infinite;
    
    i {
      font-size: 2rem;
      color: white;
    }
  }
  
  .welcome-title { 
    font-weight: 700; 
    font-size: 2.2rem; 
    letter-spacing: .2px; 
    color: $white; 
    margin: 0 0 1rem 0;
    background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .welcome-subtitle {
    color: $gray-300;
    font-size: 1.1rem;
    margin: 0 0 2rem 0;
    max-width: 500px;
    line-height: 1.6;
  }
  
  .welcome-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
    max-width: 600px;
    width: 100%;
    
    .feature-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: rgba($lightgray, 0.1);
      border-radius: 8px;
      border: 1px solid rgba($lightgray, 0.2);
      transition: all $transition-normal ease;
      
      i {
        font-size: 1.25rem;
        color: $primary;
        width: 20px;
        text-align: center;
      }
      
      span {
        color: $gray-300;
        font-weight: 500;
      }
      
      &:hover {
        background: rgba($primary, 0.1);
        border-color: rgba($primary, 0.3);
        transform: translateY(-2px);
      }
    }
  }
  
  .welcome-prompt {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: $gray-400;
    font-size: 0.95rem;
    
    i {
      color: $warning;
      font-size: 1.1rem;
    }
  }
  
  :deep(pre code) { 
    display: block; 
    padding: 1rem; 
    border-radius: 10px; 
    background: #0f111a; 
    border: 1px solid #222; 
  }
}

@keyframes welcomePulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 20px rgba(255, 107, 157, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.5), 0 8px 25px rgba(78, 205, 196, 0.3);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.bounce {
  animation: bounce 2s infinite;
}

.content-box { 
  padding: 1.5rem 1.5rem 0 1.5rem; 
  max-width: 1200px; 
  margin: 0 auto; 
  width: 100%; 
  height: 100%; 
  display: flex;
  flex-direction: column;
}
.conversation-panel { 
  min-width: 0; 
  height: 100%; 
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chat-card { 
  padding: 0; 
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  min-height: 0;
}

.chat-messages-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
}

.chat-window { 
  flex: 1;
  min-height: 0;
  max-height: calc(100vh - 280px);
  padding: 0.75rem; 
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  -webkit-overflow-scrolling: touch;
  height: 100%;
  
  /* 增强的滚动条样式 */
  &::-webkit-scrollbar {
    width: 10px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba($darkgray, 0.4);
    border-radius: 6px;
    margin: 4px 0;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, rgba($primary, 0.8) 0%, rgba($secondary, 0.8) 100%);
    border-radius: 6px;
    border: 1px solid rgba($white, 0.1);
    
    &:hover {
      background: linear-gradient(135deg, rgba($primary, 1) 0%, rgba($secondary, 1) 100%);
      box-shadow: 0 2px 8px rgba($primary, 0.3);
    }
  }
  
  /* Firefox 滚动条 */
  scrollbar-width: thin;
  scrollbar-color: rgba($primary, 0.8) rgba($darkgray, 0.4);
}

.composer-container {
  flex-shrink: 0;
  border-top: 1px solid #2a2a2a;
  background: rgba(255,255,255,.02);
  backdrop-filter: blur(8px);
  position: sticky;
  bottom: 0;
  z-index: 100;
  max-height: calc(100vh - 100px);
  overflow: hidden;
}

/* 滚动锚点优化：用户向上滚动浏览时不强制跟随到底部 */
.chat-window:hover { scroll-behavior: smooth; }

/* 页脚样式 */
.page-footer {
  flex-shrink: 0;
  border-top: 1px solid rgba($lightgray, 0.2);
  background: rgba($darkgray, 0.3);
  backdrop-filter: blur(8px);
  position: relative;
  z-index: 10;
  
  .ai-disclaimer {
    text-align: center;
    color: $gray-400;
    font-size: 0.75rem;
    
    span {
      opacity: 0.8;
      user-select: none;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      cursor: default;
      
      &.non-selectable {
        pointer-events: none;
      }
    }
  }
}

/* 移动端快速操作工具栏 */
.mobile-quick-actions {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  display: none; /* 默认隐藏，移动端显示 */
  flex-direction: column;
  gap: 0.5rem;
  z-index: 1000;
  
  .quick-action-btn {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba($primary, 0.9);
    border: none;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba($primary, 0.3);
    transition: all $transition-normal ease;
    
    &:hover {
      background: rgba($primary, 1);
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba($primary, 0.4);
    }
    
    &:active {
      transform: scale(0.95);
    }
  }
}

/* 错误条 */
.error-bar { display: flex; align-items: center; gap: .5rem; padding: .6rem .75rem; border: 1px solid rgba(#ef4444, .4); border-radius: 10px; background: rgba(#ef4444, .1); color: #ffb4b4; margin: .5rem 1rem 0; }
.error-bar .icon-btn { margin-left: auto; }

/* Toast 提示 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: toastSlideIn 0.3s ease-out;
  
  &.success {
    background: linear-gradient(135deg, #10b981, #059669);
  }
  
  &.error {
    background: linear-gradient(135deg, #ef4444, #dc2626);
  }
  
  &.info {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
  }
}

@keyframes toastSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

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

.composer { 
  padding: 0.5rem 0.5rem 0.75rem 0.5rem; 
  background: rgba(255,255,255,.02);
}

/* 输入区域样式 */
.input-area {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.composer-input { 
  width: 100%; 
  resize: vertical; 
  min-height: 60px; 
}

.char-counter {
  text-align: right;
  font-size: 0.75rem;
  color: $gray-400;
  
  .warning {
    color: $warning;
  }
  
  .danger {
    color: $danger;
  }
}





/* 快速操作栏 */
.quick-actions-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
  padding: 0.1rem;
  background: rgba($darkgray, 0.2);
  border-radius: 6px;
  border: 1px solid rgba($lightgray, 0.1);
  
  .quick-action-btn {
    background: rgba($lightgray, 0.2);
    border: 1px solid rgba($white, 0.1);
    color: $gray-300;
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all $transition-fast ease;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      color: $white;
      background: rgba($primary, 0.15);
      border-color: rgba($primary, 0.4);
      transform: translateY(-1px);
    }
    
    &:active {
      transform: translateY(0);
    }
    
    i {
      font-size: 0.875rem;
    }
  }
}

.composer-actions { 
  display: flex; 
  align-items: center; 
  gap: 0.5rem; 
  margin-top: 0.4rem; 
  
  .send-btn {
    min-width: 80px;
    height: 40px;
  }
}
.knobs { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  color: $gray-400; 
  max-height: 180px;
  overflow: hidden;
  transition: all $transition-normal ease;
  opacity: 1;
  
  &.collapsed {
    max-height: 0;
    opacity: 0;
    margin: 0;
    padding: 0;
  }
  
  label { 
    display: flex; 
    align-items: center; 
    gap: 6px; 
  }
  
  /* 自定义滑动按钮样式 */
  input[type="range"] {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    width: 120px;
    height: 6px;
    background: linear-gradient(90deg, #ff6b9d 0%, #4ecdc4 100%);
    border-radius: 3px;
    outline: none;
    cursor: pointer;
    transition: all 0.3s ease;
    
    /* 滑块样式 */
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      width: 18px;
      height: 18px;
      background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%);
      border-radius: 50%;
      cursor: pointer;
      border: 2px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      transition: all 0.3s ease;
    }
    
    &::-moz-range-thumb {
      width: 18px;
      height: 18px;
      background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%);
      border-radius: 50%;
      cursor: pointer;
      border: 2px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      transition: all 0.3s ease;
    }
    
    /* 轨道样式 */
    &::-webkit-slider-track {
      background: linear-gradient(90deg, #ff6b9d 0%, #4ecdc4 100%);
      border-radius: 3px;
      height: 6px;
    }
    
    &::-moz-range-track {
      background: linear-gradient(90deg, #ff6b9d 0%, #4ecdc4 100%);
      border-radius: 3px;
      height: 6px;
    }
    
    /* 悬停效果 */
    &:hover {
      transform: scale(1.02);
      
      &::-webkit-slider-thumb {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.4), 0 4px 12px rgba(78, 205, 196, 0.4);
      }
      
      &::-moz-range-thumb {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.4), 0 4px 12px rgba(78, 205, 196, 0.4);
      }
    }
    
    /* 焦点效果 */
    &:focus {
      &::-webkit-slider-thumb {
        box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.3), 0 0 0 3px rgba(78, 205, 196, 0.3);
      }
      
      &::-moz-range-thumb {
        box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.3), 0 0 0 3px rgba(78, 205, 196, 0.3);
      }
    }
  }
}

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

/* 模型选择样式 */
.model-select-label {
  position: relative;
  
  .model-description {
    font-size: 0.75rem;
    color: $gray-400;
    margin-top: 0.25rem;
    font-style: italic;
    max-width: 200px;
    line-height: 1.3;
  }
}

/* 加载动画样式 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  .loading-dots {
    display: flex;
    gap: 0.25rem;
    
    span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: $primary;
      animation: loadingDot 1.4s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
      &:nth-child(3) { animation-delay: 0s; }
    }
  }
}

@keyframes loadingDot {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.content-box select.form-control:focus,
.content-box input[type='number'].form-control:focus { border-color: $primary; box-shadow: 0 0 0 3px rgba($primary, 0.15); }

/* 最大字数输入框特殊样式 */
.max-tokens-input {
  background: rgba($darkgray, 0.8) !important;
  border: 1px solid rgba($lightgray, 0.6) !important;
  color: $white !important;
  padding: 0.4rem 0.6rem;
  border-radius: $border-radius-md;
  font-size: 0.875rem;
  width: 80px;
  text-align: center;
  
  &:focus {
    border-color: $primary !important;
    box-shadow: 0 0 0 3px rgba($primary, 0.15) !important;
    background: rgba($darkgray, 0.9) !important;
  }
  
  &::-webkit-inner-spin-button,
  &::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  &[type=number] {
    -moz-appearance: textfield;
    appearance: textfield;
  }
}


@media (max-width: 768px) {
  .teacher-management {
    height: calc(100vh - 4rem);
    overflow: hidden;
  }
  
  .shell {
    grid-template-columns: 1fr !important;
    grid-template-rows: auto 1fr;
    height: 100%;
    overflow: hidden;
  }
  
  .shell.collapsed {
    grid-template-columns: 1fr !important;
  }
  
  .sidebar {
    height: auto;
    max-height: 280px;
    border-right: none;
    border-bottom: 1px solid #2a2a2a;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    background: rgba(16, 16, 16, 0.98);
    backdrop-filter: blur(20px);
    
    .mobile-toggle-btn {
      display: block;
    }
    
    .collapse-btn {
      display: none;
    }
    
    .sidebar-header {
      padding: 0.5rem 0.75rem;
      
      .title {
        font-size: 0.9rem;
      }
      
      .user-info {
        .user-name {
          font-size: 0.8rem;
        }
        
        .session-count {
          font-size: 0.7rem;
        }
      }
    }
    
    .search-box {
      padding: 0.4rem 0.75rem 0.2rem;
      
      .search-input {
        font-size: 0.875rem;
        padding: 0.5rem 0.6rem;
      }
    }
    
    .new-chat-btn {
      margin: 0.5rem 0.75rem;
      padding: 0.5rem 0.75rem;
      font-size: 0.875rem;
      
      i {
        font-size: 0.9rem;
      }
    }
    
    .session-list {
      max-height: 180px;
      margin: 0.4rem 0.5rem 0.5rem;
      gap: 0.3rem;
      
      li {
        .session-item {
          padding: 0.4rem 0.5rem;
          
          .session-info {
            .text {
              font-size: 0.85rem;
            }
            
            .time {
              font-size: 0.7rem;
            }
          }
        }
        
        .item-actions {
          gap: 0.2rem;
          
          .icon-btn {
            padding: 0.2rem 0.3rem;
            font-size: 0.8rem;
          }
        }
      }
    }
  }
  
  .content-box {
    padding: 0.75rem 0.75rem 0 0.75rem;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .conversation-panel {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
  
  .chat-card {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    margin-bottom: 0;
    border-radius: 0.75rem;
  }
  
  .chat-messages-container {
    flex: 1;
    min-height: 0;
    height: 100%;
  }
  
  .chat-window {
    flex: 1;
    min-height: 0;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    padding: 0.6rem 0.6rem 0.8rem 0.6rem;
    height: 100%;
    
    /* 移动端滚动条优化 */
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background: rgba($darkgray, 0.2);
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba($primary, 0.5);
      border-radius: 2px;
      
      &:hover {
        background: rgba($primary, 0.7);
      }
    }
    
    /* 确保移动端滚动正常工作 */
    overflow-x: hidden;
    word-wrap: break-word;
  }
  
  .composer-container {
    flex-shrink: 0;
    position: sticky;
    bottom: 0;
    z-index: 100;
    max-height: calc(100vh - 70px);
    overflow: hidden;
    border-radius: 0.75rem 0.75rem 0 0;
  }
  
  .composer {
    margin-top: 0;
    padding: 0.4rem 0.4rem 0.6rem 0.4rem;
  }
  
  .page-footer {
    flex-shrink: 0;
    padding: 0.6rem 0.75rem;
    
    .ai-disclaimer span {
      font-size: 0.75rem;
    }
  }
  
  .composer-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    
    .send-btn {
      height: 44px;
      font-size: 0.9rem;
      border-radius: 0.75rem;
    }
  }
  
  .knobs {
    flex-direction: column;
    gap: 0.6rem;
    padding: 0.75rem;
    background: rgba($darkgray, 0.3);
    border-radius: 0.5rem;
    border: 1px solid rgba($lightgray, 0.1);
    
    label {
      justify-content: space-between;
      align-items: center;
      font-size: 0.85rem;
      
      input[type="range"] {
        width: 100px;
      }
      
      input[type="number"] {
        width: 70px;
        padding: 0.3rem 0.5rem;
        font-size: 0.8rem;
      }
      
      .value {
        font-size: 0.8rem;
        color: $primary;
        font-weight: 600;
      }
    }
    
    .model-select-label {
      .model-select {
        width: 100%;
        padding: 0.4rem 0.6rem;
        font-size: 0.85rem;
      }
      
      .model-description {
        font-size: 0.7rem;
        margin-top: 0.3rem;
      }
    }
  }
  
  .session-list {
    max-height: 180px;
    -webkit-overflow-scrolling: touch;
  }
  
  .msg {
    gap: 6px;
    margin-bottom: 10px;
    
    .avatar {
      width: 32px;
      height: 32px;
      font-size: 0.8rem;
    }
    
    .bubble {
      max-width: 88%;
      padding: 8px 10px;
      font-size: 0.875rem;
      border-radius: 0.75rem;
      
      .bubble-toolbar {
        top: 4px;
        right: 4px;
        
        .icon-btn {
          padding: 0.3rem;
          font-size: 0.8rem;
        }
      }
      
      .bubble-content {
        margin-top: 16px;
      }
    }
  }
  
  .composer-input {
    min-height: 80px;
    font-size: 16px;
    border-radius: 0.75rem;
    padding: 0.6rem 0.75rem;
  }
  
  .quick-actions-bar {
    margin-bottom: 0.3rem;
    padding: 0.3rem;
    gap: 0.4rem;
    
    .quick-action-btn {
      width: 32px;
      height: 32px;
      padding: 0.4rem;
      
      i {
        font-size: 0.8rem;
      }
    }
  }
  
  .mobile-quick-actions {
    display: flex;
    bottom: 1.5rem;
    right: 1.5rem;
    
    .quick-action-btn {
      width: 52px;
      height: 52px;
      font-size: 1.2rem;
      box-shadow: 0 6px 20px rgba($primary, 0.4);
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba($primary, 0.5);
      }
    }
  }
  
  /* 欢迎界面移动端优化 */
  .welcome-screen {
    padding: 1.5rem 1rem;
    min-height: 300px;
    
    .welcome-avatar {
      width: 70px;
      height: 70px;
      margin-bottom: 1.2rem;
      
      i {
        font-size: 1.8rem;
      }
    }
    
    .welcome-title {
      font-size: 1.8rem;
      margin-bottom: 0.8rem;
    }
    
    .welcome-subtitle {
      font-size: 1rem;
      margin-bottom: 1.5rem;
      max-width: 100%;
    }
    
    .welcome-features {
      grid-template-columns: 1fr;
      gap: 0.8rem;
      margin-bottom: 1.5rem;
      
      .feature-item {
        padding: 0.6rem 0.8rem;
        
        i {
          font-size: 1.1rem;
        }
        
        span {
          font-size: 0.9rem;
        }
      }
    }
    
    .welcome-prompt {
      font-size: 0.9rem;
      
      i {
        font-size: 1rem;
      }
    }
  }
  
  /* 建议问题移动端优化 */
  .suggestions {
    gap: 0.4rem;
    margin-bottom: 0.6rem;
    
    .chip {
      padding: 0.4rem 0.6rem;
      font-size: 0.85rem;
      border-radius: 0.75rem;
      min-width: 120px;
      text-align: center;
    }
  }
  
  /* 后续建议移动端优化 */
  .follow-up-suggestions {
    margin-top: 0.8rem;
    padding: 0.6rem;
    
    .suggestions-header {
      font-size: 0.8rem;
      margin-bottom: 0.6rem;
    }
    
    .suggestion-chip {
      padding: 0.4rem 0.6rem;
      font-size: 0.8rem;
      border-radius: 0.5rem;
    }
  }
}

@media (max-width: 480px) {
  .content-box {
    padding: 0.5rem 0.5rem 0 0.5rem;
  }
  
  .chat-window {
    padding: 0.4rem 0.4rem 0.6rem 0.4rem;
    max-height: calc(100vh - 160px);
    -webkit-overflow-scrolling: touch;
    
    &::-webkit-scrollbar {
      width: 3px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba($primary, 0.5);
      border-radius: 2px;
    }
  }
  
  .welcome-screen {
    padding: 1rem 0.75rem;
    min-height: 250px;
    
    .welcome-avatar {
      width: 60px;
      height: 60px;
      margin-bottom: 1rem;
      
      i {
        font-size: 1.6rem;
      }
    }
    
    .welcome-title {
      font-size: 1.6rem;
      margin-bottom: 0.6rem;
    }
    
    .welcome-subtitle {
      font-size: 0.9rem;
      margin-bottom: 1.2rem;
    }
    
    .welcome-features {
      gap: 0.6rem;
      margin-bottom: 1.2rem;
      
      .feature-item {
        padding: 0.5rem 0.6rem;
        
        i {
          font-size: 1rem;
        }
        
        span {
          font-size: 0.85rem;
        }
      }
    }
    
    .welcome-prompt {
      font-size: 0.85rem;
      
      i {
        font-size: 0.9rem;
      }
    }
  }
  
  .suggestions {
    gap: 0.3rem;
    margin-bottom: 0.5rem;
    
    .chip {
      padding: 0.35rem 0.5rem;
      font-size: 0.8rem;
      border-radius: 0.6rem;
      min-width: 100px;
    }
  }
  
  .follow-up-suggestions {
    margin-top: 0.6rem;
    padding: 0.5rem;
    
    .suggestions-header {
      font-size: 0.75rem;
      margin-bottom: 0.5rem;
    }
    
    .suggestion-chip {
      padding: 0.35rem 0.5rem;
      font-size: 0.75rem;
      border-radius: 0.4rem;
    }
  }
  
  .composer {
    padding: 0.4rem 0.4rem 0.6rem 0.4rem;
  }
  
  .page-footer {
    padding: 0.4rem 0.5rem;
    
    .ai-disclaimer span {
      font-size: 0.7rem;
    }
  }
  
  .composer-actions {
    gap: 0.6rem;
    
    .send-btn {
      height: 40px;
      font-size: 0.85rem;
    }
  }
  
  .knobs {
    gap: 0.5rem;
    padding: 0.6rem;
    
    label {
      font-size: 0.8rem;
      
      input[type="range"] {
        width: 80px;
      }
      
      input[type="number"] {
        width: 60px;
        padding: 0.25rem 0.4rem;
        font-size: 0.75rem;
      }
      
      .value {
        font-size: 0.75rem;
      }
    }
    
    .model-select-label {
      .model-select {
        padding: 0.3rem 0.5rem;
        font-size: 0.8rem;
      }
      
      .model-description {
        font-size: 0.65rem;
      }
    }
  }
  
  .msg {
    gap: 5px;
    margin-bottom: 8px;
    
    .avatar {
      width: 28px;
      height: 28px;
      font-size: 0.75rem;
    }
    
    .bubble {
      max-width: 90%;
      padding: 6px 8px;
      font-size: 0.8rem;
      border-radius: 0.6rem;
      
      .bubble-toolbar {
        top: 3px;
        right: 3px;
        
        .icon-btn {
          padding: 0.25rem;
          font-size: 0.75rem;
        }
      }
      
      .bubble-content {
        margin-top: 14px;
      }
    }
  }
  
  .composer-input {
    min-height: 70px;
    font-size: 16px;
    border-radius: 0.6rem;
    padding: 0.5rem 0.6rem;
  }
  
  .quick-actions-bar {
    margin-bottom: 0.25rem;
    padding: 0.25rem;
    gap: 0.3rem;
    
    .quick-action-btn {
      width: 28px;
      height: 28px;
      padding: 0.3rem;
      
      i {
        font-size: 0.75rem;
      }
    }
  }
  
  .mobile-quick-actions {
    bottom: 1.2rem;
    right: 1.2rem;
    
    .quick-action-btn {
      width: 48px;
      height: 48px;
      font-size: 1.1rem;
    }
  }
  
  /* 侧边栏小屏优化 */
  .sidebar {
    max-height: 250px;
    
    .sidebar-header {
      padding: 0.4rem 0.6rem;
      
      .title {
        font-size: 0.85rem;
      }
      
      .user-info {
        .user-name {
          font-size: 0.75rem;
        }
        
        .session-count {
          font-size: 0.65rem;
        }
      }
    }
    
    .search-box {
      padding: 0.3rem 0.6rem 0.15rem;
      
      .search-input {
        font-size: 0.8rem;
        padding: 0.4rem 0.5rem;
      }
    }
    
    .new-chat-btn {
      margin: 0.4rem 0.6rem;
      padding: 0.4rem 0.6rem;
      font-size: 0.8rem;
      
      i {
        font-size: 0.85rem;
      }
    }
    
    .session-list {
      max-height: 160px;
      margin: 0.3rem 0.4rem 0.4rem;
      gap: 0.25rem;
      
      li {
        .session-item {
          padding: 0.3rem 0.4rem;
          
          .session-info {
            .text {
              font-size: 0.8rem;
            }
            
            .time {
              font-size: 0.65rem;
            }
          }
        }
        
        .item-actions {
          gap: 0.15rem;
          
          .icon-btn {
            padding: 0.15rem 0.25rem;
            font-size: 0.75rem;
          }
        }
      }
    }
  }
  
  /* 触摸友好的交互优化 */
  .mobile-quick-actions {
    .quick-action-btn {
      touch-action: manipulation;
      -webkit-tap-highlight-color: transparent;
      
      &:active {
        transform: scale(0.95);
        transition: transform 0.1s ease;
      }
    }
  }
  
  /* 触摸友好的按钮和输入框 */
  .btn, .icon-btn, .tab-btn {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
    min-height: 44px; /* 触摸友好的最小高度 */
    
    &:active {
      transform: scale(0.98);
      transition: transform 0.1s ease;
    }
  }
  
  .composer-input, .search-input {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  /* 触摸友好的滚动 */
  .chat-window, .session-list {
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
    
    /* 自定义滚动条 */
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background: rgba($darkgray, 0.1);
      border-radius: 2px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba($primary, 0.4);
      border-radius: 2px;
      
      &:hover {
        background: rgba($primary, 0.6);
      }
    }
  }
  
  /* 触摸友好的标签页 */
  .tab-navigation {
    .tab-btn {
      min-height: 48px;
      padding: 0.6rem 1rem;
      
      &:active {
        transform: scale(0.95);
      }
    }
  }
  
  /* 触摸友好的建议问题 */
  .suggestions, .follow-up-suggestions {
    .chip, .suggestion-chip {
      touch-action: manipulation;
      -webkit-tap-highlight-color: transparent;
      min-height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &:active {
        transform: scale(0.95);
        transition: transform 0.1s ease;
      }
    }
  }
}
</style>

 
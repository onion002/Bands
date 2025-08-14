<template>
  <div class="poster-girl-demo">
    <PageHeader 
      title="🎭 看板娘演示" 
      subtitle="展示看板娘模块的各种功能和API使用"
    />
    
    <div class="demo-container">
      <!-- 状态展示区 -->
      <div class="demo-section">
        <h3>📊 状态监控</h3>
        <div class="status-cards">
          <div class="status-card">
            <div class="status-label">显示状态</div>
            <div class="status-value" :class="{ hidden: isHidden }">
              {{ isHidden ? '已隐藏' : '显示中' }}
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-label">拖拽状态</div>
            <div class="status-value" :class="{ active: isDragging }">
              {{ isDragging ? '拖拽中' : '静止' }}
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-label">当前消息</div>
            <div class="status-value">
              {{ currentMessage || '无消息' }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 控制面板 -->
      <div class="demo-section">
        <h3>🎮 控制面板</h3>
        <div class="control-panel">
          <div class="control-group">
            <label>基本控制</label>
            <div class="button-group">
              <button @click="togglePosterGirl" class="demo-btn">
                {{ isHidden ? '显示' : '隐藏' }}看板娘
              </button>
              <button @click="reloadPosterGirl" class="demo-btn">重载</button>
              <button @click="togglePosition" class="demo-btn">切换位置</button>
            </div>
          </div>
          
          <div class="control-group">
            <label>模型控制</label>
            <div class="button-group">
              <button @click="switchModel" class="demo-btn">随机切换模型</button>
              <button @click="sendCustomMessage" class="demo-btn">发送消息</button>
              <button @click="handleTouch" class="demo-btn">模拟触摸</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 配置面板 -->
      <div class="demo-section">
        <h3>⚙️ 配置预览</h3>
        <div class="config-preview">
          <pre>{{ JSON.stringify(pioConfig, null, 2) }}</pre>
        </div>
      </div>
      
      <!-- API示例 -->
      <div class="demo-section">
        <h3>💻 API使用示例</h3>
        <div class="api-examples">
          <div class="example-card">
            <h4>组合式API</h4>
            <pre><code>// 使用看板娘主要功能
import { usePosterGirl } from '@/modules/poster-girl'

const {
  isHidden,
  showMessage,
  switchModel,
  togglePosterGirl
} = usePosterGirl()

// 显示自定义消息
showMessage('你好！我是看板娘')

// 随机切换模型
await switchModel()</code></pre>
          </div>
          
          <div class="example-card">
            <h4>模型管理</h4>
            <pre><code>// 使用模型管理器
import { useModelManager } from '@/modules/poster-girl'

const {
  availableModels,
  currentModelIndex,
  switchToRandomModel
} = useModelManager()

// 切换到随机模型
const result = await switchToRandomModel()
if (result.success) {
  console.log('切换成功:', result.modelName)
}</code></pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { usePosterGirl } from '@/modules/poster-girl'
import PageHeader from '@/components/PageHeader.vue'

// 使用看板娘组合式API
const {
  isHidden,
  isDragging,
  currentMessage,
  pioConfig,
  showMessage,
  switchModel,
  togglePosterGirl,
  reloadPosterGirl,
  togglePosition,
  handleTouch
} = usePosterGirl()

// 发送自定义消息
const sendCustomMessage = () => {
  const messages = [
    "这是一条演示消息！",
    "看板娘模块运行正常 ✨",
    "你可以自定义任何消息内容",
    "支持数组形式的随机消息",
    "模块化架构让一切都很简单！"
  ]
  showMessage(messages)
}

onMounted(() => {
  showMessage("欢迎来到看板娘演示页面！🎉")
})
</script>

<style lang="scss" scoped>
.poster-girl-demo {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .demo-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    
    .demo-section {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      
      h3 {
        margin: 0 0 1.5rem 0;
        color: #333;
        font-size: 1.4rem;
        font-weight: 600;
      }
    }
    
    .status-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      
      .status-card {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .status-label {
          font-size: 0.85rem;
          color: #64748b;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .status-value {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
          
          &.hidden {
            color: #ef4444;
          }
          
          &.active {
            color: #10b981;
          }
        }
      }
    }
    
    .control-panel {
      .control-group {
        margin-bottom: 1.5rem;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        label {
          display: block;
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.75rem;
          font-size: 1rem;
        }
        
        .button-group {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        .demo-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 0.9rem;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
          }
          
          &:active {
            transform: translateY(0);
          }
        }
      }
    }
    
    .config-preview {
      background: #1e293b;
      color: #e2e8f0;
      padding: 1.5rem;
      border-radius: 8px;
      overflow-x: auto;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 0.85rem;
      line-height: 1.5;
      
      pre {
        margin: 0;
        white-space: pre-wrap;
      }
    }
    
    .api-examples {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1.5rem;
      
      .example-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        
        h4 {
          background: #334155;
          color: white;
          margin: 0;
          padding: 1rem;
          font-size: 1rem;
          font-weight: 600;
        }
        
        pre {
          margin: 0;
          padding: 1.5rem;
          background: #1e293b;
          color: #e2e8f0;
          overflow-x: auto;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.8rem;
          line-height: 1.6;
          
          code {
            color: inherit;
            background: none;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .poster-girl-demo .demo-container {
    padding: 1rem;
    
    .status-cards {
      grid-template-columns: 1fr;
    }
    
    .api-examples {
      grid-template-columns: 1fr;
    }
    
    .control-panel .button-group {
      flex-direction: column;
      
      .demo-btn {
        width: 100%;
      }
    }
  }
}
</style>
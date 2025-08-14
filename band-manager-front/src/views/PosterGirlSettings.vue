<template>
  <div class="poster-girl-settings">
    <div class="settings-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>🎭 看板娘设置</h1>
        <p>自定义您的虚拟助手，让她更符合您的需求</p>
      </div>

      <!-- 设置表单 -->
      <form @submit.prevent="saveSettings" class="settings-form">
        <!-- 基本设置 -->
        <div class="settings-section">
          <h3>⚙️ 基本设置</h3>
          
          <div class="form-group">
            <label for="mode">显示模式</label>
            <select id="mode" v-model="settings.mode" class="form-control">
              <option value="static">静态模式 - 只显示看板娘和文字提示</option>
              <option value="fixed">固定模式 - 增加功能按钮（推荐）</option>
              <option value="draggable">可移动模式 - 用户可以拖拽位置</option>
            </select>
          </div>

          <div class="form-group">
            <label for="hidden">移动端隐藏</label>
            <div class="checkbox-wrapper">
              <input 
                type="checkbox" 
                id="hidden" 
                v-model="settings.hidden"
                class="form-checkbox"
              >
              <span class="checkbox-label">在移动设备上隐藏看板娘</span>
            </div>
          </div>

          <div class="form-group">
            <label for="tips">启用时间小贴士</label>
            <div class="checkbox-wrapper">
              <input 
                type="checkbox" 
                id="tips" 
                v-model="settings.tips"
                class="form-checkbox"
              >
              <span class="checkbox-label">显示时间相关的生活小贴士</span>
            </div>
          </div>
        </div>

        <!-- 尺寸设置 -->
        <div class="settings-section">
          <h3>📏 尺寸设置</h3>
          
          <div class="size-inputs">
            <div class="form-group">
              <label for="width">宽度 (像素)</label>
              <input 
                type="number" 
                id="width" 
                v-model.number="settings.size.width" 
                class="form-control"
                min="100"
                max="800"
                step="10"
                placeholder="280"
              >
              <small class="form-help">设置看板娘的宽度，范围：100-800像素</small>
            </div>
            
            <div class="form-group">
              <label for="height">高度 (像素)</label>
              <input 
                type="number" 
                id="height" 
                v-model.number="settings.size.height" 
                class="form-control"
                min="100"
                max="800"
                step="10"
                placeholder="250"
              >
              <small class="form-help">设置看板娘的高度，范围：100-800像素</small>
            </div>
          </div>
          
          <div class="size-preview">
            <h4>尺寸预览</h4>
            <div class="preview-box" :style="{ width: settings.size.width + 'px', height: settings.size.height + 'px' }">
              <div class="preview-label">
                {{ settings.size.width }} × {{ settings.size.height }}
              </div>
            </div>
            <small class="form-help">预览看板娘的实际显示尺寸</small>
            
            <div class="preview-actions">
              <button 
                type="button" 
                @click="previewSize"
                class="btn btn-info btn-sm"
              >
                <i class="fas fa-eye"></i> 实时预览
              </button>
              <button 
                type="button" 
                @click="resetSize"
                class="btn btn-secondary btn-sm"
              >
                <i class="fas fa-undo"></i> 重置尺寸
              </button>
            </div>
          </div>
        </div>

        <!-- 模型设置 -->
        <div class="settings-section">
          <h3>🎨 默认模型设置</h3>
          
          <div class="form-group">
            <label for="defaultModel">默认启动模型</label>
            <select 
              id="defaultModel" 
              v-model="settings.defaultModel" 
              class="form-control"
            >
              <option 
                v-for="model in availableModels" 
                :key="model.path"
                :value="model.path"
              >
                {{ model.name }}
              </option>
            </select>
            <small class="form-help">选择看板娘启动时默认加载的模型</small>
          </div>

          <div class="model-preview">
            <h4>可用模型预览</h4>
            <div class="model-list">
              <div 
                v-for="model in availableModels" 
                :key="model.path"
                class="model-item"
                :class="{ active: model.path === settings.defaultModel }"
                @click="selectDefaultModel(model.path)"
              >
                <img :src="model.preview" :alt="model.name" class="model-preview-img">
                <div class="model-info">
                  <span class="model-name">{{ model.name }}</span>
                  <span class="model-description">{{ model.description }}</span>
                </div>
              </div>
            </div>
            
            <div class="switch-model-info">
              <h5>💡 提示</h5>
              <p>• <strong>默认模型</strong>：看板娘启动时加载的模型</p>
              <p>• <strong>随机切换</strong>：点击看板娘的切换按钮可随机切换所有可用模型</p>
              <p>• 共有 <strong>{{ availableModels.length }}</strong> 个模型可供切换</p>
            </div>
          </div>
        </div>

        <!-- 交互提示设置 -->
        <div class="settings-section">
          <h3>💬 交互提示设置</h3>
          
          <div class="form-group">
            <label for="welcome">欢迎语</label>
            <div class="array-input">
              <div 
                v-for="(item, index) in settings.content.welcome" 
                :key="index"
                class="array-item"
              >
                <input 
                  type="text" 
                  v-model="settings.content.welcome[index]" 
                  class="form-control"
                  :placeholder="`欢迎语 ${index + 1}`"
                >
                <button 
                  type="button" 
                  @click="removeArrayItem('welcome', index)"
                  class="remove-btn"
                  v-if="settings.content.welcome.length > 1"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button 
                type="button" 
                @click="addArrayItem('welcome')"
                class="add-btn"
              >
                <i class="fas fa-plus"></i> 添加欢迎语
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="touch">触摸提示</label>
            <div class="array-input">
              <div 
                v-for="(item, index) in settings.content.touch" 
                :key="index"
                class="array-item"
              >
                <input 
                  type="text" 
                  :value="getTouchMessage(index)"
                  @input="updateTouchMessage(index, $event)"
                  class="form-control"
                  :placeholder="`触摸提示 ${index + 1}`"
                >
                <button 
                  type="button" 
                  @click="removeArrayItem('touch', index)"
                  class="remove-btn"
                  v-if="(settings.content.touch || []).length > 1"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button 
                type="button" 
                @click="addArrayItem('touch')"
                class="add-btn"
              >
                <i class="fas fa-plus"></i> 添加触摸提示
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="skin">换装提示</label>
            <div class="array-input">
              <div class="array-item">
                <input 
                  type="text" 
                  :value="getSkinMessage(0)"
                  @input="updateSkinMessage(0, $event)"
                  class="form-control"
                  placeholder="换装前提示"
                >
              </div>
              <div class="array-item">
                <input 
                  type="text" 
                  :value="getSkinMessage(1)"
                  @input="updateSkinMessage(1, $event)"
                  class="form-control"
                  placeholder="换装后提示"
                >
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="home">首页提示</label>
            <input 
              type="text" 
              id="home" 
              v-model="settings.content.home" 
              class="form-control"
              placeholder="点击首页按钮时的提示"
            >
          </div>

          <div class="form-group">
            <label for="close">关闭提示</label>
            <input 
              type="text" 
              id="close" 
              v-model="settings.content.close" 
              class="form-control"
              placeholder="关闭看板娘时的提示"
            >
          </div>
        </div>

        <!-- 自定义提示设置 -->
        <div class="settings-section">
          <h3>🎯 自定义提示设置</h3>
          
          <div class="custom-tips">
            <div 
              v-for="(tip, index) in (settings.content.custom || [])" 
              :key="index"
              class="custom-tip-item"
            >
              <div class="tip-header">
                <span class="tip-number">提示 {{ index + 1 }}</span>
                <button 
                  type="button" 
                  @click="removeCustomTip(index)"
                  class="remove-btn"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
              
              <div class="tip-content">
                <div class="form-group">
                  <label>选择器</label>
                  <input 
                    type="text" 
                    v-model="tip.selector" 
                    class="form-control"
                    placeholder=".band-card, .event-card 等"
                  >
                </div>
                
                <div class="form-group">
                  <label>提示类型</label>
                  <select v-model="tip.type" class="form-control">
                    <option value="">普通提示</option>
                    <option value="read">阅读提示</option>
                    <option value="link">链接提示</option>
                  </select>
                </div>
                
                <div class="form-group" v-if="!tip.type">
                  <label>提示文字</label>
                  <input 
                    type="text" 
                    v-model="tip.text" 
                    class="form-control"
                    placeholder="鼠标悬停时显示的提示"
                  >
                </div>
              </div>
            </div>
            
            <button 
              type="button" 
              @click="addCustomTip"
              class="add-btn large"
            >
              <i class="fas fa-plus"></i> 添加自定义提示
            </button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" @click="resetSettings" class="btn btn-secondary">
            <i class="fas fa-undo"></i> 重置设置
          </button>
          <button type="button" @click="previewSettings" class="btn btn-info">
            <i class="fas fa-eye"></i> 预览效果
          </button>
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i> 保存设置
          </button>
        </div>
      </form>
    </div>

    <!-- 预览模态框 -->
    <div v-if="showPreview" class="preview-modal" @click="closePreview">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>🎭 设置预览</h3>
          <button @click="closePreview" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="preview-body">
          <p><strong>当前配置预览：</strong></p>
          <pre>{{ JSON.stringify(settings, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getCurrentConfig, saveConfig, defaultPosterGirlConfig, type PosterGirlConfig, AVAILABLE_MODELS } from '@/modules/poster-girl/config/posterGirl'

// 响应式数据
const showPreview = ref(false)
const settings = reactive<PosterGirlConfig>(getCurrentConfig())

// 可用模型列表（从全局配置导入）
const availableModels = ref(AVAILABLE_MODELS)

// 添加数组项
const addArrayItem = (key: 'welcome' | 'touch') => {
  if (Array.isArray(settings.content[key])) {
    (settings.content[key] as string[]).push('')
  }
}

// 移除数组项
const removeArrayItem = (key: 'welcome' | 'touch', index: number) => {
  if (Array.isArray(settings.content[key]) && (settings.content[key] as string[]).length > 1) {
    (settings.content[key] as string[]).splice(index, 1)
  }
}

// 获取触摸提示消息
const getTouchMessage = (index: number): string => {
  return settings.content.touch?.[index] || ''
}

// 更新触摸提示消息
const updateTouchMessage = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  if (!settings.content.touch) {
    settings.content.touch = []
  }
  if (!Array.isArray(settings.content.touch)) {
    settings.content.touch = []
  }
  settings.content.touch[index] = target.value
}

// 获取皮肤提示消息
const getSkinMessage = (index: number): string => {
  return settings.content.skin?.[index] || ''
}

// 更新皮肤提示消息
const updateSkinMessage = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  if (!settings.content.skin) {
    settings.content.skin = ['', '']
  }
  if (!Array.isArray(settings.content.skin)) {
    settings.content.skin = ['', '']
  }
  settings.content.skin[index] = target.value
}

// 添加自定义提示
const addCustomTip = () => {
  if (!settings.content.custom) {
    settings.content.custom = []
  }
  settings.content.custom.push({
    selector: '',
    type: undefined,
    text: ''
  })
}

// 移除自定义提示
const removeCustomTip = (index: number) => {
  if (settings.content.custom) {
    settings.content.custom.splice(index, 1)
  }
}

// 选择默认模型
const selectDefaultModel = (path: string) => {
  settings.defaultModel = path
}

// 预览尺寸
const previewSize = () => {
  // 发送消息给主页面，实时预览尺寸
  if (window.parent !== window) {
    window.parent.postMessage({
      type: 'previewPosterGirlSize',
      size: settings.size
    }, '*')
  }
  
  // 在设置页面显示预览信息
  alert(`尺寸预览：${settings.size.width} × ${settings.size.height}\n\n点击保存设置后，看板娘将应用新尺寸！`)
}

// 重置尺寸
const resetSize = () => {
  settings.size.width = defaultPosterGirlConfig.size.width
  settings.size.height = defaultPosterGirlConfig.size.height
}

// 重置设置
const resetSettings = () => {
  const cloned = JSON.parse(JSON.stringify(defaultPosterGirlConfig)) as PosterGirlConfig
  Object.assign(settings, cloned)
}

// 预览设置
const previewSettings = () => {
  showPreview.value = true
}

// 关闭预览
const closePreview = () => {
  showPreview.value = false
}

// 保存设置
const saveSettings = () => {
  try {
    console.log('开始保存设置...')
    console.log('当前设置:', settings)
    
    // 简单验证
    if (!settings.mode || !settings.model || !settings.content.welcome) {
      alert('设置验证失败：请填写所有必需字段')
      return
    }
    
    // 直接保存设置（验证和补全会自动处理）
    saveConfig(settings)
    
    console.log('设置保存成功，localStorage中的配置:', localStorage.getItem('posterGirlSettings'))
    
    alert('设置保存成功！看板娘将自动应用新设置。')
    
    // 通知当前窗口内其它组件
    window.dispatchEvent(new CustomEvent('posterGirl:updated', { detail: settings }))

    // 同时兼容在 iframe 中时通知父窗口
    if (window.parent !== window) {
      window.parent.postMessage({
        type: 'posterGirlConfigUpdated',
        config: settings
      }, '*')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('保存设置失败，请重试')
  }
}

// 加载保存的设置
const loadSettings = () => {
  try {
    const currentSettings = getCurrentConfig()
    Object.assign(settings, currentSettings)
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.poster-girl-settings {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem 0;
}

.settings-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
  
  h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  p {
    font-size: 1.1rem;
    opacity: 0.9;
  }
}

.settings-form {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.settings-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e8e8e8;
  
  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }
  
  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
}

.form-group {
  margin-bottom: 1rem;
  
  label {
    display: block;
    margin-bottom: 0.4rem;
    font-weight: 600;
    color: #555;
    font-size: 0.95rem;
  }
  
  .form-control {
    width: 100%;
    padding: 0.6rem 0.75rem;
    border: 1.5px solid #e1e5e9;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    
    &:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
  }
  
  .form-help {
    display: block;
    margin-top: 0.2rem;
    font-size: 0.8rem;
    color: #666;
  }
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  
  .form-checkbox {
    width: 18px;
    height: 18px;
    accent-color: #667eea;
  }
  
  .checkbox-label {
    font-weight: 500;
    color: #555;
    font-size: 0.95rem;
  }
}

.array-input {
  .array-item {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 0.4rem;
    align-items: center;
    
    .form-control {
      flex: 1;
    }
    
    .remove-btn {
      padding: 0.4rem;
      background: #ff4757;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 0.8rem;
      
      &:hover {
        background: #ff3742;
        transform: scale(1.05);
      }
    }
  }
  
  .add-btn {
    padding: 0.6rem 1.2rem;
    background: #2ed573;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 0.9rem;
    
    &:hover {
      background: #26d0ce;
      transform: translateY(-2px);
    }
    
    &.large {
      width: 100%;
      padding: 0.8rem;
      font-size: 1rem;
    }
  }
}

.model-preview {
  margin-top: 0.8rem;
  
  h4 {
    margin-bottom: 0.8rem;
    color: #333;
    font-size: 1.1rem;
  }
  
  .model-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 0.8rem;
  }
  
  .model-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem;
    border: 1.5px solid #e1e5e9;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #667eea;
      transform: translateY(-1px);
    }
    
    &.active {
      border-color: #667eea;
      background: rgba(102, 126, 234, 0.1);
    }
    
    .model-preview-img {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      object-fit: cover;
    }
    
    .model-info {
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      
      .model-name {
        font-weight: 600;
        color: #333;
        font-size: 0.95rem;
      }
      
      .model-description {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
      }
    }
  }
  
  .switch-model-info {
    margin-top: 1.2rem;
    padding: 1rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 8px;
    border-left: 4px solid #667eea;
    
    h5 {
      margin: 0 0 0.8rem 0;
      color: #667eea;
      font-size: 1rem;
      font-weight: 600;
    }
    
    p {
      margin: 0.4rem 0;
      font-size: 0.9rem;
      color: #555;
      line-height: 1.5;
      
      strong {
        color: #333;
        font-weight: 600;
      }
    }
  }
}

.custom-tips {
  .custom-tip-item {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    
    .tip-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.8rem;
      
      .tip-number {
        font-weight: 600;
        color: #333;
        font-size: 1rem;
      }
      
      .remove-btn {
        padding: 0.4rem;
        background: #ff4757;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.8rem;
        
        &:hover {
          background: #ff3742;
          transform: scale(1.05);
        }
      }
    }
    
    .tip-content {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0.8rem;
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }
  }
}

.size-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.size-preview {
  margin-top: 1.2rem;
  padding: 1.2rem;
  background: #f8f9fa;
  border-radius: 12px;
  text-align: center;
  
  h4 {
    margin-bottom: 0.8rem;
    color: #333;
    font-size: 1.1rem;
  }
  
  .preview-box {
    margin: 0 auto 0.8rem;
    border: 1.5px dashed #667eea;
    border-radius: 8px;
    background: linear-gradient(45deg, #667eea20, #764ba220);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #5a6fd8;
      background: linear-gradient(45deg, #5a6fd820, #6a4c9320);
    }
    
    .preview-label {
      color: #667eea;
      font-weight: 600;
      font-size: 1rem;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
  }
  
  .preview-actions {
    display: flex;
    gap: 0.4rem;
    justify-content: center;
    margin-top: 0.8rem;
    
    .btn-sm {
      padding: 0.4rem 0.8rem;
      font-size: 0.8rem;
    }
  }
}

.form-actions {
  display: flex;
  gap: 0.8rem;
  justify-content: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e8e8e8;
  
  .btn {
    padding: 0.8rem 1.6rem;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    &.btn-primary {
      background: #667eea;
      color: white;
      
      &:hover {
        background: #5a6fd8;
      }
    }
    
    &.btn-secondary {
      background: #6c757d;
      color: white;
      
      &:hover {
        background: #5a6268;
      }
    }
    
    &.btn-info {
      background: #17a2b8;
      color: white;
      
      &:hover {
        background: #138496;
      }
    }
    
    &.btn-sm {
      padding: 0.4rem 0.8rem;
      font-size: 0.8rem;
    }
  }
}

// 预览模态框
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  
  .preview-content {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    max-width: 800px;
    max-height: 80vh;
    overflow-y: auto;
    
    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      
      h3 {
        margin: 0;
        color: #333;
      }
      
      .close-btn {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #666;
        
        &:hover {
          color: #333;
        }
      }
    }
    
    .preview-body {
      pre {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        overflow-x: auto;
        font-size: 0.875rem;
        line-height: 1.5;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .settings-container {
    padding: 0 1rem;
  }
  
  .settings-form {
    padding: 1.2rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .form-actions {
    flex-direction: column;
    
    .btn {
      width: 100%;
      justify-content: center;
    }
  }
  
  .size-inputs {
    grid-template-columns: 1fr;
  }
  
  .tip-content {
    grid-template-columns: 1fr !important;
  }
}
</style>

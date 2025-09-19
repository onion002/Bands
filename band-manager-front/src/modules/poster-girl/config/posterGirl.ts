// 看板娘配置文件
export interface PosterGirlConfig {
  mode: 'static' | 'fixed' | 'draggable'
  hidden: boolean
  size: {
    width: number
    height: number
  }
  content: {
    welcome: string | string[]
    touch?: string | string[]
    skin?: [string, string]
    home?: string | string[]
    close?: string | string[]
    link?: string
    referer?: string
    custom?: Array<{
      selector: string
      type?: 'read' | 'link'
      text?: string
    }>
  }
  night?: string
  model: string[]
  defaultModel?: string  // 新增：默认启动模型
  tips?: boolean
  dragPosition?: {
    x: number
    y: number
  }
}

// 全局可用模型列表
export const AVAILABLE_MODELS = [
  {
    name: '默认模型 (Pio)',
    path: '/poster-girl-assets/models/pio/model.json',
    preview: '/poster-girl-assets/static/avatar.jpg',
    description: '经典的看板娘模型'
  },
  {
    name: 'Remu 模型',
    path: '/poster-girl-assets/models/remu/model.json',
    preview: '/poster-girl-assets/static/avatar.jpg',
    description: '可爱的Remu角色'
  },
  {
    name: 'Umaru 模型',
    path: '/poster-girl-assets/models/umaru/xiaomai.model.json',
    preview: '/poster-girl-assets/static/avatar.jpg',
    description: '活泼的Umaru角色'
  }
]

// 默认配置
export const defaultPosterGirlConfig: PosterGirlConfig = {
  mode: "draggable",
  hidden: false,
  tips: true, // 启用提示系统
  size: {
    width: 280,
    height: 340
  },
  content: {
    welcome: [
      "欢迎来到乐队管理系统！🎸",
      "今天想要管理什么乐队呢？",
      "让我们一起创造美妙的音乐吧！🎵"
    ],
    touch: [
      "哎呀，别摸我啦！😊",
      "我是你的音乐小助手~",
      "有什么需要帮助的吗？",
      "你来啦，我好开心！"
    ],
    skin: [
      "想看看我的新服装吗？",
      "新衣服真漂亮~"
    ],
    home: "点击这里回到首页！",
    close: "下次再见吧~",
    custom: [
      {
        selector: ".band-card",
        text: "这个乐队看起来很棒呢！"
      },
      {
        selector: ".card", 
        text: "这个卡片很有趣呢！"
      },
      {
        selector: ".music-box",
        text: "想要听美妙的音乐吗？😝"
      },
      {
        selector: ".pio-skin",
        text: "我会变身的哦😉"
      },
      {
        selector: ".pio-teacher",
        text: "我是你的音乐老师哦😉"
      },
      {
        selector: ".pio-settings",
        text: "我是你的看板娘哦😉"
      },
      {
        selector: ".pio-music",
        text: "我是你的音乐助手哦😉"
      },
      {
        selector: ".favorite-btn",
        text: "喜欢可以收藏哦！♥"
      },
      {
        selector: ".play-btn",
        text: "点击即可播放。🎧"
      },
      {
        selector: ".pio-close",
        text: "我会想你的😙"
      }

    ]
  },
  model: [
    "/poster-girl-assets/models/pio/model.json",
    "/poster-girl-assets/models/remu/model.json",
    "/poster-girl-assets/models/umaru/xiaomai.model.json"
  ],
  defaultModel: "/poster-girl-assets/models/remu/model.json"
}

// 配置模式枚举
export type ConfigMode = 'default' | 'localStorage'

// 获取当前配置模式
export function getCurrentConfigMode(): ConfigMode {
  const mode = localStorage.getItem('posterGirlConfigMode')
  return mode === 'default' ? 'default' : 'localStorage'
}

// 设置配置模式
export function setConfigMode(mode: ConfigMode): void {
  localStorage.setItem('posterGirlConfigMode', mode)
  console.log('配置模式已切换至:', mode)
}

// 获取当前配置（根据配置模式决定使用默认配置还是localStorage配置）
export function getCurrentConfig(): PosterGirlConfig {
  const configMode = getCurrentConfigMode()
  
  if (configMode === 'default') {
    console.log('使用默认配置')
    return { ...defaultPosterGirlConfig }
  }
  
  // localStorage模式
  try {
    const saved = localStorage.getItem('posterGirlSettings')
    if (saved) {
      const savedConfig = JSON.parse(saved)
      console.log('加载保存的配置:', savedConfig)
      return savedConfig
    }
  } catch (error) {
    console.error('加载看板娘配置失败:', error)
  }
  
  console.log('localStorage配置不存在，使用默认配置')
  return { ...defaultPosterGirlConfig }
}

// 检查是否有localStorage配置
export function hasLocalStorageConfig(): boolean {
  try {
    const saved = localStorage.getItem('posterGirlSettings')
    return saved !== null && saved.trim() !== ''
  } catch (error) {
    return false
  }
}

// 清除localStorage配置
export function clearLocalStorageConfig(): void {
  try {
    localStorage.removeItem('posterGirlSettings')
    console.log('localStorage配置已清除')
  } catch (error) {
    console.error('清除localStorage配置失败:', error)
  }
}

// 保存配置到localStorage
export function saveConfig(config: PosterGirlConfig): void {
  try {
    // 验证配置完整性
    const validatedConfig = validateConfig(config)
    localStorage.setItem('posterGirlSettings', JSON.stringify(validatedConfig))
    console.log('配置保存成功:', validatedConfig)
  } catch (error) {
    console.error('保存看板娘配置失败:', error)
  }
}

// 获取配置模式状态信息
export function getConfigModeInfo(): {
  currentMode: ConfigMode
  hasLocalConfig: boolean
  modeDescription: string
} {
  const currentMode = getCurrentConfigMode()
  const hasLocalConfig = hasLocalStorageConfig()
  
  let modeDescription = ''
  if (currentMode === 'default') {
    modeDescription = '使用系统默认配置，所有设置都是初始值'
  } else {
    if (hasLocalConfig) {
      modeDescription = '使用本地保存的自定义配置'
    } else {
      modeDescription = '本地模式但无自定义配置，将使用默认配置'
    }
  }
  
  return {
    currentMode,
    hasLocalConfig,
    modeDescription
  }
}

// 简单的配置验证函数
function validateConfig(config: any): PosterGirlConfig {
  // 确保配置结构完整
  if (!config.content) {
    config.content = {}
  }
  if (!config.content.welcome) {
    config.content.welcome = defaultPosterGirlConfig.content.welcome
  }
  if (!config.content.touch) {
    config.content.touch = defaultPosterGirlConfig.content.touch
  }
  if (!config.content.skin) {
    config.content.skin = defaultPosterGirlConfig.content.skin
  }
  if (!config.content.custom) {
    config.content.custom = defaultPosterGirlConfig.content.custom
  }
  if (!config.model) {
    config.model = defaultPosterGirlConfig.model
  }
  if (!config.size) {
    config.size = defaultPosterGirlConfig.size
  }
  if (config.tips === undefined) {
    config.tips = true
  }
  
  // 确保有默认模型设置
  if (!config.defaultModel && config.model && config.model.length > 0) {
    config.defaultModel = config.model[0]
  }
  
  return config as PosterGirlConfig
}

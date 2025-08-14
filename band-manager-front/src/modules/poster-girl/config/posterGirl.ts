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
    height: 250
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
        selector: "button",
        text: "点击这个按钮试试看~"
      }
    ]
  },
  model: [
    "/poster-girl-assets/models/pio/model.json",
    "/poster-girl-assets/models/remu/model.json",
    "/poster-girl-assets/models/umaru/xiaomai.model.json"
  ],
  defaultModel: "/poster-girl-assets/models/pio/model.json"
}

// 自定义配置示例
export const customPosterGirlConfig: PosterGirlConfig = {
  mode: "draggable",
  hidden: false,
  size: {
    width: 320,
    height: 280
  },
  content: {
    welcome: [
      "🎵 音乐无界，梦想无限！",
      "欢迎来到我们的音乐世界~",
      "今天想要探索什么音乐呢？"
    ],
    touch: [
      "🎸 让我们一起摇滚吧！",
      "🎹 钢琴声真美妙~",
      "🥁 鼓点节奏感十足！"
    ],
    skin: [
      "想看看我的新造型吗？",
      "新装扮很适合我呢~"
    ],
    home: "回到音乐之家！",
    close: "音乐永不停歇，下次见！",
    custom: [
      {
        selector: ".band-card",
        text: "这个乐队的风格很独特！"
      },
      {
        selector: ".card", 
        text: "这个卡片很有趣呢！"
      },
      {
        selector: "button",
        text: "点击这个按钮试试看~"
      },
      {
        type: "read",
        selector: ".post-item a"
      },
      {
        type: "link",
        selector: ".post-content a"
      }
    ]
  },
  model: [
    "/pio/models/pio/model.json",
    "/pio/models/remu/model.json"
  ],
  tips: true
}

// 获取当前配置（直接使用localStorage中的配置，如果没有则使用默认配置）
export function getCurrentConfig(): PosterGirlConfig {
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
  
  console.log('使用默认配置')
  return { ...defaultPosterGirlConfig }
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

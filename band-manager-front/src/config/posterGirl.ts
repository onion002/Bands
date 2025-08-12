// 看板娘配置文件
export interface PosterGirlConfig {
  mode: 'static' | 'fixed' | 'draggable'
  hidden: boolean
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
  tips?: boolean
}

// 默认配置
export const defaultPosterGirlConfig: PosterGirlConfig = {
  mode: "fixed",
  hidden: false,
  content: {
    welcome: [
      "欢迎来到乐队管理系统！🎸",
      "今天想要管理什么乐队呢？",
      "让我们一起创造美妙的音乐吧！🎵"
    ],
    touch: [
      "哎呀，别摸我啦！😊",
      "我是你的音乐小助手~",
      "有什么需要帮助的吗？"
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
        selector: ".event-card", 
        text: "这个活动一定很精彩！"
      },
      {
        selector: ".member-card",
        text: "这位成员很有才华呢！"
      }
    ]
  },
  model: ["/pio/models/pio/model.json"]
}

// 自定义配置示例
export const customPosterGirlConfig: PosterGirlConfig = {
  mode: "draggable",
  hidden: false,
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
        selector: ".event-card", 
        text: "这个演出一定很精彩！"
      },
      {
        selector: ".member-card",
        text: "这位音乐家很有天赋！"
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
  model: ["/pio/models/pio/model.json"],
  tips: true
}

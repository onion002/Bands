/**
 * 🚀 懒加载 Markdown 处理库
 * 减少初始包大小，按需加载重库
 */

interface MarkdownRenderer {
  render: (text: string) => string
}

interface SyntaxHighlighter {
  highlight: (code: string, language: string) => string
}

// 缓存已加载的库
let markedInstance: MarkdownRenderer | null = null
let highlightInstance: SyntaxHighlighter | null = null

/**
 * 懒加载 marked 库
 */
export async function loadMarked(): Promise<MarkdownRenderer> {
  if (markedInstance) {
    return markedInstance
  }

  try {
    const { marked } = await import('marked')
    
    // 配置 marked 选项
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: false,
      mangle: false
    })

    markedInstance = marked
    return marked
  } catch (error) {
    console.error('Failed to load marked library:', error)
    // 返回简单的文本渲染器作为后备
    return {
      render: (text: string) => text.replace(/\n/g, '<br>')
    }
  }
}

/**
 * 懒加载 highlight.js 库
 */
export async function loadHighlight(): Promise<SyntaxHighlighter> {
  if (highlightInstance) {
    return highlightInstance
  }

  try {
    const hljs = await import('highlight.js')
    
    // 只加载常用语言以减小包大小
    hljs.registerLanguage('javascript', hljs.languages.javascript!)
    hljs.registerLanguage('typescript', hljs.languages.typescript!)
    hljs.registerLanguage('html', hljs.languages.xml!)
    hljs.registerLanguage('css', hljs.languages.css!)
    hljs.registerLanguage('json', hljs.languages.json!)
    hljs.registerLanguage('bash', hljs.languages.bash!)
    hljs.registerLanguage('python', hljs.languages.python!)

    highlightInstance = hljs.default
    return hljs.default
  } catch (error) {
    console.error('Failed to load highlight.js library:', error)
    // 返回简单的代码高亮器作为后备
    return {
      highlight: (code: string) => `<pre><code>${code}</code></pre>`
    }
  }
}

/**
 * 渲染 Markdown 文本（带语法高亮）
 */
export async function renderMarkdown(text: string): Promise<string> {
  try {
    const [marked, hljs] = await Promise.all([
      loadMarked(),
      loadHighlight()
    ])

    // 使用 marked 渲染 Markdown
    const html = marked.render(text)
    
    // 应用语法高亮
    const highlightedHtml = html.replace(
      /<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
      (match, lang, code) => {
        try {
          const highlighted = hljs.highlight(code, { language: lang })
          return `<pre><code class="hljs language-${lang}">${highlighted.value}</code></pre>`
        } catch {
          return match
        }
      }
    )

    return highlightedHtml
  } catch (error) {
    console.error('Failed to render markdown:', error)
    // 返回原始文本作为后备
    return text.replace(/\n/g, '<br>')
  }
}

/**
 * 预加载 Markdown 库（可选，用于关键页面）
 */
export function preloadMarkdownLibraries(): void {
  // 在空闲时间预加载
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      loadMarked()
      loadHighlight()
    })
  } else {
    // 降级到 setTimeout
    setTimeout(() => {
      loadMarked()
      loadHighlight()
    }, 1000)
  }
}
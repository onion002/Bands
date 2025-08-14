/**
 * 轻量级Markdown渲染器
 * 只包含必要的markdown解析功能，减少bundle大小
 */

// 简单的markdown解析规则
const markdownRules = [
  // 代码块
  { 
    pattern: /```(\w+)?\n([\s\S]*?)```/g, 
    replace: (match: string, lang: string, code: string) => {
      const language = lang || 'text'
      return `<pre class="code-block"><code class="language-${language}">${escapeHtml(code.trim())}</code></pre>`
    }
  },
  // 行内代码
  { 
    pattern: /`([^`]+)`/g, 
    replace: '<code class="inline-code">$1</code>' 
  },
  // 粗体
  { 
    pattern: /\*\*(.+?)\*\*/g, 
    replace: '<strong>$1</strong>' 
  },
  // 斜体
  { 
    pattern: /\*(.+?)\*/g, 
    replace: '<em>$1</em>' 
  },
  // 链接
  { 
    pattern: /\[([^\]]+)\]\(([^)]+)\)/g, 
    replace: '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>' 
  },
  // 标题
  { 
    pattern: /^### (.+)$/gm, 
    replace: '<h3>$1</h3>' 
  },
  { 
    pattern: /^## (.+)$/gm, 
    replace: '<h2>$1</h2>' 
  },
  { 
    pattern: /^# (.+)$/gm, 
    replace: '<h1>$1</h1>' 
  },
  // 列表
  { 
    pattern: /^\- (.+)$/gm, 
    replace: '<li>$1</li>' 
  },
  // 换行
  { 
    pattern: /\n/g, 
    replace: '<br>' 
  }
]

/**
 * HTML转义
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * 渲染markdown文本
 */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  
  let result = text
  
  // 应用所有markdown规则
  for (const rule of markdownRules) {
    result = result.replace(rule.pattern, rule.replace as any)
  }
  
  // 包装列表项
  if (result.includes('<li>')) {
    result = result.replace(/<li>(.+?)<\/li>/g, '<ul><li>$1</li></ul>')
    // 合并连续的ul标签
    result = result.replace(/<\/ul>\s*<ul>/g, '')
  }
  
  return result
}

/**
 * 高亮代码块
 */
export function highlightCodeBlocks(html: string): string {
  const codeBlocks = html.match(/<pre class="code-block">[\s\S]*?<\/pre>/g)
  
  if (!codeBlocks) return html
  
  codeBlocks.forEach(block => {
    const codeElement = block.match(/<code class="language-(\w+)">([\s\S]*?)<\/code>/)
    if (codeElement) {
      const [, language, code] = codeElement
      const highlightedCode = highlightCode(code, language)
      html = html.replace(block, `<pre class="code-block"><code class="language-${language}">${highlightedCode}</code></pre>`)
    }
  })
  
  return html
}

/**
 * 高亮代码
 */
function highlightCode(code: string, language: string): string {
  // 简单的语法高亮，可以根据需要扩展
  const keywords = ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'import', 'export', 'from', 'class', 'interface', 'type']
  const strings = /"[^"]*"/g
  const comments = /\/\/.*$/gm
  
  let highlighted = code
  
  // 高亮关键字
  keywords.forEach(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'g')
    highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`)
  })
  
  // 高亮字符串
  highlighted = highlighted.replace(strings, '<span class="string">$&</span>')
  
  // 高亮注释
  highlighted = highlighted.replace(comments, '<span class="comment">$&</span>')
  
  return highlighted
}
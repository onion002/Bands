// Live2D服务 - 处理Live2D模型的加载和渲染
export class Live2DService {
	private static instance: Live2DService
	private canvas: HTMLCanvasElement | null = null
	private isInitialized = false
	private currentModel: string | null = null

	private constructor() {}

	static getInstance(): Live2DService {
		if (!Live2DService.instance) {
			Live2DService.instance = new Live2DService()
		}
		return Live2DService.instance
	}

	// 初始化Live2D
	async init(canvas: HTMLCanvasElement): Promise<boolean> {
		try {
			this.canvas = canvas
			// 动态加载Live2D脚本（固定公共路径，资源由Vite插件复制到 public/poster-girl-assets）
			if (typeof (window as any).loadlive2d === 'undefined') {
				await this.loadScript('/poster-girl-assets/static/l2d.js')
			}

			// 检查Live2D是否可用
			if (typeof (window as any).loadlive2d === 'undefined') {
				throw new Error('Live2D脚本加载失败')
			}

			this.isInitialized = true
			console.log('Live2D服务初始化成功')
			return true
		} catch (error) {
			console.error('Live2D服务初始化失败:', error)
			return false
		}
	}

	// 加载Live2D模型
	async loadModel(modelPath: string): Promise<boolean> {
		if (!this.isInitialized || !this.canvas) {
			console.error('Live2D服务未初始化')
			return false
		}

		try {
			console.log('🎯 开始加载Live2D模型:', modelPath)
			// 检查模型路径是否有效
			if (!modelPath || typeof modelPath !== 'string') {
				throw new Error('无效的模型路径')
			}
			// 使用loadlive2d函数加载模型
			if (typeof (window as any).loadlive2d === 'function') {
				console.log('📦 调用loadlive2d函数...')
				try {
					;(window as any).loadlive2d('pio', modelPath)
					this.currentModel = modelPath
					console.log('✅ Live2D模型设置完成:', modelPath)
					return true
				} catch (loadError) {
					console.error('调用loadlive2d时出错:', loadError)
					throw loadError
				}
			} else {
				throw new Error('loadlive2d函数不可用')
			}
		} catch (error) {
			console.error('❌ 加载Live2D模型失败:', error)
			return false
		}
	}

	// 切换模型
	async switchModel(): Promise<boolean> {
		if (!this.isInitialized) {
			console.error('Live2D服务未初始化')
			return false
		}
		try {
			console.log('模型切换功能待实现')
			return true
		} catch (error) {
			console.error('模型切换失败:', error)
			return false
		}
	}

	// 动态加载脚本
	private loadScript(src: string): Promise<void> {
		return new Promise((resolve, reject) => {
			const script = document.createElement('script')
			script.src = src
			script.onload = () => resolve()
			script.onerror = () => reject(new Error(`Failed to load script: ${src}`))
			document.head.appendChild(script)
		})
	}

	// 销毁服务
	destroy() {
		try {
			if (typeof (window as any).Live2D !== 'undefined' && this.canvas) {
				const gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl')
				if (gl && gl instanceof WebGLRenderingContext) {
					const ext = (gl as any).getExtension('WEBGL_lose_context')
					if (ext) {
						ext.loseContext()
					}
				}
			}
		} catch (error) {
			console.warn('清理Live2D资源时出现错误:', error)
		}
		this.canvas = null
		this.isInitialized = false
		this.currentModel = null
		console.log('Live2D服务已销毁')
	}

	// 检查是否已初始化
	isReady(): boolean {
		return this.isInitialized
	}

	// 获取当前模型
	getCurrentModel(): string | null {
		return this.currentModel
	}
}

// 导出单例实例
export const live2dService = Live2DService.getInstance()

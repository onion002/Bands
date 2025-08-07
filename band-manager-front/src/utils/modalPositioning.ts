/**
 * 弹窗定位工具类
 * 提供智能的弹窗定位策略，支持响应式布局和多种定位模式
 */

export interface ModalPosition {
  top?: string
  left?: string
  right?: string
  bottom?: string
  transform?: string
  maxWidth?: string
  maxHeight?: string
  width?: string
  height?: string
}

export interface ModalPositionOptions {
  // 定位策略
  strategy?: 'center' | 'top' | 'bottom' | 'smart' | 'custom'
  // 偏移量
  offset?: {
    top?: number
    left?: number
    right?: number
    bottom?: number
  }
  // 最大尺寸
  maxWidth?: number | string
  maxHeight?: number | string
  // 最小尺寸
  minWidth?: number | string
  minHeight?: number | string
  // 是否考虑导航栏高度
  considerNavbar?: boolean
  // 自定义边距
  margin?: number | string
  // 是否启用智能避让
  smartAvoidance?: boolean
}

export class ModalPositioning {
  private static instance: ModalPositioning
  private navbarHeight = 80 // 导航栏高度
  private defaultMargin = 20 // 默认边距

  static getInstance(): ModalPositioning {
    if (!ModalPositioning.instance) {
      ModalPositioning.instance = new ModalPositioning()
    }
    return ModalPositioning.instance
  }

  /**
   * 获取视口信息
   */
  private getViewportInfo() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      scrollY: window.scrollY,
      isMobile: window.innerWidth <= 768,
      isTablet: window.innerWidth <= 1024 && window.innerWidth > 768
    }
  }

  /**
   * 计算智能定位
   */
  private calculateSmartPosition(
    contentHeight: number,
    contentWidth: number,
    options: ModalPositionOptions
  ): ModalPosition {
    const viewport = this.getViewportInfo()
    const availableHeight = viewport.height - (options.considerNavbar ? this.navbarHeight : 0)
    const margin = typeof options.margin === 'number' ? options.margin : this.defaultMargin

    // 如果内容高度超过可用高度的80%，使用顶部对齐
    if (contentHeight > availableHeight * 0.8) {
      return this.calculateTopPosition(options)
    }

    // 如果是移动设备，优先使用底部弹出
    if (viewport.isMobile && contentHeight > availableHeight * 0.6) {
      return this.calculateBottomPosition(options)
    }

    // 默认居中
    return this.calculateCenterPosition(options)
  }

  /**
   * 计算居中定位
   */
  private calculateCenterPosition(options: ModalPositionOptions): ModalPosition {
    const viewport = this.getViewportInfo()
    const margin = typeof options.margin === 'number' ? options.margin : this.defaultMargin

    return {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      maxWidth: options.maxWidth || (viewport.isMobile ? '95vw' : '90vw'),
      maxHeight: options.maxHeight || '90vh',
      width: viewport.isMobile ? '95%' : 'auto'
    }
  }

  /**
   * 计算顶部定位
   */
  private calculateTopPosition(options: ModalPositionOptions): ModalPosition {
    const viewport = this.getViewportInfo()
    const topOffset = (options.considerNavbar ? this.navbarHeight : 0) + 
                     (options.offset?.top || this.defaultMargin)

    return {
      top: `${topOffset}px`,
      left: '50%',
      transform: 'translateX(-50%)',
      maxWidth: options.maxWidth || (viewport.isMobile ? '95vw' : '90vw'),
      maxHeight: options.maxHeight || `calc(100vh - ${topOffset + this.defaultMargin}px)`,
      width: viewport.isMobile ? '95%' : 'auto'
    }
  }

  /**
   * 计算底部定位
   */
  private calculateBottomPosition(options: ModalPositionOptions): ModalPosition {
    const viewport = this.getViewportInfo()
    const bottomOffset = options.offset?.bottom || this.defaultMargin

    return {
      bottom: `${bottomOffset}px`,
      left: '50%',
      transform: 'translateX(-50%)',
      maxWidth: options.maxWidth || (viewport.isMobile ? '95vw' : '90vw'),
      maxHeight: options.maxHeight || `calc(100vh - ${bottomOffset + this.defaultMargin}px)`,
      width: viewport.isMobile ? '95%' : 'auto'
    }
  }

  /**
   * 获取弹窗定位样式
   */
  public getModalPosition(options: ModalPositionOptions = {}): ModalPosition {
    const strategy = options.strategy || 'smart'
    
    switch (strategy) {
      case 'center':
        return this.calculateCenterPosition(options)
      case 'top':
        return this.calculateTopPosition(options)
      case 'bottom':
        return this.calculateBottomPosition(options)
      case 'smart':
        // 智能定位需要内容尺寸，这里先返回居中定位
        return this.calculateCenterPosition(options)
      default:
        return this.calculateCenterPosition(options)
    }
  }

  /**
   * 获取响应式弹窗样式
   */
  public getResponsiveModalStyles(options: ModalPositionOptions = {}): Record<string, any> {
    const viewport = this.getViewportInfo()
    const position = this.getModalPosition(options)

    const baseStyles = {
      position: 'fixed',
      zIndex: 1000,
      ...position
    }

    // 移动端特殊处理
    if (viewport.isMobile) {
      return {
        ...baseStyles,
        width: '95%',
        maxWidth: '95vw',
        margin: '10px',
        borderRadius: '16px'
      }
    }

    // 平板端处理
    if (viewport.isTablet) {
      return {
        ...baseStyles,
        width: '85%',
        maxWidth: '85vw',
        margin: '20px',
        borderRadius: '20px'
      }
    }

    // 桌面端处理
    return {
      ...baseStyles,
      borderRadius: '24px'
    }
  }

  /**
   * 获取弹窗遮罩样式
   */
  public getOverlayStyles(): Record<string, any> {
    const viewport = this.getViewportInfo()

    return {
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: viewport.isMobile ? 'flex-end' : 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: viewport.isMobile ? '0' : '20px'
    }
  }
}

// 导出单例实例
export const modalPositioning = ModalPositioning.getInstance()

// 导出便捷函数
export function useModalPosition(options?: ModalPositionOptions) {
  return modalPositioning.getModalPosition(options)
}

export function useResponsiveModal(options?: ModalPositionOptions) {
  return modalPositioning.getResponsiveModalStyles(options)
}

/**
 * Vue组合式函数：智能弹窗定位
 */
export function useSmartModal(options: ModalPositionOptions = {}) {
  const { ref, computed, onMounted, onUnmounted } = require('vue')

  const modalRef = ref<HTMLElement>()
  const isVisible = ref(false)
  const position = ref<ModalPosition>({})

  // 计算弹窗样式
  const modalStyles = computed(() => {
    return modalPositioning.getResponsiveModalStyles(options)
  })

  // 计算遮罩样式
  const overlayStyles = computed(() => {
    return modalPositioning.getOverlayStyles()
  })

  // 更新定位
  const updatePosition = () => {
    if (modalRef.value && isVisible.value) {
      const rect = modalRef.value.getBoundingClientRect()
      const smartPosition = modalPositioning.getInstance().getModalPosition({
        ...options,
        strategy: 'smart'
      })
      position.value = smartPosition
    }
  }

  // 显示弹窗
  const show = () => {
    isVisible.value = true
    // 下一帧更新位置，确保DOM已渲染
    requestAnimationFrame(updatePosition)
  }

  // 隐藏弹窗
  const hide = () => {
    isVisible.value = false
  }

  // 监听窗口大小变化
  let resizeObserver: ResizeObserver | null = null

  onMounted(() => {
    // 监听窗口大小变化
    window.addEventListener('resize', updatePosition)

    // 监听弹窗内容变化
    if (modalRef.value && 'ResizeObserver' in window) {
      resizeObserver = new ResizeObserver(updatePosition)
      resizeObserver.observe(modalRef.value)
    }
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updatePosition)
    if (resizeObserver) {
      resizeObserver.disconnect()
    }
  })

  return {
    modalRef,
    isVisible,
    position,
    modalStyles,
    overlayStyles,
    show,
    hide,
    updatePosition
  }
}

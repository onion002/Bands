/**
 * Vue组合式函数：智能弹窗管理
 * 提供统一的弹窗定位、动画和响应式支持
 */

import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { modalPositioning, type ModalPositionOptions } from '@/utils/modalPositioning'

export interface UseModalOptions extends ModalPositionOptions {
  // 弹窗类型
  type?: 'form' | 'info' | 'upload' | 'confirm'
  // 是否自动聚焦
  autoFocus?: boolean
  // 是否点击遮罩关闭
  closeOnOverlay?: boolean
  // 是否按ESC关闭
  closeOnEscape?: boolean
  // 弹窗层级
  zIndex?: number
}

export function useModal(options: UseModalOptions = {}) {
  const isVisible = ref(false)
  const modalRef = ref<HTMLElement>()
  const overlayRef = ref<HTMLElement>()
  
  // 默认配置
  const config = {
    strategy: 'smart',
    considerNavbar: true,
    autoFocus: true,
    closeOnOverlay: true,
    closeOnEscape: true,
    zIndex: 1000,
    ...options
  }

  // 计算弹窗样式类
  const modalClasses = computed(() => {
    const classes = ['modal']
    
    // 添加智能定位类
    if (config.strategy === 'smart') {
      classes.push('modal-smart-position', 'smart-center')
    } else if (config.strategy === 'top') {
      classes.push('modal-smart-position', 'smart-top')
    } else if (config.strategy === 'bottom') {
      classes.push('modal-smart-position', 'smart-bottom')
    }
    
    // 添加自适应高度类
    classes.push('modal-adaptive-height')
    
    return classes
  })

  // 计算遮罩样式类
  const overlayClasses = computed(() => {
    const classes = ['modal-overlay']
    
    // 添加层级类
    if (config.zIndex === 1010) classes.push('modal-level-2')
    else if (config.zIndex === 1020) classes.push('modal-level-3')
    else classes.push('modal-level-1')
    
    return classes
  })

  // 计算弹窗样式
  const modalStyles = computed(() => {
    return modalPositioning.getResponsiveModalStyles({
      strategy: config.strategy,
      considerNavbar: config.considerNavbar,
      maxWidth: config.maxWidth,
      maxHeight: config.maxHeight
    })
  })

  // 显示弹窗
  const show = async () => {
    isVisible.value = true
    
    // 等待DOM更新
    await nextTick()
    
    // 自动聚焦
    if (config.autoFocus && modalRef.value) {
      const focusableElement = modalRef.value.querySelector(
        'input, textarea, select, button, [tabindex]:not([tabindex="-1"])'
      ) as HTMLElement
      
      if (focusableElement) {
        focusableElement.focus()
      }
    }
    
    // 禁用页面滚动
    document.body.style.overflow = 'hidden'
  }

  // 隐藏弹窗
  const hide = () => {
    isVisible.value = false
    
    // 恢复页面滚动
    document.body.style.overflow = ''
  }

  // 切换弹窗显示状态
  const toggle = () => {
    if (isVisible.value) {
      hide()
    } else {
      show()
    }
  }

  // 处理遮罩点击
  const handleOverlayClick = (event: MouseEvent) => {
    if (config.closeOnOverlay && event.target === overlayRef.value) {
      hide()
    }
  }

  // 处理键盘事件
  const handleKeydown = (event: KeyboardEvent) => {
    if (config.closeOnEscape && event.key === 'Escape' && isVisible.value) {
      hide()
    }
  }

  // 智能定位更新
  const updatePosition = () => {
    if (!modalRef.value || !isVisible.value) return
    
    const rect = modalRef.value.getBoundingClientRect()
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight
    }
    
    // 检查是否需要调整定位策略
    if (rect.height > viewport.height * 0.8) {
      // 内容太高，使用顶部对齐
      modalRef.value.classList.remove('smart-center')
      modalRef.value.classList.add('smart-top')
    } else if (viewport.width <= 768 && rect.height > viewport.height * 0.6) {
      // 移动端内容较高，使用底部弹出
      modalRef.value.classList.remove('smart-center')
      modalRef.value.classList.add('smart-bottom')
    }
  }

  // 生命周期管理
  onMounted(() => {
    // 监听键盘事件
    document.addEventListener('keydown', handleKeydown)
    
    // 监听窗口大小变化
    window.addEventListener('resize', updatePosition)
  })

  onUnmounted(() => {
    // 清理事件监听
    document.removeEventListener('keydown', handleKeydown)
    window.removeEventListener('resize', updatePosition)
    
    // 恢复页面滚动
    document.body.style.overflow = ''
  })

  return {
    // 状态
    isVisible,
    modalRef,
    overlayRef,
    
    // 计算属性
    modalClasses,
    overlayClasses,
    modalStyles,
    
    // 方法
    show,
    hide,
    toggle,
    updatePosition,
    handleOverlayClick,
    
    // 配置
    config
  }
}

/**
 * 预设的弹窗配置
 */
export const modalPresets = {
  // 表单弹窗
  form: {
    strategy: 'smart' as const,
    considerNavbar: true,
    maxWidth: '650px',
    autoFocus: true
  },
  
  // 信息展示弹窗
  info: {
    strategy: 'center' as const,
    maxWidth: '500px',
    closeOnOverlay: true
  },
  
  // 上传弹窗
  upload: {
    strategy: 'center' as const,
    maxWidth: '550px',
    closeOnEscape: false
  },
  
  // 确认对话框
  confirm: {
    strategy: 'center' as const,
    maxWidth: '400px',
    closeOnOverlay: false,
    closeOnEscape: false
  }
}

/**
 * 便捷函数：创建特定类型的弹窗
 */
export function useFormModal(options?: UseModalOptions) {
  return useModal({ ...modalPresets.form, ...options })
}

export function useInfoModal(options?: UseModalOptions) {
  return useModal({ ...modalPresets.info, ...options })
}

export function useUploadModal(options?: UseModalOptions) {
  return useModal({ ...modalPresets.upload, ...options })
}

export function useConfirmModal(options?: UseModalOptions) {
  return useModal({ ...modalPresets.confirm, ...options })
}

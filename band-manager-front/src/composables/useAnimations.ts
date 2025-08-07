// 🎨 Vue 动画组合式函数
// 提供响应式的动画控制和优化

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { animationConfig, animationMonitor, animationUtils } from '@/utils/animationUtils'

/**
 * 基础动画控制
 */
export function useAnimation() {
  const isAnimating = ref(false)
  const animationInstance = ref<Animation | null>(null)

  const animate = async (
    element: HTMLElement,
    keyframes: Keyframe[],
    options: KeyframeAnimationOptions
  ): Promise<void> => {
    if (isAnimating.value) return

    isAnimating.value = true
    
    try {
      animationInstance.value = animationUtils.createOptimizedAnimation(
        element,
        keyframes,
        options
      )
      
      await animationInstance.value.finished
    } catch (error) {
      console.error('动画执行失败:', error)
    } finally {
      isAnimating.value = false
      animationInstance.value = null
    }
  }

  const stop = () => {
    if (animationInstance.value) {
      animationInstance.value.cancel()
      animationInstance.value = null
      isAnimating.value = false
    }
  }

  return {
    isAnimating,
    animate,
    stop
  }
}

/**
 * 进入动画
 */
export function useEnterAnimation(delay = 0) {
  const isVisible = ref(false)
  const elementRef = ref<HTMLElement>()

  const enter = async () => {
    if (!elementRef.value || isVisible.value) return

    await nextTick()
    
    const keyframes: Keyframe[] = [
      { opacity: 0, transform: 'translateY(30px) scale(0.95)' },
      { opacity: 1, transform: 'translateY(0) scale(1)' }
    ]

    const options: KeyframeAnimationOptions = {
      duration: animationConfig.getDuration(600),
      delay: animationConfig.getDelay(delay),
      easing: animationConfig.getEasing(),
      fill: 'forwards'
    }

    try {
      const animation = animationUtils.createOptimizedAnimation(
        elementRef.value,
        keyframes,
        options
      )
      
      await animation.finished
      isVisible.value = true
    } catch (error) {
      console.error('进入动画失败:', error)
      isVisible.value = true
    }
  }

  return {
    elementRef,
    isVisible,
    enter
  }
}

/**
 * 交错动画
 */
export function useStaggerAnimation() {
  const elementsRef = ref<HTMLElement[]>([])
  const isAnimating = ref(false)

  const staggerIn = async (staggerDelay = 100) => {
    if (isAnimating.value || elementsRef.value.length === 0) return

    isAnimating.value = true

    const keyframes: Keyframe[] = [
      { opacity: 0, transform: 'translateY(20px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ]

    const baseOptions: KeyframeAnimationOptions = {
      duration: animationConfig.getDuration(400),
      easing: animationConfig.getEasing(),
      fill: 'forwards'
    }

    try {
      const animations = animationUtils.createStaggeredAnimation(
        elementsRef.value,
        keyframes,
        baseOptions,
        staggerDelay
      )

      await Promise.all(animations.map(anim => anim.finished))
    } catch (error) {
      console.error('交错动画失败:', error)
    } finally {
      isAnimating.value = false
    }
  }

  return {
    elementsRef,
    isAnimating,
    staggerIn
  }
}

/**
 * 悬停动画
 */
export function useHoverAnimation() {
  const elementRef = ref<HTMLElement>()
  const isHovered = ref(false)

  const setupHoverAnimation = () => {
    if (!elementRef.value) return

    const element = elementRef.value

    const handleMouseEnter = () => {
      if (isHovered.value) return
      isHovered.value = true

      const keyframes: Keyframe[] = [
        { transform: 'translateY(0) scale(1)' },
        { transform: 'translateY(-4px) scale(1.02)' }
      ]

      const options: KeyframeAnimationOptions = {
        duration: animationConfig.getDuration(200),
        easing: animationConfig.getEasing(),
        fill: 'forwards'
      }

      animationUtils.createOptimizedAnimation(element, keyframes, options)
    }

    const handleMouseLeave = () => {
      if (!isHovered.value) return
      isHovered.value = false

      const keyframes: Keyframe[] = [
        { transform: 'translateY(-4px) scale(1.02)' },
        { transform: 'translateY(0) scale(1)' }
      ]

      const options: KeyframeAnimationOptions = {
        duration: animationConfig.getDuration(200),
        easing: animationConfig.getEasing(),
        fill: 'forwards'
      }

      animationUtils.createOptimizedAnimation(element, keyframes, options)
    }

    element.addEventListener('mouseenter', handleMouseEnter)
    element.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter)
      element.removeEventListener('mouseleave', handleMouseLeave)
    }
  }

  onMounted(() => {
    nextTick(setupHoverAnimation)
  })

  return {
    elementRef,
    isHovered
  }
}

/**
 * 音乐可视化动画
 */
export function useMusicAnimation() {
  const barsRef = ref<HTMLElement[]>([])
  const isPlaying = ref(false)
  const animations = ref<Animation[]>([])

  const startVisualization = () => {
    if (isPlaying.value || barsRef.value.length === 0) return

    isPlaying.value = true
    animations.value = []

    barsRef.value.forEach((bar, index) => {
      const keyframes: Keyframe[] = [
        { transform: 'scaleY(0.3)' },
        { transform: 'scaleY(1)' },
        { transform: 'scaleY(0.3)' }
      ]

      const options: KeyframeAnimationOptions = {
        duration: animationConfig.getDuration(1000 + (index * 100)),
        delay: animationConfig.getDelay(index * 100),
        easing: 'ease-in-out',
        iterations: Infinity
      }

      const animation = animationUtils.createOptimizedAnimation(bar, keyframes, options)
      animations.value.push(animation)
    })
  }

  const stopVisualization = () => {
    if (!isPlaying.value) return

    animations.value.forEach(animation => animation.cancel())
    animations.value = []
    isPlaying.value = false
  }

  onUnmounted(() => {
    stopVisualization()
  })

  return {
    barsRef,
    isPlaying,
    startVisualization,
    stopVisualization
  }
}

/**
 * 性能监控
 */
export function useAnimationPerformance() {
  const fps = ref(60)
  const isMonitoring = ref(false)

  const startMonitoring = () => {
    if (isMonitoring.value) return

    isMonitoring.value = true
    animationMonitor.startMonitoring()

    const updateFPS = () => {
      if (!isMonitoring.value) return
      fps.value = animationMonitor.getCurrentFPS()
      requestAnimationFrame(updateFPS)
    }

    updateFPS()
  }

  const stopMonitoring = () => {
    if (!isMonitoring.value) return

    isMonitoring.value = false
    animationMonitor.stopMonitoring()
  }

  onMounted(() => {
    if (process.env.NODE_ENV === 'development') {
      startMonitoring()
    }
  })

  onUnmounted(() => {
    stopMonitoring()
  })

  return {
    fps,
    isMonitoring,
    startMonitoring,
    stopMonitoring
  }
}

/**
 * 响应式动画配置
 */
export function useAnimationConfig() {
  const config = animationConfig
  const prefersReducedMotion = ref(false)
  const devicePerformance = ref<'high' | 'medium' | 'low'>('medium')

  onMounted(() => {
    // 初始化配置
    prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    
    // 监听偏好设置变化
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const handleChange = (e: MediaQueryListEvent) => {
      prefersReducedMotion.value = e.matches
    }
    
    mediaQuery.addEventListener('change', handleChange)
    
    onUnmounted(() => {
      mediaQuery.removeEventListener('change', handleChange)
    })
  })

  return {
    config,
    prefersReducedMotion,
    devicePerformance,
    getDuration: (duration: number) => config.getDuration(duration),
    getDelay: (delay: number) => config.getDelay(delay),
    shouldUseComplexAnimations: () => config.shouldUseComplexAnimations(),
    shouldUseParticleEffects: () => config.shouldUseParticleEffects()
  }
}

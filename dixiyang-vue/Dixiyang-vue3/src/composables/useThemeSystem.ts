import { ref, watch, onMounted, onUpdated } from 'vue'
import { useBackgroundConfig } from './useBackgroundConfig'
import { useFontConfig } from './useFontConfig'
import {
  sampleImageBrightness,
  getContrastColor,
  getColorThemeVariables,
  extractBrightness,
} from '@/utils/colorUtils'

export function useThemeSystem() {
  const bgConfig = useBackgroundConfig()
  const fontConfig = useFontConfig()

  // 当前文字颜色模式 (light 白色 / dark 黑色)
  const textColorMode = ref<'light' | 'dark'>('dark')
  // 当前采样的背景亮度
  const sampledBrightness = ref<number | null>(null)
  // 自动调整文字颜色开关
  const autoAdjustTextColor = ref<boolean>(true)

  /**
   * 强制更新CSS变量（解决优先级问题）
   */
  const forceUpdateCSSVariables = (mode: 'light' | 'dark') => {
    const colorVars = getColorThemeVariables(mode)
    const root = document.documentElement

    // 使用!important确保优先级
    Object.entries(colorVars).forEach(([varName, colorValue]) => {
      root.style.setProperty(varName, colorValue, 'important')
    })
  }

  /**
   * 根据亮度更新文字颜色
   */
  const updateTextColorByBrightness = async (brightness: number) => {
    if (!autoAdjustTextColor.value) return

    sampledBrightness.value = brightness
    const newMode = getContrastColor(brightness, 0.5)
    textColorMode.value = newMode

    // 强制更新CSS变量
    forceUpdateCSSVariables(newMode)

    // 持久化存储
    localStorage.setItem('dixiyang_text_color_mode', newMode)
    localStorage.setItem('dixiyang_auto_adjust_text_color', String(autoAdjustTextColor.value))

    updateThemeClass()
  }

  /**
   * 采样自定义图片背景的亮度
   */
  const sampleCustomImageBrightness = async (imageUrl: string) => {
    try {
      const brightness = await sampleImageBrightness(imageUrl)
      await updateTextColorByBrightness(brightness)
    } catch (error) {
      console.error('Failed to sample image brightness:', error)
      textColorMode.value = 'dark'
      forceUpdateCSSVariables('dark')
      localStorage.setItem('dixiyang_text_color_mode', 'dark')
      updateThemeClass()
    }
  }

  /**
   * 采样渐变背景的亮度（修复：从bgConfig获取实际的渐变字符串）
   */
  const sampleGradientBrightness = () => {
    try {
      // 从背景元素获取实际的渐变样式（备用方案）
      const bgElement = document.querySelector('.bg-gradient-animation')
      if (!bgElement) return 0.3

      const bgStyle = getComputedStyle(bgElement).backgroundImage
      const colorMatch = bgStyle.match(/#[0-9a-fA-F]{6}|rgba?\([^)]+\)/)

      if (colorMatch) {
        const brightness = extractBrightness(colorMatch[0])
        sampledBrightness.value = brightness
        updateTextColorByBrightness(brightness)
        return brightness
      }
    } catch (e) {
      console.error('Failed to sample gradient brightness:', e)
    }
    return 0.3
  }

  /**
   * 启用/禁用自动调整文字颜色
   */
  const setAutoAdjustTextColor = (enabled: boolean) => {
    autoAdjustTextColor.value = enabled
    localStorage.setItem('dixiyang_auto_adjust_text_color', String(enabled))

    if (enabled && sampledBrightness.value !== null) {
      updateTextColorByBrightness(sampledBrightness.value)
    } else {
      // 禁用时确保当前模式生效
      forceUpdateCSSVariables(textColorMode.value)
      localStorage.setItem('dixiyang_text_color_mode', textColorMode.value)
      updateThemeClass()
    }
  }

  /**
   * 手动设置文字颜色模式（修复：立即生效并持久化）
   */
  const setTextColorMode = (mode: 'light' | 'dark') => {
    textColorMode.value = mode
    forceUpdateCSSVariables(mode)
    localStorage.setItem('dixiyang_text_color_mode', mode)
    updateThemeClass()

    // 禁用自动调整（手动设置后）
    if (autoAdjustTextColor.value) {
      autoAdjustTextColor.value = false
      localStorage.setItem('dixiyang_auto_adjust_text_color', 'false')
    }
  }

  /**
   * 应用整个主题系统
   */
  const applyThemeSystem = () => {
    bgConfig.applyBackgroundPreset()
    bgConfig.applyColorTheme()
    fontConfig.applyFontSettings()

    // 根据当前背景类型处理
    if (bgConfig.preset.value === 'custom' && bgConfig.customImageUrl.value) {
      sampleCustomImageBrightness(bgConfig.customImageUrl.value)
    } else if (autoAdjustTextColor.value) {
      sampleGradientBrightness()
    }

    updateThemeClass()
  }

  /**
   * 更新html标签的主题class
   */
  const updateThemeClass = () => {
    const html = document.documentElement
    html.classList.remove('theme-preset-light', 'theme-preset-dark', 'theme-preset-auto')

    if (autoAdjustTextColor.value && sampledBrightness.value !== null) {
      html.classList.add('theme-preset-auto')
    } else if (textColorMode.value === 'light') {
      html.classList.add('theme-preset-light')
    } else {
      html.classList.add('theme-preset-dark')
    }
  }

  /**
   * 从localStorage加载所有主题设置（修复：立即应用）
   */
  const loadThemeFromStorage = () => {
    try {
      // 加载自动调整开关（优先）
      const savedAutoAdjust = localStorage.getItem('dixiyang_auto_adjust_text_color')
      if (savedAutoAdjust !== null) {
        autoAdjustTextColor.value = savedAutoAdjust === 'true'
      }

      // 加载文字颜色模式
      const savedTextMode = localStorage.getItem('dixiyang_text_color_mode') as 'light' | 'dark' | null
      if (savedTextMode) {
        textColorMode.value = savedTextMode
        // 立即应用，不等待其他逻辑
        forceUpdateCSSVariables(savedTextMode)
      }
    } catch (error) {
      console.error('Failed to load theme from storage:', error)
    }
  }

  /**
   * 初始化主题系统（改为立即执行，不依赖onMounted）
   */
  const initThemeSystem = async () => {
    // 先加载存储的设置
    loadThemeFromStorage()
    // 再应用主题
    applyThemeSystem()
    updateThemeClass()
  }

  /**
   * 重置所有主题设置为默认
   */
  const resetThemeToDefault = () => {
    bgConfig.resetToDefault()
    fontConfig.resetToDefault()
    textColorMode.value = 'dark'
    autoAdjustTextColor.value = true
    sampledBrightness.value = null

    // 重置CSS变量
    forceUpdateCSSVariables('dark')

    // 清除存储
    localStorage.removeItem('dixiyang_text_color_mode')
    localStorage.removeItem('dixiyang_auto_adjust_text_color')

    updateThemeClass()
  }

  /**
   * 监听背景变化并更新文字颜色
   */
  const watchBackgroundChanges = () => {
    // 监听背景预设、自定义图片、主题色变化
    watch(
      [() => bgConfig.preset.value, () => bgConfig.customImageUrl.value, () => bgConfig.colorTheme.value],
      () => {
        if (autoAdjustTextColor.value) {
          if (bgConfig.preset.value === 'custom' && bgConfig.customImageUrl.value) {
            sampleCustomImageBrightness(bgConfig.customImageUrl.value)
          } else {
            sampleGradientBrightness()
          }
        }
      },
      { immediate: true, deep: true }
    )

    // 监听自动调整开关变化
    watch(autoAdjustTextColor, (newVal) => {
      if (newVal && sampledBrightness.value !== null) {
        updateTextColorByBrightness(sampledBrightness.value)
      }
    })

    // 监听文字颜色模式变化（确保响应式）
    watch(textColorMode, () => {
      updateThemeClass()
    })
  }

  // 立即初始化（关键：不等待onMounted）
  initThemeSystem()

  // 组件挂载时启动监听
  onMounted(() => {
    watchBackgroundChanges()
  })

  return {
    // 暴露响应式状态（确保模板能响应）
    textColorMode,
    sampledBrightness,
    autoAdjustTextColor,

    // 方法
    updateTextColorByBrightness,
    sampleCustomImageBrightness,
    setAutoAdjustTextColor,
    setTextColorMode,
    applyThemeSystem,
    resetThemeToDefault,
    initThemeSystem,
  }
}

import { ref, onMounted } from 'vue'
import { sampleImageBrightness, getContrastColor, getColorThemeVariables, extractBrightness } from '@/utils/colorUtils'

/**
 * 文字颜色自适应 Composable
 * 根据背景颜色动态调整文字颜色以保证可读性
 */

export function useTextColorAdapter() {
  // 响应式状态
  const textMode = ref<'light' | 'dark'>('light')
  const backgroundBrightness = ref<number>(0.5)

  /**
   * 根据背景亮度更新文字颜色模式和CSS变量
   */
  const updateTextColorMode = (brightness: number) => {
    backgroundBrightness.value = brightness
    textMode.value = getContrastColor(brightness, 0.5)

    const colorVars = getColorThemeVariables(textMode.value)
    const root = document.documentElement

    // 应用CSS变量
    Object.entries(colorVars).forEach(([varName, colorValue]) => {
      root.style.setProperty(varName, colorValue)
    })

    // 应用特定的description样式
    applyDescriptionStyles(textMode.value)
  }

  /**
   * 应用description元素的动态样式
   */
  const applyDescriptionStyles = (mode: 'light' | 'dark') => {
    const root = document.documentElement
    if (mode === 'light') {
      // 浅色文本适合深色背景
      root.style.setProperty('--description-color', '#ffffff')
      root.style.setProperty('--description-secondary', 'rgba(255, 255, 255, 0.8)')
    } else {
      // 深色文本适合浅色背景
      root.style.setProperty('--description-color', '#1a1a1a')
      root.style.setProperty('--description-secondary', 'rgba(0, 0, 0, 0.8)')
    }
  }

  /**
   * 从自定义背景图片采样并更新文字颜色
   */
  const adaptToBackgroundImage = async (imageUrl: string) => {
    try {
      const brightness = await sampleImageBrightness(imageUrl)
      updateTextColorMode(brightness)
      return brightness
    } catch (error) {
      console.warn('Failed to sample background image brightness:', error)
      // fallback to light text
      updateTextColorMode(0.3)
    }
  }

  /**
   * 从单个RGB颜色值适应文字颜色
   */
  const adaptToColor = (rgb: string | number[]) => {
    const brightness = extractBrightness(rgb)
    updateTextColorMode(brightness)
  }

  /**
   * 从计算的样式属性获取背景颜色并适应
   */
  const adaptToComputedBackground = () => {
    try {
      const root = document.documentElement
      const bgColor = window.getComputedStyle(root).backgroundColor
      adaptToColor(bgColor)
    } catch (error) {
      console.warn('Failed to adapt to computed background:', error)
    }
  }

  /**
   * 初始化：监听背景变化
   */
  onMounted(() => {
    // 初始化默认为浅色文本（适合深色背景）
    updateTextColorMode(0.3)

    // 监听document颜色变化
    const observer = new MutationObserver(() => {
      adaptToComputedBackground()
    })

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['style'],
    })

    // cleanup
    return () => {
      observer.disconnect()
    }
  })

  return {
    textMode,
    backgroundBrightness,
    updateTextColorMode,
    adaptToBackgroundImage,
    adaptToColor,
    adaptToComputedBackground,
  }
}

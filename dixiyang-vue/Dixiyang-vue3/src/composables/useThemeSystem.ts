import { ref, watch } from 'vue'

/**
 * 文字颜色适配系统
 * 与主题 class 解耦：主题 class 定义默认颜色，此 composable 提供
 * 对文字颜色的精细控制（当用户关闭自动调整时可以手动选择）
 */

export function useThemeSystem() {
  const textColorMode = ref<'light' | 'dark'>('light')
  const sampledBrightness = ref<number | null>(null)
  const autoAdjustTextColor = ref<boolean>(true)

  /** 更新文字颜色 CSS 变量（仅当主题 class 不满足需求时使用） */
  const updateTextColorByBrightness = async (brightness: number) => {
    if (!autoAdjustTextColor.value) return
    sampledBrightness.value = brightness
    const newMode = brightness > 0.5 ? 'dark' : 'light'
    textColorMode.value = newMode
    localStorage.setItem('dixiyang_text_color_mode', newMode)
  }

  const setAutoAdjustTextColor = (enabled: boolean) => {
    autoAdjustTextColor.value = enabled
    localStorage.setItem('dixiyang_auto_adjust_text_color', String(enabled))
  }

  const setTextColorMode = (mode: 'light' | 'dark') => {
    textColorMode.value = mode
    localStorage.setItem('dixiyang_text_color_mode', mode)
    if (autoAdjustTextColor.value) {
      autoAdjustTextColor.value = false
      localStorage.setItem('dixiyang_auto_adjust_text_color', 'false')
    }
  }

  const loadFromStorage = () => {
    const savedAuto = localStorage.getItem('dixiyang_auto_adjust_text_color')
    if (savedAuto !== null) autoAdjustTextColor.value = savedAuto === 'true'
    const savedMode = localStorage.getItem('dixiyang_text_color_mode') as 'light' | 'dark' | null
    if (savedMode) textColorMode.value = savedMode
  }

  return {
    textColorMode, sampledBrightness, autoAdjustTextColor,
    updateTextColorByBrightness, setAutoAdjustTextColor,
    setTextColorMode, loadFromStorage,
  }
}

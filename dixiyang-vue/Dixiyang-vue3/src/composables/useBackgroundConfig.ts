import { ref, onMounted, watch } from 'vue'
import { sampleImageBrightness, getContrastColor, getColorThemeVariables } from '@/utils/colorUtils'
import http from '@/utils/http'

/**
 * 背景配置 Composable
 * 管理全局背景设置的状态和逻辑
 * 支持 localStorage 持久化、自定义图片，以及后端数据库同步
 */

export type BackgroundPreset = 'dynamic' | 'static' | 'gradient' | 'grid' | 'minimal' | 'custom'
export type ColorTheme = 'purple' | 'blue' | 'cyan'

interface BackgroundConfig {
  preset: BackgroundPreset
  animEnabled: boolean
  intensity: number // 0-100
  colorTheme: ColorTheme
  customImageUrl?: string // 自定义图片 URL
}

const STORAGE_KEY = 'dixiyang_bg_config'
const CUSTOM_IMAGE_KEY = 'dixiyang_bg_custom_image'

/**
 * 默认背景配置
 */
const DEFAULT_CONFIG: BackgroundConfig = {
  preset: 'dynamic',
  animEnabled: true,
  intensity: 100,
  colorTheme: 'blue',
}

export function useBackgroundConfig() {
  // 响应式状态
  const preset = ref<BackgroundPreset>(DEFAULT_CONFIG.preset)
  const animEnabled = ref<boolean>(DEFAULT_CONFIG.animEnabled)
  const intensity = ref<number>(DEFAULT_CONFIG.intensity)
  const colorTheme = ref<ColorTheme>(DEFAULT_CONFIG.colorTheme)
  const customImageUrl = ref<string | undefined>(undefined)

  /**
   * 从 localStorage 读取配置
   */
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const config = JSON.parse(stored) as Partial<BackgroundConfig>
        preset.value = config.preset || DEFAULT_CONFIG.preset
        animEnabled.value = config.animEnabled !== undefined ? config.animEnabled : DEFAULT_CONFIG.animEnabled
        intensity.value = config.intensity !== undefined ? config.intensity : DEFAULT_CONFIG.intensity
        colorTheme.value = config.colorTheme || DEFAULT_CONFIG.colorTheme
      }

      // 加载自定义图片 URL
      const customImage = localStorage.getItem(CUSTOM_IMAGE_KEY)
      if (customImage) {
        customImageUrl.value = customImage
      }
    } catch (error) {
      console.error('Failed to load background config from storage:', error)
    }
  }

  /**
   * 保存配置到 localStorage
   */
  const saveToStorage = () => {
    try {
      const config: BackgroundConfig = {
        preset: preset.value,
        animEnabled: animEnabled.value,
        intensity: intensity.value,
        colorTheme: colorTheme.value,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
    } catch (error) {
      console.error('Failed to save background config to storage:', error)
    }
  }

  /**
   * 保存自定义图片 URL
   * 同时触发色彩采样和文字颜色自动调整
   */
  const saveCustomImage = async (imageUrl: string) => {
    try {
      localStorage.setItem(CUSTOM_IMAGE_KEY, imageUrl)
      customImageUrl.value = imageUrl

      // 异步采样图片亮度，自动调整文字颜色
      try {
        const brightness = await sampleImageBrightness(imageUrl)
        const textMode = getContrastColor(brightness, 0.5)
        const colorVars = getColorThemeVariables(textMode)
        const root = document.documentElement

        // 应用文字颜色
        Object.entries(colorVars).forEach(([varName, colorValue]) => {
          root.style.setProperty(varName, colorValue)
        })

        // 记录采样结果
        localStorage.setItem('dixiyang_bg_brightness', String(brightness))
      } catch (error) {
        console.warn('Failed to sample image brightness:', error)
        // 采样失败时使用浅色文本作为fallback
        const root = document.documentElement
        root.style.setProperty('--text-primary', '#ffffff')
        root.style.setProperty('--text-secondary', 'rgba(255, 255, 255, 0.7)')
      }
    } catch (error) {
      console.error('Failed to save custom background image:', error)
    }
  }

  /**
   * 设置背景预设
   */
  const setPreset = (newPreset: BackgroundPreset) => {
    preset.value = newPreset
  }

  /**
   * 切换动画启用/禁用
   */
  const toggleAnimation = () => {
    animEnabled.value = !animEnabled.value
  }

  /**
   * 设置动画启用状态
   */
  const setAnimEnabled = (enabled: boolean) => {
    animEnabled.value = enabled
  }

  /**
   * 设置背景强度 (0-100)
   */
  const setIntensity = (newIntensity: number) => {
    intensity.value = Math.max(0, Math.min(100, newIntensity))
  }

  /**
   * 设置颜色主题
   */
  const setColorTheme = (newTheme: ColorTheme) => {
    colorTheme.value = newTheme
  }

  /**
   * 重置为默认配置
   */
  const resetToDefault = () => {
    preset.value = DEFAULT_CONFIG.preset
    animEnabled.value = DEFAULT_CONFIG.animEnabled
    intensity.value = DEFAULT_CONFIG.intensity
    colorTheme.value = DEFAULT_CONFIG.colorTheme
    customImageUrl.value = undefined
    localStorage.removeItem(CUSTOM_IMAGE_KEY)
  }

  /**
   * 从后端加载用户的背景配置
   * 使用场景：用户登录后自动拉取配置
   */
  const loadFromBackend = async (): Promise<boolean> => {
    try {
      const res = await http.get('/user/bg-config')
      if (res.code === 200 && res.data) {
        // 后端返回了配置
        const config = res.data
        preset.value = (config.preset as BackgroundPreset) || DEFAULT_CONFIG.preset
        animEnabled.value = config.animEnabled !== undefined ? config.animEnabled : DEFAULT_CONFIG.animEnabled
        intensity.value = config.intensity !== undefined ? config.intensity : DEFAULT_CONFIG.intensity
        colorTheme.value = (config.colorTheme as ColorTheme) || DEFAULT_CONFIG.colorTheme
        customImageUrl.value = config.customImageUrl

        // 同时保存到本地 localStorage
        saveToStorage()

        console.log('✅ 成功从后端加载背景配置')
        return true
      } else {
        // 后端没有配置，使用本地存储
        console.log('ℹ️ 后端没有保存配置，使用本地配置')
        loadFromStorage()
        return false
      }
    } catch (error) {
      console.warn('⚠️ 从后端加载背景配置失败，使用本地配置:', error)
      loadFromStorage()
      return false
    }
  }

  /**
   * 保存配置到后端
   * 使用场景：用户修改配置时自动保存
   */
  const saveToBackend = async (): Promise<boolean> => {
    try {
      const config: BackgroundConfig = {
        preset: preset.value,
        animEnabled: animEnabled.value,
        intensity: intensity.value,
        colorTheme: colorTheme.value,
        customImageUrl: customImageUrl.value,
      }

      const res = await http.post('/user/bg-config', config)
      if (res.code === 200) {
        console.log('✅ 背景配置已保存到后端')
        return true
      } else {
        console.warn('⚠️ 保存背景配置到后端失败:', res.msg)
        return false
      }
    } catch (error) {
      console.warn('⚠️ 保存背景配置到后端异常:', error)
      return false
    }
  }

  /**
   * 获取当前配置对象
   */
  const getConfig = (): BackgroundConfig => ({
    preset: preset.value,
    animEnabled: animEnabled.value,
    intensity: intensity.value,
    colorTheme: colorTheme.value,
    customImageUrl: customImageUrl.value,
  })

  /**
   * 应用颜色主题到 CSS 变量
   */
  const applyColorTheme = () => {
    const root = document.documentElement
    const themeColors = {
      purple: {
        neon: '#a855f7',
        secondary: '#d8b4fe',
      },
      blue: {
        neon: '#3b82f6',
        secondary: '#93c5fd',
      },
      cyan: {
        neon: '#06b6d4',
        secondary: '#06d6d6',
      },
    }

    const colors = themeColors[colorTheme.value]
    root.style.setProperty('--neon-primary', colors.neon)
    root.style.setProperty('--neon-secondary', colors.secondary)
  }

  /**
   * 应用背景预设样式到 DOM
   */
  const applyBackgroundPreset = () => {
    const root = document.documentElement
    const bgContainer = document.querySelector('.bg-gradient-animation') as HTMLElement

    if (!bgContainer) return

    // 设置背景强度
    root.style.setProperty('--bg-intensity', `${intensity.value / 100}`)

    // 根据预设类型应用背景
    if (preset.value === 'custom' && customImageUrl.value) {
      // 自定义图片
      bgContainer.style.background = `url('${customImageUrl.value}') center/cover no-repeat fixed`
      bgContainer.style.animation = 'none'
    } else {
      // 预设背景
      const backgrounds: Record<BackgroundPreset, string> = {
        dynamic: `
          radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.12) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
          radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
          radial-gradient(circle at center, #1e1b4b 0%, #0a0a0c 70%)
        `,
        static: 'linear-gradient(135deg, #0a0a0c 0%, #1a1a2e 50%, #16213e 100%)',
        gradient: `
          linear-gradient(45deg, #0a0a0c 0%, #1a0f2e 25%, #0f1a2e 50%, #1a0f2e 75%, #0a0a0c 100%)
        `,
        grid: `
          linear-gradient(90deg, transparent 24%, rgba(59, 130, 246, 0.05) 25%, rgba(59, 130, 246, 0.05) 26%, transparent 27%, transparent 74%, rgba(59, 130, 246, 0.05) 75%, rgba(59, 130, 246, 0.05) 76%, transparent 77%, transparent),
          linear-gradient(0deg, transparent 24%, rgba(59, 130, 246, 0.05) 25%, rgba(59, 130, 246, 0.05) 26%, transparent 27%, transparent 74%, rgba(59, 130, 246, 0.05) 75%, rgba(59, 130, 246, 0.05) 76%, transparent 77%, transparent),
          #0a0a0c
        `,
        minimal: '#0a0a0c',
        custom: '#0a0a0c',
      }

      bgContainer.style.background = backgrounds[preset.value]

      // 设置动画
      if (preset.value === 'dynamic' && animEnabled.value) {
        bgContainer.style.animation = 'rotate 30s linear infinite'
        bgContainer.style.backgroundSize = 'auto'
      } else {
        bgContainer.style.animation = animEnabled.value ? 'rotate 30s linear infinite' : 'none'
      }
    }

    // 应用暂停状态
    if (!animEnabled.value) {
      bgContainer.classList.add('paused')
    } else {
      bgContainer.classList.remove('paused')
    }
  }

  /**
   * 监听状态变化，自动保存到 localStorage 并应用样式
   * 同时异步保存到后端（不阻塞UI）
   */
  watch(
    () => [preset.value, animEnabled.value, intensity.value, colorTheme.value],
    () => {
      saveToStorage()
      applyColorTheme()
      applyBackgroundPreset()

      // 异步保存到后端（不主动 await，避免阻塞UI）
      // 用户可能没登录，此时会失败但不影响使用
      saveToBackend().catch(() => {
        // 静默失败，本地配置已保存
      })
    }
  )

  /**
   * 初始化：从 localStorage 加载配置
   */
  onMounted(() => {
    loadFromStorage()
    applyColorTheme()
    applyBackgroundPreset()
  })

  return {
    // 状态
    preset,
    animEnabled,
    intensity,
    colorTheme,
    customImageUrl,

    // 本地存储方法
    setPreset,
    toggleAnimation,
    setAnimEnabled,
    setIntensity,
    setColorTheme,
    resetToDefault,
    getConfig,
    loadFromStorage,
    saveToStorage,
    saveCustomImage,
    applyColorTheme,
    applyBackgroundPreset,

    // 后端同步方法
    loadFromBackend,
    saveToBackend,
  }
}

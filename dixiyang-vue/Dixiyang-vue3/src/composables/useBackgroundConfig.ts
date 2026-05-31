import { ref, onMounted, watch } from 'vue'

/**
 * 背景配置 Composable
 * 管理全局背景设置：预设主题 + 预设背景图
 * 背景图存放在 public/images/back/ 目录，通过 nginx 静态服务访问
 */

export type BackgroundPreset = 'dynamic' | 'static' | 'minimal'
export type ColorTheme = 'purple' | 'blue' | 'cyan'

/**
 * 预设背景图注册表
 * 图片放在 public/images/back/，部署后 nginx 直接 serve
 * 新增背景图：1. 放图到 public/images/back/  2. 在这里加一行
 */
export interface BgImageItem {
  id: string
  label: string
  url: string       // nginx 可访问的路径，如 /images/back/xxx.jpg
  darkText: boolean // 该背景适合深色文字吗
}

export const BG_IMAGES: BgImageItem[] = [
  // 在这里添加预设背景图，例如：
  // { id: 'sunset', label: '日落', url: '/images/back/sunset.jpg', darkText: false },
  // { id: 'forest', label: '森林', url: '/images/back/forest.jpg', darkText: false },
]

interface BackgroundConfig {
  preset: BackgroundPreset
  animEnabled: boolean
  intensity: number
  colorTheme: ColorTheme
  bgImageId?: string  // 选中的背景图 ID
}

const STORAGE_KEY = 'dixiyang_bg_config'

const DEFAULT_CONFIG: BackgroundConfig = {
  preset: 'static',
  animEnabled: true,
  intensity: 100,
  colorTheme: 'blue',
  bgImageId: undefined,
}

export function useBackgroundConfig() {
  const preset = ref<BackgroundPreset>(DEFAULT_CONFIG.preset)
  const animEnabled = ref<boolean>(DEFAULT_CONFIG.animEnabled)
  const intensity = ref<number>(DEFAULT_CONFIG.intensity)
  const colorTheme = ref<ColorTheme>(DEFAULT_CONFIG.colorTheme)
  const bgImageId = ref<string | undefined>(undefined)

  const bgImageMap = new Map(BG_IMAGES.map(i => [i.id, i]))

  /** 当前选中的背景图对象 */
  const currentBgImage = ref<BgImageItem | undefined>(undefined)

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const config = JSON.parse(stored) as Partial<BackgroundConfig>
        preset.value = config.preset || DEFAULT_CONFIG.preset
        animEnabled.value = config.animEnabled !== undefined ? config.animEnabled : DEFAULT_CONFIG.animEnabled
        intensity.value = config.intensity !== undefined ? config.intensity : DEFAULT_CONFIG.intensity
        colorTheme.value = config.colorTheme || DEFAULT_CONFIG.colorTheme
        bgImageId.value = config.bgImageId
      }
      currentBgImage.value = bgImageId.value ? bgImageMap.get(bgImageId.value) : undefined
    } catch {
      // 静默失败
    }
  }

  const saveToStorage = () => {
    try {
      const config: BackgroundConfig = {
        preset: preset.value,
        animEnabled: animEnabled.value,
        intensity: intensity.value,
        colorTheme: colorTheme.value,
        bgImageId: bgImageId.value,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
    } catch {
      // 静默失败
    }
  }

  const setPreset = (newPreset: BackgroundPreset) => {
    preset.value = newPreset
    // 切换预设主题时清除背景图
    bgImageId.value = undefined
    currentBgImage.value = undefined
  }

  /** 选择背景图 */
  const setBgImage = (id: string | undefined) => {
    bgImageId.value = id
    currentBgImage.value = id ? bgImageMap.get(id) : undefined
  }

  const toggleAnimation = () => { animEnabled.value = !animEnabled.value }
  const setAnimEnabled = (enabled: boolean) => { animEnabled.value = enabled }
  const setIntensity = (v: number) => { intensity.value = Math.max(0, Math.min(100, v)) }
  const setColorTheme = (t: ColorTheme) => { colorTheme.value = t }

  const resetToDefault = () => {
    preset.value = DEFAULT_CONFIG.preset
    animEnabled.value = DEFAULT_CONFIG.animEnabled
    intensity.value = DEFAULT_CONFIG.intensity
    colorTheme.value = DEFAULT_CONFIG.colorTheme
    bgImageId.value = undefined
    currentBgImage.value = undefined
  }

  /** 应用颜色主题 */
  const applyColorTheme = () => {
    const root = document.documentElement
    const themeColors: Record<ColorTheme, { neon: string; secondary: string }> = {
      purple: { neon: '#a855f7', secondary: '#d8b4fe' },
      blue: { neon: '#3b82f6', secondary: '#93c5fd' },
      cyan: { neon: '#06b6d4', secondary: '#06d6d6' },
    }
    const c = themeColors[colorTheme.value]
    root.style.setProperty('--neon-primary', c.neon)
    root.style.setProperty('--neon-secondary', c.secondary)
  }

  /** 应用背景预设 + 背景图到 body */
  const applyBackgroundPreset = () => {
    const root = document.documentElement
    const body = document.body

    root.style.setProperty('--bg-intensity', `${intensity.value / 100}`)

    type PresetVisual = {
      bodyBg: string; textPrimary: string; textSecondary: string; textMuted: string
      textDisabled: string; descriptionColor: string; glassBg: string; glassBorder: string; cardShadow: string
    }

    const presets: Record<BackgroundPreset, PresetVisual> = {
      dynamic: {
        bodyBg: 'radial-gradient(circle at 20% 50%, rgba(168,85,247,0.12) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(59,130,246,0.12) 0%, transparent 50%), radial-gradient(circle at 50% 0%, rgba(6,182,212,0.08) 0%, transparent 50%), #0a0a0c',
        textPrimary: '#ffffff', textSecondary: 'rgba(255,255,255,0.7)',
        textMuted: 'rgba(255,255,255,0.5)', textDisabled: 'rgba(255,255,255,0.3)',
        descriptionColor: '#e8e88e', glassBg: 'rgba(255,255,255,0.05)',
        glassBorder: 'rgba(255,255,255,0.15)', cardShadow: '0 20px 40px rgba(0,0,0,0.4)',
      },
      static: {
        bodyBg: '#f5f5f7', textPrimary: '#1a1a2e',
        textSecondary: 'rgba(26,26,46,0.7)', textMuted: 'rgba(26,26,46,0.5)',
        textDisabled: 'rgba(26,26,46,0.3)', descriptionColor: '#4a4a6a',
        glassBg: 'rgba(255,255,255,0.7)', glassBorder: 'rgba(0,0,0,0.08)',
        cardShadow: '0 8px 32px rgba(0,0,0,0.08)',
      },
      minimal: {
        bodyBg: '#0a0a0c', textPrimary: '#ffffff',
        textSecondary: 'rgba(255,255,255,0.7)', textMuted: 'rgba(255,255,255,0.5)',
        textDisabled: 'rgba(255,255,255,0.3)', descriptionColor: '#e8e88e',
        glassBg: 'rgba(255,255,255,0.03)', glassBorder: 'rgba(255,255,255,0.1)',
        cardShadow: '0 20px 40px rgba(0,0,0,0.6)',
      },
    }

    const p = presets[preset.value]

    // 如果选了背景图，叠加到 body 背景上
    if (currentBgImage.value) {
      body.style.background = `url('${currentBgImage.value.url}') center/cover no-repeat fixed`
      body.style.backgroundColor = p.bodyBg
    } else {
      body.style.background = p.bodyBg
    }
    body.style.color = p.textPrimary

    root.style.setProperty('--text-primary', p.textPrimary)
    root.style.setProperty('--text-secondary', p.textSecondary)
    root.style.setProperty('--text-muted', p.textMuted)
    root.style.setProperty('--text-disabled', p.textDisabled)
    root.style.setProperty('--description-color', p.descriptionColor)
    root.style.setProperty('--glass-bg', p.glassBg)
    root.style.setProperty('--glass-border', p.glassBorder)
    root.style.setProperty('--card-shadow', p.cardShadow)
  }

  watch(
    () => [preset.value, animEnabled.value, intensity.value, colorTheme.value, bgImageId.value],
    () => {
      saveToStorage()
      applyColorTheme()
      applyBackgroundPreset()
    }
  )

  onMounted(() => {
    loadFromStorage()
    applyColorTheme()
    applyBackgroundPreset()
  })

  return {
    preset, animEnabled, intensity, colorTheme,
    bgImageId, currentBgImage,
    setPreset, setBgImage, toggleAnimation, setAnimEnabled,
    setIntensity, setColorTheme, resetToDefault,
    getConfig: () => ({ preset: preset.value, animEnabled: animEnabled.value, intensity: intensity.value, colorTheme: colorTheme.value, bgImageId: bgImageId.value }),
    loadFromStorage, saveToStorage,
    applyColorTheme, applyBackgroundPreset,
  }
}

import { ref, watch, onMounted } from 'vue'

/**
 * 字体系统 Composable
 * 管理字体族、大小、缩放等配置
 */

export type FontFamily = 'inter' | 'serif' | 'monospace' | 'system'

interface FontConfig {
  family: FontFamily
  size: number // 像素值 12-24
  scale: number // 缩放因子 0.5-1.5
}

const FONT_STORAGE_KEY = 'dixiyang_font_config'

/**
 * 默认字体配置
 */
const DEFAULT_CONFIG: FontConfig = {
  family: 'inter',
  size: 16,
  scale: 1,
}

/**
 * 字体族映射到CSS变量名
 */
const fontFamilyMap: Record<FontFamily, string> = {
  inter: '--font-family-inter',
  serif: '--font-family-serif',
  monospace: '--font-family-monospace',
  system: '--font-family-system',
}

export function useFontConfig() {
  // 响应式状态
  const family = ref<FontFamily>(DEFAULT_CONFIG.family)
  const size = ref<number>(DEFAULT_CONFIG.size)
  const scale = ref<number>(DEFAULT_CONFIG.scale)

  /**
   * 从localStorage加载配置
   */
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(FONT_STORAGE_KEY)
      if (stored) {
        const config = JSON.parse(stored) as Partial<FontConfig>
        family.value = config.family || DEFAULT_CONFIG.family
        size.value = config.size !== undefined ? config.size : DEFAULT_CONFIG.size
        scale.value = config.scale !== undefined ? config.scale : DEFAULT_CONFIG.scale
      }
    } catch (error) {
      console.error('Failed to load font config from storage:', error)
    }
  }

  /**
   * 保存配置到localStorage
   */
  const saveToStorage = () => {
    try {
      const config: FontConfig = {
        family: family.value,
        size: size.value,
        scale: scale.value,
      }
      localStorage.setItem(FONT_STORAGE_KEY, JSON.stringify(config))
    } catch (error) {
      console.error('Failed to save font config to storage:', error)
    }
  }

  /**
   * 设置字体族
   */
  const setFontFamily = (newFamily: FontFamily) => {
    family.value = newFamily
  }

  /**
   * 设置字体大小 (12-24px)
   */
  const setFontSize = (newSize: number) => {
    size.value = Math.max(12, Math.min(24, newSize))
  }

  /**
   * 设置全局缩放因子 (0.5-1.5)
   */
  const setFontScale = (newScale: number) => {
    scale.value = Math.max(0.5, Math.min(1.5, newScale))
  }

  /**
   * 应用字体配置到DOM的:root CSS变量
   */
  const applyFontSettings = () => {
    const root = document.documentElement

    // 设置字体族变量
    const familyVar = fontFamilyMap[family.value]
    const fontFamilyValue = getComputedStyle(root).getPropertyValue(familyVar).trim()
    root.style.setProperty('--font-family', fontFamilyValue || `var(${familyVar})`)

    // 设置基础字体大小
    root.style.setProperty('--font-size-base', `${size.value}px`)

    // 设置全局缩放因子
    root.style.setProperty('--font-scale', String(scale.value))
  }

  /**
   * 获取当前配置对象
   */
  const getConfig = (): FontConfig => ({
    family: family.value,
    size: size.value,
    scale: scale.value,
  })

  /**
   * 重置为默认配置
   */
  const resetToDefault = () => {
    family.value = DEFAULT_CONFIG.family
    size.value = DEFAULT_CONFIG.size
    scale.value = DEFAULT_CONFIG.scale
  }

  /**
   * 判断字体大小是否在默认值
   */
  const isDefaultSize = (): boolean => {
    return size.value === DEFAULT_CONFIG.size
  }

  /**
   * 判断字体族是否为默认值
   */
  const isDefaultFamily = (): boolean => {
    return family.value === DEFAULT_CONFIG.family
  }

  /**
   * 判断缩放因子是否为默认值
   */
  const isDefaultScale = (): boolean => {
    return scale.value === DEFAULT_CONFIG.scale
  }

  /**
   * 生成实际应用的计算字体大小
   * 考虑基础大小 * 缩放因子
   */
  const getEffectiveFontSize = (): number => {
    return size.value * scale.value
  }

  // 监听配置变化，自动保存和应用
  watch(
    () => [family.value, size.value, scale.value],
    () => {
      saveToStorage()
      applyFontSettings()
    },
    { deep: true }
  )

  // 组件挂载时，从存储加载并应用
  onMounted(() => {
    loadFromStorage()
    applyFontSettings()
  })

  return {
    // 状态
    family,
    size,
    scale,

    // 方法
    setFontFamily,
    setFontSize,
    setFontScale,
    applyFontSettings,
    loadFromStorage,
    saveToStorage,
    getConfig,
    resetToDefault,
    isDefaultSize,
    isDefaultFamily,
    isDefaultScale,
    getEffectiveFontSize,
  }
}

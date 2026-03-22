import { ref, onMounted, watch } from 'vue'
import http from '@/utils/http'

/**
 * 文本颜色自定义 Composable
 * 管理用户自定义的字体颜色配置
 * 支持 localStorage 持久化和后端数据库同步
 */

interface TextColorConfig {
  textPrimary: string      // 主要文本颜色 (默认: #ffffff)
  textSecondary: string    // 次要文本颜色 (默认: rgba(255, 255, 255, 0.7))
  textMuted: string        // 弱化文本颜色 (默认: rgba(255, 255, 255, 0.5))
  textDisabled: string     // 禁用文本颜色 (默认: rgba(255, 255, 255, 0.3))
  descriptionColor?: string // 描述文本颜色 (默认: #e8e88e)
  linkColor?: string       // 链接文本颜色 (默认: #3b82f6)
  accentColor?: string     // 强调文本颜色 (默认: #ff6b6b)
}

const STORAGE_KEY = 'dixiyang_text_color_config'

/**
 * 默认文本颜色配置
 * 全局统一的文字颜色管理系统
 */
const DEFAULT_CONFIG: TextColorConfig = {
  textPrimary: '#ffffff',
  textSecondary: 'rgba(255, 255, 255, 0.7)',
  textMuted: 'rgba(255, 255, 255, 0.5)',
  textDisabled: 'rgba(255, 255, 255, 0.3)',
  descriptionColor: '#e8e88e',
  linkColor: '#3b82f6',
  accentColor: '#ff6b6b',
}

export function useTextColorCustomizer() {
  // 响应式状态
  const textPrimary = ref<string>(DEFAULT_CONFIG.textPrimary)
  const textSecondary = ref<string>(DEFAULT_CONFIG.textSecondary)
  const textMuted = ref<string>(DEFAULT_CONFIG.textMuted)
  const textDisabled = ref<string>(DEFAULT_CONFIG.textDisabled)
  const descriptionColor = ref<string>(DEFAULT_CONFIG.descriptionColor || '')
  const linkColor = ref<string>(DEFAULT_CONFIG.linkColor || '')
  const accentColor = ref<string>(DEFAULT_CONFIG.accentColor || '')

  const isSyncing = ref<boolean>(false)
  const syncMessage = ref<string>('')

  /**
   * 从 localStorage 读取配置
   */
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const config = JSON.parse(stored) as Partial<TextColorConfig>
        textPrimary.value = config.textPrimary || DEFAULT_CONFIG.textPrimary
        textSecondary.value = config.textSecondary || DEFAULT_CONFIG.textSecondary
        textMuted.value = config.textMuted || DEFAULT_CONFIG.textMuted
        textDisabled.value = config.textDisabled || DEFAULT_CONFIG.textDisabled
        descriptionColor.value = config.descriptionColor || DEFAULT_CONFIG.descriptionColor || ''
        linkColor.value = config.linkColor || DEFAULT_CONFIG.linkColor || ''
        accentColor.value = config.accentColor || DEFAULT_CONFIG.accentColor || ''
      }
    } catch (error) {
      console.error('Failed to load text color config from storage:', error)
    }
  }

  /**
   * 保存配置到 localStorage
   */
  const saveToStorage = () => {
    try {
      const config: TextColorConfig = {
        textPrimary: textPrimary.value,
        textSecondary: textSecondary.value,
        textMuted: textMuted.value,
        textDisabled: textDisabled.value,
        descriptionColor: descriptionColor.value,
        linkColor: linkColor.value,
        accentColor: accentColor.value,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
    } catch (error) {
      console.error('Failed to save text color config to storage:', error)
    }
  }

  /**
   * 应用文本颜色到 CSS 变量
   */
  const applyCSSVariables = () => {
    const root = document.documentElement
    root.style.setProperty('--text-primary', textPrimary.value)
    root.style.setProperty('--text-secondary', textSecondary.value)
    root.style.setProperty('--text-muted', textMuted.value)
    root.style.setProperty('--text-disabled', textDisabled.value)
    root.style.setProperty('--description-color', descriptionColor.value)
    root.style.setProperty('--link-color', linkColor.value)
    root.style.setProperty('--accent-color', accentColor.value)
  }

  /**
   * 设置主要文本颜色
   */
  const setTextPrimary = (color: string) => {
    textPrimary.value = color
  }

  /**
   * 设置次要文本颜色
   */
  const setTextSecondary = (color: string) => {
    textSecondary.value = color
  }

  /**
   * 设置弱化文本颜色
   */
  const setTextMuted = (color: string) => {
    textMuted.value = color
  }

  /**
   * 设置禁用文本颜色
   */
  const setTextDisabled = (color: string) => {
    textDisabled.value = color
  }

  /**
   * 设置描述文本颜色
   */
  const setDescriptionColor = (color: string) => {
    descriptionColor.value = color
  }

  /**
   * 设置链接文本颜色
   */
  const setLinkColor = (color: string) => {
    linkColor.value = color
  }

  /**
   * 设置强调文本颜色
   */
  const setAccentColor = (color: string) => {
    accentColor.value = color
  }

  /**
   * 获取当前配置对象
   */
  const getConfig = (): TextColorConfig => ({
    textPrimary: textPrimary.value,
    textSecondary: textSecondary.value,
    textMuted: textMuted.value,
    textDisabled: textDisabled.value,
    descriptionColor: descriptionColor.value,
    linkColor: linkColor.value,
    accentColor: accentColor.value,
  })

  /**
   * 重置为默认配置
   */
  const resetToDefault = () => {
    textPrimary.value = DEFAULT_CONFIG.textPrimary
    textSecondary.value = DEFAULT_CONFIG.textSecondary
    textMuted.value = DEFAULT_CONFIG.textMuted
    textDisabled.value = DEFAULT_CONFIG.textDisabled
    descriptionColor.value = DEFAULT_CONFIG.descriptionColor || ''
    linkColor.value = DEFAULT_CONFIG.linkColor || ''
    accentColor.value = DEFAULT_CONFIG.accentColor || ''
  }

  /**
   * 保存配置到后端
   */
  const saveToBackend = async (): Promise<boolean> => {
    try {
      isSyncing.value = true
      syncMessage.value = '正在同步...'

      const config: TextColorConfig = {
        textPrimary: textPrimary.value,
        textSecondary: textSecondary.value,
        textMuted: textMuted.value,
        textDisabled: textDisabled.value,
        descriptionColor: descriptionColor.value,
        linkColor: linkColor.value,
        accentColor: accentColor.value,
      }

      // 创建完整的背景配置 DTO（包含字体颜色）
      const bgConfigRes = await http.get('/user/bg-config')
      const bgConfigData = bgConfigRes as any
      let fullConfig = bgConfigData.data || {}

      // 合并字体颜色到背景配置中
      fullConfig = {
        ...fullConfig,
        fontColors: config,
      }

      const res = await http.post('/user/bg-config', fullConfig)
      const resData = res as any
      if (resData.code === 200) {
        syncMessage.value = '✅ 颜色已保存'
        console.log('✅ 文本颜色配置已保存到后端')
        return true
      } else {
        syncMessage.value = '❌ 保存失败'
        console.warn('⚠️ 保存文本颜色配置到后端失败:', resData.msg)
        return false
      }
    } catch (error) {
      syncMessage.value = '❌ 同步出错'
      console.warn('⚠️ 保存文本颜色配置到后端异常:', error)
      return false
    } finally {
      isSyncing.value = false
      // 2秒后清空提示信息
      setTimeout(() => {
        syncMessage.value = ''
      }, 2000)
    }
  }

  /**
   * 从后端加载配置
   */
  const loadFromBackend = async (): Promise<boolean> => {
    try {
      const res = await http.get('/user/bg-config')
      const resData = res as any
      if (resData.code === 200 && resData.data) {
        const bgConfig = resData.data
        if (bgConfig.fontColors) {
          textPrimary.value = bgConfig.fontColors.textPrimary || DEFAULT_CONFIG.textPrimary
          textSecondary.value = bgConfig.fontColors.textSecondary || DEFAULT_CONFIG.textSecondary
          textMuted.value = bgConfig.fontColors.textMuted || DEFAULT_CONFIG.textMuted
          textDisabled.value = bgConfig.fontColors.textDisabled || DEFAULT_CONFIG.textDisabled
          descriptionColor.value = bgConfig.fontColors.descriptionColor || DEFAULT_CONFIG.descriptionColor || ''
          linkColor.value = bgConfig.fontColors.linkColor || DEFAULT_CONFIG.linkColor || ''
          accentColor.value = bgConfig.fontColors.accentColor || DEFAULT_CONFIG.accentColor || ''
          console.log('✅ 从后端加载文本颜色配置成功')
          return true
        }
      }
    } catch (error) {
      console.warn('⚠️ 从后端加载文本颜色配置异常:', error)
    }
    return false
  }

  /**
   * 判断是否为默认配置
   */
  const isDefaultConfig = (): boolean => {
    return (
      textPrimary.value === DEFAULT_CONFIG.textPrimary &&
      textSecondary.value === DEFAULT_CONFIG.textSecondary &&
      textMuted.value === DEFAULT_CONFIG.textMuted &&
      textDisabled.value === DEFAULT_CONFIG.textDisabled &&
      descriptionColor.value === (DEFAULT_CONFIG.descriptionColor || '') &&
      linkColor.value === (DEFAULT_CONFIG.linkColor || '') &&
      accentColor.value === (DEFAULT_CONFIG.accentColor || '')
    )
  }

  // 监听配置变化，自动保存到 localStorage 和应用 CSS 变量
  watch(
    () => [
      textPrimary.value,
      textSecondary.value,
      textMuted.value,
      textDisabled.value,
      descriptionColor.value,
      linkColor.value,
      accentColor.value,
    ],
    () => {
      saveToStorage()
      applyCSSVariables()
    },
    { deep: true }
  )

  // 组件挂载时，从存储加载并应用
  onMounted(() => {
    loadFromStorage()
    applyCSSVariables()
  })

  return {
    // 状态
    textPrimary,
    textSecondary,
    textMuted,
    textDisabled,
    descriptionColor,
    linkColor,
    accentColor,
    isSyncing,
    syncMessage,

    // 方法
    setTextPrimary,
    setTextSecondary,
    setTextMuted,
    setTextDisabled,
    setDescriptionColor,
    setLinkColor,
    setAccentColor,
    applyCSSVariables,
    getConfig,
    resetToDefault,
    isDefaultConfig,
    saveToBackend,
    loadFromBackend,
    saveToStorage,
    loadFromStorage,
  }
}




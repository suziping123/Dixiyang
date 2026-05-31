import { ref, computed, onMounted, watch } from 'vue'

/**
 * 全局主题系统
 * 每个主题对应 main.css 中的 html.theme-xxx class
 * 应用主题只做一件事：切换 <html> 的 class
 */
export type ThemeId = 'dynamic' | 'minimal-dark' | 'minimal-light'

interface ThemeOption {
  id: ThemeId
  label: string
  icon: string
  description: string
}

export const THEMES: ThemeOption[] = [
  { id: 'dynamic',       label: '动态暗色', icon: '✨', description: '渐变背景 · 浅色文字' },
  { id: 'minimal-dark',  label: '极简暗色', icon: '🌙', description: '纯色背景 · 浅色文字' },
  { id: 'minimal-light', label: '极简亮色', icon: '☀️', description: '纯色背景 · 深色文字' },
]

/**
 * 预设背景图注册表
 * 图片放在 src/images/back/，通过 import 引用
 */
export interface BgImageItem {
  id: string
  label: string
  importFn: () => Promise<string>   // 动态 import，按需加载
}

// 使用 Vite 的 import.meta.glob 自动发现 src/images/back/ 下的图片
const bgImageGlob = import.meta.glob<string>('@/images/back/*.{png,jpg,jpeg,webp}', { eager: false, query: '?url', import: 'default' })

export const BG_IMAGES: BgImageItem[] = Object.entries(bgImageGlob).map(([path, importFn]) => ({
  id: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  label: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  importFn: importFn as () => Promise<string>,
}))

interface Config {
  themeId: ThemeId
  bgImageId?: string
}

const STORAGE_KEY = 'dixiyang_theme_config'

const DEFAULT_CONFIG: Config = {
  themeId: 'minimal-light',
  bgImageId: undefined,
}

export function useBackgroundConfig() {
  const themeId = ref<ThemeId>(DEFAULT_CONFIG.themeId)
  const bgImageId = ref<string | undefined>(undefined)
  const bgImageUrl = ref<string | undefined>(undefined)

  const activeTheme = computed(() => THEMES.find(t => t.id === themeId.value) || THEMES[0])

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const c = JSON.parse(stored) as Partial<Config>
        themeId.value = c.themeId || DEFAULT_CONFIG.themeId
        bgImageId.value = c.bgImageId
      }
    } catch {}
  }

  const saveToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId: themeId.value, bgImageId: bgImageId.value }))
  }

  /** 应用主题到 <html> + 加载背景图 */
  const applyTheme = async () => {
    const html = document.documentElement
    // 移除旧主题 class
    html.classList.remove('theme-dynamic', 'theme-minimal-dark', 'theme-minimal-light')
    // 添加新主题 class
    html.classList.add(`theme-${themeId.value}`)

    // 处理背景图
    const body = document.body
    if (bgImageId.value) {
      const item = BG_IMAGES.find(i => i.id === bgImageId.value)
      if (item) {
        try {
          const url = await item.importFn()
          bgImageUrl.value = url
          body.classList.add('has-bg-image')
          body.style.backgroundImage = `url('${url}')`
          body.style.backgroundSize = 'cover'
          body.style.backgroundPosition = 'center'
          body.style.backgroundRepeat = 'no-repeat'
          body.style.backgroundAttachment = 'fixed'
        } catch {
          body.classList.remove('has-bg-image')
          body.style.backgroundImage = ''
        }
      }
    } else {
      bgImageUrl.value = undefined
      body.classList.remove('has-bg-image')
      body.style.backgroundImage = ''
    }
  }

  const setTheme = (id: ThemeId) => { themeId.value = id }
  const setBgImage = (id: string | undefined) => {
    bgImageId.value = id
    if (!id) bgImageUrl.value = undefined
  }

  const resetToDefault = () => {
    themeId.value = DEFAULT_CONFIG.themeId
    bgImageId.value = undefined
    bgImageUrl.value = undefined
  }

  watch([themeId, bgImageId], () => {
    saveToStorage()
    applyTheme()
  })

  onMounted(() => {
    loadFromStorage()
    applyTheme()
  })

  return {
    themeId, bgImageId, bgImageUrl, activeTheme,
    setTheme, setBgImage, resetToDefault,
    loadFromStorage, saveToStorage, applyTheme,
  }
}

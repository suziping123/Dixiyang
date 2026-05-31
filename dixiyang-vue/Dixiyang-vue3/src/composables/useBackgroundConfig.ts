import { ref, computed, watch } from 'vue'

export type ThemeId = 'dark' | 'light'

interface ThemeOption { id: ThemeId; label: string; icon: string; description: string }

export const THEMES: ThemeOption[] = [
  { id: 'dark',  label: '极简暗色', icon: '🌙', description: '暗色玻璃 · 浅色文字' },
  { id: 'light', label: '极简亮色', icon: '☀️', description: '亮色玻璃 · 深色文字' },
]

const bgGlob = import.meta.glob<string>('@/images/back/*.{png,jpg,jpeg,webp}', { eager: false, query: '?url', import: 'default' })

export interface BgImageItem { id: string; label: string; importFn: () => Promise<string>; darkOverlay?: number }

export const BG_IMAGES: BgImageItem[] = Object.entries(bgGlob).map(([path, fn]) => ({
  id: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  label: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  importFn: fn as () => Promise<string>,
}))

interface Config { themeId: ThemeId; bgImageId?: string }
const STORAGE_KEY = 'dixiyang_theme_config'
const DEFAULT: Config = { themeId: 'light', bgImageId: undefined }

export function useBackgroundConfig() {
  const themeId = ref<ThemeId>(DEFAULT.themeId)
  const bgImageId = ref<string | undefined>(undefined)
  const bgImageUrl = ref<string | undefined>(undefined)
  const activeTheme = computed(() => THEMES.find(t => t.id === themeId.value) || THEMES[0])

  const loadFromStorage = () => {
    try {
      const s = localStorage.getItem(STORAGE_KEY)
      if (!s) return
      const c = JSON.parse(s) as Partial<Config>
      themeId.value = c.themeId || DEFAULT.themeId
      bgImageId.value = c.bgImageId
    } catch { /* */ }
  }

  const saveToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId: themeId.value, bgImageId: bgImageId.value }))
  }

  const apply = async () => {
    const html = document.documentElement
    const body = document.body

    // --- 主题 ---
    html.className = `theme-${themeId.value}`
    // 恢复 body 的默认背景
    body.style.cssText = ''
    body.className = ''

    // --- 背景图（真实 DOM 元素，不依赖 body background） ---
    let bgEl = document.getElementById('theme-bg')
    if (!bgEl) {
      bgEl = document.createElement('div')
      bgEl.id = 'theme-bg'
      // 直接插入到 body 的最前面
      body.insertBefore(bgEl, body.firstChild)
    }

    if (bgImageId.value) {
      const item = BG_IMAGES.find(i => i.id === bgImageId.value)
      if (item) {
        try {
          const url = await item.importFn()
          bgImageUrl.value = url
          const isDark = themeId.value === 'dark'
          const overlay = isDark
            ? 'rgba(0,0,0,' + (item.darkOverlay ?? 0.15) + ')'
            : 'rgba(255,255,255,0.1)'

          bgEl.style.cssText = `
            position: fixed; inset: 0; z-index: 0;
            background: linear-gradient(${overlay}, ${overlay}),
                        url('${url}') center/cover no-repeat fixed;
            pointer-events: none;
          `
        } catch {
          bgEl.style.cssText = 'display: none'
        }
      }
    } else {
      bgImageUrl.value = undefined
      bgEl.style.cssText = 'display: none'
    }
  }

  const setTheme = (id: ThemeId) => { themeId.value = id }
  const setBgImage = (id: string | undefined) => { bgImageId.value = id }
  const resetToDefault = () => { themeId.value = DEFAULT.themeId; bgImageId.value = undefined }

  watch([themeId, bgImageId], () => { saveToStorage(); apply() })

  return { themeId, bgImageId, bgImageUrl, activeTheme, setTheme, setBgImage, resetToDefault, apply }
}

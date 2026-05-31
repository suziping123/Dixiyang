import { ref, computed, onMounted, watch } from 'vue'

export type ThemeId = 'dynamic' | 'minimal-dark' | 'minimal-light'

interface ThemeOption { id: ThemeId; label: string; icon: string; description: string }

export const THEMES: ThemeOption[] = [
  { id: 'dynamic',       label: '动态暗色', icon: '✨', description: '渐变背景动画 · 浅色文字' },
  { id: 'minimal-dark',  label: '极简暗色', icon: '🌙', description: '纯色背景 · 浅色文字' },
  { id: 'minimal-light', label: '极简亮色', icon: '☀️', description: '纯色背景 · 深色文字' },
]

const bgImageGlob = import.meta.glob<string>('@/images/back/*.{png,jpg,jpeg,webp}', { eager: false, query: '?url', import: 'default' })

export interface BgImageItem { id: string; label: string; importFn: () => Promise<string> }

export const BG_IMAGES: BgImageItem[] = Object.entries(bgImageGlob).map(([path, fn]) => ({
  id: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  label: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  importFn: fn as () => Promise<string>,
}))

interface Config { themeId: ThemeId; bgImageId?: string }
const STORAGE_KEY = 'dixiyang_theme_config'
const DEFAULT: Config = { themeId: 'minimal-light', bgImageId: undefined }

export function useBackgroundConfig() {
  const themeId = ref<ThemeId>(DEFAULT.themeId)
  const bgImageId = ref<string | undefined>(undefined)
  const bgImageUrl = ref<string | undefined>(undefined)
  const activeTheme = computed(() => THEMES.find(t => t.id === themeId.value) || THEMES[0])

  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (!stored) return
      const c = JSON.parse(stored) as Partial<Config>
      themeId.value = c.themeId || DEFAULT.themeId
      bgImageId.value = c.bgImageId
    } catch { /* ignore */ }
  }

  const saveToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId: themeId.value, bgImageId: bgImageId.value }))
  }

  const applyTheme = async () => {
    const html = document.documentElement
    const body = document.body

    html.className = `theme-${themeId.value}`
    body.className = ''
    body.style.cssText = ''

    if (bgImageId.value) {
      const item = BG_IMAGES.find(i => i.id === bgImageId.value)
      if (item) {
        try {
          const url = await item.importFn()
          bgImageUrl.value = url
          body.classList.add('has-bg-image')

          // 多背景叠加：上层遮罩 + 下层图片
          const overlay = themeId.value === 'minimal-light'
            ? 'linear-gradient(rgba(255,255,255,0.15), rgba(255,255,255,0.15))'
            : 'linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35))'

          body.style.background = `${overlay}, url('${url}') center/cover no-repeat fixed`
          return
        } catch { /* fall through */ }
      }
    }

    // 无背景图 → 主题固有背景
    bgImageUrl.value = undefined
    if (themeId.value === 'dynamic') {
      body.classList.add('theme-dynamic-bg')
    }
  }

  const setTheme = (id: ThemeId) => { themeId.value = id }
  const setBgImage = (id: string | undefined) => { bgImageId.value = id; if (!id) bgImageUrl.value = undefined }
  const resetToDefault = () => { themeId.value = DEFAULT.themeId; bgImageId.value = undefined; bgImageUrl.value = undefined }

  watch([themeId, bgImageId], () => { saveToStorage(); applyTheme() })
  onMounted(() => { loadFromStorage(); applyTheme() })

  return { themeId, bgImageId, bgImageUrl, activeTheme, setTheme, setBgImage, resetToDefault, applyTheme }
}

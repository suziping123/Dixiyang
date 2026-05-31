import { ref, computed, watch } from 'vue'

export type ThemeId = 'dark'

interface ThemeOption { id: ThemeId; label: string; icon: string; description: string }

export const THEMES: ThemeOption[] = [
  { id: 'dark', label: '暗色', icon: '🌙', description: '暗色玻璃 · 浅色文字' },
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
const DEFAULT: Config = { themeId: 'dark', bgImageId: undefined }

// === 模块级单例状态 ===
const _themeId = ref<ThemeId>(DEFAULT.themeId)
const _bgImageId = ref<string | undefined>(undefined)
const _bgImageUrl = ref<string | undefined>(undefined)

function saveToStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId: _themeId.value, bgImageId: _bgImageId.value }))
}

async function applyBackground() {
  const body = document.body
  if (!body) return

  body.className = ''
  body.style.background = ''
  body.style.backgroundImage = ''

  let bgEl = document.getElementById('theme-bg')
  if (!bgEl) {
    bgEl = document.createElement('div')
    bgEl.id = 'theme-bg'
    body.insertBefore(bgEl, body.firstChild)
  }

  if (_bgImageId.value) {
    const item = BG_IMAGES.find(i => i.id === _bgImageId.value)
    if (item) {
      try {
        const url = await item.importFn()
        _bgImageUrl.value = url
        const overlay = 'rgba(0,0,0,' + (item.darkOverlay ?? 0.15) + ')'
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
    _bgImageUrl.value = undefined
    bgEl.style.cssText = 'display: none'
  }
}

// === 模块级 watcher（单例，不会随组件销毁而失活） ===
watch([_themeId, _bgImageId], () => {
  saveToStorage()
  document.documentElement.className = `theme-${_themeId.value}`
  applyBackground()
})

/** 在挂载前调用：读取 localStorage 并立即设置 html class（无闪烁） */
export function initTheme() {
  try {
    const s = localStorage.getItem(STORAGE_KEY)
    if (s) {
      const c = JSON.parse(s) as Partial<Config>
      _themeId.value = c.themeId || DEFAULT.themeId
      _bgImageId.value = c.bgImageId
    }
  } catch { /* */ }

  document.documentElement.className = `theme-${_themeId.value}`

  if (document.body) {
    document.body.className = ''
    document.body.style.background = ''
    document.body.style.backgroundImage = ''
    // 背景图异步加载
    applyBackground()
  }
}

/** 组件内使用的 composable（读取单例 ref） */
export function useBackgroundConfig() {
  const activeTheme = computed(() => THEMES.find(t => t.id === _themeId.value) || THEMES[0])

  return {
    themeId: _themeId,
    bgImageId: _bgImageId,
    bgImageUrl: _bgImageUrl,
    activeTheme,
    setTheme: (id: ThemeId) => { _themeId.value = id },
    setBgImage: (id: string | undefined) => { _bgImageId.value = id },
    resetToDefault: () => { _themeId.value = DEFAULT.themeId; _bgImageId.value = undefined },
  }
}

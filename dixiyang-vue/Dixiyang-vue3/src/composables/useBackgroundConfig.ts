import { ref, computed, watch } from 'vue'
import http, { assertApiResponse } from '@/utils/http'

export type ThemeId = 'dark'

interface ThemeOption { id: ThemeId; label: string; icon: string; description: string }

export const THEMES: ThemeOption[] = [
  { id: 'dark', label: '暗色', icon: '🌙', description: '暗色玻璃 · 浅色文字' },
]

const bgGlob = import.meta.glob<string>('@/images/back/*.{png,jpg,jpeg,webp}', { eager: false, query: '?url', import: 'default' })

export interface BgImageItem { id: string; label: string; importFn: () => Promise<string>; darkOverlay?: number; isCustom?: boolean; url?: string }

export const BG_IMAGES: BgImageItem[] = Object.entries(bgGlob).map(([path, fn]) => ({
  id: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  label: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
  importFn: fn as () => Promise<string>,
}))

// === 自定义背景图管理（localStorage 缓存，后端持久化） ===
const CUSTOM_BG_KEY = 'dixiyang_custom_bgs'

interface CustomBg { id: string; url: string; label: string }

function getCustomBgs(): CustomBg[] {
  try {
    return JSON.parse(localStorage.getItem(CUSTOM_BG_KEY) || '[]')
  } catch { return [] }
}

function saveCustomBgs(bgs: CustomBg[]) {
  localStorage.setItem(CUSTOM_BG_KEY, JSON.stringify(bgs))
}

export function addCustomBg(url: string, label?: string) {
  const bgs = getCustomBgs()
  const id = 'custom_' + Date.now()
  bgs.push({ id, url, label: label || `自定义 ${bgs.length + 1}` })
  saveCustomBgs(bgs)
  syncToServer()
  return id
}

export function removeCustomBg(id: string) {
  const bgs = getCustomBgs().filter(b => b.id !== id)
  saveCustomBgs(bgs)
  syncToServer()
}

export function getCustomBgImages(): BgImageItem[] {
  return getCustomBgs().map(bg => ({
    id: bg.id,
    label: bg.label,
    importFn: async () => bg.url,
    isCustom: true,
    url: bg.url,
  }))
}

// === 后端 API ===
interface BackgroundConfig {
  backgroundId?: string
  customBgs?: string  // JSON string
}

function getUserId(): number | null {
  const raw = localStorage.getItem('userId')
  if (!raw) return null
  const id = Number(raw)
  if (!id || isNaN(id)) return null
  return id
}

async function fetchFromServer(): Promise<BackgroundConfig | null> {
  const userId = getUserId()
  if (!userId) return null
  try {
    const res = await http.get('/userConfig/background', { params: { userId } })
    const ApiResponse = assertApiResponse<{ backgroundId?: string; customBgs?: string }>(res)
    return ApiResponse.data || null
  } catch {
    return null
  }
}

async function saveToServer(data: BackgroundConfig) {
  const userId = getUserId()
  if (!userId) return
  try {
    await http.post('/userConfig/background', { userId, ...data })
  } catch (e) {
    console.warn('保存背景配置到服务器失败:', e)
  }
}

// 切换/选择背景时同步到服务器
function syncToServer() {
  saveToServer({
    backgroundId: _bgImageId.value,
    customBgs: JSON.stringify(getCustomBgs()),
  })
}

// === 配置存储 ===
interface Config { themeId: ThemeId; bgImageId?: string }
const STORAGE_KEY = 'dixiyang_theme_config'
const DEFAULT: Config = { themeId: 'dark', bgImageId: undefined }

// === 模块级单例状态 ===
const _themeId = ref<ThemeId>(DEFAULT.themeId)
const _bgImageId = ref<string | undefined>(undefined)
const _bgImageUrl = ref<string | undefined>(undefined)
const _loaded = ref(false)

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
    const allImages = [...BG_IMAGES, ...getCustomBgImages()]
    const item = allImages.find(i => i.id === _bgImageId.value)
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

// === 模块级 watcher ===
watch([_themeId, _bgImageId], () => {
  saveToStorage()
  document.documentElement.className = `theme-${_themeId.value}`
  applyBackground()
  // 登录状态下同步到服务器
  if (getUserId()) syncToServer()
})

/** 在挂载前调用：读取 localStorage 并立即设置 html class（无闪烁） */
export function initTheme() {
  // 1. 先从 localStorage 读取（无闪烁）
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
    applyBackground()
  }

  // 2. 异步从服务器加载（覆盖 localStorage）
  loadFromServer()
}

/** 从服务器加载背景配置并覆盖本地 */
async function loadFromServer() {
  const data = await fetchFromServer()
  if (!data) { _loaded.value = true; return }

  // 恢复自定义背景列表
  if (data.customBgs) {
    try {
      const bgs = JSON.parse(data.customBgs) as CustomBg[]
      saveCustomBgs(bgs)
    } catch { /* */ }
  }

  // 恢复当前选中的背景
  if (data.backgroundId) {
    _bgImageId.value = data.backgroundId
    applyBackground()
  }

  _loaded.value = true
}

/** 组件内使用的 composable */
export function useBackgroundConfig() {
  const activeTheme = computed(() => THEMES.find(t => t.id === _themeId.value) || THEMES[0])

  return {
    themeId: _themeId,
    bgImageId: _bgImageId,
    bgImageUrl: _bgImageUrl,
    loaded: _loaded,
    activeTheme,
    setTheme: (id: ThemeId) => { _themeId.value = id },
    setBgImage: (id: string | undefined) => { _bgImageId.value = id },
    resetToDefault: () => { _themeId.value = DEFAULT.themeId; _bgImageId.value = undefined },
  }
}

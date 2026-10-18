// 控制台背景层：复用用户端同一机制（同源 localStorage → #theme-bg 固定照片层 + 叠色）
// 与用户端不同点：只读缓存、不回写、不请求服务端（控制台会话与用户端接口隔离）
const STORAGE_KEY = 'dixiyang_theme_config'
const CUSTOM_BG_KEY = 'dixiyang_custom_bgs'
const OVERLAY = 'rgba(0,0,0,0.15)' // 与用户端 applyBackground 默认一致
const DEFAULT_BG_HINT = '大草原-天空-宁静' // 缓存里没有选择时的内置默认（宁静系壁纸）

const bgGlob = import.meta.glob<string>('@/images/back/*.{png,jpg,jpeg,webp}', {
  eager: false,
  query: '?url',
  import: 'default',
})

interface BuiltinBg {
  id: string
  importFn: () => Promise<string>
}

function readBgImageId(): string | undefined {
  try {
    const cfg = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') as { bgImageId?: string }
    return cfg.bgImageId
  } catch {
    return undefined
  }
}

function readCustomBgUrl(id: string): string | undefined {
  try {
    const list = JSON.parse(localStorage.getItem(CUSTOM_BG_KEY) || '[]') as { id: string; url?: string }[]
    return list.find((x) => x.id === id)?.url
  } catch {
    return undefined
  }
}

export async function initConsoleBackground(): Promise<void> {
  const builtins: BuiltinBg[] = Object.entries(bgGlob).map(([path, fn]) => ({
    id: path.split('/').pop()!.replace(/\.[^.]+$/, ''),
    importFn: fn as () => Promise<string>,
  }))
  if (!builtins.length) return

  let url: string | undefined
  const bgImageId = readBgImageId()
  if (bgImageId) {
    url = readCustomBgUrl(bgImageId) // 用户端上传的自定义背景：URL 直接可用
    if (!url) {
      const builtin = builtins.find((x) => x.id === bgImageId)
      if (builtin) {
        try {
          url = await builtin.importFn()
        } catch {
          url = undefined
        }
      }
    }
  }
  if (!url) {
    const fallback = builtins.find((x) => x.id.includes(DEFAULT_BG_HINT)) ?? builtins[0]
    if (!fallback) return
    try {
      url = await fallback.importFn()
    } catch {
      return
    }
  }
  if (!url) return

  let bgEl = document.getElementById('theme-bg')
  if (!bgEl) {
    bgEl = document.createElement('div')
    bgEl.id = 'theme-bg'
    document.body.insertBefore(bgEl, document.body.firstChild)
  }
  bgEl.style.cssText = `
    position: fixed; inset: 0; z-index: 0;
    background: linear-gradient(${OVERLAY}, ${OVERLAY}), url('${url}') center/cover no-repeat fixed;
    pointer-events: none;
  `
}

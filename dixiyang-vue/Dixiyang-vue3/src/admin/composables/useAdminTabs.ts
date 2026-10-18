// 多页签状态（浏览器式）：模块级单例；会话内持久化 sessionStorage
// keep-alive 的缓存清单由 LayoutView 用 keepNames 控制（关签即从 include 移除 → 缓存被丢弃）
import { computed, ref, watch } from 'vue'
import { CONSOLE_PAGES, FIXED_TAB, pageByName, pageByRouteName } from '../menu'

export interface AdminTab {
  name: string
  path: string
}

const SESSION_KEY = 'dixiyang_admin_tabs'

function loadTabs(): AdminTab[] {
  let arr: AdminTab[] = []
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    if (raw) {
      arr = (JSON.parse(raw) as AdminTab[]).filter(
        (t) => t && typeof t.name === 'string' && CONSOLE_PAGES.some((p) => p.name === t.name),
      )
    }
  } catch {
    arr = []
  }
  if (!arr.some((t) => t.name === FIXED_TAB)) {
    const fixed = pageByName(FIXED_TAB)
    if (fixed) arr.unshift({ name: fixed.name, path: fixed.path })
  }
  return arr
}

const tabs = ref<AdminTab[]>(loadTabs())
const activeName = ref<string>(FIXED_TAB)

watch(
  tabs,
  (v) => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(v))
    } catch {
      /* sessionStorage 不可用则仅内存态 */
    }
  },
  { deep: true },
)

export function useAdminTabs() {
  /** 路由变化时调用：若是控制台页面则确保开签并激活（刷新 / 直达 URL 同路径） */
  const syncRoute = (routeName: unknown) => {
    const page = pageByRouteName(routeName)
    if (!page) return
    if (!tabs.value.some((t) => t.name === page.name)) {
      tabs.value.push({ name: page.name, path: page.path })
    }
    activeName.value = page.name
  }

  /** 关闭页签：返回"应导航到的相邻签"（关闭的是当前签时），否则 null */
  const closeTab = (name: string): AdminTab | null => {
    if (name === FIXED_TAB) return null
    const idx = tabs.value.findIndex((t) => t.name === name)
    if (idx < 0) return null
    tabs.value.splice(idx, 1)
    if (activeName.value !== name) return null
    // 关的是当前签：优先激活右邻，无则左邻（与浏览器关闭标签一致）
    return tabs.value[idx] ?? tabs.value[idx - 1] ?? tabs.value[0] ?? null
  }

  /** keep-alive include 清单：已开签的组件名 */
  const keepNames = computed(() =>
    tabs.value.map((t) => pageByName(t.name)?.keepName).filter((n): n is string => Boolean(n)),
  )

  return { tabs, activeName, syncRoute, closeTab, keepNames }
}

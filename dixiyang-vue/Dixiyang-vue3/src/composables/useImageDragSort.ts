import { ref, computed, onBeforeUnmount } from 'vue'

const THRESHOLD = 6 // px，超过才进入拖拽（区分点按/滚动）

/**
 * 配图网格拖拽排序（Pointer Events，桌面+触屏通用，零依赖）。
 * 语义：move（从原位抽出，插到落点格子位置），第一张即封面。
 * 用法：grid 容器绑 pointerdown/move/up/cancel → 返回的处理器；
 *       单元格 :class="{ dragging: dragIndex===i, 'drop-target': overIndex===i }"；
 *       网格样式需 touch-action: none（否则触屏先被页面滚动抢走）。
 * 注意：只依赖 .img-grid > .img-cell DOM 结构，被拖数组在 getList() 里原地 splice（reactive 生效）。
 */
export function useImageDragSort(getList: () => string[]) {
  const dragIndex = ref<number | null>(null)
  const overIndex = ref<number | null>(null)
  const ghostSrc = ref('')
  const active = ref(false) // 已过阈值，真正拖拽中
  const ghostPos = ref({ x: 0, y: 0 })

  let pending = false
  let startX = 0
  let startY = 0
  let pointerId = -1
  let fromIdx = -1

  const ghostStyle = computed(() => ({
    left: `${ghostPos.value.x}px`,
    top: `${ghostPos.value.y}px`,
    display: active.value ? 'block' : 'none',
  }))

  const reset = () => {
    pending = false
    active.value = false
    dragIndex.value = null
    overIndex.value = null
    ghostSrc.value = ''
    fromIdx = -1
    document.body.style.userSelect = ''
  }

  const onGridPointerDown = (e: PointerEvent) => {
    const target = e.target as HTMLElement
    // 删除/添加按钮上的按下不启动拖拽
    if (target.closest('.img-del, .img-add')) return
    const cell = target.closest('.img-cell') as HTMLElement | null
    const grid = cell?.parentElement
    if (!cell || !grid) return
    const cells = [...grid.querySelectorAll('.img-cell')]
    const idx = cells.indexOf(cell)
    if (idx < 0) return
    pending = true
    active.value = false
    fromIdx = idx
    startX = e.clientX
    startY = e.clientY
    pointerId = e.pointerId
    grid.setPointerCapture(e.pointerId)
  }

  const onGridPointerMove = (e: PointerEvent) => {
    if (!pending || e.pointerId !== pointerId) return
    if (!active.value) {
      if (Math.hypot(e.clientX - startX, e.clientY - startY) < THRESHOLD) return
      active.value = true
      dragIndex.value = fromIdx
      ghostSrc.value = getList()[fromIdx] ?? ''
      document.body.style.userSelect = 'none'
    }
    ghostPos.value = { x: e.clientX + 12, y: e.clientY + 12 }
    const under = document.elementFromPoint(e.clientX, e.clientY)
    const cell = under?.closest?.('.img-cell') as HTMLElement | null
    const grid = under?.closest?.('.img-grid')
    if (cell && grid) {
      const cells = [...grid.querySelectorAll('.img-cell')]
      const idx = cells.indexOf(cell)
      overIndex.value = idx >= 0 ? idx : null
    } else {
      overIndex.value = null
    }
  }

  const onGridPointerUp = (e: PointerEvent) => {
    if (!pending || e.pointerId !== pointerId) return
    if (active.value && overIndex.value != null && fromIdx >= 0 && overIndex.value !== fromIdx) {
      const list = getList()
      const [moved] = list.splice(fromIdx, 1)
      if (moved !== undefined) list.splice(overIndex.value, 0, moved)
    }
    reset()
  }

  onBeforeUnmount(reset)

  return {
    dragIndex,
    overIndex,
    ghostSrc,
    ghostStyle,
    onGridPointerDown,
    onGridPointerMove,
    onGridPointerUp,
  }
}

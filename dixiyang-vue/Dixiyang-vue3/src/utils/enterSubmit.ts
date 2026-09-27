// 回车提交：在输入框按回车 → 先跳下一可聚焦输入框，最后一框才触发提交
// 用法：@keyup.enter="enterSubmit(handleLogin, $event)"

/** 收集容器内可见的可聚焦输入控件（不含隐藏/禁用/按钮） */
function collectFields(root: ParentNode): HTMLElement[] {
  const sel =
    'input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  return Array.from(root.querySelectorAll<HTMLElement>(sel)).filter((el) => {
    if (el.closest('button, a, [role="button"], [role="combobox"]')) return false
    // el-select / el-input-number 等内部 input 参与跳转
    const style = window.getComputedStyle(el)
    return style.display !== 'none' && style.visibility !== 'hidden'
  })
}

/**
 * 回车处理：
 * 1. 焦点在 textarea/select/按钮/下拉上 → 不处理（交给自身行为）
 * 2. 表单内还有下一个输入框 → 焦点跳到下一框
 * 3. 已是最后一个输入框 → 执行提交 fn
 */
export function enterSubmit(fn: () => unknown, e?: Event) {
  const run = (ev: Event) => {
    const el = ev.target as HTMLElement | null
    if (!el) return
    if (el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') return
    if (el.closest('button, a, .el-select, [role="button"], [role="combobox"]')) return

    const root =
      el.closest('form, .el-form, .creating-card, .settings-wrapper, .dialog-right') as HTMLElement | null
    if (root) {
      const fields = collectFields(root)
      // 当前焦点可能是 input 外层，归一到可聚焦元素
      const current =
        fields.find((f) => f === el || f.contains(el) || el.contains(f)) ?? el
      const idx = fields.indexOf(current as HTMLElement)
      if (idx > -1 && idx < fields.length - 1) {
        ev.preventDefault?.()
        const next = fields[idx + 1]
        next?.focus()
        // 输入框内容全选，便于直接覆盖
        if (next && typeof (next as HTMLInputElement).select === 'function') {
          ;(next as HTMLInputElement).select()
        }
        return
      }
    }
    return fn()
  }

  // 模板两种用法均支持：enterSubmit(fn, $event) 立即执行；enterSubmit(fn) 返回处理器
  if (e) return run(e)
  return run
}

/**
 * 落地页动效编排（单屏 instrument：面板切换 = 签名动效「抽稿换页」）
 * 规则：
 * - 仅在 (min-width: 769px) and (prefers-reduced-motion: no-preference) 下接管；
 *   其余场景由 CSS 静态规则呈现完成态（is-active / 移动端纵向流）
 * - 面板显隐：GSAP 用 inline autoAlpha 覆盖 CSS；动画结束 clearProps 交还给 CSS
 * - 滚轮/方向键驱动切换，转场期间加锁防连发
 */
import { onMounted, onUnmounted, watch, type Ref } from 'vue'
import gsap from 'gsap'

const fmt = (n: number) => Math.round(n).toLocaleString('en-US')

export function useLandingMotion(
  root: Ref<HTMLElement | null>,
  active: Ref<number>,
  count: number,
) {
  let mm: gsap.MatchMedia | null = null
  let tl: gsap.core.Timeline | null = null
  let locked = false
  let desktopMotion = false

  /* 面板内元素入场 + 数字落定（每次切入时播） */
  const playEnter = (panel: HTMLElement) => {
    const items = panel.querySelectorAll<HTMLElement>('[data-ld-in]')
    if (items.length) {
      gsap.fromTo(
        items,
        { y: 20, autoAlpha: 0 },
        {
          y: 0,
          autoAlpha: 1,
          duration: 0.55,
          stagger: 0.06,
          ease: 'power4.out',
          overwrite: 'auto',
        },
      )
    }
    panel.querySelectorAll<HTMLElement>('[data-counter]').forEach((elm) => {
      const target = Number(elm.dataset.counter || 0)
      const state = { v: 0 }
      elm.textContent = fmt(0)
      gsap.to(state, {
        v: target,
        duration: 1.2,
        ease: 'power2.out',
        onUpdate: () => {
          elm.textContent = fmt(state.v)
        },
      })
    })
  }

  /* 抽稿换页：旧稿被抽走（上移+微旋），新稿自下叠上 */
  const swap = (fromIdx: number, toIdx: number) => {
    const el = root.value
    if (!el) return
    const list = Array.from(el.querySelectorAll<HTMLElement>('.ld-panel'))
    const from = list[fromIdx]
    const to = list[toIdx]
    if (!from || !to || from === to) return

    tl?.kill()
    /* 同步设态，避免新面板在 paint 前闪一帧 */
    gsap.set(from, { autoAlpha: 1, y: 0, rotate: 0 })
    gsap.set(to, { autoAlpha: 0, y: 22, rotate: 0.3 })

    locked = true
    tl = gsap.timeline({
      onComplete: () => {
        gsap.set(from, { clearProps: 'opacity,visibility,transform' })
        locked = false
      },
    })
    tl.to(from, { autoAlpha: 0, y: -14, rotate: -0.35, duration: 0.3, ease: 'power3.in' })
      .to(to, { autoAlpha: 1, y: 0, rotate: 0, duration: 0.48, ease: 'power4.out' }, 0.14)
      .add(() => playEnter(to), 0.3)
  }

  const go = (next: number) => {
    if (locked) return
    const clamped = Math.max(0, Math.min(count - 1, next))
    if (clamped === active.value) return
    active.value = clamped
  }

  /* 键盘：↑↓ / PageUp·PageDown 恒切换；←→ 仅在非按钮焦点时切换 */
  const onKey = (e: KeyboardEvent) => {
    if (!desktopMotion) return
    const target = e.target as HTMLElement | null
    const onInteractive = !!target?.closest('button, a')
    let next: number | null = null
    if (e.key === 'ArrowDown' || e.key === 'PageDown') {
      next = active.value + 1
    } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
      next = active.value - 1
    } else if (!onInteractive && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
      next = active.value + (e.key === 'ArrowRight' ? 1 : -1)
    } else if (e.key === 'Home') {
      next = 0
    } else if (e.key === 'End') {
      next = count - 1
    }
    if (next === null) return
    e.preventDefault()
    go(next)
  }

  /* 滚轮：单屏无滚动，deltaY 即切换指令（锁定期内吞掉惯性） */
  const onWheel = (e: WheelEvent) => {
    if (!desktopMotion || locked) return
    if (Math.abs(e.deltaY) < 12) return
    go(active.value + (e.deltaY > 0 ? 1 : -1))
  }

  /* watch：DOM 更新后（is-active 已落位）执行转场 */
  const stopWatch = watch(
    active,
    (val, old) => {
      if (!desktopMotion || old === undefined) return
      swap(old, val)
      /* 焦点跟随（键盘/点击切换后落到对应 tab） */
      const el = root.value
      const tabs = el?.querySelectorAll<HTMLButtonElement>('.ld-index__btn')
      tabs?.[val]?.focus({ preventScroll: true })
    },
    { flush: 'post' },
  )

  onMounted(() => {
    const el = root.value
    if (!el) return

    mm = gsap.matchMedia()
    mm.add(
      '(min-width: 769px) and (prefers-reduced-motion: no-preference)',
      () => {
        desktopMotion = true
        playEnter(el.querySelector('.ld-panel.is-active') ?? el)
        el.addEventListener('wheel', onWheel, { passive: true })
        window.addEventListener('keydown', onKey)
        return () => {
          desktopMotion = false
          el.removeEventListener('wheel', onWheel)
          window.removeEventListener('keydown', onKey)
          tl?.kill()
          gsap.set(el.querySelectorAll('.ld-panel'), {
            clearProps: 'opacity,visibility,transform',
          })
        }
      },
    )
  })

  onUnmounted(() => {
    stopWatch()
    mm?.revert()
  })
}

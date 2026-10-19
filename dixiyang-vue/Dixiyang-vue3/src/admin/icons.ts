/**
 * 控制台自绘导航图标（EP 图标库无「多人 / 多书」语义，按 EP 风格补绘：
 * 1024 viewBox、fill=currentColor、不设宽高由外层 CSS 控制 —— 与 @element-plus/icons-vue 用法完全一致）
 */
import { h } from 'vue'
import type { FunctionalComponent } from 'vue'

/** 多个人（用户管理：管理对象是"用户们"，非单个用户） */
export const UsersNavIcon: FunctionalComponent = () =>
  h('svg', { viewBox: '0 0 1024 1024', xmlns: 'http://www.w3.org/2000/svg', fill: 'currentColor' }, [
    // 后排（右）
    h('circle', { cx: 688, cy: 296, r: 144 }),
    h('path', {
      d: 'M688 504c-132 0-240 100-240 224v96a48 48 0 0 0 48 48h384a48 48 0 0 0 48-48v-96c0-124-108-224-240-224z',
    }),
    // 前排（左，覆盖后排左缘）
    h('circle', { cx: 384, cy: 344, r: 176 }),
    h('path', {
      d: 'M384 552c-152 0-272 108-272 248v72a48 48 0 0 0 48 48h448a48 48 0 0 0 48-48v-72c0-140-120-248-272-248z',
    }),
  ])

/** 多本书（灵感墙管理：管理对象是"本子们"，非单个本子/书） */
export const BooksNavIcon: FunctionalComponent = () =>
  h('svg', { viewBox: '0 0 1024 1024', xmlns: 'http://www.w3.org/2000/svg', fill: 'currentColor' }, [
    h('rect', { x: 176, y: 160, width: 200, height: 560, rx: 28 }),
    h('rect', { x: 424, y: 256, width: 200, height: 464, rx: 28 }),
    h('rect', { x: 672, y: 192, width: 200, height: 528, rx: 28 }),
    // 书架底座
    h('rect', { x: 120, y: 800, width: 784, height: 80, rx: 24 }),
  ])

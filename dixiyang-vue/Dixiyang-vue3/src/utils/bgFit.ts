/**
 * 背景图「端适配」判定（纯函数，无副作用，便于单测）
 *
 * 背景以 `center/cover` 铺满整个视口（`#theme-bg`），因此**图片长宽比决定它在两端被裁掉多少**：
 * - 桌面视口 ≈ 16:9（宽高比 1.78）：横图几乎不裁；竖图只剩中间 `A/1.78` 的高度
 * - 手机视口 ≈ 9:19.5（宽高比 0.46）：竖图几乎不裁；横图只剩中间 `0.46/A` 的宽度
 *
 * 判定口径（含「清晰度门槛」，避免形状合适但放大发虚）：
 * - 竖图 `A ≤ 0.8` 且长边 `≥ 750`（手机 375 宽 @2x 门槛）→ `mobile`
 * - 横图 `A ≥ 1.6` 且长边 `≥ 1920`（1080p 长边门槛）→ `desktop`
 * - 其余（近方图、分辨率不足的横图、≥1.2 的中等比例）→ `both`
 * - 尺寸未知/非法 → `null`（按通用处理，不显示角标）
 *
 * 分析依据与逐图结论见 `dixiyang-vue/docs/背景图端适配分类.md`。
 */
export type BgFit = 'desktop' | 'mobile' | 'both'

/** 横图算「电脑优先」的最小宽高比（16:10） */
export const BG_FIT_DESKTOP_MIN_ASPECT = 1.6
/** 横图算「电脑优先」的最小长边（1920 = 1080p；不到就降级为通用，桌面放大发虚） */
export const BG_FIT_DESKTOP_MIN_LONG_SIDE = 1920
/** 竖图算「手机优先」的最大宽高比（4:5） */
export const BG_FIT_MOBILE_MAX_ASPECT = 0.8
/** 竖图算「手机优先」的最小长边（750 = 手机 375 宽 @2x） */
export const BG_FIT_MOBILE_MIN_LONG_SIDE = 750

/**
 * 判定一张图的端适配
 * @param width 原始宽（px），未知则传 undefined
 * @param height 原始高（px）
 * @returns `desktop` 电脑优先 / `mobile` 手机优先 / `both` 通用 / `null` 尺寸未知
 */
export function classifyBgFit(width?: number | null, height?: number | null): BgFit | null {
  if (!width || !height || width <= 0 || height <= 0) return null
  const aspect = width / height
  const longSide = Math.max(width, height)
  if (aspect <= BG_FIT_MOBILE_MAX_ASPECT) {
    return longSide >= BG_FIT_MOBILE_MIN_LONG_SIDE ? 'mobile' : 'both'
  }
  if (aspect >= BG_FIT_DESKTOP_MIN_ASPECT) {
    return longSide >= BG_FIT_DESKTOP_MIN_LONG_SIDE ? 'desktop' : 'both'
  }
  return 'both'
}

/**
 * 排序权重：当前端对应组 `0` → 通用 `1` → 另一端 `2`（尺寸未知按通用处理）
 * @param fit 分类结果
 * @param current 当前端（按视口长宽比判定：竖屏 = 手机口径）
 */
export function bgFitRank(fit: BgFit | null, current: 'desktop' | 'mobile'): number {
  if (fit === current) return 0
  if (!fit || fit === 'both') return 1
  return 2
}

/** 角标文案：只给明确适合某一端的图打标，通用/未知返回空串 */
export function bgFitBadge(fit: BgFit | null): string {
  if (fit === 'desktop') return '电脑'
  if (fit === 'mobile') return '手机'
  return ''
}

/** 卡片 tooltip 文案（hover/focus 时解释为什么这样分类） */
export function bgFitTip(fit: BgFit | null): string {
  if (fit === 'desktop') return '适合电脑端：横图（16:10 以上、长边 1920 起），手机端只显示中间一条'
  if (fit === 'mobile') return '适合手机端：竖图，手机屏几乎完整显示'
  if (fit === 'both') return '通用：两端都能用，但边缘会被裁掉一部分（主体居中更稳）'
  return '尺寸未探测到，暂按通用处理'
}

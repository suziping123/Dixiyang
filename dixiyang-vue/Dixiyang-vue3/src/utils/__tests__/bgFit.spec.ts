import { describe, expect, it } from 'vitest'
import { bgFitBadge, bgFitRank, bgFitTip, classifyBgFit, type BgFit } from '../bgFit'

describe('classifyBgFit：宽高比 + 清晰度门槛', () => {
  it('竖图（A≤0.8）且长边够 → 手机优先（含上传实测样本）', () => {
    expect(classifyBgFit(1965, 3000)).toBe('mobile') // 5fb72e12… A=0.66
    expect(classifyBgFit(2267, 4000)).toBe('mobile') // b56bfd72… A=0.57
    expect(classifyBgFit(3072, 4096)).toBe('mobile') // 梁俊杰… A=0.75（内置）
  })

  it('横图 A≥1.6 且长边≥1920 → 电脑优先', () => {
    expect(classifyBgFit(2880, 1440)).toBe('desktop') // c42bca35… A=2.0
    expect(classifyBgFit(3840, 2160)).toBe('desktop') // 内置 16:9
    expect(classifyBgFit(1920, 1080)).toBe('desktop') // 边界：正好 1920
  })

  it('横向形状合适但分辨率不足 → 降级通用（桌面放大发虚）', () => {
    expect(classifyBgFit(1200, 659)).toBe('both') // 361ac288… A=1.82 但长边 1200
    expect(classifyBgFit(1180, 715)).toBe('both') // d6261fc0… 长边 1180
    expect(classifyBgFit(1280, 800)).toBe('both') // A=1.6 边界但长边 1280
  })

  it('近方 / 中等比例（1.2~1.6）→ 通用', () => {
    expect(classifyBgFit(4342, 3280)).toBe('both') // 大草原 A=1.32（内置）
    expect(classifyBgFit(1050, 1050)).toBe('both') // 封面方图
    expect(classifyBgFit(810, 530)).toBe('both') // A=1.53
  })

  it('尺寸未知 / 非法 → null（按通用处理，不打角标）', () => {
    expect(classifyBgFit()).toBeNull()
    expect(classifyBgFit(undefined, undefined)).toBeNull()
    expect(classifyBgFit(0, 100)).toBeNull()
    expect(classifyBgFit(100, 0)).toBeNull()
    expect(classifyBgFit(-100, 100)).toBeNull()
  })

  it('门槛边界值逐一校验', () => {
    expect(classifyBgFit(800, 1000)).toBe('mobile') // A=0.8 正好
    expect(classifyBgFit(320, 400)).toBe('both') // A=0.8 但长边 400 < 750
    expect(classifyBgFit(750, 1000)).toBe('mobile') // 长边 1000 ≥ 750
    expect(classifyBgFit(1920, 1200)).toBe('desktop') // A=1.6 正好 + 长边 1920
    expect(classifyBgFit(1919, 1199)).toBe('both') // 长边 1919 < 1920
  })
})

describe('bgFitRank：当前端置顶排序', () => {
  const fits: (BgFit | null)[] = ['desktop', 'both', 'mobile', null]

  it('桌面端视角：电脑 0 → 通用 1 → 手机 2', () => {
    expect(fits.map((f) => bgFitRank(f, 'desktop'))).toEqual([0, 1, 2, 1])
  })

  it('手机端视角：手机 0 → 通用 1 → 电脑 2', () => {
    expect(fits.map((f) => bgFitRank(f, 'mobile'))).toEqual([2, 1, 0, 1])
  })
})

describe('bgFitBadge / bgFitTip', () => {
  it('只有明确的端才打角标', () => {
    expect(bgFitBadge('desktop')).toBe('电脑')
    expect(bgFitBadge('mobile')).toBe('手机')
    expect(bgFitBadge('both')).toBe('')
    expect(bgFitBadge(null)).toBe('')
  })

  it('每种分类都有解释文案', () => {
    for (const fit of ['desktop', 'mobile', 'both', null] as (BgFit | null)[]) {
      expect(bgFitTip(fit).length).toBeGreaterThan(4)
    }
  })
})

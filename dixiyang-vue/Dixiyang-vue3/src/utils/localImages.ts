/**
 * 预设封面图注册表
 *
 * cover_url 格式约定：
 *   - "preset:xxx"  → 从本注册表查找（如 "preset:silicon-age"）
 *   - "https://..."  → 直接作为远程 URL 使用
 *   - 空/null        → 使用默认封面
 *
 * 新增预设封面步骤：
 *   1. 把图片放到 src/images/back/ 目录
 *   2. 在下面 PRESET_COVERS 中添加一行
 */
import siliconAge from '@/images/back/silicon-age.png'

export interface PresetCover {
  id: string       // 唯一标识，对应 cover_url 中的 "preset:{id}"
  label: string    // 前端展示名称
  thumb: string    // 缩略图（import 的图片资源）
}

export const PRESET_COVERS: PresetCover[] = [
  { id: 'silicon-age', label: '硅基时代', thumb: siliconAge },
  // 后续新增封面在这里加，例如：
  // { id: 'cyber-city', label: '赛博都市', thumb: cyberCityImg },
]

const presetMap = new Map(PRESET_COVERS.map(c => [c.id, c]))

/**
 * 解析封面图片路径
 */
export function resolveCoverUrl(coverUrl: string | undefined): string {
  if (!coverUrl) return ''

  // preset:xxx → 从注册表查找
  if (coverUrl.startsWith('preset:')) {
    const id = coverUrl.slice(7)
    const preset = presetMap.get(id)
    return preset ? preset.thumb : ''
  }

  // 完整 URL
  if (coverUrl.startsWith('http://') || coverUrl.startsWith('https://')) {
    return coverUrl
  }

  // 兜底：当作相对路径
  return coverUrl
}

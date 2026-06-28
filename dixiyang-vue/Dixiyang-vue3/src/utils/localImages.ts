/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-05-31 17:39:02
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-05-31 22:05:57
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\utils\localImages.ts
 * @Description: 预设封面图注册表
 *
 * cover_url 格式约定：
 *   - "preset:xxx"      → 从预设目录自动查找（如 "preset:silicon-age"）
 *   - "https://..."     → 直接作为远程 URL 使用
 *   - "/api/uploads/..." → 本地上传的文件（相对路径，自动拼接当前域名）
 *   - 空/null            → 使用默认封面
 *
 * 新增预设封面步骤：
 *   1. 把图片放到 src/images/presets/ 目录
 *   2. 命名格式：{id}.png 或 {id}.jpg（如 silicon-age.png）
 *   3. 无需修改任何代码，直接使用 "preset:{id}" 引用
 */

const PRESET_DIR = '/images/presets/'
const DEFAULT_COVER = '/images/default-cover.png'

export interface PresetCover {
  id: string
  label: string
  thumb: string
}

const presetModules = import.meta.glob('/src/images/presets/*', {
  eager: true,
  query: { inline: '' },
  import: 'default'
}) as Record<string, string>

const PRESET_COVERS: PresetCover[] = Object.keys(presetModules).map(path => {
  const filename = path.split('/').pop() || ''
  const ext = filename.split('.').pop() || ''
  const id = filename.replace(`.${ext}`, '')
  const label = id.split('-').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')

  return {
    id,
    label,
    thumb: presetModules[path]
  }
})

const presetMap = new Map(PRESET_COVERS.map(c => [c.id, c]))

export function resolveNovelCover(coverUrl: string | undefined): string {
  if (!coverUrl) return DEFAULT_COVER
  if (coverUrl.startsWith('http')) return coverUrl
  if (coverUrl.startsWith('/')) return coverUrl

  if (coverUrl.startsWith('preset:')) {
    const key = coverUrl.slice(7)
    const preset = presetMap.get(key)
    if (preset) return preset.thumb
  }

  return DEFAULT_COVER
}

export { PRESET_COVERS, presetMap }

export function resolveCoverUrl(coverUrl: string | undefined): string {
  if (!coverUrl) return ''

  if (coverUrl.startsWith('preset:')) {
    const id = coverUrl.slice(7)
    const preset = presetMap.get(id)
    return preset ? preset.thumb : ''
  }

  if (coverUrl.startsWith('http://') || coverUrl.startsWith('https://')) {
    return coverUrl
  }

  if (coverUrl.startsWith('/')) {
    return coverUrl
  }

  return coverUrl
}

/**
 * 色彩工具库
 * 用于图片采样、亮度计算、文字对比度自适应
 */

/**
 * 从RGB字符串计算相对亮度
 * 使用标准亮度公式：L = (R*0.299 + G*0.587 + B*0.114) / 255
 * @param rgb - RGB字符串或[R,G,B]数组，如 "rgb(255,0,0)" 或 [255,0,0]
 * @returns 亮度值 (0-1)
 */
export function extractBrightness(rgb: string | number[]): number {
  let r = 0, g = 0, b = 0

  if (Array.isArray(rgb)) {
    r = rgb[0] ?? 0
    g = rgb[1] ?? 0
    b = rgb[2] ?? 0
  } else if (typeof rgb === 'string') {
    const match = rgb.match(/\d+/g)
    if (match && match.length >= 3) {
      r = parseInt(match[0] ?? '0')
      g = parseInt(match[1] ?? '0')
      b = parseInt(match[2] ?? '0')
    }
  }

  const brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
  return Math.max(0, Math.min(1, brightness))
}

/**
 * 根据亮度值获取建议的文字颜色
 * @param brightness - 亮度值 (0-1)
 * @param threshold - 亮度阈值，高于此值返回'dark'，低于返回'light'
 * @returns 'light' (浅色/白色) 或 'dark' (深色/黑色)
 */
export function getContrastColor(brightness: number, threshold: number = 0.5): 'light' | 'dark' {
  return brightness > threshold ? 'dark' : 'light'
}

/**
 * 异步采样图片的主色调亮度
 * 使用Canvas绘制图片，采样中心像素
 * @param imageUrl - 图片URL或Base64数据
 * @returns Promise<number> 采样到的亮度值 (0-1)
 */
export async function sampleImageBrightness(imageUrl: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'

    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('无法获取Canvas 2D context'))
          return
        }

        canvas.width = 100
        canvas.height = 100
        ctx.drawImage(img, 0, 0, 100, 100)

        const imageData = ctx.getImageData(50, 50, 1, 1)
        const data = imageData.data
        const brightness = extractBrightness([(data[0] ?? 0), (data[1] ?? 0), (data[2] ?? 0)])

        resolve(brightness)
      } catch (error) {
        reject(error)
      }
    }

    img.onerror = () => {
      reject(new Error(`无法加载图片: ${imageUrl}`))
    }

    img.src = imageUrl
  })
}

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
    // 解析 "rgb(255, 0, 0)" 或 "rgba(255, 0, 0, 1)" 格式
    const match = rgb.match(/\d+/g)
    if (match && match.length >= 3) {
      r = parseInt(match[0] ?? '0')
      g = parseInt(match[1] ?? '0')
      b = parseInt(match[2] ?? '0')
    }
  }

  // 相对亮度公式
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

    // 图片加载完成时的处理
    img.onload = () => {
      try {
        // 创建Canvas并绘制图片
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('无法获取Canvas 2D context'))
          return
        }

        // 设置Canvas大小
        canvas.width = 100
        canvas.height = 100

        // 绘制图片，缩放到Canvas大小
        ctx.drawImage(img, 0, 0, 100, 100)

        // 采样中心像素的图像数据
        const imageData = ctx.getImageData(50, 50, 1, 1)
        const data = imageData.data

        // 提取RGB值
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

/**
 * 获取全局颜色主题CSS变量
 * 注意：所有文字颜色现在由 TextColorCustomizer 全局系统统一管理
 * 此函数仅返回基础CSS变量名，实际颜色值由 useTextColorCustomizer composable 设置
 * @param contrastMode - 'light' 或 'dark'（该参数已弃用，保留仅为向后兼容）
 * @returns CSS变量名的参考
 */
export function getColorThemeVariables(contrastMode: 'light' | 'dark') {
  // 所有文字颜色现在通过 CSS 变量统一管理
  // 这些是可用的 CSS 变量名，具体颜色值由 useTextColorCustomizer 设置
  const cssVariables = {
    '--text-primary': '由 useTextColorCustomizer 管理',
    '--text-secondary': '由 useTextColorCustomizer 管理',
    '--text-muted': '由 useTextColorCustomizer 管理',
    '--text-disabled': '由 useTextColorCustomizer 管理',
    '--description-color': '由 useTextColorCustomizer 管理',
    '--link-color': '由 useTextColorCustomizer 管理',
    '--accent-color': '由 useTextColorCustomizer 管理',
  }

  console.warn(
    '⚠️ getColorThemeVariables() 已弃用。所有文字颜色现在由 TextColorCustomizer 全局系统管理。'
  )

  return cssVariables
}

/**
 * 检查两个颜色之间的对比度（WCAG相对亮度对比度）
 * @param rgb1 - 第一个颜色RGB
 * @param rgb2 - 第二个颜色RGB
 * @returns 对比度值 (1-21)，推荐值 >= 4.5 为可读
 */
export function getContrastRatio(rgb1: number[], rgb2: number[]): number {
  const lum1 = getRelativeLuminance(rgb1)
  const lum2 = getRelativeLuminance(rgb2)

  const lighter = Math.max(lum1, lum2)
  const darker = Math.min(lum1, lum2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * 计算WCAG相对亮度
 * @param rgb - RGB数组 [R,G,B]
 * @returns 相对亮度值 (0-1)
 */
export function getRelativeLuminance(rgb: number[]): number {
  const rCalc = (rgb[0] ?? 0) / 255
  const gCalc = (rgb[1] ?? 0) / 255
  const bCalc = (rgb[2] ?? 0) / 255

  const r = rCalc <= 0.03928 ? rCalc / 12.92 : Math.pow((rCalc + 0.055) / 1.055, 2.4)
  const g = gCalc <= 0.03928 ? gCalc / 12.92 : Math.pow((gCalc + 0.055) / 1.055, 2.4)
  const b = bCalc <= 0.03928 ? bCalc / 12.92 : Math.pow((bCalc + 0.055) / 1.055, 2.4)

  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/**
 * 将HEX颜色转换为RGB数组
 * @param hex - 16进制颜色，如 "#ffffff" 或 "ffffff"
 * @returns RGB数组 [R,G,B]
 */
export function hexToRgb(hex: string): number[] {
  const cleanHex = hex.replace('#', '')
  const r = parseInt(cleanHex.substring(0, 2), 16)
  const g = parseInt(cleanHex.substring(2, 4), 16)
  const b = parseInt(cleanHex.substring(4, 6), 16)
  return [r, g, b]
}

/**
 * 采样图片的多个位置获得更准确的主色调亮度
 * @param imageUrl - 图片URL
 * @param samplePoints - 采样点数量 (默认9个，3x3网格)
 * @returns Promise<number> 平均亮度值
 */
export async function sampleImageBrightnessMultiPoint(
  imageUrl: string,
  samplePoints: number = 9
): Promise<number> {
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

        canvas.width = 300
        canvas.height = 300
        ctx.drawImage(img, 0, 0, 300, 300)

        // 计算采样点数
        const gridSize = Math.sqrt(samplePoints)
        const stepX = 300 / (gridSize + 1)
        const stepY = 300 / (gridSize + 1)

        let totalBrightness = 0
        let count = 0

        // 多点采样
        for (let i = 1; i <= gridSize; i++) {
          for (let j = 1; j <= gridSize; j++) {
            const y = Math.floor(stepY * i)
            const x = Math.floor(stepX * j)

            const imageData = ctx.getImageData(x, y, 1, 1)
            const data = imageData.data
            const brightness = extractBrightness([(data[0] ?? 0), (data[1] ?? 0), (data[2] ?? 0)])
            totalBrightness += brightness
            count++
          }
        }

        const averageBrightness = totalBrightness / count
        resolve(averageBrightness)
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

/**
 * 压缩图片，减小文件大小
 * @param file - 输入的图片文件
 * @param maxWidth - 最大宽度，默认 1920px
 * @param maxHeight - 最大高度，默认 1080px
 * @param quality - 压缩质量 0-1，默认 0.7
 * @returns Promise<string> 压缩后的Data URL
 */
export async function compressImage(
  file: File,
  maxWidth: number = 1920,
  maxHeight: number = 1080,
  quality: number = 0.7
): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (event) => {
      const img = new Image()

      img.onload = () => {
        try {
          // 计算缩放尺寸
          let width = img.width
          let height = img.height

          if (width > maxWidth || height > maxHeight) {
            const aspectRatio = width / height
            if (width > height) {
              width = maxWidth
              height = Math.round(width / aspectRatio)
              if (height > maxHeight) {
                height = maxHeight
                width = Math.round(height * aspectRatio)
              }
            } else {
              height = maxHeight
              width = Math.round(height * aspectRatio)
              if (width > maxWidth) {
                width = maxWidth
                height = Math.round(width / aspectRatio)
              }
            }
          }

          // 创建Canvas并绘制压缩后的图片
          const canvas = document.createElement('canvas')
          canvas.width = width
          canvas.height = height

          const ctx = canvas.getContext('2d')
          if (!ctx) {
            reject(new Error('无法获取Canvas 2D context'))
            return
          }

          ctx.drawImage(img, 0, 0, width, height)

          // 转换为WebP格式或JPEG，质量为指定值
          const mimeType = file.type === 'image/png' ? 'image/png' : 'image/jpeg'
          const compressedDataUrl = canvas.toDataURL(mimeType, quality)

          resolve(compressedDataUrl)
        } catch (error) {
          reject(error)
        }
      }

      img.onerror = () => {
        reject(new Error('图片加载失败'))
      }

      img.src = event.target?.result as string
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsDataURL(file)
  })
}

/**
 * 文字颜色自动适配功能 - 测试演示
 * 这个文件演示了如何使用文字颜色自动适配功能
 */

import { useTextColorAdapter } from '@/composables/useTextColorAdapter'
import { useThemeSystem } from '@/composables/useThemeSystem'
import { sampleImageBrightness, getContrastColor, extractBrightness } from '@/utils/colorUtils'

/**
 * 测试场景 1: 采样浅色背景图片
 */
export async function testLightBackground() {
  const lightImageUrl = 'https://example.com/light-bg.jpg'

  try {
    const brightness = await sampleImageBrightness(lightImageUrl)
    console.log(`亮度: ${brightness}`) // 输出类似: 亮度: 0.7

    const textMode = getContrastColor(brightness, 0.5)
    console.log(`推荐文字模式: ${textMode}`) // 输出: 推荐文字模式: dark (深色文字)
  } catch (error) {
    console.error('采样失败:', error)
  }
}

/**
 * 测试场景 2: 采样深色背景图片
 */
export async function testDarkBackground() {
  const darkImageUrl = 'https://example.com/dark-bg.jpg'

  try {
    const brightness = await sampleImageBrightness(darkImageUrl)
    console.log(`亮度: ${brightness}`) // 输出类似: 亮度: 0.2

    const textMode = getContrastColor(brightness, 0.5)
    console.log(`推荐文字模式: ${textMode}`) // 输出: 推荐文字模式: light (浅色文字)
  } catch (error) {
    console.error('采样失败:', error)
  }
}

/**
 * 测试场景 4: 手动测试RGB颜色亮度
 */
export function testRGBBrightness() {
  // 测试白色
  const whiteBrightness = extractBrightness([255, 255, 255])
  console.log(`白色亮度: ${whiteBrightness}`) // 输出: 1.0

  // 测试黑色
  const blackBrightness = extractBrightness([0, 0, 0])
  console.log(`黑色亮度: ${blackBrightness}`) // 输出: 0.0

  // 测试灰色
  const grayBrightness = extractBrightness([128, 128, 128])
  console.log(`灰色亮度: ${grayBrightness}`) // 输出: 约 0.5

  // 测试红色
  const redBrightness = extractBrightness([255, 0, 0])
  console.log(`红色亮度: ${redBrightness}`) // 输出: 约 0.299
}

/**
 * 测试场景 5: 使用 CSS 变量验证
 */
export function checkCSSVariables() {
  const root = document.documentElement
  const computedStyle = getComputedStyle(root)

  console.log('当前 CSS 变量:')
  console.log('--text-primary:', computedStyle.getPropertyValue('--text-primary'))
  console.log('--text-secondary:', computedStyle.getPropertyValue('--text-secondary'))
  console.log('--description-color:', computedStyle.getPropertyValue('--description-color'))
}

/**
 * 测试场景 6: 完整工作流演示
 */
export async function demoCompleteWorkflow() {
  console.log('=== 开始演示完整工作流 ===\n')

  const textColorAdapter = useTextColorAdapter()

  try {
    console.log('1. 当前状态:')
    console.log(`   文字模式: ${textColorAdapter.textMode.value}`)
    console.log(`   背景亮度: ${textColorAdapter.backgroundBrightness.value}\n`)

    console.log('2. 检查应用的 CSS 变量...')
    checkCSSVariables()
    console.log()

    console.log('=== 演示完成 ===')
  } catch (error) {
    console.error('演示失败:', error)
  }
}

// 导出用于外部调用
export {
  testLightBackground,
  testDarkBackground,
  testRGBBrightness,
  checkCSSVariables,
  demoCompleteWorkflow
}

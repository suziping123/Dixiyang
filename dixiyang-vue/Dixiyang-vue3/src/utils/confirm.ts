/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-24 14:05:51
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-24 14:05:57
 * @FilePath: \Dixiyang\dixiyang-vue\Dixiyang-vue3\src\utils\confirm.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { ElMessageBox } from "element-plus"

/**
 * 确认对话框（危险操作警告）
 * @param message 提示内容
 * @param title 窗口标题，默认「确认操作」；危险删除/登出等场景传「警告」
 * @returns 用户点击确认按钮返回true,点击取消返回false
 */
export function confirmDelete(message: string = "确定删除吗？", title: string = "确认操作"): Promise<boolean> {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    autofocus: false // 危险操作：不自动聚焦确认按钮，避免回车直接触发删除
  }).then(() => true).catch(() => false)
}
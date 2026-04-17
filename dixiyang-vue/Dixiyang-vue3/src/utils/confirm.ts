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
 * 错误消息弹窗组件
 * @param message 错误消息内容
 * @returns Promise<boolean> 用户点击确认按钮返回true,点击取消返回false
 */
export function confirmDelete(message: string = "确定删除吗？"): Promise<boolean> {
  return ElMessageBox.confirm(message, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => true).catch(() => false)
}
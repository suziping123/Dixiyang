<template>
  <!-- 输入弹窗（新建卷/新建章节共用）：复用全局 html .el-dialog 样式与移动端底部抽屉响应式 -->
  <el-dialog v-model="promptState.visible" :title="promptState.title" width="min(420px, 92vw)" @close="onPromptClose">
    <p v-if="promptState.message" class="dlg-text">{{ promptState.message }}</p>
    <el-input
      v-model="promptState.value"
      :placeholder="promptState.placeholder"
      @keyup.enter="closePrompt(promptState.value)"
    />
    <template #footer>
      <el-button @click="closePrompt(null)">取消</el-button>
      <el-button type="primary" @click="closePrompt(promptState.value)">确定</el-button>
    </template>
  </el-dialog>

  <!-- 确认弹窗（删除确认等共用）：danger 时确认钮红色，与角色/时间线页一致 -->
  <el-dialog v-model="confirmState.visible" :title="confirmState.title" width="min(400px, 92vw)" @close="onConfirmClose">
    <p class="dlg-text">{{ confirmState.message }}</p>
    <template #footer>
      <el-button @click="closeConfirm(false)">{{ confirmState.cancelText }}</el-button>
      <el-button :type="confirmState.danger ? 'danger' : 'primary'" @click="closeConfirm(true)">
        {{ confirmState.confirmText }}
      </el-button>
    </template>
  </el-dialog>

  <!-- 离开确认（三态）：保存离开 / 继续离开 / 关闭(X、ESC)=取消离开 -->
  <el-dialog
    v-model="leaveState.visible"
    title="未上传的修改"
    width="min(420px, 92vw)"
    :close-on-click-modal="false"
    @close="onLeaveClose"
  >
    <p class="dlg-text">{{ leaveState.message }}</p>
    <template #footer>
      <el-button @click="closeLeave('cancel')">取消</el-button>
      <el-button @click="closeLeave('leave')">继续离开</el-button>
      <el-button type="primary" @click="closeLeave('save')">保存到云端</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

export interface PromptOptions {
  title: string
  message?: string
  placeholder?: string
  defaultValue?: string
}

export interface ConfirmOptions {
  title: string
  message: string
  danger?: boolean
  confirmText?: string
  cancelText?: string
}

export type LeaveChoice = 'save' | 'leave' | 'cancel'

const promptState = reactive({
  visible: false,
  title: '',
  message: '',
  placeholder: '',
  value: '',
})
const confirmState = reactive({
  visible: false,
  title: '',
  message: '',
  danger: false,
  confirmText: '确定',
  cancelText: '取消',
})
const leaveState = reactive({ visible: false, message: '' })

let promptResolve: ((v: string | null) => void) | null = null
let confirmResolve: ((v: boolean) => void) | null = null
let leaveResolve: ((v: LeaveChoice) => void) | null = null

/** 输入弹窗：返回输入内容，取消/ESC/关闭返回 null */
function prompt(opts: PromptOptions): Promise<string | null> {
  promptState.title = opts.title
  promptState.message = opts.message ?? ''
  promptState.placeholder = opts.placeholder ?? ''
  promptState.value = opts.defaultValue ?? ''
  promptState.visible = true
  return new Promise((res) => {
    promptResolve = res
  })
}
function closePrompt(result: string | null): void {
  promptState.visible = false
  promptResolve?.(result)
  promptResolve = null
}
/** ESC/X 关闭：若按钮未先 resolve，按取消处理 */
function onPromptClose(): void {
  if (promptResolve) {
    promptResolve(null)
    promptResolve = null
  }
}

/** 确认弹窗：确认 true，取消/关闭 false */
function confirm(opts: ConfirmOptions): Promise<boolean> {
  confirmState.title = opts.title
  confirmState.message = opts.message
  confirmState.danger = opts.danger ?? false
  confirmState.confirmText = opts.confirmText ?? '确定'
  confirmState.cancelText = opts.cancelText ?? '取消'
  confirmState.visible = true
  return new Promise((res) => {
    confirmResolve = res
  })
}
function closeConfirm(result: boolean): void {
  confirmState.visible = false
  confirmResolve?.(result)
  confirmResolve = null
}
function onConfirmClose(): void {
  if (confirmResolve) {
    confirmResolve(false)
    confirmResolve = null
  }
}

/** 离开确认三态：save=保存后离开，leave=不保存离开，cancel=取消离开 */
function confirmLeave(message: string): Promise<LeaveChoice> {
  leaveState.message = message
  leaveState.visible = true
  return new Promise((res) => {
    leaveResolve = res
  })
}
function closeLeave(choice: LeaveChoice): void {
  leaveState.visible = false
  leaveResolve?.(choice)
  leaveResolve = null
}
function onLeaveClose(): void {
  if (leaveResolve) {
    leaveResolve('cancel')
    leaveResolve = null
  }
}

defineExpose({ prompt, confirm, confirmLeave })
</script>

<style scoped>
.dlg-text {
  margin: 0 0 14px;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-secondary);
  word-break: break-word;
}
</style>
